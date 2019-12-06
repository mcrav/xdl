from typing import Optional, List, Dict
from .clean_vessel import CleanVessel
from ...base_steps import Step, AbstractStep
from ..steps_utility import Transfer
from ....localisation import HUMAN_READABLE_STEPS

class FilterThrough(AbstractStep):
    """Filter contents of from_vessel through a cartridge,
    e.g. a Celite cartridge, and optionally elute with a solvent as well.

    Args:
        from_vessel (str): Vessel with contents to filter.
        to_vessel (str): Vessel to pass filtered contents to.
        through (str): Substrate to pass from_vessel contents through. Either
            this or through_cartridge must be given.
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
        through_cartridge (str): Internal property. Cartridge to pass
            from_vessel contents through.
        buffer_flask (str): Given internally. If from_vessel and to_vessel are
            the same buffer_flask will be used to push contents of from_vessel
            to temporarily, before moving to to_vessel.
    """
    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
        through: Optional[str] = None,
        eluting_solvent: Optional[str] = None,
        eluting_volume: Optional[float] = None,
        eluting_repeats: Optional[int] = 'default',
        move_speed: Optional[float] = 'default',
        aspiration_speed: Optional[float] = 'default',
        eluting_solvent_vessel: Optional[str] = None,
        flush_cartridge_vessel: Optional[str] = None,
        through_cartridge: Optional[str] = None,
        cartridge_dead_volume: Optional[float] = 'default',
        buffer_flask: Optional[str] = None,
        buffer_flask_max_volume: Optional[float] = None,
        to_vessel_max_volume: Optional[float] = None,
        **kwargs
    ):
        super().__init__(locals())

    def final_sanity_check(self, graph):
        if self.eluting_solvent:
            assert self.eluting_solvent_vessel
            # assert self.to_vessel_max_volume > self.eluting_volume
        if self.from_vessel == self.to_vessel:
            assert self.buffer_flask
        assert self.through_cartridge

    def on_prepare_for_execution(self, graph):
        if self.buffer_flask:
            self.buffer_flask_max_volume = graph.nodes[self.buffer_flask]['max_volume']

        if self.to_vessel:
            self.to_vessel_max_volume = graph.nodes[self.to_vessel]['max_volume']

    def get_steps(self) -> List[Step]:
        filter_through_to_vessel = self.to_vessel
        filter_through_to_vessel_max_volume = self.to_vessel_max_volume

        if self.to_vessel == self.from_vessel:
            filter_through_to_vessel = self.buffer_flask
            filter_through_to_vessel_max_volume = self.buffer_flask_max_volume

        if filter_through_to_vessel_max_volume == None:
            filter_through_to_vessel_max_volume = 100

        steps = [self.get_initial_filter_through_step(filter_through_to_vessel)]

        if self.eluting_solvent and self.eluting_volume:
            for _ in range(self.eluting_repeats):
                # Done like this so if 1 l is being added to 250 mL flask, it is
                # added in portions.
                volume_added = 0
                while volume_added < self.eluting_volume:
                    volume_to_add = min(
                        self.eluting_volume - volume_added,
                        filter_through_to_vessel_max_volume
                    )
                    # Transfer to from_vessel to rinse any residual product, then
                    # transfer through cartridge to target vess
                    steps.extend(self.get_eluting_steps(
                        filter_through_to_vessel, volume_to_add))
                    volume_added += volume_to_add

        if self.flush_cartridge_vessel:
            steps.append(
                self.get_flush_cartridge_step(filter_through_to_vessel))

        #  Clean from vessel and transfer back from buffer flask
        if self.to_vessel == self.from_vessel:
            if self.eluting_solvent:
                steps.extend([
                    CleanVessel(vessel=self.from_vessel,
                                solvent=self.eluting_solvent),
                ])
            steps.extend([
                Transfer(from_vessel=self.buffer_flask,
                         to_vessel=self.to_vessel,
                         volume='all',
                         move_speed=self.move_speed,
                         aspiration_speed=self.aspiration_speed),
            ])
        return steps

    def get_initial_filter_through_step(self, filter_through_to_vessel):
        return Transfer(
            from_vessel=self.from_vessel,
            to_vessel=filter_through_to_vessel,
            through=self.through_cartridge,
            volume='all',
            move_speed=self.move_speed,
            aspiration_speed=self.aspiration_speed)

    def get_eluting_steps(self, filter_through_to_vessel,  volume):
        return [
            Transfer(
                from_vessel=self.eluting_solvent_vessel,
                to_vessel=self.from_vessel,
                volume=volume),

            Transfer(
                from_vessel=self.from_vessel,
                to_vessel=filter_through_to_vessel,
                through=self.through_cartridge,
                volume=volume,
                move_speed=self.move_speed,
                aspiration_speed=self.aspiration_speed)
        ]

    def get_flush_cartridge_step(self, filter_through_to_vessel):
        return Transfer(
            from_vessel=self.flush_cartridge_vessel,
            to_vessel=filter_through_to_vessel,
            through=self.through_cartridge,
            volume=self.cartridge_dead_volume,
            move_speed=self.move_speed,
            aspiration_speed=self.aspiration_speed
        )

    @property
    def buffer_flasks_required(self):
        if self.to_vessel == self.from_vessel:
            return 1
        return 0

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
