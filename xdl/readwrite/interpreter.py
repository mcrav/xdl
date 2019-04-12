import logging
import re
import copy
from typing import Dict, List, Any, Optional, Union
from lxml import etree
from .validation import check_attrs_are_valid
from .utils import (convert_time_str_to_seconds, convert_volume_str_to_ml, 
                    convert_mass_str_to_g)
from ..constants import SYNTHESIS_ATTRS
from ..utils import parse_bool, XDLError, raise_error
from ..steps import MakeSolution, Step
from ..reagents import Reagent
from ..hardware import Hardware, Component
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
        try:
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
        except Exception as e:
            raise_error(e, 'Error parsing XDL.')
    else:
        raise XDLError('Empty XDL given.')
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
    for attr in SYNTHESIS_ATTRS: 
        if attr['name'] in raw_attr:
           processed_attr[attr['name']] = raw_attr[attr['name']]
           if attr['type'] == bool:
               processed_attr[attr['name']] = parse_bool(raw_attr[attr['name']])
    return processed_attr

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
    # Check if step name is valid and get step class.
    if not xdl_step_element.tag in STEP_OBJ_DICT:
        raise XDLError(f'{xdl_step_element.tag} is not a valid step type.')
    step_type = STEP_OBJ_DICT[xdl_step_element.tag]
    # Check all attributes are valid.
    attrs = dict(xdl_step_element.attrib)
    check_attrs_are_valid(attrs, step_type)
    # Try to instantiate step, any invalid values given will throw an error
    # here.
    try:
        step = step_type(**attrs)
    except Exception as e:
        raise_error(
            e,
            f'Error instantiating {step_type.__name__} step with following properties: \n{attrs}')
    return step

def xdl_to_component(xdl_component_element: etree._Element) -> Component:
    """Given XDL component element return corresponding Component object.
    
    Arguments:
       xdl_component_element (lxml.etree._Element): XDL component lxml 
                                                      element.

    Returns:
        Component: Component object corresponding to component in 
                     xdl_component_element.
    """
    attrs = dict(xdl_component_element.attrib)
    # Check 'id' is in attrs..
    if not 'id' in attrs:
        raise XDLError(
            "'id' attribute not specified for component.")
    #  Check 'type' is in attrs.
    if not 'type' in attrs:
        raise XDLError(
            f"'type' attribute not specified for {attrs['id']} component.")
    check_attrs_are_valid(attrs, Component)
    # Rename 'type' attr to 'component_type' to avoid conflict with Python
    # built-in function type.
    attrs['component_type'] = attrs['type']
    del attrs['type']
    # Try to instantiate components, any invalid values given will throw an
    # error here.
    try:
        component = Component(**attrs)
    except Exception as e:
        raise_error(
            e,
            f'Error instantiating Component with following attributes: \n{attrs}'
        )
    return component

def xdl_to_reagent(xdl_reagent_element: etree._Element) -> Reagent:
    """Given XDL reagent element return corresponding Reagent object.
    
    Arguments:
        xdl_reagent_element (lxml.etree._Element): XDL reagent lxml element.
        
    Returns:
        Reagent: Reagent object corresponding to reagent in 
                   xdl_reagent_element.
    """
    # Check attrs are valid for Reagent
    attrs = dict(xdl_reagent_element.attrib)
    if not 'id' in attrs:
        raise XDLError(
            "'id' attribute not specified for reagent.")
    check_attrs_are_valid(attrs, Reagent)
    # Try to instantiate Reagent object and return it.
    try:
        reagent = Reagent(**attrs)
    except Exception as e:
        raise_error(
            e,
            f'Error instantiating Reagent with following attributes: \n{attrs}'
        )
    return reagent