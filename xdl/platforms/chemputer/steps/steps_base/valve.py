# For type annotations
if False:
    from chempiler import Chempiler
from logging import Logger

from .....step_utils.base_steps import AbstractBaseStep

class CValveMoveToPosition(AbstractBaseStep):
    """Move valve to given position.

    Args:
        valve_name (str): Node name of the valve to move.
        position (int): Position to move valve to.
    """
    def __init__(self, valve_name: str, position: int) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.valve_name], [], []

    def execute(
        self,
        chempiler: 'Chempiler',
        logger: Logger = None,
        level: int = 0
    ) -> None:
        valve = chempiler[self.valve_name]
        valve.move_to_position(self.position)
        return True
