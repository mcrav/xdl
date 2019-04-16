from typing import Optional
from ..base_step import Step
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
    CRotavapLiftUp
)
from ..steps_utility import Wait


class Rotavap(Step):
    """Rotavap contents of given vessel at given temp and given pressure for
    given time.

    Args:
        rotavap_name (str): Name of rotavap vessel.
        temp (float): Temperature to set rotavap water bath to in °C.
        vacuum_pressure (float): Pressure to set rotavap vacuum to in mbar.
        time (float): Time to rotavap for in seconds.
        rotation_speed (float): Speed in RPM to rotate flask at.
    """
    def __init__(
        self,
        rotavap_name: str,
        temp: float,
        pressure: float,
        time: Optional[float] = 'default',
        rotation_speed: Optional[float] = 'default',
        **kwargs
    ):
        super().__init__(locals())

        self.steps = [
            # Start rotation
            CRotavapSetRotationSpeed(self.rotavap_name, self.rotation_speed),
            CRotavapStartRotation(self.rotavap_name),

            # Lower flask into bath.
            CRotavapLiftDown(self.rotavap_name),

            # Start heating
            CRotavapSetTemp(self.rotavap_name, self.temp),
            CRotavapStartHeater(self.rotavap_name),

            # Start vacuum
            CSetVacuumSetPoint(self.rotavap_name, self.pressure),
            CStartVacuum(self.rotavap_name),
            
            # Wait for evaporation to happen.
            Wait(time=self.time),

            # Stop evaporation.
            CStopVacuum(self.rotavap_name),
            CVentVacuum(self.rotavap_name),
            CRotavapStopRotation(self.rotavap_name),
            CRotavapStopHeater(self.rotavap_name),
            CRotavapLiftUp(self.rotavap_name),            
        ]

        self.human_readable = 'Rotavap contents of {rotavap_name} at {temp} °C and {pressure} mbar for {time}.'.format(
            **self.properties)

        self.requirements = {
            'rotavap_name': {
                'rotavap': True,
            }
        }
