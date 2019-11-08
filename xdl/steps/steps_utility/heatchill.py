from typing import Optional, List, Dict, Any

from ..base_steps import AbstractStep, Step
from ..steps_base import (
    CChillerSetTemp,
    CStartChiller,
    CSetRecordingSpeed,
    CChillerWaitForTemp,
    CStopChiller,
    CRampChiller,
    CSetCoolingPower,

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

class StartHeatChill(AbstractStep):
    """Start heating/chilling vessel to given temp and leave heater/chiller on.
    Don't wait to reach temp.

    Args:
        vessel (str): Vessel to heat/chill.
        temp (float): Temperature to heat/chill to in degrees C.
        vessel_type (str): Given internally. Used to know whether to use
            heater or chiller base steps. 'filter', 'rotavap' or 'reactor'
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        vessel_type: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        steps = []
        if self.vessel_type == 'filter':
            steps = [
                CChillerSetTemp(vessel=self.vessel, temp=self.temp),
                CStartChiller(vessel=self.vessel),
            ]
        elif self.vessel_type == 'reactor':
            steps = [
                CStirrerSetTemp(vessel=self.vessel, temp=self.temp),
                CStirrerHeat(vessel=self.vessel),
            ]
        elif self.vessel_type == 'rotavap':
            steps = [
                CRotavapSetTemp(rotavap_name=self.vessel, temp=self.temp),
                CRotavapStartHeater(rotavap_name=self.vessel),
            ]
        return steps

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp]
            }
        }

class HeatChillSetTemp(AbstractStep):
    """Start heating/chilling vessel to given temp and leave heater/chiller on.
    Don't wait to reach temp.

    Args:
        vessel (str): Vessel to set temp.
        temp (float): Temperature to set in degrees C.
        vessel_type (str): Given internally. Used to know whether to use
            heater or chiller base steps. 'filter', 'rotavap' or 'reactor'
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        vessel_type: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        steps = []
        if self.vessel_type == 'filter':
            steps = [
                CChillerSetTemp(vessel=self.vessel, temp=self.temp),
            ]
        elif self.vessel_type == 'reactor':
            steps = [
                CStirrerSetTemp(vessel=self.vessel, temp=self.temp),
            ]
        elif self.vessel_type == 'rotavap':
            steps = [
                CRotavapSetTemp(rotavap_name=self.vessel, temp=self.temp),
            ]
        return steps

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp]
            }
        }

class HeatChillToTemp(AbstractStep):
    """Heat/Chill vessel to given temp.

    Args:
        vessel (str): Vessel to heat/chill.
        temp (float): Temperature to heat/chill to in degrees C.
        active (bool): If True, will actively heat/chill to the desired temp and
            leave heater/chiller on. If False, stop heating/chilling and wait
            for the temp to be reached.
        continue_heatchill (bool): If True, heating/chilling will be left on
            at end of step, even if active is False.
        stir (bool): If True, step will be stirred, otherwise False.
        stir_speed (float): Speed to stir at, only used if stir == True.
        vessel_type (str): Given internally. Used to know whether to use
            heater or chiller base steps. 'filter', 'rotavap' or 'reactor'
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        active: bool = 'default',
        continue_heatchill: bool = 'default',
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
            steps = self.get_initial_heatchill_steps() + [
                CSetRecordingSpeed(self.wait_recording_speed),
                CChillerWaitForTemp(vessel=self.vessel),
                CSetRecordingSpeed(self.after_recording_speed),
            ] + self.get_final_heatchill_steps()

        elif self.vessel_type == 'reactor':
            steps = self.get_initial_heatchill_steps() + [
                CSetRecordingSpeed(self.wait_recording_speed),
                CStirrerWaitForTemp(vessel=self.vessel),
                CSetRecordingSpeed(self.after_recording_speed),
            ] + self.get_final_heatchill_steps()

        elif self.vessel_type == 'rotavap':
            steps = self.get_initial_heatchill_steps() + [
                Wait(time=DEFAULT_ROTAVAP_WAIT_FOR_TEMP_TIME),
            ] + self.get_final_heatchill_steps()

        if self.stir:
            steps.insert(0, StartStir(vessel=self.vessel,
                                      vessel_type=self.vessel_type,
                                      stir_speed=self.stir_speed))
        else:
            steps.insert(0, StopStir(
                vessel=self.vessel, vessel_type=self.vessel_type))
        return steps

    def get_initial_heatchill_steps(self) -> List[Step]:
        if self.active:
            return [StartHeatChill(vessel=self.vessel, temp=self.temp)]

        else:
            return [HeatChillSetTemp(vessel=self.vessel, temp=self.temp),
                    StopHeatChill(vessel=self.vessel)]

    def get_final_heatchill_steps(self) -> List[Step]:
        # Inactive heatchilling, need to switch on at end
        if self.continue_heatchill and not self.active:
            return [StartHeatChill(vessel=self.vessel, temp=self.temp)]

        # Active heatchilling, need to switch off at end
        elif not self.continue_heatchill and self.active:
            return [StopHeatChill(vessel=self.vessel)]

        # Inactive leaving off, or active leaving on.
        else:
            return []


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

    def syntext(self) -> str:
        verb = 'heated'
        if self.temp < 25:
            verb = 'chilled'
        return f'{self.vessel} was {verb} to {self.temp} °C.'

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

    def syntext(self) -> str:
        return f'Heating was discontinued for {self.vessel}.'

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
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        steps = []
        if self.vessel_type == 'filter':
            steps = [ChillerReturnToRT(vessel=self.vessel)]

        elif self.vessel_type == 'reactor':
            steps = [StirrerReturnToRT(vessel=self.vessel)]

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

class StirrerReturnToRT(AbstractStep):
    def __init__(
        self,
        vessel: str,
        wait_recording_speed: Optional[float] = 'default',
        after_recording_speed: Optional[float] = 'default',
    ):
        super().__init__(locals())

    def get_steps(self):
        return [
            CStirrerSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
            CStopHeat(vessel=self.vessel),
            CSetRecordingSpeed(self.wait_recording_speed),
            CStirrerWaitForTemp(vessel=self.vessel),
            CSetRecordingSpeed(self.after_recording_speed),
        ]

class ChillerReturnToRT(AbstractStep):
    def __init__(
        self,
        vessel: str,
        vessel_class: str = None,
        wait_recording_speed: Optional[float] = 'default',
        after_recording_speed: Optional[float] = 'default',
    ):
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        self.properties['vessel_class'] = graph[self.vessel]['class']
        self.update()

    def get_steps(self):
        if self.vessel_class == 'JULABOCF41':
            return [
                CChillerSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
                CSetCoolingPower(vessel=self.vessel, cooling_power=0),
                CStartChiller(vessel=self.vessel),
                CSetRecordingSpeed(self.wait_recording_speed),
                CChillerWaitForTemp(vessel=self.vessel),
                CSetRecordingSpeed(self.after_recording_speed),
                CSetCoolingPower(vessel=self.vessel, cooling_power=100),
                CStopChiller(self.vessel)
            ]

        elif self.vessel_class == 'HuberPetiteFleur':
            return [
                CRampChiller(
                    vessel=self.vessel,
                    ramp_duration='1 hr',
                    end_temperature=ROOM_TEMPERATURE
                )
            ]
        else:
            return []
