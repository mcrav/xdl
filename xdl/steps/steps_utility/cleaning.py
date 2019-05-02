from typing import Optional, List

from ..base_step import AbstractStep, Step
from ..steps_base import CMove
from .stirring import Stir
from .liquid_handling import Transfer
from ...constants import DEFAULT_CLEAN_BACKBONE_VOLUME

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

    @property
    def human_readable(self) -> str:
        return 'Clean backbone with {solvent}.'.format(**self.properties)


class CleanVessel(AbstractStep):

    def __init__(
        self,
        vessel: str,
        solvent: str,
        stir_time: Optional[float] = 'default',
        volume: Optional[float] = None,
        repeat: Optional[float] = 2,
        solvent_vessel: Optional[str] = None,
        waste_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        """Clean given vessel with given solvent.
        
        Args:
            vessel (str): Vessel to clean.
            solvent (str): Solvent to clean vessel with.
            stir_time (float): Time to stir for after solvent is added.
            volume (float): Volume of solvent to use. If not supplied will be
                given internally according to vessel max volume.
            repeat (int): Number of cleans to do.
            solvent_vessel (str): Given internally. Flask containing solvent.
            waste_vessel (str): Given internally. Vessel to send waste solvent
                to.
        """
        super().__init__(locals())

    def get_steps(self):
        steps = []
        for _ in range(self.repeat):
            steps.extend([
                CMove(from_vessel=self.solvent_vessel,
                    to_vessel=self.vessel,
                    volume=self.volume),
                Stir(vessel=self.vessel,
                    time=self.stir_time),
                Transfer(from_vessel=self.vessel,
                        to_vessel=self.waste_vessel,
                        volume='all'),
            ])
        return steps

    @property
    def human_readable(self) -> str:
        return 'Clean {vessel} with {solvent} ({volume} mL).'.format(
            **self.properties)
