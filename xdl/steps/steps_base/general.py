from typing import Optional, List
# For type annotations
if False:
    from chempiler import Chempiler
from logging import Logger

from ..base_steps import Step, AbstractBaseStep

class Confirm(AbstractBaseStep):
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

class CSetRecordingSpeed(AbstractBaseStep):
    """Sets the timelapse speed of the camera module.

    Args:
        recording_speed (float): Factor by which the recording should be sped up, i.e. 2 would mean twice the normal speed. 1 means normal speed.
    """
    def __init__(self, recording_speed: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.camera.change_recording_speed(self.recording_speed)
        return True

class CWait(AbstractBaseStep):
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

    def duration(self, chempiler):
        return self.time

class CBreakpoint(AbstractBaseStep):
    """Introduces a breakpoint in the script. The execution is halted until the operator
    resumes it.
    """
    def __init__(self) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.breakpoint()
        return True

class CMove(AbstractBaseStep):
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
        through: Optional[List[str]] = []
    ) -> None:
        super().__init__(locals())


    def execute(self, chempiler, logger=None, level=0):
        chempiler.move(
            src=self.from_vessel,
            dest=self.to_vessel,
            volume=self.volume,
            initial_pump_speed=self.aspiration_speed,
            mid_pump_speed=self.move_speed,
            end_pump_speed=self.dispense_speed,
            src_port=self.from_port,
            dest_port=self.to_port,
            through_nodes=self.through,
        )
        return True

    def duration(self, chempiler):
        return chempiler.move_duration(
            src=self.from_vessel,
            dest=self.to_vessel,
            volume=self.volume,
            initial_pump_speed=self.aspiration_speed,
            mid_pump_speed=self.move_speed,
            end_pump_speed=self.dispense_speed,
            src_port=self.from_port,
            dest_port=self.to_port,
            through_nodes=self.through,
        )

    def locks(self, chempiler):
        return chempiler.move_locks(
            src=self.from_vessel,
            dest=self.to_vessel,
            volume=self.volume,
            src_port=self.from_port,
            dest_port=self.to_port,
            through_nodes=self.through,
        )

class CConnect(AbstractBaseStep):
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
            src=self.from_vessel,
            dest=self.to_vessel,
            src_port=self.from_port,
            dest_port=self.to_port,
        )
        return True

    def locks(self, chempiler):
        return chempiler.connect_locks(
            src=self.from_vessel,
            dest=self.to_vessel,
            src_port=self.from_port,
            dest_port=self.to_port,
        )
