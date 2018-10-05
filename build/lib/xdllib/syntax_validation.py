from lxml import etree
from io import StringIO
from .namespace import XDL_STEP_NAMESPACE, XDL_HARDWARE_NAMESPACE
from .utils import float_regex
from .steps import MakeSolution
import inspect
import re
import traceback

ACCEPTABLE_MASS_UNITS = ['ug', 'mg', 'g', 'kg']
ACCEPTABLE_VOLUME_UNITS = ['ul', 'ml', 'cl', 'dl', 'l', 'cc']
XDL_ACCEPTABLE_UNITS = {
    'volume': ACCEPTABLE_VOLUME_UNITS,
    'mass': ACCEPTABLE_MASS_UNITS,
    'mol': ['umol', 'mmol', 'mol'],
    'time': ['s', 'sec', 'secs', 'second', 'seconds', 'm', 'min', 'mins', 'minute', 'minutes', 'h', 'hr', 'hrs', 'hour', 'hours'],
    'temperature': ['c', 'k', 'f'],
    'solute_masses': ACCEPTABLE_MASS_UNITS,
    'solvent_volume': ACCEPTABLE_VOLUME_UNITS,
}

XDL_STEP_COMPULSORY_ATTRIBUTES = {
    'Add': ['reagent', 'vessel', 'quantity'],
}

REAGENT_QUANTITY_ATTRIBUTES = ['mass', 'mol', 'volume'] # step properties that expect a quantity

REAGENT_ATTRIBS = ['reagent', 'solute', 'solvent'] # step properties that expect a reagent declared in Reagents section

class XDLSyntaxValidator(object):
    """
    Validate that XDL is syntactically correct.
    """

    def __init__(self, xdl, validate=True):
        """
        Load and validate XDL.
        """
        try:
            self.xdl_tree = etree.parse(StringIO(xdl))
            self.components = self.get_section_children('Hardware')
            self.reagents = self.get_section_children('Reagents')
            self.steps = self.get_section_children('Procedure')
            if validate:
                self.validate_xdl()

        except Exception:
            self.valid = False
            traceback.print_exc()
            print('\nFailed to load XDL.')
        
    def validate_xdl(self):
        """Run all validation tests on XDL and store result in self.valid."""
        self.valid = (self.has_three_base_tags() and self.all_reagents_declared() and self.all_vessels_declared() and
                      self.steps_in_namespace() and self.hardware_in_namespace() and self.check_quantities() and
                      self.check_step_attributes())

    def get_section_children(self, section):
        """Get children of given section tag."""
        for element in self.xdl_tree.findall('*'):
            if element.tag == section:
                return element.findall('*')
        return []

    def has_three_base_tags(self):
        """
        Check file has Hardware, Reagents and Procedure sections and nothing else.
        """
        has_hardware = False
        has_reagents = False
        has_procedure = False
        extra_sections = False
        for element in self.xdl_tree.findall('*'):
            if element.tag == 'Hardware':
                has_hardware = True
            elif element.tag == 'Reagents':
                has_reagents = True
            elif element.tag == 'Procedure':
                has_procedure = True
            else:
                self.print_syntax_error(f'Unrecognised element: <{element.tag}>', element)
                extra_sections = True
        for has_section, name in zip([has_hardware, has_reagents, has_procedure], ['Hardware', 'Reagents', 'Procedure']):
            if not has_section:
                self.print_syntax_error(f'Missing section: <{name}>')
        return has_hardware and has_reagents and has_procedure and not extra_sections   

    def all_reagents_declared(self):
        """
        Check all reagents used in steps are declared in the Reagents section.
        """
        declared_reagent_ids = [reagent.attrib['rid'] for reagent in self.reagents]
        all_reagents_declared = True
        for step in self.steps:
            for reagent_attrib in REAGENT_ATTRIBS:
                if reagent_attrib in step.attrib:
                    step_reagents = step.attrib[reagent_attrib]
                    if ' ' in step_reagents:
                        step_reagents = step_reagents.split(' ')
                    else:
                        step_reagents = [step_reagents]
                    for reagent in step_reagents:
                        if reagent not in declared_reagent_ids:
                            all_reagents_declared = False
                            self.print_syntax_error(f'{reagent} used in procedure but not declared in <Reagent> section.', step)
        return all_reagents_declared

    def all_vessels_declared(self):
        """
        Check all vessels used in steps are declared in the Hardware section.
        """
        declared_vessel_ids = [component.attrib['cid'] for component in self.components]
        all_vessels_declared = True
        for step in self.steps:
            for attr, val in step.attrib.items():
                if attr == 'vessel':
                    if not val in declared_vessel_ids:
                        all_vessels_declared = False
                        self.print_syntax_error(f'{val} used in procedure but not declared in <Hardware> section.', step)
        return all_vessels_declared

    def steps_in_namespace(self):
        """Check all step tags are in the XDL namespace."""
        steps_recognised = True
        for step in self.steps:
            if step.tag not in XDL_STEP_NAMESPACE:
                self.print_syntax_error(f'{step.tag} is not a recognised step type.', step)
                steps_recognised = False
        return steps_recognised
        
    def hardware_in_namespace(self):
        """Check all the component tags are in the XDL namespace."""
        hardware_recognised = True
        for component in self.components:
            if component.tag not in XDL_HARDWARE_NAMESPACE:
                self.print_syntax_error(f'{component.tag} is not a recognised component type.', component)
                hardware_recognised = False
        return hardware_recognised

    def check_quantities(self):
        """Check all quantities are in a valid format."""
        quantities_valid = True
        for component in self.components:
            for attr, val in component.attrib.items():
                if attr == 'volume':
                    if not self.check_quantity_syntax(attr, val, component):
                        quantities_valid = False
        for step in self.steps:
            for attr, val in step.attrib.items():
                if attr in ['volume', 'mol', 'mass', 'temperature', 'time']:
                    if not self.check_quantity_syntax(attr, val, step):
                        quantities_valid = False
                elif attr in ['volumes', 'solute_masses']:
                    for item in val.split(' '):
                        if not self.check_quantity_syntax(attr, item, step):
                            quantities_valid = False
        return quantities_valid

    def check_quantity_syntax(self, quantity_type, quantity_str, quantity_element):
        """
        Check quantity is in valid format.
        
        Arguments:
            quantity_type {str} -- XDL attribute, i.e. 'mass', 'volume', 'time', 'temperature'
            quantity_str {str} -- XDL value, i.e. '5g', '20 ml', '2hrs', '77'
            quantity_element {Step} -- Step object containing quantity
        
        Returns:
            bool -- True is quantity is valid, otherwise False
        """
        if len(quantity_str.split(' ')) > 1:
            return False
        quantity_valid = True
        quantity_str = quantity_str.lower()
        number_match = re.match(float_regex, quantity_str)
        if number_match is None:
            quantity_valid = False
            number = ''
        else:
            number = number_match.group(1)
        try:
            f = float(number)
        except ValueError:
            quantity_valid = False
        remainder = quantity_str.lstrip(number)
        if not remainder:
            quantity_valid = True
        elif remainder.strip() not in XDL_ACCEPTABLE_UNITS[quantity_type]:
            quantity_valid = False
        else:
            quantity_valid = True
        if not quantity_valid:
            self.print_syntax_error(f'{quantity_str} is not a valid {quantity_type}.\nAcceptable units are {", ".join(XDL_ACCEPTABLE_UNITS[quantity_type])}',
                                quantity_element)
        return quantity_valid

    def check_step_attributes(self):
        """Check that all compulsory Step attributes are present."""
        step_attributes_valid = True
        for step in self.steps:
            # Check length of solutes and solute_masses lists are the same
            if isinstance(step, MakeSolution):
                if len(step.solutes.split()) != len(step.solute_masses.split()):
                    self.print_syntax_error('Length of solutes and solute_masses lists are different.', step)
            if step.tag in XDL_STEP_COMPULSORY_ATTRIBUTES:
                has_quantity = True
                for attr in XDL_STEP_COMPULSORY_ATTRIBUTES[step.tag]:
                    # 'quantity' wildcard used if mass and volume are both acceptable, but
                    # one of them must be present.
                    if attr == 'quantity':
                        has_quantity = False
                        for quantity_attr in REAGENT_QUANTITY_ATTRIBUTES:
                            if quantity_attr in step.attrib:
                                has_quantity = True
                                break
                    elif attr not in step.attrib:
                        self.print_syntax_error(f'Step missing {attr} attribute.', step)
                        step_attributes_valid = False
                if not has_quantity:
                    self.print_syntax_error(f'Step missing {attr} attribute.', step)
                    step_attributes_valid = False
        return step_attributes_valid

    def print_syntax_error(self, error, element=None):
        """Print syntax error.
        
        Arguments:
            error {str} -- Error message.
        
        Keyword Arguments:
            element {lxml.etree.Element} -- Element producing error. Used to give an error line number.
        """
        s = 'XDL Syntax Error'
        if element is not None:
            s += f' (line {element.sourceline}): '
        else:
            s += ': '
        s += error
        print(s + '\n')


