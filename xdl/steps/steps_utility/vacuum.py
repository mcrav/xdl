from typing import List, Dict, Any
from ..base_step import Step, AbstractStep
from ..steps_base import CStartVacuum, CStopVacuum, CSetVacuumSetPoint

class StartVacuum(AbstractStep):
    """Start vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to start vacuum on.
    """
    def __init__(
        self, vessel: str, pressure: float = 'default', **kwargs) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [
            CSetVacuumSetPoint(
                vessel=self.vessel, vacuum_pressure=self.pressure),
            CStartVacuum(vessel=self.vessel)
        ]

    def get_human_readable(self) -> Dict[str, str]:
        en = 'Start vacuum for {vessel}.'.format(**self.properties)
        return {
            'en': en,
        }

class StopVacuum(AbstractStep):
    """Stop vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to stop vacuum on.
    """
    def __init__(self, vessel: str, **kwargs) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [CStopVacuum(vessel=self.vessel)]

    def get_human_readable(self) -> Dict[str, str]:
        en = 'Stop vacuum for {vessel}.'.format(**self.properties)
        return {
            'en': en,
        }
