from typing import Optional, List, Dict, Any

from ..base_step import AbstractStep, Step
from ..steps_base import (
    CChillerSetTemp,
    CStartChiller,
    CSetRecordingSpeed,
    CChillerWaitForTemp,
    CStopChiller,

    CStirrerSetTemp,
    CStirrerHeat,
    CStirrerWaitForTemp,
    CStir,
    CSetStirRate,
    CStopStir,
    CStopHeat,

    CRotavapStartHeater,
    CRotavapStopHeater,
    CRotavapSetTemp,
    CRotavapStopRotation,
)
from .general import Wait
from .stirring import StopStir, StartStir
from ...constants import (
    ROOM_TEMPERATURE,
    DEFAULT_ROTAVAP_WAIT_FOR_TEMP_TIME
)
from ...utils.errors import XDLError
from ...localisation import HUMAN_READABLE_STEPS

class HeatChillToTemp(AbstractStep):
    """Heat/Chill vessel to given temp and leave heater/chiller on.
    
    Args:
        vessel (str): Vessel to heat/chill.
        temp (float): Temperature to heat/chill to in degrees C.
        stir (bool): If True, step will be stirred, otherwise False.
        stir_speed (float): Speed to stir at, only used if stir == True.
        vessel_type (str): Given internally. Used to know whether to use
            heater or chiller base steps. 'ChemputerFilter' or
            'ChemputerReactor'.
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        stir: Optional[bool] = True,
        stir_speed: Optional[float] = 'default',
        vessel_type: Optional[str] = None,
        wait_recording_speed: Optional[float] = 'default',
        after_recording_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        steps = []
        if self.vessel_type == 'filter':
            steps = [
                CChillerSetTemp(vessel=self.vessel, temp=self.temp),
                CStartChiller(vessel=self.vessel),
                CSetRecordingSpeed(self.wait_recording_speed),
                CChillerWaitForTemp(vessel=self.vessel),
                CSetRecordingSpeed(self.after_recording_speed),
            ]
        elif self.vessel_type == 'reactor':
            steps = [
                CStirrerSetTemp(vessel=self.vessel, temp=self.temp),
                CStirrerHeat(vessel=self.vessel),
                CSetRecordingSpeed(self.wait_recording_speed),
                CStirrerWaitForTemp(vessel=self.vessel),
                CSetRecordingSpeed(self.after_recording_speed),
            ]
        elif self.vessel_type == 'rotavap':
            steps = [
                CRotavapSetTemp(rotavap_name=self.vessel, temp=self.temp),
                CRotavapStartHeater(rotavap_name=self.vessel),
                Wait(time=DEFAULT_ROTAVAP_WAIT_FOR_TEMP_TIME),
            ]

        if self.stir:
            steps.insert(0, StartStir(vessel=self.vessel,
                                      vessel_type=self.vessel_type,
                                      stir_speed=self.stir_speed))
        else:
            steps.insert(0, StopStir(
                vessel=self.vessel, vessel_type=self.vessel_type))
        return steps
    
    def human_readable(self, language='en') -> str:
        try:
            if self.stir:
                return HUMAN_READABLE_STEPS['HeatChillToTemp (stirring)'][language].format(
                    **self.formatted_properties())
            else:
                return HUMAN_READABLE_STEPS[
                    'HeatChillToTemp (not stirring)'][language].format(
                        **self.formatted_properties())
        except KeyError:
            return self.name

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp]
            }
        }

class StopHeatChill(AbstractStep):
    """Stop heater/chiller on given vessel..
    
    Args:
        vessel (str): Name of vessel attached to heater/chiller..
        vessel_type (str): Given internally. Used to know whether to use
            heater or chiller base steps. 'ChemputerFilter' or
            'ChemputerReactor'.
    """
    def __init__(
        self, vessel: str, vessel_type: Optional[str] = None, **kwargs) -> None:
        super().__init__(locals())
    
    def get_steps(self) -> List[Step]:
        steps = []
        if self.vessel_type == 'filter':
            steps = [CStopChiller(self.vessel)]

        elif self.vessel_type == 'reactor':
            steps = [CStopHeat(self.vessel)]

        elif self.vessel_type == 'rotavap':
            steps = [CRotavapStopHeater(self.vessel)]

        return steps

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'heatchill': True,
            }
        }

class HeatChillReturnToRT(AbstractStep):
    """Let heater/chiller return to room temperatre and then stop
    heating/chilling.
    
    Args:
        vessel (str): Vessel to attached to heater/chiller to return to room
            temperature.
        stir (bool): If True, step will be stirred, otherwise False.
        stir_speed (float): Speed to stir at, only used if stir == True.
        vessel_type (str): Given internally. Used to know whether to use
            heater or chiller base steps. 'ChemputerFilter' or
            'ChemputerReactor'.
    """
    def __init__(
        self,
        vessel: str,
        stir: Optional[bool] = True,
        stir_speed: Optional[float] = 'default',
        vessel_type: Optional[str] = None,
        wait_recording_speed: Optional[float] = 'default',
        after_recording_speed: Optional[float] = 'default',
        **kwargs) -> None:
        super().__init__(locals())
            
    def get_steps(self) -> List[Step]:
        steps = []
        if self.vessel_type == 'filter':
            steps = [
                CChillerSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
                CStartChiller(vessel=self.vessel),
                CSetRecordingSpeed(self.wait_recording_speed),
                CChillerWaitForTemp(vessel=self.vessel),
                CSetRecordingSpeed(self.after_recording_speed),
                CStopChiller(self.vessel)
            ]
        elif self.vessel_type == 'reactor':
            steps = [
                CStirrerSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
                CStirrerHeat(vessel=self.vessel),
                CSetRecordingSpeed(self.wait_recording_speed),
                CStirrerWaitForTemp(vessel=self.vessel),
                CSetRecordingSpeed(self.after_recording_speed),
                CStopHeat(self.vessel),
            ]
        elif self.vessel_type == 'rotavap':
            steps = [
                CRotavapStopHeater(rotavap_name=self.vessel),
                Wait(time=DEFAULT_ROTAVAP_WAIT_FOR_TEMP_TIME),
            ]

        if self.stir:
            steps.insert(0, StartStir(vessel=self.vessel,
                                      vessel_type=self.vessel_type,
                                      stir_speed=self.stir_speed))
        else:
            steps.insert(0, StopStir(
                vessel=self.vessel, vessel_type=self.vessel_type))
        return steps

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'heatchill': True,
            }
        }