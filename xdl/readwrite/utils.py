import re
from typing import Tuple

############
### MISC ###
############

# Should match, '1', '11', '1.1', '1.01', '13.12' etc.
float_regex: str = r'([0-9]+([.][0-9]+)?)'

def parse_bool(s: str) -> bool:
    """Parse string for bool."""
    if s.strip().lower() in ['true', '1']:
        return True
    elif s.strip().lower() in ['false', '0']:
        return False
    return None


##################
### UNIT WORDS ###
##################

VOLUME_CL_UNIT_WORDS: Tuple[str] = ('cl', 'cL',)
VOLUME_ML_UNIT_WORDS: Tuple[str] = ('cc', 'ml','mL', 'cm3')
VOLUME_DL_UNIT_WORDS: Tuple[str] = ('dl', 'dL')
VOLUME_L_UNIT_WORDS: Tuple[str] = ('l', 'L')

MASS_G_UNIT_WORDS: Tuple[str] = ('g', 'grams')
MASS_KG_UNIT_WORDS: Tuple[str] = ('kg', 'kilograms')
MASS_MG_UNIT_WORDS: Tuple[str] = ('mg', 'milligrams')
MASS_UG_UNIT_WORDS: Tuple[str] = ('ug', 'micrograms')


#########################################
### CONVERT VALUES TO STANDARDS UNITS ###
#########################################

def convert_time_str_to_seconds(time_str: str) -> float:
    """Convert time str to float with unit seconds i.e. '2hrs' -> 7200."""
    time_str = time_str.lower()
    if time_str.endswith(('h', 'hr', 'hrs', 'hour', 'hours', )):
        multiplier = 3600
    elif time_str.endswith(('m', 'min', 'mins', 'minute', 'minutes')):
        multiplier = 60
    elif time_str.endswith(('s', 'sec', 'secs', 'second', 'seconds',)):
        multiplier = 1
    else:
        multiplier = 1
    return float(re.match(float_regex, time_str).group(1)) * multiplier

def convert_volume_str_to_ml(volume_str: str) -> float:
    """Convert volume str to float with unit mL i.e. '1l' -> 1000.""" 
    if volume_str == 'all':
        return volume_str
    volume_str = volume_str.lower()
    if volume_str.endswith(VOLUME_ML_UNIT_WORDS):
        multiplier = 1
    elif volume_str.endswith(VOLUME_L_UNIT_WORDS):
        multiplier = 1000
    elif volume_str.endswith(VOLUME_DL_UNIT_WORDS):
        multiplier = 100
    elif volume_str.endswith(VOLUME_CL_UNIT_WORDS):
        multiplier = 10
    else:
        multiplier = 1 
    return float(re.match(float_regex, volume_str).group(1)) * multiplier

def convert_mass_str_to_g(mass_str: str) -> float:
    """Convert mass str to float with unit grams i.e. '20mg' -> 0.02."""
    mass_str = mass_str.lower()
    if mass_str.endswith(MASS_G_UNIT_WORDS):
        multiplier = 1
    elif mass_str.endswith(MASS_KG_UNIT_WORDS):
        multiplier = 1000
    elif mass_str.endswith(MASS_MG_UNIT_WORDS):
        multiplier = 1e-3
    elif mass_str.endswith(MASS_UG_UNIT_WORDS):
        multiplier = 1e-6
    else:
        multiplier = 1
    return float(re.match(float_regex, mass_str).group(1)) * multiplier

