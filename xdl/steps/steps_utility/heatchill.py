from typing import Optional

from ..base_step import Step
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
)
from ...constants import ROOM_TEMPERATURE

class HeatChillToTemp(Step):
    """Heat/Chill vessel to given temp and leave heater/chiller on.
    
    Args:
        vessel (str): Vessel to heat/chill.
        temp (float): Temperature to heat/chill to in degrees C.
        stir (bool): If True, step will be stirred, otherwise False.
        stir_rpm (float): Speed to stir at, only used if stir == True.
        vessel_type (str): Given internally. Used to know whether to use
            heater or chiller base steps. 'ChemputerFilter' or
            'ChemputerReactor'.
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        stir: Optional[bool] = True,
        stir_rpm: Optional[float] = None,
        vessel_type: Optional[str] = None,
        wait_recording_speed: Optional[float] = 'default',
        after_recording_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:

        super().__init__(locals())
        self.steps = []
        if self.vessel_type == 'ChemputerFilter':
            self.steps = [
                CChillerSetTemp(vessel=self.vessel, temp=self.temp),
                CStartChiller(vessel=self.vessel),
                CSetRecordingSpeed(self.wait_recording_speed),
                CChillerWaitForTemp(vessel=self.vessel),
                CSetRecordingSpeed(self.after_recording_speed),
            ]
        elif self.vessel_type == 'ChemputerReactor':
            self.steps = [
                CStirrerSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
                CStirrerHeat(vessel=self.vessel),
                CSetRecordingSpeed(self.wait_recording_speed),
                CStirrerWaitForTemp(vessel=self.vessel),
                CSetRecordingSpeed(self.after_recording_speed),
            ]

        if self.stir:
            self.steps.insert(0, CStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm='default'))
        else:
            self.steps.insert(0, CStopStir(vessel=self.vessel))

        self.human_readable = 'Heat/Chill {0} to {1} °C.'.format(
            self.vessel, self.temp)

        self.requirements = {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp]
            }
        }

class StopHeatChill(Step):
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
        self.steps = []
        if self.vessel_type == 'ChemputerFilter':
            self.steps = [
                CStopChiller(self.vessel)
            ]
        elif self.vessel_type == 'ChemputerReactor':
            self.steps = [
                CStopHeat(self.vessel)
            ]
    
        self.human_readable = 'Stop heater/chiller for {0}.'.format(self.vessel)
    
        self.requirements = {
            'vessel': {
                'heatchill': True,
            }
        }

class HeatChillReturnToRT(Step):
    """Let heater/chiller return to room temperatre and then stop
    heating/chilling.
    
    Args:
        vessel (str): Vessel to attached to heater/chiller to return to room
            temperature.
        stir (bool): If True, step will be stirred, otherwise False.
        stir_rpm (float): Speed to stir at, only used if stir == True.
        vessel_type (str): Given internally. Used to know whether to use
            heater or chiller base steps. 'ChemputerFilter' or
            'ChemputerReactor'.
    """
    def __init__(
        self,
        vessel: str,
        stir: Optional[bool] = True,
        stir_rpm: Optional[float] = None,
        vessel_type: Optional[str] = None,
        **kwargs) -> None:

        super().__init__(locals())
        self.steps = []
        if self.vessel_type == 'ChemputerFilter':
            self.steps = [
                CChillerSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
                CStartChiller(vessel=self.vessel),
                CChillerWaitForTemp(vessel=self.vessel),
                CStopChiller(self.vessel)
            ]
        elif self.vessel_type == 'ChemputerReactor':
            self.steps = [
                CStirrerSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
                CStirrerHeat(vessel=self.vessel),
                CStirrerWaitForTemp(vessel=self.vessel),
                CStopHeat(self.vessel),
            ]

        if self.stir:
            self.steps.insert(0, CStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm='default'))
        else:
            self.steps.insert(0, CStopStir(vessel=self.vessel))
            
        self.human_readable = 'Stop heater/chiller for {0} and wait for it to return to room temperature'.format(
            self.vessel)

        self.requirements = {
            'vessel': {
                'heatchill': True,
            }
        }