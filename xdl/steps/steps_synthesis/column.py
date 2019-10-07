from typing import Optional
from ..base_steps import AbstractStep
from ..steps_utility import Transfer
from .filter_through import FilterThrough

class RunColumn(AbstractStep):
    """Purify using column chromatography.

    Args:
        from_vessel (str): Vessel containing mixture to purify.
        to_vessel (str): Vessel to send purified mixture to.
        column (str): Column cartridge to use for purification.
        move_speed (float): Optional. Speed with which to move liquid through
            the column.
        waste_vessel (str): Given internally. Vessel to send waste to.
        buffer_flask (str): Given internally. Vessel to use to temporarily
            transfer reaction mixture to if from_vessel and to_vessel are the
            same.
    """
    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
        column: str = None,
        move_speed: Optional[float] = 'default',
        buffer_flask: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self):
        steps = [
            FilterThrough(
                from_vessel=self.from_vessel,
                to_vessel=self.to_vessel,
                through_cartridge=self.column,
                move_speed=self.move_speed,
                buffer_flask=self.buffer_flask,
            )
        ]

        return steps
