import re
import itertools
from .constants import *
from .steps_xdl import Add

float_regex = r'([0-9]+([.][0-9]+)?)'

VOLUME_CL_UNIT_WORDS = ('cl', 'cL',)
VOLUME_ML_UNIT_WORDS = ('cc', 'ml','mL', 'cm3')
VOLUME_DL_UNIT_WORDS = ('dl', 'dL')
VOLUME_L_UNIT_WORDS = ('l', 'L')

# Attrib preprocessing

def convert_time_str_to_seconds(time_str):
    time_str = time_str.lower()
    if time_str.endswith(('h', 'hr', 'hrs', 'hour', 'hours', )):
        multiplier = 3600
    elif time_str.endswith(('m', 'min', 'mins', 'minute', 'minutes')):
        multiplier = 60
    elif time_str.endswith(('s', 'sec', 'secs', 'second', 'seconds',)):
        multiplier = 1
    else:
        multiplier = 1
    return str(int(float(re.match(float_regex, time_str).group(1)) * multiplier))

def convert_volume_str_to_ml(volume_str):
    volume_str = volume_str.lower()
    if volume_str.endswith(VOLUME_ML_UNIT_WORDS):
        multiplier = 1
    elif volume_str.endswith(VOLUME_L_UNIT_WORDS):
        multiplier = 1000
    elif volume_str.endswith(VOLUME_DL_UNIT_WORDS):
        multiplier = 100
    elif volume_str.endswith(VOLUME_CL_UNIT_WORDS):
        multiplier = 10
    return str(float(re.match(float_regex, volume_str).group(1)) * multiplier)

def find_reagent_obj(reagent_id, reagents):
    reagent_obj = None
    for reagent in reagents:
        if reagent_id == reagent.properties['id']:
            reagent_obj = reagent
            break
    return reagent_obj

def cas_str_to_int(cas_str):
    if cas_str:
        return int(cas_str.replace('-', ''))
    else:
        return None

# Safety

def get_reagent_combinations(steps, reagents):
    vessel_contents = {}
    combos = []
    for step in steps:
        if isinstance(step, Add):
            vessel = step.properties['vessel']
            reagent = step.properties['reagent']
            vessel_contents.setdefault(vessel, []).append(reagent)
            if len(vessel_contents[vessel]) > 1:
                combos.extend(list(itertools.combinations(vessel_contents[vessel], 2)))
    
    combos = set([frozenset(item) for item in combos if len(set(item)) > 1])
    cas_combos = []
    for combo in combos:
        combo = list(combo)
        combo[0] = cas_str_to_int(find_reagent_obj(combo[0], reagents).properties['cas'])
        combo[1] = cas_str_to_int(find_reagent_obj(combo[1], reagents).properties['cas'])
        if combo[0] and combo[1]:
            cas_combos.append(frozenset(combo))
    return set(cas_combos)