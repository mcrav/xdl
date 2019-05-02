from typing import Optional, List
from ..base_step import Step, AbstractStep
from ..steps_utility import Transfer
from ..steps_base import CStir, CStopStir

class AddCorrosive(AbstractStep):
    """Add corrosive reagent that can't come into contact with a valve.

    Args:
        reagent (str): Reagent to add.
        vessel (str): Vessel to add reagent to.
        volume (float): Volume of reagent to add.
        reagent_vessel (str): Used internally. Vessel containing reagent.
        air_vessel (str): Used internally. Vessel containing air.
    """

    def __init__(
        self,
        reagent: str,
        vessel: str,
        volume: float,
        reagent_vessel: Optional[str] = None,
        air_vessel: Optional[str] = None,
        stir: Optional[bool] = True,
        **kwargs
    ) -> None:
        super().__init__(locals())
        
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

    @property
    def human_readable(self) -> str:
        return 'Transfer corrosive reagent {0} ({1} mL) to {2}.'.format(
            self.reagent, self.volume, self.vessel,)