from typing import Optional, List
from .....step_utils import AbstractStep, Step
from ..steps_base import CMove
from .....constants import DEFAULT_CLEAN_BACKBONE_VOLUME

class CleanBackbone(AbstractStep):

    def __init__(
        self,
        solvent: str,
        waste_vessels: Optional[List[str]] = [],
        solvent_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [CMove(from_vessel=self.solvent_vessel,
                      to_vessel=waste_vessel,
                      volume=DEFAULT_CLEAN_BACKBONE_VOLUME)
                for waste_vessel in self.waste_vessels]
