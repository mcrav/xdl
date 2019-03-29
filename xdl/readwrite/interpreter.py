import logging
import re
import copy
from typing import Dict, List, Any, Optional, Union
from lxml import etree
from .utils import (convert_time_str_to_seconds, convert_volume_str_to_ml, 
                    convert_mass_str_to_g)
from ..utils import parse_bool
from ..steps import MakeSolution, Step
from ..reagents import Reagent
from ..hardware import Hardware, Component
from .syntax_validation import XDLSyntaxValidator
from ..utils.namespace import (STEP_OBJ_DICT, BASE_STEP_OBJ_DICT)

def xdl_file_to_objs(xdl_file: str, logger: logging.Logger) -> Dict[str, Any]:
    """Given XDL file return steps, hardware and reagents.
    
    Arguments:
        xdl_file (str): Path to XDL file.
    
    Returns:
        Dict: (steps, hardware, reagents)
                  steps: List of Step objects.
                  hardware: Hardware object.
                  reagents: List of Reagent objects.
    """
    with open(xdl_file) as fileobj:
        return xdl_str_to_objs(fileobj.read(), logger)

def xdl_str_to_objs(xdl_str: str, logger: logging.Logger) -> Dict[str, Any]:
    """Given XDL str return steps, hardware and reagents.
    
    Arguments:
        xdl_str (str): XDL str.
    
    Returns:
        Tuple: (steps, hardware, reagents)
                  steps: List of Step objects.
                  hardware: Hardware object.
                  reagents: List of Reagent objects.
    """
    if xdl_str:
        if xdl_valid(xdl_str, logger):
            steps = steps_from_xdl(xdl_str)
            hardware = hardware_from_xdl(xdl_str)
            reagents = reagents_from_xdl(xdl_str)
            synthesis_attrs = synthesis_attrs_from_xdl(xdl_str)
            parsed_xdl = {
                'steps': steps,
                'hardware': hardware,
                'reagents': reagents,
            }
            parsed_xdl['procedure_attrs'] = synthesis_attrs
            return parsed_xdl
        else:
            logger.error('Invalid XDL given.')
    else:
        logger.error('No XDL given.')
    return None

def synthesis_attrs_from_xdl(xdl_str: str) -> Dict[str, Any]:
    """Return attrs from <Synthesis> tag.

    Arguments:
        xdl_str (str): XDL string.

    Returns:
        dict: attr dict from <Synthesis> tag.
    """
    raw_attr = etree.fromstring(xdl_str).attrib
    processed_attr = {}
    for attr_name, attr_type in [
        ('auto_clean', bool),
        ('organic_cleaning_reagent', str),
        ('aqueous_cleaning_reagent', str),
        ('dry_run', bool),
    ]:
        if attr_name in raw_attr:
           processed_attr[attr_name] = raw_attr[attr_name]
           if attr_type == bool:
               processed_attr[attr_name] = parse_bool(raw_attr[attr_name])
    return processed_attr

def xdl_valid(xdl_str: str, logger: logging.Logger = None) -> bool:
    """Return True if XDL is valid, otherwise False.
    
    Arguments:
        xdl_str (str): XDL str.
    
    Returns:
        bool: True if XDL is valid, otherwise False.
    """
    return XDLSyntaxValidator(xdl_str, logger=logger).valid

def steps_from_xdl(xdl_str: str) -> List[Step]:
    """Given XDL str return list of Step objects.
    
    Arguments:
        xdl_str (str): XDL str.
    
    Returns:
        List[Step]: List of Step objects corresponding to procedure described
                      in xdl_str.
    """
    steps = []
    xdl_tree = etree.fromstring(xdl_str)
    for element in xdl_tree.findall('*'):
        if element.tag == 'Procedure':
            for step_xdl in element.findall('*'):
                steps.append(xdl_to_step(step_xdl))
    return steps

def hardware_from_xdl(xdl_str: str) -> Hardware:
    """Given XDL str return Hardware object.
    
    Arguments:
        xdl_str (str): XDL str.
    
    Returns:
        Hardware: Hardware object containing all Component objects described
                    by XDL.
    """
    return Hardware(components_from_xdl(xdl_str))

def components_from_xdl(xdl_str: str) -> List[Component]:
    """Given XDL str return list of Component objects.
    
    Arguments:
        xdl_str (str): XDL str.
    
    Returns:
        List[Component]: List of Component objects corresponding to 
                           components described in xdl_str.
    """
    components = []
    xdl_tree = etree.fromstring(xdl_str)
    for element in xdl_tree.findall('*'):
        if element.tag == 'Hardware':
            for component_xdl in element.findall('*'):
                components.append(xdl_to_component(component_xdl))
    return components

def reagents_from_xdl(xdl_str: str) -> List[Reagent]:
    """Given XDL str return list of Reagent objects.
    
    Arguments:
        xdl_str (str): XDL str.
    
    Returns:
        List[Reagent]: List of Reagent objects corresponding to reagents
                         described in xdl_str.
    """
    reagents = []
    xdl_tree = etree.fromstring(xdl_str)
    for element in xdl_tree.findall('*'):
        if element.tag == 'Reagents':
            for reagent_xdl in element.findall('*'):
                reagents.append(xdl_to_reagent(reagent_xdl))
    return reagents 

def xdl_to_step(xdl_step_element: etree._Element) -> Step:
    """Given XDL step element return corresponding Step object.
    
    Arguments:
       xdl_step_element (lxml.etree._Element): XDL step lxml element.

    Returns:
        Step: Step object corresponding to step in xdl_step_element.
    """
    step_type = STEP_OBJ_DICT[xdl_step_element.tag]
    attr = dict(xdl_step_element.attrib)
    return step_type(**attr)

def xdl_to_component(xdl_component_element: etree._Element) -> Component:
    """Given XDL component element return corresponding Component object.
    
    Arguments:
       xdl_component_element (lxml.etree._Element): XDL component lxml 
                                                      element.

    Returns:
        Component: Component object corresponding to component in 
                     xdl_component_element.
    """
    attr = dict(xdl_component_element.attrib)
    attr['component_type'] = attr['type']
    del attr['type']
    return Component(**attr)

def xdl_to_reagent(xdl_reagent_element: etree._Element) -> Reagent:
    """Given XDL reagent element return corresponding Reagent object.
    
    Arguments:
        xdl_reagent_element (lxml.etree._Element): XDL reagent lxml element.
        
    Returns:
        Reagent: Reagent object corresponding to reagent in 
                   xdl_reagent_element.
    """
    attr = dict(xdl_reagent_element.attrib)
    return Reagent(**attr)