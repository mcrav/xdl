# For type annotations
if False:
    from chempiler import Chempiler
from logging import Logger

from ..base_step import AbstractBaseStep

class CValveMoveToPosition(AbstractBaseStep):
    """Move valve to given position.
    
    Args:
        valve_name (str): Node name of the valve to move.
        position (int): Position to move valve to.
    """
    def __init__(self, valve_name: str, position: int) -> None:
        super().__init__(locals())

    def execute(
        self,
        chempiler: 'Chempiler',
        logger: Logger = None,
        level: int = 0
    ) -> None:
        valve = chempiler[self.valve_name]
        valve.move_to_position(self.position)
        return True
    