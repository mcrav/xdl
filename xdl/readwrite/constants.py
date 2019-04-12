from typing import List, Dict

#########################
### SYNTAX VALIDATION ###
#########################

ACCEPTABLE_MASS_UNITS: List[str] = ['ug', 'mg', 'g', 'kg']
ACCEPTABLE_VOLUME_UNITS: List[str] = ['ul', 'ml', 'cl', 'dl', 'l', 'cc']
ACCEPTABLE_MOL_UNITS: List[str] = ['umol', 'mmol', 'mol']
ACCEPTABLE_TIME_UNITS: List[str] = [
    's', 'sec', 'secs', 'second', 'seconds',
    'm', 'min', 'mins', 'minutes',
    'h', 'hr', 'hrs', 'hour', 'hours',]
ACCEPTABLE_TEMP_UNITS: List[str] = ['c', 'k', 'f']

XDL_ACCEPTABLE_UNITS: Dict[str, List[str]] = {
    'volume': ACCEPTABLE_VOLUME_UNITS,
    'mass': ACCEPTABLE_MASS_UNITS,
    'mol': ACCEPTABLE_MOL_UNITS,
    'time': ACCEPTABLE_TIME_UNITS,
    'temperature': ACCEPTABLE_TEMP_UNITS,
    'solute_masses': ACCEPTABLE_MASS_UNITS,
    'solvent_volume': ACCEPTABLE_VOLUME_UNITS,
}

# step properties that expect a reagent declared in Reagents section
REAGENT_PROPS: List[str] = ['reagent', 'solute', 'solvent']