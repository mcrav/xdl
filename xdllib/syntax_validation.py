from lxml import etree
from io import StringIO
import xdllib.steps_chasm
import xdllib.steps_xdl
import xdllib.components
import inspect
import re
from .utils import float_regex

class XDLSyntaxValidator(object):

    def __init__(self, xdl):
        self.xdl_tree = etree.parse(StringIO(xdl))
        self.components = self.get_section_children('Hardware')
        self.reagents = self.get_section_children('Reagents')
        self.steps = self.get_section_children('Procedure')
        self.validate_xdl()

    def validate_xdl(self):
        self.valid = (self.has_three_base_tags() and self.all_reagents_declared() and self.all_vessels_declared() and
                      self.steps_in_namespace() and self.hardware_in_namespace() and self.check_quantities() and
                      self.check_step_attributes())

    def get_section_children(self, section):
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
        declared_reagent_ids = [reagent.attrib['id'] for reagent in self.reagents]
        used_reagent_ids = [step.attrib['reagent'] for step in self.steps if 'reagent' in step.attrib]
        used_reagent_elements = [step for step in self.steps if 'reagent' in step.attrib] # Could be optimised
        all_reagents_declared = True
        for reagent_id, reagent_element in zip(used_reagent_ids, used_reagent_elements):
            if reagent_id not in declared_reagent_ids:
                all_reagents_declared = False
                self.print_syntax_error(f'{reagent_id} used in procedure but not declared in <Reagent> section.', reagent_element)
        return all_reagents_declared

    def all_vessels_declared(self):
        """
        Check all vessels used in steps are declared in the Hardware section.
        """
        declared_vessel_ids = [component.attrib['id'] for component in self.components]
        used_vessel_ids = []
        used_vessel_elements = []
        for step in self.steps:
            for attr, val in step.attrib.items():
                if 'vessel' in attr:
                    used_vessel_ids.append(val)
                    used_vessel_elements.append(step)
        all_vessels_declared = True
        for vessel_id, vessel_element in zip(used_vessel_ids, used_vessel_elements):
            if vessel_id not in declared_vessel_ids:
                all_vessels_declared = False
                self.print_syntax_error(f'{vessel_id} used in procedure but not declared in <Hardware> section.', vessel_element)
        return all_vessels_declared

    def steps_in_namespace(self):
        steps_recognised = True
        for step in self.steps:
            if step.tag not in XDL_STEP_NAMESPACE:
                self.print_syntax_error(f'{step.tag} is not a recognised step type.', step)
                steps_recognised = False
        return steps_recognised
        
    def hardware_in_namespace(self):
        hardware_recognised = True
        for component in self.components:
            if component.tag not in XDL_HARDWARE_NAMESPACE:
                self.print_syntax_error(f'{component.tag} is not a recognised component type.', component)
                hardware_recognised = False
        return hardware_recognised

    def check_quantities(self):
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
        return quantities_valid

    def check_quantity_syntax(self, quantity_type, quantity_str, quantity_element):
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
            print(remainder.strip())
            quantity_valid = False
        else:
            quantity_valid = True
        if not quantity_valid:
            self.print_syntax_error(f'{quantity_str} is not a valid {quantity_type}.\nAcceptable units are {", ".join(XDL_ACCEPTABLE_UNITS[quantity_type])}',
                                quantity_element)
        return quantity_valid

    def check_step_attributes(self):
        step_attributes_valid = True
        for step in self.steps:
            if step.tag in XDL_STEP_COMPULSORY_ATTRIBUTES:
                has_quantity = True
                for attr in XDL_STEP_COMPULSORY_ATTRIBUTES[step.tag]:
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
        s = 'XDL Syntax Error'
        if element is not None:
            s += f' (line {element.sourceline}): '
        else:
            s += ': '
        s += error
        print(s + '\n')



# Get Namespace

def get_class_names_from_module(mod):
    return [item[0] for item in inspect.getmembers(mod, inspect.isclass)]

XDL_STEP_NAMESPACE = get_class_names_from_module(xdllib.steps_chasm)
XDL_STEP_NAMESPACE.extend(get_class_names_from_module(xdllib.steps_xdl))
XDL_STEP_NAMESPACE.extend([
    'Heat',
    'Stir',
])

XDL_HARDWARE_NAMESPACE = [item for item in get_class_names_from_module(xdllib.components) if item not in ['XDLElement', 'Component', 'Hardware']]

XDL_ACCEPTABLE_UNITS = {
    'volume': ['ul', 'ml', 'cl', 'dl', 'l', 'cc'],
    'mass': ['ug', 'mg', 'g', 'kg'],
    'mol': ['umol', 'mmol', 'mol'],
    'time': ['s', 'sec', 'secs', 'second', 'seconds', 'm', 'min', 'mins', 'minute', 'minutes', 'h', 'hr', 'hrs', 'hour', 'hours'],
    'temperature': ['c', 'k', 'f'],
}

step_files = ['steps_chasm.py', 'steps_xdl']

XDL_STEP_COMPULSORY_ATTRIBUTES = {
    'Add': ['reagent', 'vessel', 'quantity'],
}

REAGENT_QUANTITY_ATTRIBUTES = ['mass', 'mol', 'volume']

