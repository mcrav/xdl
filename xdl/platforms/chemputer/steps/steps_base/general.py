from typing import Optional
from logging import Logger
from .....step_utils.base_steps import AbstractBaseStep
from ..base_step import ChemputerStep
from ...localisation import HUMAN_READABLE_STEPS
from .....utils.errors import XDLError
from .....utils.misc import SanityCheck
from ...constants import CHEMPUTER_FLASK
import datetime

class Confirm(ChemputerStep, AbstractBaseStep):
    """Get the user to confirm something before execution continues.

    Args:
        msg (str): Message to get user to confirm experiment should continue.
    """

    PROP_TYPES = {
        'msg': str
    }

    def __init__(self, msg: str, **kwargs) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [], [], []

    def execute(
        self, chempiler, logger: Logger = None, level: int = 0
    ) -> bool:
        keep_going = input(self.msg)
        if not keep_going or keep_going.lower() in ['y', 'yes']:
            return True
        return False

class CSetRecordingSpeed(ChemputerStep, AbstractBaseStep):
    """Sets the timelapse speed of the camera module.

    Args:
        recording_speed (float): Factor by which the recording should be sped
            up, i.e. 2 would mean twice the normal speed. 1 means normal speed.
    """

    PROP_TYPES = {
        'recording_speed': float
    }

    def __init__(self, recording_speed: float) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.camera.change_recording_speed(self.recording_speed)
        return True

class CWait(ChemputerStep, AbstractBaseStep):
    """Delays execution of the script for a set amount of time. This command
    will immediately reply with an estimate of when the waiting will be
    finished, and also give regular updates indicating that it is still alive.

    Args:
        time (int): Time to wait in seconds.
    """

    PROP_TYPES = {
        'time': float
    }

    def __init__(self, time: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.wait(self.time)
        return True

    def locks(self, chempiler):
        return [], [], []

    def duration(self, chempiler):
        return self.time

class CWaitUntil(ChemputerStep, AbstractBaseStep):
    """Waits until a specified start time has been reached. This command will
    immediately reply with an estimate of when the waiting will be finished,
    and also give regular updates indicating that it is still alive.

    Args:
        second (float): Optional. Start time in seconds
        minute (float): Optional. Start time in minutes
        day (float): Optional. Specific day of start time
        month (float): Optional. Specific month of start time
        year (float): Optional. Specific year of start time
        hour (float): Specific hour of start time
    """

    DEFAULT_PROPS = {
        'second': 0,  # seconds
        'minute': 0,  # minutes
        'day': 0,  # days
        'month': 0,  # month
        'year': 0  # year
    }

    PROP_TYPES = {
        'hour': int,
        'minute': int,
        'second': float,
        'day': int,
        'month': int,
        'year': int
    }

    def __init__(
        self,
        hour: int,
        second: Optional[float] = 'default',
        minute: Optional[int] = 'default',
        day: Optional[int] = 'default',
        month: Optional[int] = 'default',
        year: Optional[int] = 'default',
    ) -> None:
        super().__init__(locals())

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=0 <= self.hour <= 23,
                error_msg=f'Hour property must be one of 0-23.\
 {self.hour} is invalid.'
            ),

            SanityCheck(
                condition=0 <= self.minute <= 60,
                error_msg=f'Minute property must be one of 0-59.\
 {self.minute} is invalid.'
            ),

            SanityCheck(
                condition=0 <= self.second <= 60,
                error_msg=f'Second property must be one of 0-59.\
 {self.second} is invalid.'
            ),

            SanityCheck(
                condition=0 <= self.day <= 31,
                error_msg=f'Day property must be one of 1-31.\
 {self.day} is invalid.'
            ),

            SanityCheck(
                condition=0 <= self.month <= 12,
                error_msg=f'Month property must be one of 1-12.\
 {self.month} is invalid.'
            ),

            SanityCheck(
                condition=0 <= self.year <= datetime.MAXYEAR,
                error_msg=f'Year property out of range.\
 {self.year} is invalid.'
            ),
        ]

    def get_target_datetime(self) -> dict:
        """Get the datetime to wait until. If a date has not been specified, use
        today or tomorrow if given time has already passed today.
        """
        today = datetime.datetime.today()

        # If date not given use today.
        if not self.day:
            year = today.year
            month = today.month
            day = today.day

            target_datetime = datetime.datetime(
                year=year,
                month=month,
                day=day,
                hour=self.hour,
                minute=self.minute,
                second=self.second
            )

            # Start time is in the past, go forward a day.
            if target_datetime < today:
                target_datetime += datetime.timedelta(days=1)

        else:
            year = self.year
            month = self.month
            day = self.day

            target_datetime = datetime.datetime(
                year=year,
                month=month,
                day=day,
                hour=self.hour,
                minute=self.minute,
                second=self.second
            )

        return target_datetime

    def get_wait_time(self) -> float:
        """Get time to wait for. Should be called at the time the step is being
        executed as it uses the current time.
        """
        target_datetime = self.get_target_datetime()
        wait_time = (
            target_datetime - datetime.datetime.today()).total_seconds()

        # Check not waiting until time in the past.
        if wait_time < 0:
            raise XDLError(
                f'Trying to wait until time in the past {target_datetime}.')

        return wait_time

    def execute(self, chempiler, logger=None, level=0):
        chempiler.wait(self.get_wait_time())
        return True

    def locks(self, chempiler):
        return [], [], []

    def duration(self, chempiler):
        return self.time_diff

    def human_readable(self, language='en') -> str:
        props = self.formatted_properties()
        props.update({
            'target_datetime': self.get_target_datetime()})
        return HUMAN_READABLE_STEPS['WaitUntil'][language].format(
            **props)

class CBreakpoint(ChemputerStep, AbstractBaseStep):
    """Introduces a breakpoint in the script. The execution is halted until the
    operator resumes it.
    """
    def __init__(self) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.breakpoint()
        return True

class CMove(ChemputerStep, AbstractBaseStep):
    """Moves a specified volume from one node in the graph to another. Moving
    from and to the same node is supported.

    Args:
        from_vessel (str): Vessel name to move from.
        to_vessel (str): Vessel name to move to.
        volume (float): Volume to move in mL. 'all' moves everything.
        move_speed (float): Speed at which liquid is moved in mL / min.
            (optional)
        aspiration_speed (float): Speed at which liquid aspirates from
            from_vessel. (optional)
        dispense_speed (float): Speed at which liquid dispenses from
            from_vessel. (optional)
    """

    DEFAULT_PROPS = {
        'move_speed': 40,  # mL / min
        'aspiration_speed': 10,  # mL / min
        'dispense_speed': 40,  # mL / min
        'use_backbone': True,
    }

    PROP_TYPES = {
        'from_vessel': str,
        'to_vessel': str,
        'volume': float,
        'move_speed': float,
        'aspiration_speed': float,
        'dispense_speed': float,
        'from_port': str,
        'to_port': str,
        'unique': bool,
        'through': str,
        'use_backbone': bool
    }

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
        through: Optional[str] = [],
        use_backbone: Optional[bool] = 'default',
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
            use_backbone=self.use_backbone,
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
            use_backbone=self.use_backbone,
        )

    def locks(self, chempiler):
        return chempiler.move_locks(
            src=self.from_vessel,
            dest=self.to_vessel,
            volume=self.volume,
            src_port=self.from_port,
            dest_port=self.to_port,
            through_nodes=self.through,
            use_backbone=self.use_backbone,
        )

    def reagents_consumed(self, graph):
        reagents_consumed = {}
        node = graph.nodes[self.from_vessel]
        if node['class'] == CHEMPUTER_FLASK and node['chemical']:
            reagents_consumed[node['chemical']] = self.volume
        return reagents_consumed

class CConnect(ChemputerStep, AbstractBaseStep):
    """Connect two nodes together.

    Args:
        from_vessel (str): Node name to connect from.
        to_vessel (str): Node name to connect to.
        from_port (str): Port name to connect from.
        to_port (str): Port name to connect to.
        unique (bool): Must use unique route.
    """

    PROP_TYPES = {
        'from_vessel': str,
        'to_vessel': str,
        'from_port': str,
        'to_port': str,
        'unique': bool
    }

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
