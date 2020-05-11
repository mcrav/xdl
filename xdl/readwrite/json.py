import json

from .errors import (
    XDLJSONMissingHardwareError,
    XDLJSONMissingReagentsError,
    XDLJSONMissingStepsError,
    XDLJSONHardwareNotArrayError,
    XDLJSONReagentsNotArrayError,
    XDLJSONStepsNotArrayError,
    XDLJSONInvalidSectionError,
    XDLInvalidStepTypeError,
    XDLJSONMissingPropertiesError,
    XDLJSONMissingStepNameError,
)
from ..reagents import Reagent
from ..hardware import Hardware, Component

VALID_SECTIONS = ['steps', 'reagents', 'hardware']

def xdl_from_json_file(xdl_json_file, platform):
    """Convert .json file with JSON XDL format to XDL object."""
    with open(xdl_json_file) as fd:
        xdl_json = json.load(fd)
    return xdl_from_json(xdl_json, platform)

def validate_xdl_json(xdl_json):
    """Validate XDL JSON Dict is correct format."""
    if 'steps' not in xdl_json:
        raise XDLJSONMissingStepsError()
    if 'reagents' not in xdl_json:
        raise XDLJSONMissingReagentsError()
    if 'hardware' not in xdl_json:
        raise XDLJSONMissingHardwareError()
    if type(xdl_json['steps']) is not list:
        raise XDLJSONStepsNotArrayError()
    if type(xdl_json['reagents']) is not list:
        raise XDLJSONReagentsNotArrayError()
    if type(xdl_json['hardware']) is not list:
        raise XDLJSONHardwareNotArrayError()
    for k in xdl_json:
        if k not in VALID_SECTIONS:
            raise XDLJSONInvalidSectionError(k)
    for step_json in xdl_json['steps']:
        validate_xdl_step_json(step_json)
    for reagent_json in xdl_json['reagents']:
        validate_xdl_element_json(reagent_json)
    for component_json in xdl_json['hardware']:
        validate_xdl_element_json(component_json)

def validate_xdl_step_json(step_json):
    if 'name' not in step_json:
        raise XDLJSONMissingStepNameError()
    if 'properties' not in step_json:
        raise XDLJSONMissingPropertiesError()
    if 'children' in step_json:
        for child in step_json['children']:
            validate_xdl_step_json(child)

def validate_xdl_element_json(xdl_element_json):
    if 'properties' not in xdl_element_json:
        raise XDLJSONMissingPropertiesError()

def xdl_from_json(xdl_json, platform):
    """Convert JSON XDL format Dict to XDL object."""
    validate_xdl_json(xdl_json)
    xdl_steps = [
        xdl_step_from_json(step_json, platform)
        for step_json in xdl_json['steps']
    ]
    xdl_reagents = [
        xdl_element_from_json(reagent_json, Reagent)
        for reagent_json in xdl_json['reagents']
    ]
    xdl_hardware = Hardware([
        xdl_element_from_json(reagent_json, Component)
        for reagent_json in xdl_json['hardware']
    ])
    return {
        'steps': xdl_steps,
        'reagents': xdl_reagents,
        'hardware': xdl_hardware,
        'procedure_attrs': {},
    }

def xdl_step_from_json(step_json, platform):
    """Convert JSON XDL format step Dict to Step object."""
    step_name = step_json['name']
    if step_name not in platform.step_library:
        raise XDLInvalidStepTypeError(step_name)
    step_type = platform.step_library[step_name]
    step_properties = step_json['properties']
    step_properties['children'] = []
    if 'children' in step_json:
        step_properties['children'] = [
            xdl_step_from_json(child, platform)
            for child in step_json['children']
        ]
    return step_type(**step_properties)

def xdl_element_from_json(xdl_element_json, xdl_element_type):
    return xdl_element_type(**xdl_element_json['properties'])

def xdl_to_json(xdl_obj, full_properties: bool = False):
    """Convert XDL object to JSON format immediately useable by XDLApp."""
    xdl_steps_json = [
        xdl_step_to_json(step, full_properties) for step in xdl_obj.steps]
    xdl_reagents_json = [
        xdl_element_to_json(reagent) for reagent in xdl_obj.reagents]
    xdl_hardware_json = [
        xdl_element_to_json(component) for component in xdl_obj.hardware]

    xdl_json = {
        'steps': xdl_steps_json,
        'reagents': xdl_reagents_json,
        'hardware': xdl_hardware_json
    }
    return xdl_json

def xdl_step_to_json(xdl_step, full_properties: bool = False):
    """Convert XDL Step to JSON format immediately useable by XDLApp."""
    xdl_step_properties = {
        k: v
        for k, v in xdl_step.properties.items()
        if (k != 'children'
            and (full_properties or k not in xdl_step.INTERNAL_PROPS))
    }
    children = xdl_step.children if 'children' in xdl_step.properties else []
    xdl_step_json = {
        'name': xdl_step.name,
        'properties': xdl_step_properties,
        'children': [xdl_step_to_json(child) for child in children]
    }
    return xdl_step_json

def xdl_element_to_json(xdl_step):
    """Convert XDL Reagent or Component to JSON format immediately useable by
    XDLApp.
    """
    xdl_step_properties = {
        k: v for k, v in xdl_step.properties.items()
    }
    xdl_step_json = {
        'name': xdl_step.id,
        'properties': xdl_step_properties,
    }
    return xdl_step_json
