from typing import Optional, Union, List
import re
from .errors import XDLError
from .prop_limits import (
    POSITIVE_FLOAT_PROP_LIMIT,
    POSITIVE_INT_PROP_LIMIT,
    BOOL_PROP_LIMIT
)

DEFAULT_PROP_LIMITS = {
    float: POSITIVE_FLOAT_PROP_LIMIT,
    int: POSITIVE_INT_PROP_LIMIT,
    bool: BOOL_PROP_LIMIT,
}

def parse_bool(s: str) -> bool:
    """Parse bool from string.

    Args:
        s (str): str representing bool.

    Returns:
        bool: True is s lower case is 'true' or '1', otherwise False.

    Raises:
        ValueError: If s.lower() is not 'true' or 'false'.
    """
    if type(s) == bool:
        return s
    elif type(s) == str:
        if s.lower() == 'true':
            return True
        elif s.lower() == 'false':
            return False
    else:
        return None

def days_to_seconds(x):
    return x * 60 * 60 * 24

def minutes_to_seconds(x):
    return x * 60

def hours_to_seconds(x):
    return x * 60 * 60

def no_conversion(x):
    return x

def cl_to_ml(x):
    return x * 10

def dl_to_ml(x):
    return x * 10**2

def l_to_ml(x):
    return x * 10**3

def ul_to_ml(x):
    return x * 10**-3

def kilogram_to_grams(x):
    return x * 10**3

def milligram_to_grams(x):
    return x * 10**-3

def microgram_to_grams(x):
    return x * 10**-6


UNIT_CONVERTERS = {
    'ml': no_conversion,
    'millilitre': no_conversion,
    'milliliter': no_conversion,
    'milliliters': no_conversion,
    'millilitres': no_conversion,
    'cm3': no_conversion,
    'cc': no_conversion,

    'cl': cl_to_ml,
    'centilitre': cl_to_ml,
    'centiliter': cl_to_ml,
    'centilitres': cl_to_ml,
    'centiliters': cl_to_ml,

    'dl': dl_to_ml,
    'decilitre': dl_to_ml,
    'deciliter': dl_to_ml,
    'decilitres': dl_to_ml,
    'deciliters': dl_to_ml,

    'l': l_to_ml,
    'liter': l_to_ml,
    'litre': l_to_ml,
    'liters': l_to_ml,
    'litres': l_to_ml,

    'μl': ul_to_ml,
    'ul': ul_to_ml,
    'microlitre': ul_to_ml,
    'microliter': ul_to_ml,
    'microlitres': ul_to_ml,
    'microliters': ul_to_ml,

    'kg': kilogram_to_grams,
    'kilogram': kilogram_to_grams,
    'kilograms': kilogram_to_grams,
    'g': no_conversion,
    'gram': no_conversion,
    'grams': no_conversion,
    'mg': milligram_to_grams,
    'milligram': milligram_to_grams,
    'milligrams': milligram_to_grams,
    'ug': microgram_to_grams,
    'μg': microgram_to_grams,
    'microgram': microgram_to_grams,
    'micrograms': microgram_to_grams,

    '°c': lambda x: x,
    'k': lambda x: x - 273.15,
    'f': lambda x: (x - 32) / 1.8,

    'days': days_to_seconds,
    'day': days_to_seconds,

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
    if type(val) != str:
        return val

    float_regex_pattern = r'([-]?[0-9]+(?:[.][0-9]+)?)'
    unit_search = re.search(r'[a-zA-Zμ°]+[3]?', val)
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
    prop_types = xdl_class.PROP_TYPES
    prop_limits = xdl_class.PROP_LIMITS

    for prop, val in properties.items():

        # Check for special cases
        if val == 'default' or prop == 'kwargs':
            continue

        if val == 'None':
            properties[prop] = None
            continue

        elif prop == 'repeat':
            properties[prop] = int(val)
            continue

        elif prop == 'children':
            properties[prop] = val
            continue

        # Get prop type
        try:
            prop_type = prop_types[prop]
        except KeyError:
            raise XDLError(
                f'Missing prop type for "{prop}" in {xdl_class.__name__}')

        # Remove any whitespace errors
        if type(val) == str:
            while '  ' in val:
                val = val.replace('  ', ' ')
            val = val.strip()

        # Validate val with prop limit
        try:
            prop_limit = prop_limits[prop]
        except KeyError:
            prop_limit = None

        test_prop_limit(prop_limit, prop_type, prop, val, xdl_class.__name__)

        # Do type conversion, and conversion to std units
        if prop_type == str:
            if val:
                properties[prop] = str(val)

        elif prop_type == float:
            if type(val) == str:
                properties[prop] = convert_val_to_std_units(val)

        elif prop_type == bool:
            if type(val) == str:
                properties[prop] = parse_bool(val)

        # Used by 3 option stir property in WashSolid
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
            if bool_val is not None:
                properties[prop] = bool_val

        elif prop_type == int:
            try:
                properties[prop] = int(val)
            except TypeError:
                pass

        elif prop_type == List[str]:
            if type(val) == str:
                split_list = val.split()
                for i in range(len(split_list)):
                    if (type(split_list[i]) == str
                            and split_list[i].lower() == 'none'):
                        split_list[i] = None
                properties[prop] = split_list
            elif type(val) == list:
                pass

        elif prop_type == Union[str, int]:
            if type(val) == str:
                if re.match(r'[0-9]+', val):
                    properties[prop] = int(val)

        if 'port' in prop:
            try:
                properties[prop] = int(properties[prop])
            except (ValueError, TypeError):
                pass

    return properties

def test_prop_limit(prop_limit, prop_type, prop, val, step_name):
    """Assert that given val is compatible with prop limit."""
    if val is None:
        return

    if prop_limit is None:
        if prop_type in DEFAULT_PROP_LIMITS:
            prop_limit = DEFAULT_PROP_LIMITS[prop_type]
        else:
            return

    val = str(val)
    try:
        assert re.match(prop_limit, val)
    except AssertionError:
        raise XDLError(
            f'{step_name}: Value "{val}" does not match "{prop}" prop limit\
 {prop_limit}.'
        )
