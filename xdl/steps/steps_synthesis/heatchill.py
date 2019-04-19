from typing import Optional, List, Dict, Any
from ..base_step import Step, AbstractStep
from ..steps_utility import Wait, HeatChillToTemp, StopHeatChill
from ..steps_base import CSetStirRate, CStir, CStopStir

class HeatChill(AbstractStep):
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

    @property
    def steps(self) -> List[Step]:
        steps = [
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
            steps.insert(0, CStir(vessel=self.vessel))
            if self.stir_rpm:
                steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm='default'))
        else:
            steps.insert(0, CStopStir(vessel=self.vessel))
        return steps

    @property
    def human_readable(self) -> str:
        return 'Heat/Chill {vessel} to {temp} °C for {time} s.'.format(
            **self.properties)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp],
            }
        }