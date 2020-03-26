##################
# Regex patterns #
##################

FLOAT_PATTERN = r'([-]?[0-9]+(?:[.][0-9]+)?)'
POSITIVE_FLOAT_PATTERN = r'([0-9]+(?:[.][0-9]+)?)'

VOLUME_UNITS_PATTERN = r'(l|L|litre|litres|liter|liters|ml|mL|cm3|cc|milliltre|millilitres|milliliter|milliliters|cl|cL|centiltre|centilitres|centiliter|centiliters|dl|dL|deciltre|decilitres|deciliter|deciliters|ul|uL|μl|μL|microlitre|microlitres|microliter|microliters)?'

MASS_UNITS_PATTERN = r'(g|gram|grams|kg|kilogram|kilograms|mg|milligram|milligrams|ug|μg|microgram|micrograms)?'

TEMP_UNITS_PATTERN = r'(°C|K|F)?'

TIME_UNITS_PATTERN = r'(days|day|h|hr|hrs|hour|hours|m|min|mins|minute|minutes|s|sec|secs|second|seconds)?'

PRESSURE_UNITS_PATTERN = r'(mbar|bar|torr|Torr|mmhg|mmHg|atm|Pa|pa)?'

ROTATION_SPEED_UNITS_PATTERN = r'(rpm|RPM)?'

###############
# Prop limits #
###############

def generate_quantity_units_pattern(quantity_pattern, units_pattern):
    return r'^((' + quantity_pattern + r'[ ]?'\
        + units_pattern + r')|(' + quantity_pattern + r'))$'


VOLUME_PROP_LIMIT = r'^(all|(' + POSITIVE_FLOAT_PATTERN + r'[ ]?'\
    + VOLUME_UNITS_PATTERN + r')|(' + POSITIVE_FLOAT_PATTERN + r'))$'

MASS_PROP_LIMIT = generate_quantity_units_pattern(
    POSITIVE_FLOAT_PATTERN, MASS_UNITS_PATTERN)

TEMP_PROP_LIMIT = generate_quantity_units_pattern(
    FLOAT_PATTERN, TEMP_UNITS_PATTERN)

TIME_PROP_LIMIT = generate_quantity_units_pattern(
    POSITIVE_FLOAT_PATTERN, TIME_UNITS_PATTERN)

PRESSURE_PROP_LIMIT = generate_quantity_units_pattern(
    POSITIVE_FLOAT_PATTERN, PRESSURE_UNITS_PATTERN)

ROTATION_SPEED_PROP_LIMIT = generate_quantity_units_pattern(
    POSITIVE_FLOAT_PATTERN, ROTATION_SPEED_UNITS_PATTERN)

POSITIVE_INT_PROP_LIMIT = r'^[0-9]+$'

POSITIVE_FLOAT_PROP_LIMIT = r'^' + POSITIVE_FLOAT_PATTERN + r'$'

BOOL_PROP_LIMIT = r'^(false|False|true|True)$'

_hundred_float = r'(100(?:[.][0]+)?)'
_ten_to_ninety_nine_float = r'([0-9][0-9](?:[.][0-9]+)?)'
_zero_to_ten_float = r'([0-9](?:[.][0-9]+)?)'
PERCENT_RANGE_PROP_LIMIT = r'^(' + _hundred_float + r'|'\
    + _ten_to_ninety_nine_float + r'|' + _zero_to_ten_float + r')$'
