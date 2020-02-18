from typing import Optional
from .....step_utils import AbstractStep
from .....step_utils.special_steps import Loop
from .general import Wait
from .cleaning import CleanBackbone
from .....utils.misc import SanityCheck

class Standby(AbstractStep):
    """Move solvent around once every specified time interval to prevent
    sticking of valves and pumps. Continues indefinitely.

    Args:
        solvent (str): Solvent with which to clean
        time_interval (str): Activate periodically after this many hours.
    """

    PROP_TYPES = {
        'solvent': str,
        'time_interval': float
    }

    def __init__(
        self,
        solvent: str,
        time_interval: Optional[float] = '24 h',
    ):
        super().__init__(locals())

    def get_steps(self):
        """Wait for end of time interval and begin cleaning"""
        loop_steps = [
            Wait(time=self.time_interval),
            CleanBackbone(solvent=self.solvent)
        ]
        return [Loop(loop_steps)]

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=self.time_interval >= 3600.0,
                error_msg='Please specify standby time interval of at least 1\
 hour.',
            )
        ]
