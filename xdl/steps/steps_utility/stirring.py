from typing import Optional, Dict, Any, List

from ..base_steps import AbstractStep, Step
from ..steps_base import (
    CStir,
    CSetStirRate,
    CStopStir,
    CRotavapSetRotationSpeed,
    CRotavapStartRotation,
    CRotavapStopRotation,
)
from .general import Wait
from .rotavap import RotavapStir
from ...constants import DEFAULT_DISSOLVE_ROTAVAP_ROTATION_SPEED

class SetStirRate(AbstractStep):
    """Set stir rate. Works on rotavap, reactor or filter.

    Args:
        vessel (str): Vessel to set stir rate for.
        stir_speed (float): Stir rate in RPM
        vessel_type (str): Given internally. 'filter', 'rotavap' or 'reactor'.
    """
    def __init__(
        self, vessel: str, stir_speed: float, vessel_type: Optional[str] = None
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        if self.vessel_type == 'rotavap':
            return [CRotavapSetRotationSpeed(rotavap_name=self.vessel,
                                             rotation_speed=self.stir_speed)]
        else:
            return [CSetStirRate(vessel=self.vessel, stir_speed=self.stir_speed)]

class StartStir(AbstractStep):
    """Start stirring given vessel.

    Args:
        vessel (str): Vessel name to stir.
        stir_speed (int, optional): Speed in RPM to stir at.
    """
    def __init__(
        self,
        vessel: str,
        vessel_type: Optional[str] = None,
        stir_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        if self.vessel_type == 'rotavap':
            #  Limit RPM if high one meant for stirrer passed in by accident.
            stir_speed = min(
                self.stir_speed, DEFAULT_DISSOLVE_ROTAVAP_ROTATION_SPEED)
            return [
                CRotavapSetRotationSpeed(rotavap_name=self.vessel,
                                         rotation_speed=stir_speed),
                CRotavapStartRotation(rotavap_name=self.vessel)
            ]
        return [
            CStir(vessel=self.vessel),
            CSetStirRate(vessel=self.vessel, stir_speed=self.stir_speed),
        ]

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'stir': True
            }
        }

class StopStir(AbstractStep):
    """Stop stirring given vessel.

    Args:
        vessel (str): Vessel name to stop stirring.
        vessel_has_stirrer (bool): True if vessel has stirrer, otherwise False.
            The point of this is that StopStir can be used and if there is no
            stirrer then it is just ignored rather than an error being raised.
    """
    def __init__(
        self,
        vessel:str,
        vessel_type: str = None,
        vessel_has_stirrer: bool = True,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        if self.vessel_has_stirrer:
            return [CStopStir(vessel=self.vessel)]
        elif self.vessel_type == 'rotavap':
            return [CRotavapStopRotation(rotavap_name=self.vessel)]
        return []

class Stir(AbstractStep):
    """Stir given vessel for given time at room temperature.

    Args:
        vessel (str): Vessel to stir.
        time (float): Time to stir for.
        stir_speed (float): Stir rate in RPM.
        vessel_type (str): Given internally. 'reactor', 'filter', 'rotavap',
            'flask' or 'separator'.
    """
    def __init__(
        self,
        vessel: str,
        time: float,
        stir_speed: Optional[float] = 'default',
        vessel_type: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        if self.vessel_type == 'rotavap':
            # Limit stir_speed as rotavap can't rotate as fast as stirrer.
            stir_speed = min(
                self.stir_speed, DEFAULT_DISSOLVE_ROTAVAP_ROTATION_SPEED)
            return [
                RotavapStir(
                    rotavap_name=self.vessel,
                    stir_speed=stir_speed,
                    time=self.time),
            ]
        else:
            return [
                StartStir(vessel=self.vessel, stir_speed=self.stir_speed),
                Wait(time=self.time),
                StopStir(vessel=self.vessel),
            ]

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'stir': True,
            }
        }
