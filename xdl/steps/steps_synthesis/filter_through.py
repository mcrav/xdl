from typing import Optional, List, Dict
from .clean_vessel import CleanVessel
from ..base_step import Step, AbstractStep
from ..steps_utility import Transfer
from ...localisation import HUMAN_READABLE_STEPS

class FilterThrough(AbstractStep):
    """Filter contents of from_vessel through a cartridge,
    e.g. a Celite cartridge, and optionally elute with a solvent as well.
    
    Args:
        from_vessel (str): Vessel with contents to filter.
        to_vessel (str): Vessel to pass filtered contents to.
        through_cartridge (str): Cartridge to pass from_vessel contents through.
        eluting_solvent (str): Solvent to elute with after filtering.
        eluting_volume (float): Volume of solvent to elute with after filtering.
        eluting_repeats (float): Number of times to elute with eluting_solvent
            and eluting_volume. Defaults to 1.
        move_speed (float): Move speed in mL / min.
        aspiration_speed (float): Aspiration speed in mL / min.
        eluting_solvent_vessel (str): Given internally. Flask containing eluting
            solvent.
        flush_cartridge_vessel (str): Given internally. Flask to flush dead
            volume of cartridge with after main transfers are done. Order of
            preference is nitrogen > air > nothing.
        cartridge_dead_volume (float): Volume of gas to push through if flushing
            cartridge dead volume.
        buffer_flask (str): Given internally. If from_vessel and to_vessel are
            the same buffer_flask will be used to push contents of from_vessel
            to temporarily, before moving to to_vessel.
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
        eluting_solvent_vessel: Optional[str] = None,
        flush_cartridge_vessel: Optional[str] = None,
        cartridge_dead_volume: Optional[float] = 'default',
        buffer_flask: Optional[str] = None,
        **kwargs
    ):
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        filter_through_to_vessel = self.to_vessel
        if self.to_vessel == self.from_vessel:
            filter_through_to_vessel = self.buffer_flask
        steps = [Transfer(from_vessel=self.from_vessel,
                          to_vessel=filter_through_to_vessel,
                          through=self.through_cartridge,
                          volume='all',
                          move_speed=self.move_speed,
                          aspiration_speed=self.aspiration_speed)]

        if self.eluting_solvent:
            steps.append(Transfer(from_vessel=self.eluting_solvent_vessel,
                                  to_vessel=filter_through_to_vessel,
                                  through=self.through_cartridge,
                                  volume=self.eluting_volume,
                                  move_speed=self.move_speed,
                                  aspiration_speed=self.aspiration_speed,
                                  repeat=self.eluting_repeats))
        
        if self.flush_cartridge_vessel:
            steps.append(Transfer(from_vessel=self.flush_cartridge_vessel,
                                  to_vessel=filter_through_to_vessel,
                                  through=self.through_cartridge,
                                  volume=self.cartridge_dead_volume,
                                  move_speed=self.move_speed,
                                  aspiration_speed=self.aspiration_speed))

        if self.to_vessel == self.from_vessel:
            steps.extend([
                CleanVessel(vessel=self.from_vessel,
                            solvent=self.eluting_solvent),
                Transfer(from_vessel=self.buffer_flask,
                         to_vessel=self.to_vessel,
                         volume='all',
                         move_speed=self.move_speed,
                         aspiration_speed=self.aspiration_speed),
            ])
        return steps

    def human_readable(self, language='en'):
        try:
            if self.eluting_solvent:
                return HUMAN_READABLE_STEPS['FilterThrough (eluting)'][language].format(
                    **self.formatted_properties())
            else:
                return HUMAN_READABLE_STEPS['FilterThrough (not eluting)'][language].format(
                    **self.formatted_properties())
        except KeyError:
            return self.name