from typing import Optional
from .....step_utils.base_steps import AbstractStep
from .filter_through import FilterThrough
from ...utils.execution import get_buffer_flask

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

    DEFAULT_PROPS = {
        'move_speed': 5,  # mL / min
        'eluting_repeats': 1,
    }

    PROP_TYPES = {
        'from_vessel': str,
        'to_vessel': str,
        'column': str,
        'move_speed': float,
        'buffer_flask': str,
        'eluting_solvent': str,
        'eluting_volume': float,
        'eluting_repeats': int,
    }

    INTERNAL_PROPS = [
        'buffer_flask',
    ]

    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
        column: str = None,
        eluting_solvent: str = None,
        eluting_volume: float = None,
        eluting_repeats: int = 'default',
        move_speed: Optional[float] = 'default',

        # Internal properties
        buffer_flask: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.buffer_flask:
            self.buffer_flask = get_buffer_flask(
                graph, self.from_vessel, return_single=True)

    @property
    def buffer_flasks_required(self):
        if self.to_vessel == self.from_vessel:
            return 1
        return 0

    def get_steps(self):
        steps = [
            FilterThrough(
                from_vessel=self.from_vessel,
                to_vessel=self.to_vessel,
                through_cartridge=self.column,
                move_speed=self.move_speed,
                buffer_flask=self.buffer_flask,
                eluting_repeats=self.eluting_repeats,
                eluting_solvent=self.eluting_solvent,
                eluting_volume=self.eluting_volume
            )
        ]

        return steps
