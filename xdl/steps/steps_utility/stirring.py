from typing import Optional

from ..base_step import Step
from ..steps_base import (
    CStir,
    CSetStirRate,
    CStopStir)
from .general import Wait

class StartStir(Step):
    """Start stirring given vessel.

    Args:
        vessel (str): Vessel name to stir.
        stir_rpm (int, optional): Speed in RPM to stir at.
    """
    def __init__(
        self,
        vessel: str,
        stir_rpm: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            CStir(vessel=self.vessel),
            CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm),
        ]

        self.human_readable = 'Set stir rate to {stir_rpm} RPM and start stirring {vessel}.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'stir': True,
            }
        }

class StopStir(Step):
    """Stop stirring given vessel.
    
    Args:
        vessel (str): Vessel name to stop stirring.
    """
    def __init__(self, vessel: str, **kwargs) -> None:
        super().__init__(locals())

        self.steps = [CStopStir(vessel=self.vessel)]

        self.human_readable = 'Stop stirring {0}.'.format(self.vessel)

        self.requirements = {
            'vessel': {
                'stir': True,
            }
        }

class Stir(Step):
    """Stir given vessel for given time at room temperature.

    Args:
        vessel (str): Vessel to stir.
        time (float): Time to stir for.
    """
    def __init__(
        self,
        vessel: str,
        time: float,
        stir_rpm: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            StartStir(vessel=self.vessel, stir_rpm=self.stir_rpm),
            Wait(time=self.time),
            StopStir(vessel=self.vessel),
        ]

        self.human_readable = 'Stir {vessel} for {time} s.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'stir': True,
            }
        }