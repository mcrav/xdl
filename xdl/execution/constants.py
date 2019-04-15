from typing import List
from ..steps import *

################
### CLEANING ###
################

#: Solvents that shouldn't be used for cleaning backbone.
#: Toluene tends to dissolve glue in syringe pumps.
CLEANING_SOLVENT_BLACKLIST: List[str] = ['toluene']

SOLVENT_CONTAINING_STEPS: List[type] = [
    Add, Dissolve, WashFilterCake, Separate, AddFilterDeadVolume]

# Steps after which backbone should be cleaned
CLEAN_BACKBONE_AFTER_STEPS: List[type] = [
    Add,
    Separate,
    MakeSolution,
    WashFilterCake,
    Filter,
    Dry,
    AddFilterDeadVolume,
    RemoveFilterDeadVolume,
]