
from .utils import cas_str_to_int, find_reagent_obj
from .steps import Add
import itertools

dangerous_combinations = {
    frozenset((67641, 16853853)): 'Acetone and LiAlH4 boom fucking boom!',
    # Alcohols and LiALH4,
}

def procedure_is_safe(steps, reagents):
    """
    Return True if procedure is safe.
    Print message for every unsafe feature found.
    """
    safe = True
    combinations = get_reagent_combinations(steps, reagents)
    for combo in combinations:
        if combo in dangerous_combinations:
            print(f'SAFETY WARNING: {dangerous_combinations[combo]}')
            safe = False
    return safe

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