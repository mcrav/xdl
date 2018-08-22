import re
import itertools
from constants import *
from steps_xdl import Add

float_regex = r'([0-9]+([.][0-9]+)?)'



# Attrib preprocessing

def convert_time_str_to_seconds(time_str):
    time_str = time_str.lower()
    if time_str.endswith(('h', 'hr', 'hrs', 'hour', 'hours', )):
        multiplier = 3600
    elif time_str.endswith(('m', 'min', 'mins', 'minute', 'minutes')):
        multiplier = 60
    elif time_str.endswith(('s', 'sec', 'secs', 'second', 'seconds',)):
        multiplier = 1
    return str(int(float(re.match(float_regex, time_str).group(1)) * multiplier))

def convert_volume_str_to_ml(volume_str):
    print(f'VOLUME STR: {volume_str}')
    volume_str = volume_str.lower()
    if volume_str.endswith(volume_ml_unit_words):
        multiplier = 1
    elif volume_str.endswith(volume_l_unit_words):
        multiplier = 1000
    elif volume_str.endswith(volume_dl_unit_words):
        multiplier = 100
    elif volume_str.endswith(volume_cl_unit_words):
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
    return int(cas_str.replace('-', ''))

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
        cas_combos.append(frozenset(combo))
        cas_combos.append(frozenset((67641, 16853853)))
    return set(cas_combos)