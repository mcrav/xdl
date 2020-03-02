from typing import Optional, List
import math
from .clean_vessel import CleanVessel
from .....step_utils.base_steps import Step, AbstractStep
from ..base_step import ChemputerStep
from ..steps_utility import Transfer
from .....step_utils.special_steps import Repeat
from ...localisation import HUMAN_READABLE_STEPS
from .....utils.misc import SanityCheck
from ...utils.execution import (
    get_reagent_vessel, get_flush_tube_vessel, get_cartridge, get_buffer_flask)

class FilterThrough(ChemputerStep, AbstractStep):
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

    DEFAULT_PROPS = {
        'move_speed': 5,  # mL / min
        'aspiration_speed': 5,  # mL / min
        'eluting_repeats': 1,
        'cartridge_dead_volume': '25 mL',
    }

    PROP_TYPES = {
        'from_vessel': str,
        'to_vessel': str,
        'through': str,
        'eluting_solvent': str,
        'eluting_volume': float,
        'eluting_repeats': int,
        'move_speed': float,
        'aspiration_speed': float,
        'eluting_solvent_vessel': str,
        'flush_cartridge_vessel': str,
        'through_cartridge': str,
        'cartridge_dead_volume': float,
        'buffer_flask': str,
        'from_vessel_max_volume': float
    }

    INTERNAL_PROPS = [
        'eluting_solvent_vessel',
        'flush_cartridge_vessel',
        'through_cartridge',
        'cartridge_dead_volume',
        'buffer_flask',
        'buffer_flask_max_volume',
        'to_vessel_max_volume',
    ]

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

        # Internal properties
        eluting_solvent_vessel: Optional[str] = None,
        flush_cartridge_vessel: Optional[str] = None,
        through_cartridge: Optional[str] = None,
        cartridge_dead_volume: Optional[float] = 'default',
        buffer_flask: Optional[str] = None,
        from_vessel_max_volume: Optional[float] = None,
        **kwargs
    ):
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):

        if not self.buffer_flask:
            self.buffer_flask = get_buffer_flask(
                graph, self.from_vessel, return_single=True)

        if self.eluting_solvent:
            if not self.eluting_solvent_vessel:
                self.eluting_solvent_vessel = get_reagent_vessel(
                    graph, self.eluting_solvent)

        if not self.flush_cartridge_vessel:
            self.flush_cartridge_vessel = get_flush_tube_vessel(
                graph, self.to_vessel)

        if not self.from_vessel_max_volume:
            self.from_vessel_max_volume = graph.nodes[
                self.from_vessel]['max_volume']

        if not self.through_cartridge:
            self.through_cartridge = get_cartridge(graph, self.through)

        if not self.cartridge_dead_volume:
            cartridge = graph.nodes[self.through_cartridge]
            if 'dead_volume' in cartridge:
                self.cartridge_dead_volume = cartridge['dead_volume']

    def sanity_checks(self, graph):
        to_vessel_max_volume = graph.nodes[self.to_vessel]['max_volume']

        checks = [

            SanityCheck(
                condition=(self.from_vessel != self.to_vessel
                           or self.buffer_flask),
                error_msg=f'Trying to filter through cartridge to and from the same\
 vessel, but cannot find buffer flask to use.'
            ),

            SanityCheck(
                condition=self.through_cartridge,
                error_msg=f'Trying to filter through "{self.through}" but cannot find\
 cartridge containing {self.through}.'
            ),

        ]

        if self.eluting_solvent:
            checks.extend([
                SanityCheck(
                    condition=self.eluting_solvent_vessel,
                    error_msg=f'"{self.eluting_solvent}" specified as eluting solvent but\
 no vessel found containing {self.eluting_solvent}.'
                ),

                SanityCheck(
                    condition=(
                        self.eluting_volume * self.eluting_repeats
                        <= to_vessel_max_volume
                    ),
                    error_msg=f'Eluting volume ({self.eluting_volume * self.eluting_repeats} mL) is\
 > to_vessel max volume ({to_vessel_max_volume} mL).'
                ),
            ])

            if self.from_vessel == self.to_vessel:
                buffer_flask_max_volume = graph.nodes[
                    self.buffer_flask]['max_volume']
                checks.append(
                    SanityCheck(
                        condition=(self.eluting_volume * self.eluting_repeats
                                   <= buffer_flask_max_volume),
                        error_msg=f'Eluting volume ({self.eluting_volume * self.eluting_repeats} mL) is\
 > buffer flask max volume ({buffer_flask_max_volume} mL).'
                    )
                )

        return checks

    def get_steps(self) -> List[Step]:
        # Not going from and to same vessel.
        if self.from_vessel != self.to_vessel:

            # No elution
            if not self.eluting_solvent:
                return self.get_no_elution_steps()

            # With elution
            else:

                # Internal props not added
                if self.from_vessel_max_volume is None:
                    return []

                # Eluting volume <= from_vessel max volume, one transfer
                elif self.eluting_volume <= self.from_vessel_max_volume:
                    return self.get_non_portionwise_elution_steps()

                # Eluting volume > from_vessel max volume, portionwise transfers
                else:
                    return self.get_portionwise_elution_steps()

        # Going from and to same vessel.
        else:

            # No elution
            if not self.eluting_solvent:
                return self.get_no_elution_steps_with_buffer()

            # With elution
            else:

                if self.from_vessel_max_volume is None:
                    return []

                # Eluting volume <= from_vessel max volume, one transfer
                elif self.eluting_volume <= self.from_vessel_max_volume:
                    return self.get_non_portionwise_elution_steps_with_buffer()

                # Eluting volume > from_vessel max volume, portionwise transfer
                else:
                    # If from_vessel max volume > eluting volume and from vessel
                    # and to vessel are the same then eluting will overflow
                    # the flask. Raise error in final sanity check.
                    return []

    def get_no_elution_steps(self) -> List[Step]:
        """Single transfer, no elution, no buffer flask."""
        return (
            self.get_filter_through_transfer_steps()
            + self.get_flush_cartridge_steps()
        )

    def get_non_portionwise_elution_steps(self):
        """Single transfer, single elution, no buffer flask."""
        return (
            self.get_filter_through_transfer_steps()
            + self.get_single_elution_steps()
            + self.get_flush_cartridge_steps()
        )

    def get_portionwise_elution_steps(self):
        """Single transfer, portionwise elution, no buffer flask."""
        return (
            self.get_filter_through_transfer_steps()
            + self.get_multi_elution_steps()
            + self.get_flush_cartridge_steps()
        )

    def get_no_elution_steps_with_buffer(self):
        """Single transfer, no elution, using buffer flask."""
        return (
            self.get_filter_through_transfer_to_buffer_steps()
            + self.get_flush_cartridge_to_buffer_steps()
            + self.get_transfer_back_from_buffer_steps()
        )

    def get_non_portionwise_elution_steps_with_buffer(self):
        """Single transfer, single elution, using buffer flask."""
        return (
            self.get_filter_through_transfer_to_buffer_steps()
            + self.get_flush_cartridge_to_buffer_steps()
            + self.get_single_elution_to_buffer_steps()
            + self.get_clean_from_and_to_vessel_steps()
            + self.get_transfer_back_from_buffer_steps()
        )

    ###########
    # General #
    ###########

    def get_filter_through_transfer_steps(self):
        return [
            Transfer(
                from_vessel=self.from_vessel,
                to_vessel=self.to_vessel,
                through=self.through,
                volume='all',
                move_speed=self.move_speed,
                aspiration_speed=self.aspiration_speed
            )
        ]

    def get_flush_cartridge_steps(self):
        if self.flush_cartridge_vessel:
            return [
                Transfer(
                    from_vessel=self.flush_cartridge_vessel,
                    to_vessel=self.to_vessel,
                    through=self.through,
                    volume=self.cartridge_dead_volume,
                    move_speed=self.move_speed,
                    aspiration_speed=self.aspiration_speed
                )
            ]
        return []

    ###########
    # Elution #
    ###########

    def get_single_elution_steps(self):
        eluting_steps = [
            Transfer(
                from_vessel=self.eluting_solvent_vessel,
                to_vessel=self.from_vessel,
                volume=self.eluting_volume),

            Transfer(
                from_vessel=self.from_vessel,
                to_vessel=self.to_vessel,
                through=self.through,
                volume=self.eluting_volume,
                move_speed=self.move_speed,
                aspiration_speed=self.aspiration_speed)
        ]

        if self.eluting_repeats > 1:
            return [
                Repeat(repeats=self.eluting_repeats, children=eluting_steps)
            ]

        return eluting_steps

    def get_multi_elution_steps(self):
        n_portions = math.floor(
            self.eluting_volume / self.from_vessel_max_volume)
        final_portion_vol = self.eluting_volume % self.from_vessel_max_volume
        portion_vol = (self.eluting_volume - final_portion_vol) / n_portions
        eluting_steps = [
            Repeat(
                repeats=n_portions,
                children=self.get_single_portion_elution_steps(portion_vol)
            ),
        ] + self.get_single_portion_elution_steps(final_portion_vol)
        if self.eluting_repeats > 1:
            return [
                Repeat(repeats=self.eluting_repeats, children=eluting_steps)
            ]
        return eluting_steps

    def get_single_portion_elution_steps(self, volume):
        if volume:
            return [
                Transfer(
                    from_vessel=self.eluting_solvent_vessel,
                    to_vessel=self.from_vessel,
                    volume=volume
                ),

                Transfer(
                    from_vessel=self.from_vessel,
                    to_vessel=self.to_vessel,
                    through=self.through,
                    volume=volume,
                    move_speed=self.move_speed,
                    aspiration_speed=self.aspiration_speed
                )
            ]
        return []

    #######################
    # General With Buffer #
    #######################

    def get_filter_through_transfer_to_buffer_steps(self):
        return [
            Transfer(
                from_vessel=self.from_vessel,
                to_vessel=self.buffer_flask,
                through=self.through,
                volume='all',
                move_speed=self.move_speed,
                aspiration_speed=self.aspiration_speed
            )
        ]

    def get_flush_cartridge_to_buffer_steps(self):
        if self.flush_cartridge_vessel:
            return [
                Transfer(
                    from_vessel=self.flush_cartridge_vessel,
                    to_vessel=self.buffer_flask,
                    through=self.through,
                    volume=self.cartridge_dead_volume,
                    move_speed=self.move_speed,
                    aspiration_speed=self.aspiration_speed
                )
            ]
        return []

    def get_transfer_back_from_buffer_steps(self):
        return [
            Transfer(
                from_vessel=self.buffer_flask,
                to_vessel=self.to_vessel,
                volume='all',
                move_speed=self.move_speed,
                aspiration_speed=self.aspiration_speed
            )
        ]

    #######################
    # Elution With Buffer #
    #######################

    def get_clean_from_and_to_vessel_steps(self):
        return [
            CleanVessel(
                vessel=self.from_vessel,
                solvent=self.eluting_solvent
            )
        ]

    def get_single_elution_to_buffer_steps(self):
        eluting_steps = [
            Transfer(
                from_vessel=self.eluting_solvent_vessel,
                to_vessel=self.from_vessel,
                volume=self.eluting_volume),

            Transfer(
                from_vessel=self.from_vessel,
                to_vessel=self.buffer_flask,
                through=self.through,
                volume=self.eluting_volume,
                move_speed=self.move_speed,
                aspiration_speed=self.aspiration_speed)
        ]
        if self.eluting_repeats > 1:
            return [
                Repeat(repeats=self.eluting_repeats, children=eluting_steps)
            ]
        return eluting_steps

    @property
    def buffer_flasks_required(self):
        if self.to_vessel == self.from_vessel:
            return 1
        return 0

    def human_readable(self, language='en'):
        try:
            if self.eluting_solvent:
                return HUMAN_READABLE_STEPS[
                    'FilterThrough (eluting)'][language].format(
                        **self.formatted_properties())
            else:
                return HUMAN_READABLE_STEPS[
                    'FilterThrough (not eluting)'][language].format(
                        **self.formatted_properties())
        except KeyError:
            return self.name
