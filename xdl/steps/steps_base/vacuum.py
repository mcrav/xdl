from typing import Optional
# For type annotations
if False:
    from chempiler import Chempiler
from logging import Logger

from ..base_step import Step

class CGetVacuumSetPoint(Step):
    """Reads the current vacuum setpoint.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_vacuum_set_point(self.vessel)
        return True

class CSetVacuumSetPoint(Step):
    """Sets a new vacuum setpoint.

    Args:
        vessel:$ (str): Name of the node the vacuum pump is attached to.
        vacuum_pressure (float): Vacuum pressure setpoint in mbar.
    """
    def __init__(self, vessel: str, vacuum_pressure: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_vacuum_set_point(
            self.vessel, self.vacuum_pressure)
        return True

class CStartVacuum(Step):
    """Starts the vacuum pump.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.start_vacuum(self.vessel)
        return True

class CStopVacuum(Step):
    """Stops the vacuum pump.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.stop_vacuum(self.vessel)
        return True

class CVentVacuum(Step):
    """Vents the vacuum pump to ambient pressure.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.vent_vacuum(self.vessel)
        return True

class CSetSpeedSetPoint(Step):
    """Sets the speed of the vacuum pump (0-100%).

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        vacuum_pump_speed (float): Vacuum pump speed in percent.
    """
    def __init__(self, vessel: str, vacuum_pump_speed: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_speed_set_point(self.vessel, self.set_point)
        return True

class CSetEndVacuumSetPoint(Step):
    """
    Sets the switch off vacuum set point.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        vacuum_set_point (int): Set point value to set vacuum to.
    """
    def __init__(self, vessel: str, vacuum_set_point: int) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_end_vacuum_set_point(
            self.vessel, self.vacuum_set_point)
        return True

class CGetEndVacuumSetPoint(Step):
    """
    Gets the set point (target) for the switch off vacuum in mode Auto.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_end_vacuum_set_point(self.vessel)
        return True

class CSetRuntimeSetPoint(Step):
    """
    Sets the switch off vacuum set point.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        time (float): Desired runtime.
    """
    def __init__(self, vessel: str, time: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_runtime_set_point(self.vessel, self.time)
        return True

class CGetRuntimeSetPoint(Step):
    """
    Gets the set point (target) for the run time in mode Auto.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_runtime_set_point(self.vessel)
        return True
