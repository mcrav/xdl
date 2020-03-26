import re

class PropLimit(object):
    """Convenience class for storing prop limit.

    Arguments:
        regex (str): Regex pattern that should match with valid values and not
            match with invalid values.
        hint (str): Optional. Useful hint for what valid value should look like.
        default (str): Optional. Default valid value.
    """
    def __init__(
        self,
        regex,
        hint='',
        default='',
    ):
        self.regex = regex
        self.hint = hint
        self.default = default

    def validate(self, value):
        return re.match(self.regex, value)


##################
# Regex patterns #
##################

FLOAT_PATTERN = r'([-]?[0-9]+(?:[.][0-9]+)?)'
POSITIVE_FLOAT_PATTERN = r'([0-9]+(?:[.][0-9]+)?)'

BOOL_PATTERN = r'(false|False|true|True)'

VOLUME_UNITS_PATTERN = r'(l|L|litre|litres|liter|liters|ml|mL|cm3|cc|milliltre|millilitres|milliliter|milliliters|cl|cL|centiltre|centilitres|centiliter|centiliters|dl|dL|deciltre|decilitres|deciliter|deciliters|ul|uL|μl|μL|microlitre|microlitres|microliter|microliters)?'

MASS_UNITS_PATTERN = r'(g|gram|grams|kg|kilogram|kilograms|mg|milligram|milligrams|ug|μg|microgram|micrograms)?'

TEMP_UNITS_PATTERN = r'(°C|K|F)?'

TIME_UNITS_PATTERN = r'(days|day|h|hr|hrs|hour|hours|m|min|mins|minute|minutes|s|sec|secs|second|seconds)?'

PRESSURE_UNITS_PATTERN = r'(mbar|bar|torr|Torr|mmhg|mmHg|atm|Pa|pa)?'

ROTATION_SPEED_UNITS_PATTERN = r'(rpm|RPM)?'

###############
# Prop limits #
###############

def generate_quantity_units_pattern(
        quantity_pattern, units_pattern, hint='', default=''):
    return PropLimit(
        regex=r'^((' + quantity_pattern + r'[ ]?'\
            + units_pattern + r'$)|(^' + quantity_pattern + r'))$',
        hint=hint,
        default=default
    )


VOLUME_PROP_LIMIT = PropLimit(
    regex=r'^(all|(' + POSITIVE_FLOAT_PATTERN + r'[ ]?'\
        + VOLUME_UNITS_PATTERN + r')|(' + POSITIVE_FLOAT_PATTERN + r'))$',
    hint='Expecting number followed by standard volume units, e.g. "5.5 mL"',
    default='0 mL',
)

MASS_PROP_LIMIT = generate_quantity_units_pattern(
    POSITIVE_FLOAT_PATTERN,
    MASS_UNITS_PATTERN,
    hint='Expecting number followed by standard mass units, e.g. "2.3 g"',
    default='0 g'
)

TEMP_PROP_LIMIT = generate_quantity_units_pattern(
    FLOAT_PATTERN,
    TEMP_UNITS_PATTERN,
    hint='Expecting number in degrees celsius or number followed by standard temperature units, e.g. "25", "25°C", "298 K".',
    default='25°C',
)

TIME_PROP_LIMIT = generate_quantity_units_pattern(
    POSITIVE_FLOAT_PATTERN,
    TIME_UNITS_PATTERN,
    hint='Expecting number followed by standard time units, e.g. "15 mins", "3 hrs".',
    default='0 mins'
)

PRESSURE_PROP_LIMIT = generate_quantity_units_pattern(
    POSITIVE_FLOAT_PATTERN,
    PRESSURE_UNITS_PATTERN,
    hint='Expecting number followed by standard pressure units, e.g. "50 mbar", "1 atm".',
    default='1 atm'
)

ROTATION_SPEED_PROP_LIMIT = generate_quantity_units_pattern(
    POSITIVE_FLOAT_PATTERN,
    ROTATION_SPEED_UNITS_PATTERN,
    hint='Expecting RPM value, e.g. "400 RPM".',
    default='400 RPM',
)

POSITIVE_INT_PROP_LIMIT = PropLimit(
    r'[0-9]+',
    hint='Expecting positive integer value, e.g. "3"',
    default='1',
)

POSITIVE_FLOAT_PROP_LIMIT = PropLimit(
    regex=POSITIVE_FLOAT_PATTERN,
    hint='Expecting positive float value, e.g. "3", "3.5"',
    default='0',
)

BOOL_PROP_LIMIT = PropLimit(
    BOOL_PATTERN,
    hint='Expecting one of "false" or "true".',
    default='false',
)

_hundred_float = r'(100(?:[.][0]+)?)'
_ten_to_ninety_nine_float = r'([0-9][0-9](?:[.][0-9]+)?)'
_zero_to_ten_float = r'([0-9](?:[.][0-9]+)?)'
PERCENT_RANGE_PROP_LIMIT = PropLimit(
    r'^(' + _hundred_float + '|'\
        + _ten_to_ninety_nine_float + '|' + _zero_to_ten_float + ')$',
    hint='Expecting number from 0-100 representing a percentage, e.g. "50", "8.5".',
    default='0',
)
