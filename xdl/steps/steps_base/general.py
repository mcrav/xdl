
from typing import Optional
# For type annotations
if False:
    from chempiler import Chempiler
from logging import Logger

from ..base_step import Step

class Confirm(Step):
    """Get the user to confirm something before execution continues.

    Args:
        msg (str): Message to get user to confirm experiment should continue.
    """

    def __init__(self, msg: str) -> None:
        super().__init__(locals())

    def execute(
        self, chempiler: 'Chempiler', logger: Logger = None, level: int = 0
    ) -> bool:
        keep_going = input(self.msg)
        if not keep_going or keep_going.lower() in ['y', 'yes']:
            return True
        return False

class CSetRecordingSpeed(Step):
    """Sets the timelapse speed of the camera module.

    Args:
        recording_speed (float): Factor by which the recording should be sped up, i.e. 2 would mean twice the normal speed. 1 means normal speed.
    """
    def __init__(self, recording_speed: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.camera.change_recording_speed(self.recording_speed)
        return True

class CWait(Step):
    """Delays execution of the script for a set amount of time. This command will
    immediately reply with an estimate of when the waiting will be finished, and also
    give regular updates indicating that it is still alive.

    Args:
        time (int): Time to wait in seconds.
    """
    def __init__(self, time: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.wait(self.time)
        return True

class CBreakpoint(Step):
    """Introduces a breakpoint in the script. The execution is halted until the operator
    resumes it.
    """
    def __init__(self) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.breakpoint()
        return True
class CMove(Step):
    """Moves a specified volume from one node in the graph to another. Moving from and to
    the same node is supported.

    Args:
        from_vessel (str): Vessel name to move from.
        to_vessel (str): Vessel name to move to.
        volume (float): Volume to move in mL. 'all' moves everything.
        move_speed (float): Speed at which liquid is moved in mL / min. (optional)
        aspiration_speed (float): Speed at which liquid aspirates from from_vessel. (optional)
        dispense_speed (float): Speed at which liquid dispenses from from_vessel. (optional)
    """
    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
        volume: float,
        move_speed: Optional[float] = 'default',
        aspiration_speed: Optional[float] = 'default',
        dispense_speed: Optional[float] = 'default',
        from_port: Optional[str] = None,
        to_port: Optional[str] = None,
        unique: Optional[bool] = False,
        through: Optional[str] = None
    ) -> None:
        super().__init__(locals())


    def execute(self, chempiler, logger=None, level=0):
        chempiler.move(
            src_node=self.from_vessel,
            dst_node=self.to_vessel,
            volume=self.volume,
            speed=(self.aspiration_speed, self.move_speed, self.dispense_speed),
            src_port=self.from_port,
            dst_port=self.to_port,
            unique=self.unique,
            through_node=self.through,
        )
        return True

class CConnect(Step):
    """Connect two nodes together.
    
    Args:
        from_vessel (str): Node name to connect from.
        to_vessel (str): Node name to connect to.
        from_port (str): Port name to connect from.
        to_port (str): Port name to connect to.
        unique (bool): Must use unique route.
    """
    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
        from_port: Optional[str] = None,
        to_port: Optional[str] = None,
        unique: Optional[bool] = True
    ) -> None:
        super().__init__(locals())
        
    def execute(self, chempiler, logger=None, level=0):
        chempiler.connect(
            src_node=self.from_vessel,
            dst_node=self.to_vessel,
            src_port=self.from_port,
            dst_port=self.to_port,
            unique=self.unique,
        )
        return True