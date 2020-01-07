from ...steps.chemobot.collection import STEP_OBJ_DICT
from .executor import XDLExecutor
from ..abstract_platform import AbstractPlatform

class ModularWheelPlatform(AbstractPlatform):

    @property
    def step_library(self):
        return STEP_OBJ_DICT

    @property
    def executor(self):
        return XDLExecutor
