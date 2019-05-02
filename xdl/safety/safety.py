
import itertools
import copy
from typing import Dict, List, Set

from .utils import cas_str_to_int, find_reagent_obj
from ..steps import (
    Add, CMove, Transfer, Separate, Step)
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