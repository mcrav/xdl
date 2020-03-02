from .....step_utils.base_steps import AbstractBaseStep
from ..base_step import ChemputerStep

class CSwitchVacuum(ChemputerStep, AbstractBaseStep):
    """Using PneumaticController switch given port to vacuum supply.

    Args:
        pneumatic_controller (str): Name of PneumaticController node.
        port (int): Port of PneumaticController to supply vacuum from.
    """

    PROP_TYPES = {
        'pneumatic_controller': str,
        'port': int
    }

    def __init__(self, pneumatic_controller: str, port: int):
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.pneumatic_controller], [], []

    def execute(self, chempiler, logger=None, level=0):
        pneumatic_controller = chempiler[self.pneumatic_controller]
        pneumatic_controller.switch_vacuum(self.port)
        return True

class CSwitchArgon(ChemputerStep, AbstractBaseStep):
    """Using PneumaticController switch given port to argon supply.

    Args:
        pneumatic_controller (str): Name of PneumaticController node.
        port (int): Port of PneumaticController to supply argon from.
        pressure (str): 'low' or 'high'. Defaults to 'low'.
    """

    PROP_TYPES = {
        'pneumatic_controller': str,
        'port': int,
        'pressure': str
    }

    def __init__(
        self,
        pneumatic_controller: str,
        port: int,
        pressure: str = 'low'
    ) -> None:
        super().__init__(locals())

    def locks(self, chempiler):
        return [self.pneumatic_controller], [], []

    def execute(self, chempiler, logger=None, level=0):
        pneumatic_controller = chempiler[self.pneumatic_controller]
        pneumatic_controller.switch_argon(self.port, pressure=self.pressure)
        return True
