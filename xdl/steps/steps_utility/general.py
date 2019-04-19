from typing import Optional, List

from ..base_step import AbstractStep, Step
from ..steps_base import CSetRecordingSpeed, CWait

class Wait(AbstractStep):
    """Wait for given time.

    Args:
        time (int): Time in seconds
        wait_recording_speed (int): Recording speed during wait (faster) ~2000
        after_recording_speed (int): Recording speed after wait (slower) ~14
    """
    def __init__(
        self,
        time: float,
        wait_recording_speed: Optional[float] = 'default',
        after_recording_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    @property
    def steps(self) -> List[Step]:
        return [
            CSetRecordingSpeed(self.wait_recording_speed),
            CWait(self.time),
            CSetRecordingSpeed(self.after_recording_speed),
        ]

    @property
    def human_readable(self) -> str:
       return 'Wait for {time} s.'.format(**self.properties) 