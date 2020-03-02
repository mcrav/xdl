from typing import Optional, List
from .steps.collection import STEP_OBJ_DICT
from .executor import ChemputerExecutor
from ..abstract_platform import AbstractPlatform
from .graphgen import graph_from_template

class ChemputerPlatform(AbstractPlatform):

    @property
    def step_library(self):
        return STEP_OBJ_DICT

    @property
    def executor(self):
        return ChemputerExecutor

    def graph(
        self,
        xdl_obj,
        template: Optional[str] = None,
        save: Optional[str] = None,
        auto_fix_issues: Optional[bool] = True,
        ignore_errors: Optional[List[int]] = []
    ):
        return graph_from_template(
            xdl_obj,
            template=template,
            save=save,
            auto_fix_issues=auto_fix_issues,
            ignore_errors=ignore_errors
        )
