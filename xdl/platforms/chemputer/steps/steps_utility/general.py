from typing import Optional, List
from .....step_utils.base_steps import AbstractStep, Step
from ..steps_base import CSetRecordingSpeed, CWait, CWaitUntil
from .....localisation import HUMAN_READABLE_STEPS

class Wait(AbstractStep):
    """Wait for given time.

    Args:
        time (int): Time in seconds
        wait_recording_speed (int): Recording speed during wait (faster) ~2000
        after_recording_speed (int): Recording speed after wait (slower) ~14
    """

    DEFAULT_PROPS = {
        'wait_recording_speed': 2000,
        'after_recording_speed': 14,
    }

    PROP_TYPES = {
        'time': float,
        'wait_recording_speed': float,
        'after_recording_speed': float
    }

    def __init__(
        self,
        time: float,
        wait_recording_speed: Optional[float] = 'default',
        after_recording_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [
            CSetRecordingSpeed(self.wait_recording_speed),
            CWait(self.time),
            CSetRecordingSpeed(self.after_recording_speed),
        ]

class WaitUntil(AbstractStep):
    """Waits until a specified start time has been reached. This command will
    immediately reply with an estimate of when the waiting will be finished,
    and also give regular updates indicating that it is still alive.

    Args:
        second (float): Optional. Start time in seconds
        minute (float): Optional. Start time in minutes
        day (float): Optional. Specific day of start time
        month (float): Optional. Specific month of start time
        year (float): Optional. Specific year of start time
        hour (float): Specific hour of start time
        wait_recording_speed (int): Recording speed during wait (faster) ~2000
        after_recording_speed (int): Recording speed after wait (slower) ~14
    """
    DEFAULT_PROPS = {
        'second': 0,  # seconds
        'minute': 0,  # minutes
        'day': 0,  # days
        'month': 0,  # month
        'year': 0,  # year
        'wait_recording_speed': 2000,
        'after_recording_speed': 14,
    }

    PROP_TYPES = {
        'hour': int,
        'minute': int,
        'second': float,
        'day': int,
        'month': int,
        'year': int,
        'wait_recording_speed': float,
        'after_recording_speed': float
    }

    def __init__(
        self,
        hour: int,
        second: Optional[float] = 'default',
        minute: Optional[int] = 'default',
        day: Optional[int] = 'default',
        month: Optional[int] = 'default',
        year: Optional[int] = 'default',
        wait_recording_speed: Optional[float] = 'default',
        after_recording_speed: Optional[float] = 'default',
    ) -> None:
        super().__init__(locals())

    def get_steps(self):
        return [
            CSetRecordingSpeed(self.wait_recording_speed),
            CWaitUntil(
                hour=self.hour,
                minute=self.minute,
                second=self.second,
                day=self.day,
                month=self.month,
                year=self.year,
            ),
            CSetRecordingSpeed(self.after_recording_speed),
        ]

    def human_readable(self, language='en') -> str:
        props = self.formatted_properties()
        props.update({
            'target_datetime': self.steps[1].get_target_datetime()})
        return HUMAN_READABLE_STEPS['WaitUntil'][language].format(
            **props)
