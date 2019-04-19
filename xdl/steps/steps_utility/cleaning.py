from typing import Optional, List

from ..base_step import Step
from ..steps_base import CMove
from .stirring import Stir
from .liquid_handling import Transfer
from ...constants import DEFAULT_CLEAN_BACKBONE_VOLUME

class CleanBackbone(Step):

    def __init__(
        self,
        solvent: str,
        waste_vessels: Optional[List[str]] = [],
        solvent_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = []
        for waste_vessel in self.waste_vessels:
            self.steps.append(CMove(
                from_vessel=self.solvent_vessel, to_vessel=waste_vessel,
                volume=DEFAULT_CLEAN_BACKBONE_VOLUME))

        self.human_readable = 'Clean backbone with {0}.'.format(self.solvent)

class CleanVessel(Step):

    def __init__(
        self,
        vessel: str,
        solvent: str,
        stir_time: Optional[float] = 'default',
        volume: Optional[float] = None,
        solvent_vessel: Optional[str] = None,
        waste_vessel: Optional[str] = None,
    ) -> None:
        """Clean given vessel with given solvent.
        
        Args:
            vessel (str): Vessel to clean.
            solvent (str): Solvent to clean vessel with.
            stir_time (float): Time to stir for after solvent is added.
            volume (float): Volume of solvent to use. If not supplied will be
                given internally according to vessel max volume.
            solvent_vessel (str): Given internally. Flask containing solvent.
            waste_vessel (str): Given internally. Vessel to send waste solvent
                to.
        """
        super().__init__(locals())
        self.steps = [
            CMove(from_vessel=self.solvent_vessel,
                  to_vessel=self.vessel,
                  volume=self.volume),
            Stir(vessel=self.vessel,
                 time=self.stir_time),
            Transfer(from_vessel=self.vessel,
                     to_vessel=self.waste_vessel,
                     volume='all'),
        ]

        self.human_readable = 'Clean {vessel} with {solvent} ({volume} mL).'.format(
            **self.properties)
        