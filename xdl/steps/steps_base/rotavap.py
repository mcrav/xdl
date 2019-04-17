from typing import Optional
# For type annotations
if False:
    from chempiler import Chempiler
from logging import Logger

from ..base_step import Step

class CRotavapStartHeater(Step):
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

class CRotavapStopHeater(Step):
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

class CRotavapStartRotation(Step):
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

class CRotavapStopRotation(Step):
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

class CRotavapLiftUp(Step):
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

class CRotavapLiftDown(Step):
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

class CRotavapReset(Step):
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

class CRotavapSetTemp(Step):
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

class CRotavapSetRotationSpeed(Step):
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

class CRotavapSetInterval(Step):
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
        