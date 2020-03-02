from .....step_utils.base_steps import AbstractBaseStep
from ..base_step import ChemputerStep

class CStir(ChemputerStep, AbstractBaseStep):
    """Starts the stirring operation of a hotplate or overhead stirrer.

    Args:
        vessel (str): Vessel name to stir.
    """

    PROP_TYPES = {
        'vessel': str
    }

    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.stir(self.vessel)
        return True

class CStirrerHeat(ChemputerStep, AbstractBaseStep):
    """Starts the heating operation of a hotplate stirrer.

    Args:
        vessel (str): Vessel name to heat.
    """

    PROP_TYPES = {
        'vessel': str
    }

    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.heat(self.vessel)
        return True

class CStopStir(ChemputerStep, AbstractBaseStep):
    """Stops the stirring operation of a hotplate or overhead stirrer.

    Args:
        vessel (str): Vessel name to stop stirring.
    """

    PROP_TYPES = {
        'vessel': str
    }

    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.stop_stir(self.vessel)
        return True

class CStopHeat(ChemputerStep, AbstractBaseStep):
    """Stop heating hotplace stirrer.

    Args:
        vessel (str): Vessel name to stop heating.
    """

    PROP_TYPES = {
        'vessel': str
    }

    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.stop_heat(self.vessel)
        return True

class CStirrerSetTemp(ChemputerStep, AbstractBaseStep):
    """Sets the temperature setpoint of a hotplate stirrer. This command is NOT
    available for overhead stirrers!

    Args:
        vessel (str): Vessel name to set temperature of hotplate stirrer.
        temp (float): Temperature in °C
    """

    PROP_TYPES = {
        'vessel': str,
        'temp': float
    }

    def __init__(self, vessel: str, temp: float) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.set_temp(self.vessel, self.temp)
        return True

class CSetStirRate(ChemputerStep, AbstractBaseStep):
    """Sets the stirring speed setpoint of a hotplate or overhead stirrer.

    Args:
        vessel (str): Vessel name to set stir speed.
        stir_speed (float): Stir speed in RPM.
    """

    PROP_TYPES = {
        'vessel': str,
        'stir_speed': float
    }

    def __init__(self, vessel: str, stir_speed: float) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.vessel], [], []

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.set_stir_rate(self.vessel, self.stir_speed)
        return True

class CStirrerWaitForTemp(ChemputerStep, AbstractBaseStep):
    """Delays the script execution until the current temperature of the
    hotplate is within 0.5 °C of the setpoint. This command is NOT available
    for overhead stirrers!

    Args:
        vessel (str): Vessel name to wait for temperature.
    """

    PROP_TYPES = {
        'vessel': str
    }

    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [], [self.vessel], []

    def duration(self, chempiler):
        return 2  # arbitrary value for the moment

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.wait_for_temp(self.vessel)
        return True
