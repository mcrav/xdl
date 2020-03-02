from typing import Optional, List, Dict, Any

from .....step_utils.base_steps import AbstractStep, Step
from ..base_step import ChemputerStep
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

class RotavapStartRotation(ChemputerStep, AbstractStep):
    """Start stirring given vessel.

    Args:
        rotavap_name (str): Rotavap name to start rotation for.
        rotation_speed (float): Speed in RPM to rotate rotavap flask at.
    """

    DEFAULT_PROPS = {
        'rotation_speed': '150 RPM',
    }

    PROP_TYPES = {
        'rotavap_name': str,
        'rotation_speed': float
    }

    def __init__(
        self,
        rotavap_name: str,
        rotation_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [
            CRotavapSetRotationSpeed(
                rotavap_name=self.rotavap_name,
                rotation_speed=self.rotation_speed),
            CRotavapStartRotation(rotavap_name=self.rotavap_name)
        ]

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStopRotation(ChemputerStep, AbstractStep):
    """Stop stirring given vessel.

    Args:
        rotavap_name (str): Rotavap name to start rotation for.
    """

    PROP_TYPES = {
        'rotavap_name': str
    }

    def __init__(
        self, rotavap_name: str, **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [CRotavapStopRotation(rotavap_name=self.rotavap_name)]

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStir(ChemputerStep, AbstractStep):
    """Stir given vessel for given time at room temperature.

    Args:
        rotavap_name (str): Rotavap name to start rotation for.
        time (float): Time to stir for.
        continue_stirring (bool): Continue stirring after stirring time elapses.
        stir_speed (float): Speed to rotate rotavap flask at.
    """

    DEFAULT_PROPS = {
        'stir_speed': '250 RPM',
    }

    PROP_TYPES = {
        'rotavap_name': str,
        'time': float,
        'continue_stirring': bool,
        'stir_speed': float
    }

    def __init__(
        self,
        rotavap_name: str,
        time: float,
        continue_stirring: bool = False,
        stir_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:

        steps = [
            RotavapStartRotation(
                rotavap_name=self.rotavap_name,
                rotation_speed=self.stir_speed
            ),
            Wait(time=self.time),
        ]

        if self.continue_stirring is True:
            return steps
        else:
            steps.append(RotavapStopRotation(rotavap_name=self.rotavap_name))
            return steps

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStopEverything(ChemputerStep, AbstractStep):
    """Stop vacuum, lift rotavap flask up, vent vacuum, stop heater and stop
    rotation.

    Args:
        rotavap_name (str): Name of rotavap to stop evaporating with.
    """

    PROP_TYPES = {
        'rotavap_name': str
    }

    def __init__(self, rotavap_name: str) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [
            CStopVacuum(self.rotavap_name),
            CRotavapLiftUp(self.rotavap_name),
            CVentVacuum(self.rotavap_name),
            CRotavapStopHeater(self.rotavap_name),
            CRotavapStopRotation(self.rotavap_name),
        ]

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapStartVacuum(ChemputerStep, AbstractStep):
    """Start vacuum at given pressure.

    Args:
        rotavap_name (str): Name of rotavap to start vacuum.
        pressure (float): Pressure in mbar to set vacuum to.
    """

    PROP_TYPES = {
        'rotavap_name': str,
        'pressure': float
    }

    def __init__(self, rotavap_name: str, pressure: float) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [
            CSetVacuumSetPoint(self.rotavap_name, self.pressure),
            CStartVacuum(self.rotavap_name),
        ]

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class RotavapHeatToTemp(ChemputerStep, AbstractStep):
    """Set rotavap temperature to given temp and start heater.

    Args:
        rotavap_name (str): Name of rotavap to start heating.
        temp (float): Temperature to heat rotavap to.
    """

    PROP_TYPES = {
        'rotavap_name': str,
        'temp': float
    }

    def __init__(self, rotavap_name: str, temp: float) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [
            CRotavapSetTemp(self.rotavap_name, self.temp),
            CRotavapStartHeater(self.rotavap_name),
        ]

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'rotavap_name': {
                'rotavap': True,
            }
        }
