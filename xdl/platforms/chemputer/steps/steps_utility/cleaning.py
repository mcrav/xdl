from typing import Optional, List
from .....step_utils import AbstractStep, Step
from ..steps_base import CMove
from .....constants import DEFAULT_CLEAN_BACKBONE_VOLUME
from ...utils.execution import get_reagent_vessel

class CleanBackbone(AbstractStep):

    def __init__(
        self,
        solvent: str,
        waste_vessels: Optional[List[str]] = [],
        solvent_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.solvent_vessel:
            self.solvent_vessel = get_reagent_vessel(graph, self.solvent)

    def get_steps(self) -> List[Step]:
        return [CMove(from_vessel=self.solvent_vessel,
                      to_vessel=waste_vessel,
                      volume=DEFAULT_CLEAN_BACKBONE_VOLUME)
                for waste_vessel in self.waste_vessels]
