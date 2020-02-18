# For type annotations
from .....step_utils.base_steps import AbstractBaseStep

class CValveMoveToPosition(AbstractBaseStep):
    """Move valve to given position.

    Args:
        valve_name (str): Node name of the valve to move.
        position (int): Position to move valve to.
    """

    PROP_TYPES = {
        'valve_name': str,
        'position': int
    }

    def __init__(self, valve_name: str, position: int) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.valve_name], [], []

    def execute(self, chempiler, logger=None, level=0) -> None:
        valve = chempiler[self.valve_name]
        valve.move_to_position(self.position)
        return True
