from typing import Optional

from ..base_step import Step
from ..steps_base import CSetRecordingSpeed, CWait

class Wait(Step):
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

        self.steps = [
            CSetRecordingSpeed(self.wait_recording_speed),
            CWait(self.time),
            CSetRecordingSpeed(self.after_recording_speed),
        ]

        self.human_readable = 'Wait for {0} s.'.format(self.time)