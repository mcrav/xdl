from typing import List, Dict

#########################
### SYNTAX VALIDATION ###
#########################

#: step properties that expect a reagent declared in Reagents section
REAGENT_PROPS: List[str] = ['reagent', 'solute', 'solvent']

#: These properties should always be written even if they are default.
ALWAYS_WRITE: List[str] = {
    'WashSolid': ['volume'],
}