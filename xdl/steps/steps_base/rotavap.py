from typing import Optional
# For type annotations
if False:
    from chempiler import Chempiler
from logging import Logger

from ..base_step import AbstractBaseStep

class CRotavapStartHeater(AbstractBaseStep):
    """Starts the heating bath of a rotary evaporator.

    Args:
        rotavap_name (str): Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        rotavap = chempiler[self.rotavap_name]
        rotavap.start_heater()
        return True

class CRotavapStopHeater(AbstractBaseStep):
    """Stops the heating bath of a rotary evaporator.

    Args:
        rotavap_name (str): Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        rotavap = chempiler[self.rotavap_name]
        rotavap.stop_heater()
        return True

class CRotavapStartRotation(AbstractBaseStep):
    """Starts the rotation of a rotary evaporator.

    Args:
        rotavap_name (str): Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        rotavap = chempiler[self.rotavap_name]
        rotavap.start_rotation()
        return True

class CRotavapStopRotation(AbstractBaseStep):
    """Stops the rotation of a rotary evaporator.

    Args:
        rotavap_name (str): Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        rotavap = chempiler[self.rotavap_name]
        rotavap.stop_rotation()
        return True

class CRotavapLiftUp(AbstractBaseStep):
    """Lifts the rotary evaporator arm up.

    Args:
        rotavap_name (str): Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        rotavap = chempiler[self.rotavap_name]
        rotavap.lift_up()
        return True

class CRotavapLiftDown(AbstractBaseStep):
    """Lifts the rotary evaporator down.

    Args:
        rotavap_name (str): Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        rotavap = chempiler[self.rotavap_name]
        rotavap.lift_down()
        return True

class CRotavapReset(AbstractBaseStep):
    """
    Resets the rotary evaporator.

    Args:
        rotavap_name (str): Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        rotavap = chempiler[self.rotavap_name]
        rotavap.reset_rotavap()
        return True

class CRotavapSetTemp(AbstractBaseStep):
    """Sets the temperature setpoint for the heating bath.

    Args:
        rotavap_name (str): Name of the node representing the rotary evaporator.
        temp (float): Temperature in °C.
    """
    def __init__(self, rotavap_name: str, temp: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        rotavap = chempiler[self.rotavap_name]
        rotavap.temperature_sp = self.temp
        return True

class CRotavapSetRotationSpeed(AbstractBaseStep):
    """Sets the rotation speed setpoint for the rotary evaporator.

    Args:
        rotavap_name (str): Name of the node representing the rotary evaporator.
        rotation_speed (float): Rotation speed setpoint in RPM.
    """
    def __init__(self, rotavap_name: str, rotation_speed: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        rotavap = chempiler[self.rotavap_name]
        rotavap.rotation_speed_sp = self.rotation_speed
        return True

class CRotavapSetInterval(AbstractBaseStep):
    """Sets the interval time for the rotary evaporator, causing it to periodically switch
    direction. Setting this to 0 deactivates interval operation.

    Args:
        rotavap_name (str): Name of the node representing the rotary evaporator.
        interval (int): Interval time in seconds.
    """
    def __init__(self, rotavap_name: str, interval: int) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        rotavap = chempiler[self.rotavap_name]
        rotavap.set_interval(self.interval)
        return True

class CRotavapAutoEvaporation(AbstractBaseStep):
    """Perform the rotavap built-in auto-evaporation routine.

    Args:
        rotavap_name (str): Node name of the rotavap.
        sensitivity (int): Sensitivity mode to use. 0, 1 or 2 (Low, medium, high
            respectively).
        vacuum_limit (float): Minimum pressure for the process.
        time_limit (float): Maximum time to use for the process.
        vent_after (bool): If True, vacuum will be vented after the process is
            complete.
    """
    def __init__(
        self,
        rotavap_name: str,
        sensitivity: int,
        vacuum_limit: float,
        time_limit: float,
        vent_after: Optional[bool] = True
    ):
        super().__init__(locals())
    
    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.auto_evaporation(
            node_name=self.rotavap_name,
            auto_mode=self.sensitivity,
            vacuum_limit=self.vacuum_limit,
            duration=self.time_limit / 60,
            vent_after=self.vent_after)
        return True
