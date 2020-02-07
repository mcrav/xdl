from typing import List
from .....step_utils.base_steps import Step, AbstractStep
from ..steps_base import CStartVacuum, CStopVacuum, CSetVacuumSetPoint

class StartVacuum(AbstractStep):
    """Start vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to start vacuum on.
    """

    DEFAULT_PROPS = {
        'pressure': '400 mbar',
    }

    def __init__(
        self, vessel: str, pressure: float = 'default', **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [
            CSetVacuumSetPoint(
                vessel=self.vessel, vacuum_pressure=self.pressure),
            CStartVacuum(vessel=self.vessel)
        ]

class StopVacuum(AbstractStep):
    """Stop vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to stop vacuum on.
    """
    def __init__(self, vessel: str, **kwargs) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [CStopVacuum(vessel=self.vessel)]
