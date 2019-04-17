
import itertools
import copy
from typing import Dict, List, Set

from .utils import cas_str_to_int, find_reagent_obj
from ..steps import (
    Add, CMove, Transfer, Separate, WashFilterCake, Step)
from ..reagents import Reagent

dangerous_combinations: Dict[frozenset, str] = {
    frozenset((67641, 16853853)): 'Acetone and LiAlH4 boom fucking boom!',
    # Alcohols and LiALH4,
}

def procedure_is_safe(steps: List[Step], reagents: List[Reagent]) -> bool:
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

def get_reagent_combinations(steps: List[Step], reagents: List[Reagent]) -> Set:
    """REWRITE USING iter_vessel_contents
    
    Get all combinations of reagents in given procedure.
    
    Arguments:
        steps (list): list of Step objects.
        reagents (list): List of Reagent objects.
    
    Returns:
        set: Set of frozensets of pairs of CAS numbers.
    """
    return set()
    # vessel_contents = {}
    # combos = []
    # for step in steps:
    #     vessel = None
    #     if isinstance(step, Add):
    #         vessel = step.properties['vessel']
    #         reagent = step.properties['reagent']
    #         vessel_contents.setdefault(vessel, []).append(reagent)

    #     elif isinstance(step, MakeSolution):
    #         vessel = step.properties['vessel']
    #         solutes = step.properties['solutes']
    #         solvent = step.properties['solvent']
    #         vessel_contents.setdefault(vessel, []).extend(solutes)
    #         vessel_contents[vessel].append(solvent)

    #     elif isinstance(step, (CMove, Transfer)):
    #         vessel_contents[step.to_vessel] = copy.copy(vessel_contents[step.from_vessel])
    #         if step.volume == 'all':
    #             vessel_contents[step.from_vessel] = []
                
    #     elif isinstance(step, Extract):
    #         vessel_contents[step.from_vessel].append(step.solvent)

    #     elif isinstance(step, WashFilterCake):
    #         vessel_contents.setdefault(step.filter_vessel, []).append(step.solvent)

    # for vessel, contents in vessel_contents.items():
    #     combos.extend(list(itertools.combinations(contents, 2)))

    # combos = set([frozenset(item) for item in combos if len(set(item)) > 1])
    # cas_combos = []
    # for combo in combos:
    #     combo = list(combo)
    #     combo[0] = cas_str_to_int(find_reagent_obj(combo[0], reagents).properties['cas'])
    #     combo[1] = cas_str_to_int(find_reagent_obj(combo[1], reagents).properties['cas'])
    #     if combo[0] and combo[1]:
    #         cas_combos.append(frozenset(combo))
    # return set(cas_combos)