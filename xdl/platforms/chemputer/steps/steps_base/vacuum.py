from .....step_utils.base_steps import AbstractBaseStep
from .....constants import DEFAULT_VACUUM_VENT_WAIT_TIME

class CGetVacuumSetPoint(AbstractBaseStep):
    """Reads the current vacuum setpoint.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_vacuum_set_point(self.vessel)
        return True

class CSetVacuumSetPoint(AbstractBaseStep):
    """Sets a new vacuum setpoint.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        vacuum_pressure (float): Vacuum pressure setpoint in mbar.
    """
    def __init__(self, vessel: str, vacuum_pressure: float) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_vacuum_set_point(
            self.vessel, self.vacuum_pressure)
        return True

class CStartVacuum(AbstractBaseStep):
    """Starts the vacuum pump.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.start_vacuum(self.vessel)
        return True

class CStopVacuum(AbstractBaseStep):
    """Stops the vacuum pump.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.stop_vacuum(self.vessel)
        return True

class CVentVacuum(AbstractBaseStep):
    """Vents the vacuum pump to ambient pressure.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def duration(self, chempiler):
        return DEFAULT_VACUUM_VENT_WAIT_TIME

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.vent_vacuum(self.vessel)
        return True

class CSetSpeedSetPoint(AbstractBaseStep):
    """Sets the speed of the vacuum pump (0-100%).

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        vacuum_pump_speed (float): Vacuum pump speed in percent.
    """
    def __init__(self, vessel: str, vacuum_pump_speed: float) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_speed_set_point(self.vessel, self.set_point)
        return True

class CSetEndVacuumSetPoint(AbstractBaseStep):
    """
    Sets the switch off vacuum set point.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        vacuum_set_point (int): Set point value to set vacuum to.
    """
    def __init__(self, vessel: str, vacuum_set_point: int) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_end_vacuum_set_point(
            self.vessel, self.vacuum_set_point)
        return True

class CGetEndVacuumSetPoint(AbstractBaseStep):
    """
    Gets the set point (target) for the switch off vacuum in mode Auto.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_end_vacuum_set_point(self.vessel)
        return True

class CSetRuntimeSetPoint(AbstractBaseStep):
    """
    Sets the switch off vacuum set point.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        time (float): Desired runtime.
    """
    def __init__(self, vessel: str, time: float) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_runtime_set_point(self.vessel, self.time)
        return True

class CGetRuntimeSetPoint(AbstractBaseStep):
    """
    Gets the set point (target) for the run time in mode Auto.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_runtime_set_point(self.vessel)
        return True
