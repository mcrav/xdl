from .....step_utils.base_steps import AbstractBaseStep
from ..base_step import ChemputerStep
from ...constants import DEFAULT_VACUUM_VENT_WAIT_TIME


class CGetVacuumSetPoint(ChemputerStep, AbstractBaseStep):
    """Reads the current vacuum setpoint.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """

    PROP_TYPES = {
        'vessel': str
    }

    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_vacuum_set_point(self.vessel)
        return True

class CSetVacuumSetPoint(ChemputerStep, AbstractBaseStep):
    """Sets a new vacuum setpoint.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        vacuum_pressure (float): Vacuum pressure setpoint in mbar.
    """

    PROP_TYPES = {
        'vessel': str,
        'vacuum_pressure': float
    }

    def __init__(self, vessel: str, vacuum_pressure: float) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_vacuum_set_point(
            self.vessel, self.vacuum_pressure)
        return True

class CStartVacuum(ChemputerStep, AbstractBaseStep):
    """Starts the vacuum pump.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """

    PROP_TYPES = {
        'vessel': str
    }

    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.start_vacuum(self.vessel)
        return True

class CStopVacuum(ChemputerStep, AbstractBaseStep):
    """Stops the vacuum pump.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """

    PROP_TYPES = {
        'vessel': str
    }

    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.stop_vacuum(self.vessel)
        return True

class CVentVacuum(ChemputerStep, AbstractBaseStep):
    """Vents the vacuum pump to ambient pressure.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """

    PROP_TYPES = {
        'vessel': str
    }

    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def duration(self, graph):
        return DEFAULT_VACUUM_VENT_WAIT_TIME

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.vent_vacuum(self.vessel)
        return True

class CSetSpeedSetPoint(ChemputerStep, AbstractBaseStep):
    """Sets the speed of the vacuum pump (0-100%).

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        vacuum_pump_speed (float): Vacuum pump speed in percent.
    """

    PROP_TYPES = {
        'vessel': str,
        'vacuum_pump_speed': float
    }

    def __init__(self, vessel: str, vacuum_pump_speed: float) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_speed_set_point(self.vessel, self.set_point)
        return True

class CSetEndVacuumSetPoint(ChemputerStep, AbstractBaseStep):
    """
    Sets the switch off vacuum set point.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        vacuum_set_point (int): Set point value to set vacuum to.
    """

    PROP_TYPES = {
        'vessel': str,
        'vacuum_set_point': int
    }

    def __init__(self, vessel: str, vacuum_set_point: int) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_end_vacuum_set_point(
            self.vessel, self.vacuum_set_point)
        return True

class CGetEndVacuumSetPoint(ChemputerStep, AbstractBaseStep):
    """
    Gets the set point (target) for the switch off vacuum in mode Auto.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """

    PROP_TYPES = {
        'vessel': str
    }

    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_end_vacuum_set_point(self.vessel)
        return True

class CSetRuntimeSetPoint(ChemputerStep, AbstractBaseStep):
    """
    Sets the switch off vacuum set point.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        time (float): Desired runtime.
    """

    PROP_TYPES = {
        'vessel': str,
        'time': float
    }

    def __init__(self, vessel: str, time: float) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_runtime_set_point(self.vessel, self.time)
        return True

class CGetRuntimeSetPoint(ChemputerStep, AbstractBaseStep):
    """
    Gets the set point (target) for the run time in mode Auto.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """

    PROP_TYPES = {
        'vessel': str
    }

    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_runtime_set_point(self.vessel)
        return True
