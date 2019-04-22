from typing import Optional

from ..base_step import Step
from ..steps_base import (
    CRotavapSetRotationSpeed,
    CRotavapStartRotation,
    CRotavapStopRotation,
    CStopVacuum,
    CVentVacuum,
    CRotavapLiftUp,
    CRotavapStopHeater,
    CSetVacuumSetPoint,
    CStartVacuum,
    CRotavapSetTemp,
    CRotavapStartHeater,
)
from .general import Wait

class RotavapStartRotation(Step):
    """Start stirring given vessel.

    Args:
        rotavap_name (str): Rotavap name to start rotation for.
        rotation_speed (float): Speed in RPM to rotate rotavap flask at.
    """
    def __init__(
        self,
        rotavap_name: str,
        rotation_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            CRotavapSetRotationSpeed(
                rotavap_name=self.rotavap_name,
                rotation_speed=self.rotation_speed),
            CRotavapStartRotation(rotavap_name=self.rotavap_name)
        ]

        self.human_readable = 'Set rotation speed to {rotation_speed} RPM and start rotation for {rotavap_name}.'.format(
            **self.properties)

        self.requirements = {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStopRotation(Step):
    """Stop stirring given vessel.
    
    Args:
        rotavap_name (str): Rotavap name to start rotation for.
    """
    def __init__(
        self, rotavap_name: str, **kwargs) -> None:
        super().__init__(locals())

        self.steps = [CRotavapStopRotation(rotavap_name=self.rotavap_name)]

        self.human_readable = 'Stop rotation for {rotavap_name}.'.format(
            **self.properties)

        self.requirements = {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStir(Step):
    """Stir given vessel for given time at room temperature.

    Args:
        rotavap_name (str): Rotavap name to start rotation for.
        time (float): Time to stir for.
        stir_rpm (float): Speed to rotate rotavap flask at.
    """
    def __init__(
        self,
        rotavap_name: str,
        time: float,
        stir_rpm: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            RotavapStartRotation(
                rotavap_name=self.rotavap_name,
                rotation_speed=self.stir_rpm
            ),
            Wait(time=self.time),
            RotavapStopRotation(rotavap_name=self.rotavap_name)
        ]

        self.human_readable = 'Use rotavap rotation to stir {rotavap_name} for {time} s at {stir_rpm} RPM.'.format(
            **self.properties)

        self.requirements = {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStopEverything(Step):
    """Stop vacuum, lift rotavap flask up, vent vacuum, stop heater and stop
    rotation.
    
    Args:
        rotavap_name (str): Name of rotavap to stop evaporating with.
    """
    def __init__(self, rotavap_name: str) -> None:
        super().__init__(locals())

        self.steps = [
            CStopVacuum(self.rotavap_name),
            CRotavapLiftUp(self.rotavap_name),
            CVentVacuum(self.rotavap_name),
            CRotavapStopHeater(self.rotavap_name),
            CRotavapStopRotation(self.rotavap_name),
        ]

        self.human_readable = 'Stop vacuum, lift rotavap flask up, vent vacuum, stop heater and stop rotation for {rotavap_name}'.format(
            **self.properties)

        self.requirements = {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStartVacuum(Step):
    """Start vacuum at given pressure.
    
    Args:
        rotavap_name (str): Name of rotavap to start vacuum.
        pressure (float): Pressure in mbar to set vacuum to.
    """
    def __init__(self, rotavap_name: str, pressure: float) -> None:
        super().__init__(locals())

        self.steps = [
            CSetVacuumSetPoint(self.rotavap_name, self.pressure),
            CStartVacuum(self.rotavap_name),
        ]

        self.human_readable = 'Start vacuum at {pressure} mbar for {rotavap_name}'.format(
            **self.properties)

        self.requirements = {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapHeatToTemp(Step):
    """Set rotavap temperature to given temp and start heater.
    
    Args:
        rotavap_name (str): Name of rotavap to start heating.
        temp (float): Temperature to heat rotavap to.
    """
    def __init__(self, rotavap_name: str, temp: float) -> None:
        super().__init__(locals())
        
        self.steps = [
            CRotavapSetTemp(self.rotavap_name, self.temp),
            CRotavapStartHeater(self.rotavap_name),
        ]

        self.human_readable = 'Set rotavap temperature to {temp} and start heater for {rotavap_name}'.format(
            **self.properties)

        self.requirements = {
            'rotavap_name': {
                'rotavap': True,
            }
        }