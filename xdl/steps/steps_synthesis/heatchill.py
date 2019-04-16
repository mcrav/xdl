from typing import Optional
from ..base_step import Step
from ..steps_utility import Wait, HeatChillToTemp, StopHeatChill
from ..steps_base import CSetStirRate, CStir, CStopStir

class HeatChill(Step):
    """Heat or chill vessel to given temp for given time.
    
    Args:
        vessel (str): Vessel to heat/chill.
        temp (float): Temperature to heat/chill vessel to in °C.
        time (float): Time to heat/chill vessel for in seconds.
        stir (bool): True if step should be stirred, otherwise False.
        stir_rpm (float): Speed to stir at in RPM. Only use if stir == True.
        vessel_type (str): Given internally. Vessel type so the step knows what
            base steps to use. 'ChemputerFilter' or 'ChemputerReactor'.
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        time: float,
        stir: bool = True, 
        stir_rpm: float = 'default',
        vessel_type: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())
        self.steps = [
            HeatChillToTemp(
                vessel=self.vessel,
                temp=self.temp,
                stir=self.stir,
                stir_rpm=self.stir_rpm,
                vessel_type=self.vessel_type),
            Wait(time=self.time),
            StopHeatChill(vessel=self.vessel, vessel_type=self.vessel_type),
        ]
        if self.stir:
            self.steps.insert(0, CStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm='default'))
        else:
            self.steps.insert(0, CStopStir(vessel=self.vessel))

        self.human_readable = 'Heat/Chill {vessel} to {temp} °C for {time} s.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp],
            }
        }
