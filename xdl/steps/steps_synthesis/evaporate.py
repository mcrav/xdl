from typing import Optional, List, Dict, Any
from ..base_step import Step, AbstractStep
from ..steps_base import (
    CRotavapSetRotationSpeed,
    CRotavapStartRotation,
    CRotavapLiftDown,
    CRotavapSetTemp,
    CRotavapStartHeater,
    CSetVacuumSetPoint,
    CStartVacuum,
    CStopVacuum,
    CVentVacuum,
    CRotavapStopRotation,
    CRotavapStopHeater,
    CRotavapLiftUp,
    CRotavapAutoEvaporation,
)
from ..steps_utility import (
    Wait,
    Transfer,
    RotavapStopEverything,
    RotavapHeatToTemp,
    RotavapStartVacuum,
    RotavapStartRotation,
)
from ...constants import COLLECT_PORT

class Evaporate(AbstractStep):
    """Evaporate contents of given vessel at given temp and given pressure for
    given time.

    Args:
        rotavap_name (str): Name of rotavap vessel.
        temp (float): Temperature to set rotavap water bath to in °C.
        pressure (float): Pressure to set rotavap vacuum to in mbar. Has no
            effect if mode == 'auto', otherwise must be passed.
        time (float): Time to rotavap for in seconds.
        rotation_speed (float): Speed in RPM to rotate flask at.
        mode (str): 'manual' or 'auto'. If 'manual', given time/temp/pressure
            are used. If 'auto', automatic pressure/time evaluation built into
            the rotavap are used. In this case time and pressure should still be
            given, but correspond to maximum time and minimum pressure that if
            either is reached, the evaporation will stop.
    """
    def __init__(
        self,
        rotavap_name: str,
        temp: float,
        pressure: Optional[float] = None,
        time: Optional[float] = 'default',
        rotation_speed: Optional[float] = 'default',
        mode: Optional[str] = 'manual',
        waste_vessel: Optional[str] = None,
        collection_flask_volume: Optional[float] = None,
        **kwargs
    ):
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        collection_flask_volume = 'all'
        if self.collection_flask_volume:
            collection_flask_volume = self.collection_flask_volume

        steps = [
            # Start rotation
            RotavapStartRotation(self.rotavap_name, self.rotation_speed),
            # Lower flask into bath.
            CRotavapLiftDown(self.rotavap_name),
            # Start heating
            RotavapHeatToTemp(self.rotavap_name, self.temp),
            # Start vacuum
            RotavapStartVacuum(self.rotavap_name, self.pressure),
            # Wait for evaporation to happen.
            Wait(time=self.time),
            # Stop evaporation.
            RotavapStopEverything(self.rotavap_name),
            # Empty collect flask
            Transfer(from_vessel=self.rotavap_name,
                        to_vessel=self.waste_vessel,
                        from_port=COLLECT_PORT,
                        volume=collection_flask_volume)
        ]

        if self.mode == 'auto':
            steps[-3] = CRotavapAutoEvaporation(
                rotavap_name=self.rotavap_name,
                sensitivity=2, # High sensitivity
                vacuum_limit=1, # Auto pressure
                time_limit=self.time,
                vent_after=True
            )            
        return steps

    def get_human_readable(self) -> Dict[str, str]:
        en = 'Evaporate contents of {rotavap_name} at {temp} °C and {pressure} mbar for {time}.'.format(
            **self.properties)
        return {
            'en': en,
        }

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }