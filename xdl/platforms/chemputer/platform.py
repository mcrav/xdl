from .steps.collection import STEP_OBJ_DICT
from .executor import ChemputerExecutor
from ..abstract_platform import AbstractPlatform
from ...utils import schema

class ChemputerPlatform(AbstractPlatform):

    @property
    def step_library(self):
        return STEP_OBJ_DICT

    @property
    def executor(self):
        return ChemputerExecutor

    @property
    def schema(self):
        return schema.generate_schema(STEP_OBJ_DICT)
