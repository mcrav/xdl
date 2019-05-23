from typing import Optional, List, Dict, Any
from ..base_step import Step, AbstractStep
from ..steps_utility import Wait, HeatChillToTemp, StopHeatChill
from ..steps_base import (
    CRotavapSetRotationSpeed,
    CRotavapStartRotation,
    CRotavapStopRotation,
    CRotavapSetTemp,
    CRotavapStartHeater,
    CRotavapStopHeater,
    CRotavapLiftDown,
    CRotavapLiftUp,
    CStopVacuum,
    CVentVacuum
)
from .add import Add
from ...constants import DEFAULT_DISSOLVE_ROTAVAP_ROTATION_SPEED, EVAPORATE_PORT

class Dissolve(AbstractStep):
    """Dissolve contents of vessel in given solvent.
    
    Args:
        vessel (str): Vessel to dissolve contents of. 
        solvent (str): Solvent to dissolve contents of vessel with.
        volume (float): Volume of solvent to use.
        port (str): Port to add solvent to.
        temp (float): Temperature to stir at. Optional.
        time (float): Time to stir for. Optional.
        solvent_vessel (str): Given internally. Flask containing solvent.
        vessel_type (str): Given internally. 'reactor', 'filter', 'rotavap',
            'flask' or 'separator'.
    """
    def __init__(
        self,
        vessel: str,
        solvent: str,
        volume: float,
        port: Optional[str] = None,
        temp: Optional[float] = 'default',
        time: Optional[float] = 'default',
        stir_rpm: Optional[float] = 'default',
        solvent_vessel: Optional[str] = None,
        vessel_type: Optional[str] = None,
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        if self.vessel_type == 'rotavap':
            steps = [
                Add(reagent=self.solvent,
                    volume=self.volume,
                    vessel=self.vessel,
                    port=EVAPORATE_PORT,
                    stir=False),
                CRotavapSetTemp(self.vessel, self.temp),
                CRotavapStartHeater(self.vessel),
                CRotavapSetRotationSpeed(
                    self.vessel, DEFAULT_DISSOLVE_ROTAVAP_ROTATION_SPEED),
                CRotavapStartRotation(self.vessel),
                CRotavapLiftDown(self.vessel),

                Wait(self.time),

                CRotavapStopRotation(self.vessel),
                CRotavapStopHeater(self.vessel),
                CRotavapLiftUp(self.vessel),
            ]
        else:
            steps = [
                Add(reagent=self.solvent,
                    volume=self.volume,
                    vessel=self.vessel,
                    port=self.port),
                HeatChillToTemp(
                    vessel=self.vessel,
                    temp=self.temp,
                    stir=True,
                    stir_rpm=self.stir_rpm),
                Wait(self.time),
                StopHeatChill(vessel=self.vessel),
            ]
        return steps

    def get_human_readable(self) -> Dict[str, str]:
        en = 'Dissolve contents of {vessel} in {solvent} ({volume} mL) at {temp} °C over {time} seconds.'.format(
            **self.properties)
        return {
            'en': en,
        }

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp],
                'stir': True,
            }
        }
        