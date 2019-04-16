from typing import Optional, Union, List
import logging
import copy
import re
import sys

def parse_bool(s: str) -> bool:
    """Parse bool from string.

    Args:
        s (str): str representing bool.

    Returns:
        bool: True is s lower case is 'true' or '1', otherwise False.
    """
    if s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False
    return None

minutes_to_seconds = lambda x: x * 60
hours_to_seconds = lambda x: x * 60 * 60
no_conversion = lambda x: x

UNIT_CONVERTERS = {
    'ml': no_conversion,
    'cm3': no_conversion,
    'cc': no_conversion,
    'cl': lambda x: x * 10,
    'dl': lambda x: x * 10**2,
    'l': lambda x: x * 10**3,

    'kg': lambda x: x * 10**3,
    'g': lambda x: x,
    'mg': lambda x: x * 10**-3,
    'ug': lambda x: x * 10**-6,

    '°c': lambda x: x,
    'k': lambda x: x + 273.15,
    'f': lambda x: (x - 32 / 1.8),

    'h': hours_to_seconds,
    'hour': hours_to_seconds,
    'hours': hours_to_seconds,
    'hr': hours_to_seconds,
    'hrs': hours_to_seconds,
    'm': minutes_to_seconds,
    'min': minutes_to_seconds,
    'mins': minutes_to_seconds,
    'minutes': minutes_to_seconds,
    's': no_conversion,
    'secs': no_conversion,
    'seconds': no_conversion,
}


def convert_val_to_std_units(val):
    float_regex_pattern = r'([-]?[0-9]+(?:[.][0-9]+)?)' 
    unit_search = re.search(r'[a-zA-Z°]+', val)
    val_search = re.search(float_regex_pattern, val)
    if val_search:
        val = float(val_search[0])
        if unit_search:
            unit = unit_search[0]
            return UNIT_CONVERTERS[unit.lower()](val)
        else:
            return val
    return val 

def clean_properties(xdl_class, properties):
    annotations = xdl_class.__init__.__annotations__
    for prop, val in properties.items():
        if val == 'default' or prop == 'kwargs':
            continue
        elif prop == 'repeat':
            properties[prop] = int(val)
            continue

        prop_type = annotations[prop]
        if prop_type in [str, Optional[str]]:
            pass

        elif prop_type in [float, Optional[float]]:
            if type(val) == str:
                properties[prop] = convert_val_to_std_units(val)

        elif prop_type in [bool, Optional[bool]]:
            if type(val) == str:
                properties[prop] = parse_bool(val)

        elif prop_type == Union[str, List[str]]:
            if type(val) == str:
                properties[prop] = val.split(' ')
            elif type(val) == list:
                pass

        elif prop_type == Union[float, List[float]]:
            if type(val) == float:
                properties[prop] = [val]
            elif type(val) == list:
                pass

        elif prop_type == Union[bool, str]:
            bool_val = parse_bool(val)
            if bool_val != None:
                return bool_val
            else:
                return val

    return properties