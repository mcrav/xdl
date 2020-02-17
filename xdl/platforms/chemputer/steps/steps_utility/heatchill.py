from typing import Optional, List, Dict, Any

from .....step_utils.base_steps import AbstractStep, Step
from .....constants import (
    CHILLER_MIN_TEMP,
    CHILLER_MAX_TEMP,
    HEATER_MAX_TEMP,
)
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
    CStopHeat,

    CRotavapStartHeater,
    CRotavapStopHeater,
    CRotavapSetTemp,
)
from .general import Wait
from .stirring import StopStir, StartStir
from .....constants import (
    ROOM_TEMPERATURE,
    DEFAULT_ROTAVAP_WAIT_FOR_TEMP_TIME
)
from .....utils.misc import SanityCheck
from .....localisation import HUMAN_READABLE_STEPS
from ...utils.execution import get_heater_chiller, get_vessel_type

def heater_chiller_sanity_checks(heater, chiller, temp):
    checks = []
    if not heater and chiller:
        for condition in [
            temp <= CHILLER_MAX_TEMP,
            temp >= CHILLER_MIN_TEMP
        ]:
            checks.append(
                SanityCheck(
                    condition=condition,
                    error_msg=f'{temp} is an invalid temperature for a\
 chiller.',
                )
            )

    if not chiller and heater:
        for condition in [
            temp >= 18,
            temp <= HEATER_MAX_TEMP
        ]:
            checks.append(
                SanityCheck(
                    condition=condition,
                    error_msg=f'{temp} is an invalid temperature for a heater.'
                )
            )

    checks.append(
        SanityCheck(
            condition=CHILLER_MIN_TEMP <= temp <= HEATER_MAX_TEMP,
            error_msg=f'{temp} is an invalid temperature for a heater or a\
 chiller.'
        )
    )
    return checks

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
        heater: Optional[str] = None,
        chiller: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.vessel_type:
            self.vessel_type = get_vessel_type(graph, self.vessel)

        self.heater, self.chiller = get_heater_chiller(graph, self.vessel)

    def get_steps(self) -> List[Step]:
        steps = []
        if self.vessel_type:
            # Rotavap
            if self.vessel_type == 'rotavap':
                steps = self.get_rotavap_steps()

            else:
                # Temp less than 25, try use chiller
                if self.chiller:
                    if CHILLER_MIN_TEMP <= self.temp <= CHILLER_MAX_TEMP:
                        steps = self.get_chiller_steps()
                    elif self.heater and 18 <= self.temp <= HEATER_MAX_TEMP:
                        steps = self.get_heater_steps()

                # Temp greater than 25, try use heater, if not available try
                # use chiller.
                elif self.heater and 18 <= self.temp <= HEATER_MAX_TEMP:
                    steps = self.get_heater_steps()

        return steps

    def get_chiller_steps(self):
        return [
            CChillerSetTemp(vessel=self.vessel, temp=self.temp),
            CStartChiller(vessel=self.vessel),
        ]

    def get_heater_steps(self):
        return [
            CStirrerSetTemp(vessel=self.vessel, temp=self.temp),
            CStirrerHeat(vessel=self.vessel),
        ]

    def get_rotavap_steps(self):
        return [
            CRotavapSetTemp(rotavap_name=self.vessel, temp=self.temp),
            CRotavapStartHeater(rotavap_name=self.vessel),
        ]

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=(
                    self.heater
                    or self.chiller
                    or self.vessel_type == 'rotavap'
                ),
                error_msg=f'Trying to heat/chill vessel "{self.vessel}" with\
 no heater or chiller attached.'
            ),
            SanityCheck(
                condition=self.steps,
                error_msg=f'Unable to heat/chill vessel "{self.vessel}".\
 {self.properties}'
            )
        ] + heater_chiller_sanity_checks(self.heater, self.chiller, self.temp)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp]
            }
        }

class HeatChillSetTemp(AbstractStep):
    """Set temp on heater/chiller.

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
        heater: Optional[str] = None,
        chiller: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.vessel_type:
            self.vessel_type = get_vessel_type(graph, self.vessel)

        self.heater, self.chiller = get_heater_chiller(graph, self.vessel)

    def get_steps(self) -> List[Step]:
        steps = []
        if self.vessel_type:
            if self.vessel_type == 'rotavap':
                steps.append(
                    CRotavapSetTemp(rotavap_name=self.vessel, temp=self.temp),
                )
            else:
                if self.chiller:
                    steps.append(
                        CChillerSetTemp(vessel=self.vessel, temp=self.temp),
                    )
                if self.heater:
                    steps.append(
                        CStirrerSetTemp(vessel=self.vessel, temp=self.temp),
                    )
        return steps

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=self.steps
            )
        ] + heater_chiller_sanity_checks(self.heater, self.chiller, self.temp)

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

    DEFAULT_PROPS = {
        'active': True,
        'continue_heatchill': True,
        'stir': True,
        'stir_speed': '250 RPM',
        'wait_recording_speed': 2000,
        'after_recording_speed': 14,
    }

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
        heater: Optional[str] = None,
        chiller: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())
        assert temp is not None

    def on_prepare_for_execution(self, graph):
        if not self.vessel_type:
            self.vessel_type = get_vessel_type(graph, self.vessel)

        self.heater, self.chiller = get_heater_chiller(graph, self.vessel)

    def get_steps(self) -> List[Step]:
        steps = []
        if self.vessel_type:
            steps = self.get_initial_heatchill_steps()
            if self.vessel_type == 'rotavap':
                steps += [
                    Wait(time=DEFAULT_ROTAVAP_WAIT_FOR_TEMP_TIME),
                ]
            else:
                if self.chiller:
                    if CHILLER_MIN_TEMP <= self.temp <= CHILLER_MAX_TEMP:
                        steps += self.get_chiller_steps()

                    elif self.heater and 18 <= self.temp <= HEATER_MAX_TEMP:
                        steps += self.get_heater_steps()

                elif self.heater and 18 <= self.temp <= HEATER_MAX_TEMP:
                    steps += self.get_heater_steps()

            steps += self.get_final_heatchill_steps()

        if self.stir:
            steps.insert(0, StartStir(vessel=self.vessel,
                                      vessel_type=self.vessel_type,
                                      stir_speed=self.stir_speed))
        else:
            steps.insert(0, StopStir(
                vessel=self.vessel, vessel_type=self.vessel_type))
        return steps

    def sanity_checks(self, graph):
        return heater_chiller_sanity_checks(
            self.heater, self.chiller, self.temp)

    def get_chiller_steps(self):
        return [
            CSetRecordingSpeed(self.wait_recording_speed),
            CChillerWaitForTemp(vessel=self.vessel),
            CSetRecordingSpeed(self.after_recording_speed),
        ]

    def get_heater_steps(self):
        return [
            CSetRecordingSpeed(self.wait_recording_speed),
            CStirrerWaitForTemp(vessel=self.vessel),
            CSetRecordingSpeed(self.after_recording_speed),
        ]

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
                return HUMAN_READABLE_STEPS[
                    'HeatChillToTemp (stirring)'][language].format(
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
        self,
        vessel: str,
        vessel_type: Optional[str] = None,
        heater: str = None,
        chiller: str = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.vessel_type:
            self.vessel_type = get_vessel_type(graph, self.vessel)

        self.heater, self.chiller = get_heater_chiller(graph, self.vessel)

    def get_steps(self) -> List[Step]:
        steps = []
        if self.vessel_type:
            if self.vessel_type == 'rotavap':
                steps.append(CRotavapStopHeater(self.vessel))
            else:
                if self.chiller:
                    steps.append(CStopChiller(self.vessel))

                if self.heater:
                    steps.append(CStopHeat(self.vessel))

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

    DEFAULT_PROPS = {
        'stir': True,
        'stir_speed': '250 RPM',
        'wait_recording_speed': 2000,
        'after_recording_speed': 14,
    }

    def __init__(
        self,
        vessel: str,
        stir: Optional[bool] = 'default',
        stir_speed: Optional[float] = 'default',
        vessel_type: Optional[str] = None,
        wait_recording_speed: Optional[float] = 'default',
        after_recording_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.vessel_type:
            self.vessel_type = get_vessel_type(graph, self.vessel)

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

    DEFAULT_PROPS = {
        'wait_recording_speed': 2000,
        'after_recording_speed': 14,
    }

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

    DEFAULT_PROPS = {
        'wait_recording_speed': 2000,
        'after_recording_speed': 14,
    }

    def __init__(
        self,
        vessel: str,
        vessel_class: str = None,
        wait_recording_speed: Optional[float] = 'default',
        after_recording_speed: Optional[float] = 'default',
    ):
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        self.vessel_class = graph.nodes[self.vessel]['class']

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
