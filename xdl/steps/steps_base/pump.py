
from typing import Optional
# For type annotations
if False:
    from chempiler import Chempiler
from logging import Logger

from ..base_step import AbstractBaseStep

class CSeparatePhases(AbstractBaseStep):
    """
    Args:
        lower_phase_vessel (str): Name of vessel to transfer lower phase to.
        lower_phase_port (str): Name of port to transfer lower phase to
        upper_phase_vessel (str): Name of vessel to transfer upper phase to.
        separator_top (str): Name of separator top node in graph.
        separator_bottom (str): Name of separator bottom node in graph.
        dead_volume_target (str): Name of waste vessel to transfer dead
                                    volume between phases to.
    """
    def __init__(
        self,
        lower_phase_vessel: str,
        upper_phase_vessel: str,
        separation_vessel: str,
        dead_volume_target: str,
        lower_phase_port: Optional[str] = None,
        upper_phase_port: Optional[str] = None
    ) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.pump.separate_phases(
            separator_flask=self.separation_vessel,
            lower_phase_target=self.lower_phase_vessel,
            lower_phase_port=self.lower_phase_port,
            upper_phase_target=self.upper_phase_vessel,
            upper_phase_port=self.upper_phase_port,
            dead_volume_target=self.dead_volume_target,
        )
        return True