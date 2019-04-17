from typing import Optional
# For type annotations
if False:
    from chempiler import Chempiler
from logging import Logger

from ..base_step import Step

class CStir(Step):
    """Starts the stirring operation of a hotplate or overhead stirrer.

    Args:
        vessel (str): Vessel name to stir.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.stir(self.vessel)
        return True

class CStirrerHeat(Step):
    """Starts the heating operation of a hotplate stirrer.

    Args:
        vessel (str): Vessel name to heat.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.heat(self.vessel)
        return True

class CStopStir(Step):
    """Stops the stirring operation of a hotplate or overhead stirrer.

    Args:
        vessel (str): Vessel name to stop stirring.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.stop_stir(self.vessel)
        return True

class CStopHeat(Step):
    """Stop heating hotplace stirrer.

    Args:
        vessel (str): Vessel name to stop heating.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.stop_heat(self.vessel)
        return True

class CStirrerSetTemp(Step):
    """Sets the temperature setpoint of a hotplate stirrer. This command is NOT available
    for overhead stirrers!

    Args:
        vessel (str): Vessel name to set temperature of hotplate stirrer.
        temp (float): Temperature in °C
    """
    def __init__(self, vessel: str, temp: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.set_temp(self.vessel, self.temp)
        return True

class CSetStirRate(Step):
    """Sets the stirring speed setpoint of a hotplate or overhead stirrer.

    Args:
        vessel (str): Vessel name to set stir speed.
        stir_rpm (float): Stir speed in RPM.
    """
    def __init__(self, vessel: str, stir_rpm: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.set_stir_rate(self.vessel, self.stir_rpm)
        return True

class CStirrerWaitForTemp(Step):
    """Delays the script execution until the current temperature of the hotplate is within
    0.5 °C of the setpoint. This command is NOT available for overhead stirrers!

    Args:
        vessel (str): Vessel name to wait for temperature.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.wait_for_temp(self.vessel)
        return True
