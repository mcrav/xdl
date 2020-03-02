from typing import Optional, List
from .....step_utils.base_steps import Step, AbstractStep
from ..base_step import ChemputerStep
from ..steps_utility import Transfer
from ..steps_base import CStir, CStopStir
from ...utils.execution import get_reagent_vessel

class AddCorrosive(ChemputerStep, AbstractStep):
    """Add corrosive reagent that can't come into contact with a valve.

    Args:
        reagent (str): Reagent to add.
        vessel (str): Vessel to add reagent to.
        volume (float): Volume of reagent to add.
        reagent_vessel (str): Used internally. Vessel containing reagent.
        air_vessel (str): Used internally. Vessel containing air.
    """

    PROP_TYPES = {
        'reagent': str,
        'vessel': str,
        'volume': float,
        'stir': bool,
        'reagent_vessel': str,
        'air_vessel': str
    }

    INTERNAL_PROPS = [
        'reagent_vessel',
        'air_vessel',
    ]

    def __init__(
        self,
        reagent: str,
        vessel: str,
        volume: float,
        stir: Optional[bool] = True,

        # Internal properties
        reagent_vessel: Optional[str] = None,
        air_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.reagent_vessel:
            self.reagent_vessel = get_reagent_vessel(graph, self.reagent)

    def get_steps(self) -> List[Step]:
        steps = [
            Transfer(
                from_vessel=self.air_vessel,
                to_vessel=self.vessel,
                through=self.reagent_vessel,
                volume=self.volume)
        ]
        if self.stir:
            steps.insert(0, CStir(vessel=self.vessel))
        else:
            steps.insert(0, CStopStir(vessel=self.vessel))
        return steps
