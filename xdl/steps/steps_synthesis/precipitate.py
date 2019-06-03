from typing import List, Dict, Any, Optional

from ..base_step import AbstractStep, Step
from ..steps_utility import Stir, HeatChillToTemp

class Precipitate(AbstractStep):
    """Step to cause precipitation by changing temperature and stirring for some
    time.
    
    Args:
        vessel (str): Vessel to trigger precipitation in.
        temp (float): Optional. Temperature to chill to to cause precipitation.
            If not given room temperature is used.
        time (float): Optional.  Time to stir vessel for after temp is reached.
    """
    def __init__(
        self,
        vessel: str,
        temp: Optional[float] = 'default',
        time: Optional[float] = 'default'
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [
            HeatChillToTemp(vessel=self.vessel, temp=self.temp, stir=True),
            Stir(vessel=self.vessel, time=self.time),
        ]

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'temp': [self.temp]
            }
        }
