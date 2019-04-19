from typing import Optional, List, Dict, Any

from ..base_step import AbstractStep, Step
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

class RotavapStartRotation(AbstractStep):
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

    @property
    def steps(self) -> List[Step]:
        return [
            CRotavapSetRotationSpeed(
                rotavap_name=self.rotavap_name,
                rotation_speed=self.rotation_speed),
            CRotavapStartRotation(rotavap_name=self.rotavap_name)
        ]

    @property
    def human_readable(self) -> str:
        return 'Set rotation speed to {rotation_speed} RPM and start rotation for {rotavap_name}.'.format(
            **self.properties)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStopRotation(AbstractStep):
    """Stop stirring given vessel.
    
    Args:
        rotavap_name (str): Rotavap name to start rotation for.
    """
    def __init__(
        self, rotavap_name: str, **kwargs) -> None:
        super().__init__(locals())

    @property
    def steps(self) -> List[Step]:
        return [CRotavapStopRotation(rotavap_name=self.rotavap_name)]

    @property
    def human_readable(self) -> str:
        return 'Stop rotation for {rotavap_name}.'.format(
            **self.properties)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStir(AbstractStep):
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

    @property
    def steps(self) -> List[Step]:
        return [
            RotavapStartRotation(
                rotavap_name=self.rotavap_name,
                rotation_speed=self.stir_rpm
            ),
            Wait(time=self.time),
            RotavapStopRotation(rotavap_name=self.rotavap_name)
        ]

    @property
    def human_readable(self) -> str:
        return 'Use rotavap rotation to stir {rotavap_name} for {time} s at {stir_rpm} RPM.'.format(
            **self.properties)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStopEverything(AbstractStep):
    """Stop vacuum, lift rotavap flask up, vent vacuum, stop heater and stop
    rotation.
    
    Args:
        rotavap_name (str): Name of rotavap to stop evaporating with.
    """
    def __init__(self, rotavap_name: str) -> None:
        super().__init__(locals())

    @property
    def steps(self) -> List[Step]:
        return [
            CStopVacuum(self.rotavap_name),
            CRotavapLiftUp(self.rotavap_name),
            CVentVacuum(self.rotavap_name),
            CRotavapStopHeater(self.rotavap_name),
            CRotavapStopRotation(self.rotavap_name),
        ]

    @property
    def human_readable(self) -> str:
        return 'Stop vacuum, lift rotavap flask up, vent vacuum, stop heater and stop rotation for {rotavap_name}'.format(
            **self.properties)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStartVacuum(AbstractStep):
    """Start vacuum at given pressure.
    
    Args:
        rotavap_name (str): Name of rotavap to start vacuum.
        pressure (float): Pressure in mbar to set vacuum to.
    """
    def __init__(self, rotavap_name: str, pressure: float) -> None:
        super().__init__(locals())

    @property
    def steps(self) -> List[Step]:
        return [
            CSetVacuumSetPoint(self.rotavap_name, self.pressure),
            CStartVacuum(self.rotavap_name),
        ]

    @property
    def human_readable(self) -> str:
        return 'Start vacuum at {pressure} mbar for {rotavap_name}'.format(
            **self.properties)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapHeatToTemp(AbstractStep):
    """Set rotavap temperature to given temp and start heater.
    
    Args:
        rotavap_name (str): Name of rotavap to start heating.
        temp (float): Temperature to heat rotavap to.
    """
    def __init__(self, rotavap_name: str, temp: float) -> None:
        super().__init__(locals())
        
    @property
    def steps(self) -> List[Step]:
        return [
            CRotavapSetTemp(self.rotavap_name, self.temp),
            CRotavapStartHeater(self.rotavap_name),
        ]

    @property
    def human_readable(self) -> str:
        return 'Set rotavap temperature to {temp} and start heater for {rotavap_name}'.format(
            **self.properties)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }