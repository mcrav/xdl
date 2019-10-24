from typing import Optional, List, Dict, Any
from ..base_steps import Step, AbstractStep
from ..steps_utility import (
    Wait, HeatChillToTemp, StopHeatChill, StartStir, StopStir)

class HeatChill(AbstractStep):
    """Heat or chill vessel to given temp for given time.

    Args:
        vessel (str): Vessel to heat/chill.
        temp (float): Temperature to heat/chill vessel to in °C.
        time (float): Time to heat/chill vessel for in seconds.
        stir (bool): True if step should be stirred, otherwise False.
        stir_speed (float): Speed to stir at in RPM. Only use if stir == True.
        vessel_type (str): Given internally. Vessel type so the step knows what
            base steps to use. 'ChemputerFilter' or 'ChemputerReactor'.
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        time: float,
        stir: bool = True,
        stir_speed: float = 'default',
        vessel_type: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        steps = [
            HeatChillToTemp(
                vessel=self.vessel,
                temp=self.temp,
                stir=self.stir,
                stir_speed=self.stir_speed,
                vessel_type=self.vessel_type),
            Wait(time=self.time),
            StopHeatChill(vessel=self.vessel, vessel_type=self.vessel_type),
        ]
        if self.stir:
            steps.insert(0, StartStir(vessel=self.vessel,
                                      vessel_type=self.vessel_type,
                                      stir_speed=self.stir_speed))
        else:
            steps.insert(0, StopStir(
                vessel=self.vessel, vessel_type=self.vessel_type))
        return steps

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp],
            }
        }

    def syntext(self):
        verb = 'heated'
        if self.temp < 25:
            verb = 'chilled'
        formatted_properties = self.formatted_properties()
        s = f'{self.vessel} was {verb} to {formatted_properties["temp"]} for {formatted_properties["time"]}.'
        return s
