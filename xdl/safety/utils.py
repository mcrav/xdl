from typing import List, Union
from ..reagents import Reagent

def find_reagent_obj(reagent_id: str, reagents: List[Reagent]) -> Reagent:
    """Return reagent object, given reagent_id and list of reagents."""
    reagent_obj = None
    for reagent in reagents:
        if reagent_id == reagent.id:
            reagent_obj = reagent
            break
    return reagent_obj

def cas_str_to_int(cas_str: str) -> Union[int, None]:
    """Convert CAS str to int. i.e. '56-43-1' -> 56431"""
    if cas_str:
        return int(cas_str.replace('-', ''))
    else:
        return None