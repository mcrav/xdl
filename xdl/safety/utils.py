def find_reagent_obj(reagent_id, reagents):
    """Return reagent object, given reagent_id and list of reagents."""
    reagent_obj = None
    for reagent in reagents:
        if reagent_id == reagent.rid:
            reagent_obj = reagent
            break
    return reagent_obj

def cas_str_to_int(cas_str):
    """Convert CAS str to int. i.e. '56-43-1' -> 56431"""
    if cas_str:
        return int(cas_str.replace('-', ''))
    else:
        return None