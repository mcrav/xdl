from lxml import etree
from .utils import (convert_time_str_to_seconds, convert_volume_str_to_ml, 
                    convert_mass_str_to_g, parse_bool)
from ..steps import MakeSolution
from ..reagents import Reagent
from ..hardware import Hardware, Component
from .syntax_validation import XDLSyntaxValidator
from ..utils.namespace import (STEP_OBJ_DICT, BASE_STEP_OBJ_DICT)
from ..constants import XDL_HARDWARE_CHEMPUTER_CLASS_MAP

def xdl_file_to_objs(xdl_file, logger):
    """Given XDL file return steps, hardware and reagents.
    
    Arguments:
        xdl_file {str} -- Path to XDL file.
    
    Returns:
        Tuple -- (steps, hardware, reagents)
                  steps    -- List of Step objects.
                  hardware -- Hardware object.
                  reagents -- List of Reagent objects.
    """
    with open(xdl_file) as fileobj:
        return xdl_str_to_objs(fileobj.read(), logger)

def xdl_str_to_objs(xdl_str, logger):
    """Given XDL str return steps, hardware and reagents.
    
    Arguments:
        xdl_str {str} -- XDL str.
    
    Returns:
        Tuple -- (steps, hardware, reagents)
                  steps    -- List of Step objects.
                  hardware -- Hardware object.
                  reagents -- List of Reagent objects.
    """
    if xdl_str:
        if xdl_valid(xdl_str):
            steps = steps_from_xdl(xdl_str)
            hardware = hardware_from_xdl(xdl_str)
            reagents = reagents_from_xdl(xdl_str)
            synthesis_attrs = synthesis_attrs_from_xdl(xdl_str)
            parsed_xdl = {
                'steps': steps,
                'hardware': hardware,
                'reagents': reagents,
            }
            parsed_xdl.update(synthesis_attrs)
            return parsed_xdl
        else:
            logger.error('Invalid XDL given.')
    else:
        logger.error('No XDL given.')
    return None

def synthesis_attrs_from_xdl(xdl_str):
    """Return attrs from <Synthesis> tag.

    Arguments:
        xdl_str (str): XDL string.

    Returns:
        dict: attr dict from <Synthesis> tag.
    """
    return etree.fromstring(xdl_str).attrib

def xdl_valid(xdl_str):
    """Return True if XDL is valid, otherwise False.
    
    Arguments:
        xdl_str {str} -- XDL str.
    
    Returns:
        bool -- True if XDL is valid, otherwise False.
    """
    return XDLSyntaxValidator(xdl_str).valid

def steps_from_xdl(xdl_str):
    """Given XDL str return list of Step objects.
    
    Arguments:
        xdl_str {str} -- XDL str.
    
    Returns:
        List[Step] -- List of Step objects corresponding to procedure described
                      in xdl_str.
    """
    steps = []
    xdl_tree = etree.fromstring(xdl_str)
    for element in xdl_tree.findall('*'):
        if element.tag == 'Procedure':
            for step_xdl in element.findall('*'):
                steps.append(xdl_to_step(step_xdl))
    return steps

def hardware_from_xdl(xdl_str):
    """Given XDL str return Hardware object.
    
    Arguments:
        xdl_str {str} -- XDL str.
    
    Returns:
        Hardware -- Hardware object containing all Component objects described
                    by XDL.
    """
    return Hardware(components_from_xdl(xdl_str))

def components_from_xdl(xdl_str):
    """Given XDL str return list of Component objects.
    
    Arguments:
        xdl_str {str} -- XDL str.
    
    Returns:
        List[Component] -- List of Component objects corresponding to 
                           components described in xdl_str.
    """
    components = []
    xdl_tree = etree.fromstring(xdl_str)
    for element in xdl_tree.findall('*'):
        if element.tag == 'Hardware':
            for component_xdl in element.findall('*'):
                components.append(xdl_to_component(component_xdl))
    return components

def reagents_from_xdl(xdl_str):
    """Given XDL str return list of Reagent objects.
    
    Arguments:
        xdl_str {str} -- XDL str.
    
    Returns:
        List[Reagent] -- List of Reagent objects corresponding to reagents
                         described in xdl_str.
    """
    reagents = []
    xdl_tree = etree.fromstring(xdl_str)
    for element in xdl_tree.findall('*'):
        if element.tag == 'Reagents':
            for reagent_xdl in element.findall('*'):
                reagents.append(xdl_to_reagent(reagent_xdl))
    return reagents 

def xdl_to_step(xdl_step_element):
    """Given XDL step element return corresponding Step object.
    
    Arguments:
       xdl_step_element {lxml.etree._Element} -- XDL step lxml element.

    Returns:
        Step -- Step object corresponding to step in xdl_step_element.
    """
    step_type = STEP_OBJ_DICT[xdl_step_element.tag]
    return step_type(
        **preprocess_step_attrib(step_type, xdl_step_element.attrib)
    )

def xdl_to_component(xdl_component_element):
    """Given XDL component element return corresponding Component object.
    
    Arguments:
       xdl_component_element {lxml.etree._Element} -- XDL component lxml 
                                                      element.

    Returns:
        Component -- Component object corresponding to component in 
                     xdl_component_element.
    """
    attr = preprocess_attrib(xdl_component_element.attrib)
    attr['type'] = XDL_HARDWARE_CHEMPUTER_CLASS_MAP[
        xdl_component_element.tag]
    component = Component(attr['xid'], attr)  
    return component

def xdl_to_reagent(xdl_reagent_element):
    """Given XDL reagent element return corresponding Reagent object.
    
    Arguments:
        xdl_reagent_element {lxml.etree._Element} -- XDL reagent lxml element.
        
    Returns:
        Reagent -- Reagent object corresponding to reagent in 
                   xdl_reagent_element.
    """
    reagent = Reagent()
    reagent.load_properties(preprocess_attrib(xdl_reagent_element.attrib))
    return reagent

def preprocess_step_attrib(step_type, attrib):
    """Process:
    1. Convert strs to bools i.e. 'false' -> False
    2. Convert all time strs to floats with second as unit.
    3. Convert all volume strs to floats with mL as unit.
    4. Convert all mass strs to floats with mL as unit.
    5. Convert MakeSolution solutes and solute_masses attributes to lists.

    Arguments:
        step {Step} -- Step object to preprocess attributes for.
        attrib {lxml.etree._Attrib} -- Raw attribute dictionary from XDL
    
    Returns:
        dict -- Dict of processed attributes.
    """
    attr = preprocess_attrib(attrib)
    if 'clean_tubing' in attr:
        if attr['clean_tubing'].lower() == 'false':
            attr['clean_tubing'] = False
        else:
            attr['clean_tubing'] = True

    if 'time' in attr:
        attr['time'] = convert_time_str_to_seconds(attr['time'])
    
    if 'volume' in attr and attr['volume'] != 'all':
        attr['volume'] = convert_volume_str_to_ml(attr['volume'])

    if 'solvent_volume' in attr:
        attr['solvent_volume'] = convert_volume_str_to_ml(attr['solvent_volume'])

    if 'mass' in attr:
        attr['mass'] = convert_mass_str_to_g(attr['mass'])

    if 'product_bottom' in attr:
        attr['product_bottom'] = parse_bool(attr['product_bottom'])

    if step_type == MakeSolution:
        attr['solutes'] = attr['solutes'].split(' ')
        attr['solute_masses'] = attr['solute_masses'].split(' ')
        attr['solute_masses'] = [convert_mass_str_to_g(item) 
                                 for item in attr['solute_masses']]
    return attr

def preprocess_attrib(attrib):
    """Change id key to xid.
    
    Args:
        attrib (lxml.etree._Attrib): Raw attribute dictionary from XDL
    
    Returns:
        dict: Dict of processed attributes.
    """
    attr = dict(attrib)
    if 'id' in attr:
        attr['xid'] = attr['id']
        del attr['id']
    return attr
