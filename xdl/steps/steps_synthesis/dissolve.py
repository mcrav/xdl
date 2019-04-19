from typing import Optional, List, Dict, Any
from ..base_step import Step, AbstractStep
from ..steps_utility import Wait, HeatChillToTemp
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
        vessel_is_rotavap (bool): Given internally. True is vessel is a rotavap.
            Needed as different procedure used for dissolving a solid in a
            rotavap.
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
        vessel_is_rotavap: Optional[bool] = False,
    ) -> None:
        super().__init__(locals())

    @property
    def steps(self) -> List[Step]:
        if self.vessel_is_rotavap:
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
            ]
        return steps

    @property
    def human_readable(self) -> str:
        return 'Dissolve contents of {vessel} in {solvent} ({volume} mL) at {temp} °C over {time} seconds.'.format(
            **self.properties)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp],
                'stir': True,
            }
        }
        