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

    Raises:
        ValueError: If s.lower() is not 'true' or 'false'.
    """
    if s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False
    raise ValueError(f'{s} cannot be parsed as a bool.')

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
    'ul': lambda x: x * 10**-3,

    'kg': lambda x: x * 10**3,
    'g': lambda x: x,
    'mg': lambda x: x * 10**-3,
    'ug': lambda x: x * 10**-6,

    '°c': lambda x: x,
    'k': lambda x: x - 273.15,
    'f': lambda x: (x - 32) / 1.8,

    'h': hours_to_seconds,
    'hour': hours_to_seconds,
    'hours': hours_to_seconds,
    'hr': hours_to_seconds,
    'hrs': hours_to_seconds,
    'm': minutes_to_seconds,
    'min': minutes_to_seconds,
    'mins': minutes_to_seconds,
    'minute': minutes_to_seconds,
    'minutes': minutes_to_seconds,
    's': no_conversion,
    'sec': no_conversion,
    'secs': no_conversion,
    'second': no_conversion,
    'seconds': no_conversion,

    'mbar': no_conversion,
    'bar': lambda x: x * 10**3,
    'torr': lambda x: x * 1.33322,
    'mmhg': lambda x: x * 1.33322,
    'atm': lambda x: x * 1013.25,
    'pa': lambda x: x * 0.01,

    'rpm': lambda x: x,
}

def convert_val_to_std_units(val: str) -> float:
    """Given str of value with/without units, convert it into standard unit and
    return float value.
    
    Standard units:

    time      seconds
    volume    mL
    pressure  mbar
    temp      °c
    mass      g
    
    Arguments:
        val (str): Value (and units) as str. If no units are specified it is
            assumed value is already in default units.
    
    Returns:
        float: Value in default units.
    """
    float_regex_pattern = r'([-]?[0-9]+(?:[.][0-9]+)?)' 
    unit_search = re.search(r'[a-zA-Z°]+[3]?', val)
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

        #  Used by 3 option stir property in WashSolid
        elif prop_type == Optional[Union[bool, str]]:
            if type(val) == str:
                try:
                    properties[prop] = parse_bool(val)
                except ValueError:
                    pass

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
                properties[prop] = bool_val

        elif prop_type in [int, Optional[int]]:
            try:
                properties[prop] = int(val)
            except TypeError:
                pass

    return properties