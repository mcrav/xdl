from typing import Optional, Dict
from ..base_step import AbstractStep
from ..steps_utility import (
    StartStir, StopStir, Wait, HeatChillToTemp, HeatChillReturnToRT)
from ..steps_base import CMove
from .dry import Dry

class CleanVessel(AbstractStep):

    def __init__(
        self,
        vessel: str,
        solvent: str,
        stir_time: Optional[float] = 'default',
        stir_speed: Optional[float] = 'default',
        temp: Optional[float] = None,
        volume: Optional[float] = None,
        cleans: Optional[float] = 2,
        solvent_vessel: Optional[str] = None,
        waste_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        """Clean given vessel with given solvent.
        
        Args:
            vessel (str): Vessel to clean.
            solvent (str): Solvent to clean vessel with.
            stir_time (float): Time to stir for after solvent is added.
            stir_speed (float): Speed to stir at in RPM.
            volume (float): Volume of solvent to use. If not supplied will be
                given internally according to vessel max volume.
            cleans (int): Number of cleans to do.
            solvent_vessel (str): Given internally. Flask containing solvent.
            waste_vessel (str): Given internally. Vessel to send waste solvent
                to.
        """
        super().__init__(locals())

    def get_steps(self):
        steps = []
        for _ in range(self.cleans):
            steps.extend([
                StartStir(vessel=self.vessel),
                CMove(from_vessel=self.solvent_vessel,
                      to_vessel=self.vessel,
                      volume=self.volume),
                Wait(time=self.stir_time),
                CMove(from_vessel=self.vessel,
                      to_vessel=self.waste_vessel,
                      volume=self.volume),
                StopStir(vessel=self.vessel),
            ])
        steps.append(Dry(vessel=self.vessel))
        if self.temp != None and (self.temp < 20 or self.temp > 25):
            steps.insert(
                1, HeatChillToTemp(vessel=self.vessel, temp=self.temp))
            steps.append(HeatChillReturnToRT(vessel=self.vessel, stir=False))
        return steps
