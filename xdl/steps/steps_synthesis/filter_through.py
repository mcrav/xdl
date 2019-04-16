from typing import Optional
from ..base_step import Step
from ..steps_utility import Transfer

class FilterThrough(Step):
    """Filter contents of from_vessel through a cartridge,
    e.g. a Celite cartridge, and optionally elute with a solvent as well.
    
    Args:
        from_vessel (str): Vessel with contents to filter.
        to_vessel (str): Vessel to pass filtered contents to.
        through_cartridge (str): Cartridge to pass from_vessel contents through.
        eluting_solvent (Optional[str]): Optional. Solvent to elute with after
            filtering.
        eluting_volume (Optional[float]): Optional. Volume of solvent to elute
            with after filtering.
        eluting_repeats (Optional[float]): Optional. Number of times to elute
            with eluting_solvent and eluting_volume. Defaults to 1.
        move_speed (Optional[float]): Optional. Move speed in mL / min.
        aspiration_speed (Optional[float]): Optional. Aspiration speed in
            mL / min.
    """
    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
        through_cartridge: str,
        eluting_solvent: Optional[str] = None,
        eluting_volume: Optional[float] = None,
        eluting_repeats: Optional[float] = 'default',
        move_speed: Optional[float] = 'default',
        aspiration_speed: Optional[float] = 'default',
    ):
        super().__init__(locals())

        self.steps = [
            Transfer(
                from_vessel=self.from_vessel,
                to_vessel=self.to_vessel,
                through=self.through_cartridge,
                volume='all',
                move_speed=self.move_speed,
                aspiration_speed=self.aspiration_speed)
        ]
        if self.eluting_solvent:
            self.steps.append(Transfer(
                from_vessel=self.eluting_solvent_vessel,
                to_vessel=self.to_vessel,
                through=self.through_cartridge,
                volume=self.eluting_volume,
                move_speed=self.move_speed,
                aspiration_speed=self.aspiration_speed,
                repeat=self.eluting_repeats))

        self.human_readable = 'Contents of {from_vessel} was filtered through {through_cartridge} into {to_vessel}'.format(
            **self.properties)
        if self.eluting_solvent:
            self.human_readable += ', eluting with {eluting_repeats} x {eluting_volume} mL of {eluting_solvent}.'.format(
                **self.properties)
        else:
            self.human_readable += '.'
