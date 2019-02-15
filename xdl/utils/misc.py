from typing import Optional, Union, List
import copy
import re

def parse_bool(s: str) -> bool:
    """Parse bool from string.

    Args:
        s (str): str representing bool.

    Returns:
        bool: True is s lower case is 'true' or '1', otherwise False.
    """
    if s.lower() in ['true', '1']:
        return True
    return False

def get_port_str(port: str) -> str:
    """Get str representing port for using in human_readable strings.
    
    Args:
        port (str): Port name
    
    Returns:
        str: if port is 'top' return '(port top)' if port is None return ''
    """
    if port:
        return '(port {0})'.format(port)
    return ''

def minutes_to_seconds(x):
    return x * 60

UNIT_CONVERTERS = {
    'ml': lambda x: x,
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

    'h': lambda x: x * 60 * 60,
    'm': minutes_to_seconds,
    'min': minutes_to_seconds,
    'mins': minutes_to_seconds,
    's': lambda x: x,
}


def convert_val_to_std_units(val):
    unit_search = re.search(r'[a-zA-Z°]+', val)
    val_search = re.search(r'[0-9.]+', val)
    if val_search:
        val = float(val_search[0])
        if unit_search:
            unit = unit_search[0]
            return UNIT_CONVERTERS[unit.lower()](val)
        else:
            return val
    return None

def clean_properties(xdl_class, properties):
    annotations = xdl_class.__init__.__annotations__
    for prop, val in properties.items():
        if val == 'default':
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
    return properties