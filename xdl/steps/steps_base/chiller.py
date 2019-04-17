from typing import Optional
# For type annotations
if False:
    from chempiler import Chempiler
from logging import Logger

from ..base_step import Step

class CStartChiller(Step):
    """Starts the recirculation chiller.

    Args:
        vessel (str): Vessel to chill. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.start_chiller(self.vessel)
        return True

class CStopChiller(Step):
    """Stops the recirculation chiller.

    Args:
        vessel (str): Vessel to stop chilling. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.stop_chiller(self.vessel)
        return True

class CChillerSetTemp(Step):
    """Sets the temperature setpoint.

    Args:
        vessel (str): Vessel to set chiller temperature. Name of the node the chiller is attached to.
        temp (float): Temperature in °C.
    """
    def __init__(self, vessel: str, temp: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.set_temp(self.vessel, self.temp)
        return True

class CChillerWaitForTemp(Step):
    """Delays the script execution until the current temperature of the chiller is within
    0.5°C of the setpoint.

    Args:
        vessel (str): Vessel to wait for temperature. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.wait_for_temp(self.vessel)
        return True

class CRampChiller(Step):
    """Causes the chiller to ramp the temperature up or down. Only available for Petite
    Fleur.

    Args:
        vessel (str): Vessel to ramp chiller on. Name of the node the chiller is attached to.
        ramp_duration (int): Desired duration of the ramp in seconds.
        end_temperature (float): Final temperature of the ramp in °C.
    """
    def __init__(
        self,
        vessel: str,
        ramp_duration: int,
        end_temperature: float
    ) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.ramp_chiller(self.vessel, self.ramp_duration, self.end_temperature)
        return True

class CSetCoolingPower(Step):
    """Sets the cooling power (0-100%). Only available for CF41.

    Args:
        vessel (str): Vessel to set cooling power of chiller. Name of the node the chiller is attached to.
        cooling_power (float): Desired cooling power in percent.
    """
    def __init__(self, vessel: str, cooling_power: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.cooling_power(self.vessel, self.cooling_power)
        return True