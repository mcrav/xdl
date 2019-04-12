from typing import List, Dict

#########################
### SYNTAX VALIDATION ###
#########################

#: step properties that expect a reagent declared in Reagents section
REAGENT_PROPS: List[str] = ['reagent', 'solute', 'solvent']