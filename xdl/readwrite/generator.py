from typing import List, Any
from lxml import etree
from ..reagents import Reagent
from ..hardware import Hardware
from ..steps import Add, Step
from ..constants import DEFAULT_VALS, INTERNAL_PROPERTIES

class XDLGenerator(object):   
    """
    Class for generating XDL from lists of hardware, reagents and steps.
    """

    def __init__(
        self,
        steps: List[Step],
        hardware: Hardware,
        reagents: List[Reagent],
        full_properties: bool = False,
    ) -> None:
        """
        Generate XDL from steps, hardware and reagents.
        
        Args:
            steps (List[xdl.steps.Step]): List of Step objects
            hardware (xdl.hardware.Hardware): Hardware object.
            reagents (List[xdl.reagents.Reagent]): List of Reagent objects
            full_properties (bool): If True, all properties will be included.
                If False, only properties that differ from their default values
                and that aren't internal properties will be included.
                Including full properties is recommended for making XDL files
                that will stand the test of time, as defaults may change in new
                versions of XDL.
        """
        self.hardware, self.reagents, self.steps = hardware, reagents, steps
        self.full_properties = full_properties
        self._generate_xdl()

    def _generate_xdl(self) -> None:
        """Generate XDL tree."""
        self.xdltree = etree.Element('Synthesis')
        self._append_hardware_tree()
        self._append_reagents_tree()
        self._append_procedure_tree()

    def _append_hardware_tree(self) -> None:
        """Create and add Hardware section to XDL tree."""
        hardware_tree = etree.Element('Hardware')
        for component in self.hardware:
            component_tree = etree.Element('Component')
            for prop, val in component.properties.items():
                if prop == 'xid': prop = 'id'
                if val != None:
                    if prop == 'component_type':
                        component_tree.attrib['type'] = str(val)
                    else:
                        component_tree.attrib[prop] = str(val)
            hardware_tree.append(component_tree)
        self.xdltree.append(hardware_tree)

    def _append_reagents_tree(self) -> None:
        """Create and add Reagents section to XDL tree."""
        reagents_tree = etree.Element('Reagents')
        for reagent in self.reagents:
            reagent_tree = etree.Element('Reagent')
            for prop, val in reagent.properties.items():
                if prop == 'xid': prop = 'id'
                if val != None:
                    reagent_tree.attrib[prop] = str(val)
            reagents_tree.append(reagent_tree)
        self.xdltree.append(reagents_tree)

    def _append_procedure_tree(self) -> None:
        """Create and add Procedure section to XDL tree."""
        procedure_tree = etree.Element('Procedure')
        for step in self.steps:
            step_tree = etree.Element(step.name)
            for prop, val in step.properties.items():
                if val != None:
                    # if self.full_properties is False ignore some properties.
                    if not self.full_properties:
                        # Don't write properties that are the same as the default.
                        if (step.name in DEFAULT_VALS
                            and prop in DEFAULT_VALS[step.name]
                            and DEFAULT_VALS[step.name][prop] == val):
                            continue
                        
                        # Don't write internal properties.
                        elif (step.name in INTERNAL_PROPERTIES
                             and prop in INTERNAL_PROPERTIES[step.name]):
                             continue
                    # Convert value to nice units and add to element attrib.
                    step_tree.attrib[prop] = format_property(prop, val)

            procedure_tree.append(step_tree)
        self.xdltree.append(procedure_tree)

    def save(self, save_file: str) -> None:
        """Save XDL tree to given file path."""
        with open(save_file, 'w') as fileobj:
            fileobj.write(self.as_string())

    def as_string(self) -> str:
        """Return XDL tree as XML string."""
        return get_xdl_string(self.xdltree)

def get_xdl_string(xdltree: etree._ElementTree) -> str:
    """Convert XDL etree to pretty XML string.
    
    Args:
        xdltree (etree.ElementTree): etree of XDL

    Returns:
        str: XML string
    """
    indent = '  '
    # Synthesis tag
    s = '<Synthesis>\n'
    indent_level = 1
    # Hardware, Reagents and Procedure tags
    for element in xdltree.findall('*'):
        s += f'{indent * indent_level}<{element.tag}>\n'
        indent_level += 1
        # Component, Reagent and Step tags
        for element2 in element.findall('*'):
            s += f'{indent * indent_level}<{element2.tag}\n'
            indent_level += 1
            # Element Properties
            for attr, val in element2.attrib.items():
                if val != None:
                    s += f'{indent * indent_level}{attr}="{val}"\n'
            s = s[:-1] + ' />\n'
            indent_level -= 1
        indent_level -= 1
        s += f'{indent * indent_level}</{element.tag}>\n\n'
    s += '</Synthesis>\n'
    return s

def format_property(prop: str, val: Any) -> str:
    """Given property key and value in standard units, convert value
    to sensitive units and return str ready for putting in XDL.
    E.g. time: 3600 -> '1 hr', volume 2000 -> '2 l'.
    If no modifications are required just return str of val.
    
    Args:
        prop (str): Property name.
        val (Any): Property value.
    
    Returns:
        str: Value converted to nice units if necessary and returned
            as neat str ready for outputting.
    """
    if 'time' in prop:
        return format_time(val)
    
    elif 'volume' in prop:
        return format_volume(val)

    elif 'mass' in prop:
        return format_mass(val)

    elif 'temp' in prop:
        return format_temp(val)

    elif type(val) == list:
        return ' '.join([str(item) for item in val])

    return str(val)
    
def format_volume(val_ml: float) -> str:
    """Return formatted volume in sensible units.
    
    Args:
        val_ml (float): Volume in mL.
    
    Returns:
        str: Formatted volume in sensible units.
    """
    # litres
    if val_ml > 1000:
        l = val_ml / 1000
        return f'{format_val(l)} l'
    # microlitres
    elif val_ml < 0.1:
        ul = val_ml * 1000
        return f'{format_val(ul)} ul'
    # millilitres
    return f'{format_val(val_ml)} mL'

def format_time(val_seconds: float) -> str:
    """Return formatted time in sensible units.
    
    Args:
        val_seconds (float): Time in seconds.
    
    Returns:
        str: Formatted time in sensible units.
    """
    val = val_seconds
    if val_seconds > 60:
        minutes = val_seconds / 60
        # hours
        if minutes > 60:
            hours = minutes / 60
            val_str = f'{format_val(hours)} hrs'
            val = hours
        # minutes
        else:
            val_str = f'{format_val(minutes)} mins'
            val = minutes
    # seconds
    else:
        val_str = f'{format_val(val_seconds)} secs'
    # Convert '1 hrs' to '1 hr'.
    if val == 1:
        val_str = val_str[:-1]
    return val_str
    
def format_mass(val_grams: float) -> str:
    """Return formatted mass in sensible units.
    
    Args:
        val_grams (float): Mass in grams.
    
    Returns:
        str: Formatted mass in sensible units.
    """
    if val_grams > 1000:
        # kilograms
        kg = val_grams / 1000
        return f'{format_val(kg)} kg'
    elif val_grams < 0.1:
        # milligrams
        mg = val_grams * 1000
        return f'{format_val(mg)} mg'
    # grams
    return f'{format_val(val_grams)} g'

def format_temp(val_celsius: float) -> str:
    """Return formatted temperature.
    
    Args:
        val_celsius (float): Temperature in °C.
    
    Returns:
        str: Formatted temperature. 
    """
    if type(val_celsius) == str: # 'reflux' or 'None'
        return val_celsius
    else:
        return f'{format_val(val_celsius)}°C'

def format_val(val: float) -> str:
    """Format float and return as str. Rules are round to two decimal places,
    then remove any trailing 0s and decimal point if necessary.
    
    Args:
        val (float): Number to format.
    
    Returns:
        str: Number rounded to two decimal places with trailing '0' and '.'
            removed.
    """
    hours_str = f'{val:.2f}'
    return hours_str.rstrip('0').rstrip('0').rstrip('.')
    