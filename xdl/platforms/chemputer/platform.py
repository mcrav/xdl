from .steps.collection import STEP_OBJ_DICT
from .executor import ChemputerExecutor
from ..abstract_platform import AbstractPlatform

class ChemputerPlatform(AbstractPlatform):

    @property
    def step_library(self):
        return STEP_OBJ_DICT

    @property
    def executor(self):
        return ChemputerExecutor
