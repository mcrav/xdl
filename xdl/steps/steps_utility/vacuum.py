from ..base_step import Step
from ..steps_base import CStartVacuum, CStopVacuum, CSetVacuumSetPoint

class StartVacuum(Step):
    """Start vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to start vacuum on.
    """
    def __init__(
        self, vessel: str, pressure: float = 'default', **kwargs) -> None:
        super().__init__(locals())

        self.steps = [
            CSetVacuumSetPoint(
                vessel=self.vessel, vacuum_pressure=self.pressure),
            CStartVacuum(vessel=self.vessel)
        ]

        self.human_readable = f'Start vacuum for {self.vessel}.'

class StopVacuum(Step):
    """Stop vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to stop vacuum on.
    """
    def __init__(self, vessel: str, **kwargs) -> None:
        super().__init__(locals())

        self.steps = [
            CStopVacuum(vessel=self.vessel)
        ]

        self.human_readable = f'Stop vacuum for {self.vessel}.'
