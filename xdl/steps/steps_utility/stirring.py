from typing import Optional, Dict, Any, List

from ..base_step import AbstractStep, Step
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
    """[summary]
    
    Args:
        vessel (str): [description]
        stir_rpm (float): [description]
        vessel_type (Optional[str], optional): [description]. Defaults to None.
    """
    def __init__(
        self, vessel: str, stir_rpm: float, vessel_type: Optional[str] = None
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        if self.vessel_type == 'rotavap':
            return [CRotavapSetRotationSpeed(rotavap_name=self.vessel,
                                             rotation_speed=self.stir_rpm)]
        else:
            return [CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm)]

    def human_readable(self) -> str:
        return 'Set stir rate of {vessel} to {stir_rpm} RPM.'.format(
            **self.properties)



class StartStir(AbstractStep):
    """Start stirring given vessel.

    Args:
        vessel (str): Vessel name to stir.
        stir_rpm (int, optional): Speed in RPM to stir at.
    """
    def __init__(
        self,
        vessel: str,
        vessel_type: Optional[str] = None,
        stir_rpm: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())
        
    def get_steps(self) -> List[Step]:
        if self.vessel_type == 'rotavap':
            #  Limit RPM if high one meant for stirrer passed in by accident.
            stir_rpm = min(
                self.stir_rpm, DEFAULT_DISSOLVE_ROTAVAP_ROTATION_SPEED)
            return [
                CRotavapSetRotationSpeed(rotavap_name=self.vessel,
                                         rotation_speed=stir_rpm),
                CRotavapStartRotation(rotavap_name=self.vessel)
            ]
        return [
            CStir(vessel=self.vessel),
            CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm),
        ]

    @property
    def human_readable(self) -> str:
        return 'Set stir rate to {stir_rpm} RPM and start stirring {vessel}.'.format(
            **self.properties)

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

    @property
    def human_readable(self) -> str:
        return 'Stop stirring {0}.'.format(self.vessel)

class Stir(AbstractStep):
    """Stir given vessel for given time at room temperature.

    Args:
        vessel (str): Vessel to stir.
        time (float): Time to stir for.
        stir_rpm (float): Stir rate in RPM.
        vessel_type (str): Given internally. 'reactor', 'filter', 'rotavap',
            'flask' or 'separator'.
    """
    def __init__(
        self,
        vessel: str,
        time: float,
        stir_rpm: Optional[float] = 'default',
        vessel_type: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        if self.vessel_type == 'rotavap':
            # Limit stir_rpm as rotavap can't rotate as fast as stirrer.
            stir_rpm = min(
                self.stir_rpm, DEFAULT_DISSOLVE_ROTAVAP_ROTATION_SPEED)
            return [
                RotavapStir(
                    rotavap_name=self.vessel,
                    stir_rpm=stir_rpm,
                    time=self.time),
            ]
        else:
            return [
                StartStir(vessel=self.vessel, stir_rpm=self.stir_rpm),
                Wait(time=self.time),
                StopStir(vessel=self.vessel),
            ]

    @property
    def human_readable(self) -> str:
        return 'Stir {vessel} for {time} s at {stir_rpm} RPM.'.format(
            **self.properties)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'stir': True,
            }
        }
 