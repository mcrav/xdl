from typing import Optional, Dict, Any, List
from .....step_utils.base_steps import Step, AbstractStep
from .add import Add
from ..steps_utility import Transfer, Wait, Stir, SeparatePhases
from .....constants import (
    BOTTOM_PORT,
    DEFAULT_SEPARATION_FAST_STIR_TIME,
    DEFAULT_SEPARATION_FAST_STIR_SPEED,
    DEFAULT_SEPARATION_SLOW_STIR_TIME,
    DEFAULT_SEPARATION_SLOW_STIR_SPEED,
    DEFAULT_SEPARATION_SETTLE_TIME,
)
from .....utils.errors import XDLError
from .....localisation import HUMAN_READABLE_STEPS
from ...utils.execution import get_buffer_flasks

class Separate(AbstractStep):
    """Extract contents of from_vessel using given amount of given solvent.
    NOTE: If n_separations > 1, to_vessel/to_port must be capable of giving
    and receiving material.

    Args:
        purpose (str): 'extract' or 'wash'. Used in iter_vessel_contents.
        from_vessel (str): Vessel name with contents to be separated.
        from_port (str): from_vessel port to use.
        separation_vessel (str): Separation vessel name.
        to_vessel (str): Vessel to send product phase to.
        to_port (str): to_vessel port to use.
        solvent (str): Solvent to extract with.
        solvent_volume (float): Volume of solvent to extract with.
        product_bottom (bool): True if product in bottom phase, otherwise False.
        through (str): Optional. Chemical to transfer product phase through
            on way to to_vessel.
        through_cartridge (str): Optional. Node name of cartridge to transfer
            product phase through on way to to_vessel. Supplied internally if
            through is given.
        n_separations (int): Number of separations to perform.
        waste_phase_to_vessel (str): Vessel to send waste phase to.
        waste_phase_to_port (str): waste_phase_to_vessel port to use.
        waste_vessel (str): Given internally. Vessel to send waste to.
    """
    def __init__(
        self,
        purpose: str,
        from_vessel: str,
        separation_vessel: str,
        to_vessel: str,
        product_bottom: bool,
        solvent: Optional[str] = None,
        through: Optional[str] = None,
        through_cartridge: Optional[str] = None,
        from_port: Optional[str] = None,
        to_port: Optional[str] = None,
        solvent_volume: Optional[float] = 'default',
        n_separations: Optional[int] = 1,
        waste_phase_to_vessel: Optional[str] = None,
        waste_phase_to_port: Optional[str] = None,
        waste_vessel: Optional[str] = None,
        buffer_flasks: Optional[List[str]] = [None, None],
        remove_dead_volume: Optional[bool] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    @property
    def dead_volume_target(self):
        return self.waste_vessel if self.remove_dead_volume else None

    def get_steps(self) -> List[Step]:
        """It may seem mental having this many methods with lots of duplicate
        code but the condensed version with lots of if statements for different
        scenarios was took too long to see what was going on. Better just to
        have clear routines for every scenario.
        """
        if not self.waste_phase_to_vessel and self.waste_vessel:
            self.waste_phase_to_vessel = self.waste_vessel
        if not self.n_separations:
            self.n_separations = 1

        if self.n_separations > 1:
            if self.purpose == 'wash':
                return self._get_multi_wash_steps()

            elif self.purpose == 'extract':
                return self._get_multi_extract_steps()

            raise XDLError('Invalid purpose given to Separate step.\nValid\
 purposes: "wash" or "extract"')

        else:
            return self._get_single_separation_steps()

    #################################
    # Separation Routine Components #
    #################################

    def _get_initial_reaction_mixture_transfer_step(self):
        """Transfer reaction mixture to separator."""
        steps = []
        if self.from_vessel != self.separation_vessel:
            steps.append(
                # Move from from_vessel to separation_vessel
                Transfer(
                    from_vessel=self.from_vessel,
                    from_port=self.from_port,
                    to_vessel=self.separation_vessel,
                    to_port=BOTTOM_PORT,
                    volume='all'
                )
            )
        return steps

    def _get_add_solvent_step(self):
        """Add washing/extraction solvent to separator."""
        steps = []
        if self.solvent:
            steps.append(
                # Move solvent to separation_vessel
                Add(reagent=self.solvent,
                    vessel=self.separation_vessel,
                    port=BOTTOM_PORT,
                    volume=self.solvent_volume,
                    waste_vessel=self.waste_vessel)
            )
        return steps

    def _get_stir_separator_before_separation_steps(self):
        """Stir separator and wait for phases to appear."""
        return [
            # Stir separation_vessel
            Stir(vessel=self.separation_vessel,
                 time=DEFAULT_SEPARATION_FAST_STIR_TIME,
                 stir_speed=DEFAULT_SEPARATION_FAST_STIR_SPEED),
            Stir(vessel=self.separation_vessel,
                 time=DEFAULT_SEPARATION_SLOW_STIR_TIME,
                 stir_speed=DEFAULT_SEPARATION_SLOW_STIR_SPEED),
            # Wait for phases to separate
            Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
        ]

    def _get_final_separate_phases_step(self):
        """Get final SeparatePhases step in separation routine."""
        if self.product_bottom:
            if self.to_vessel != self.separation_vessel:
                return [SeparatePhases(
                    separation_vessel=self.separation_vessel,
                    lower_phase_vessel=self.to_vessel,
                    lower_phase_port=self.to_port,
                    upper_phase_vessel=self.waste_phase_to_vessel,
                    upper_phase_port=self.waste_phase_to_port,
                    dead_volume_vessel=self.dead_volume_target,
                    dead_volume_through=self.through_cartridge,
                    lower_phase_through=self.through_cartridge
                )]
            else:
                return [
                    SeparatePhases(
                        separation_vessel=self.separation_vessel,
                        lower_phase_vessel=self.buffer_flasks[0],
                        upper_phase_vessel=self.waste_phase_to_vessel,
                        upper_phase_port=self.waste_phase_to_port,
                        dead_volume_vessel=self.dead_volume_target,
                    ),
                    Transfer(
                        from_vessel=self.buffer_flasks[0],
                        to_vessel=self.separation_vessel,
                        volume='all'
                    )
                ]
        else:
            if (self.n_separations > 1
                    and self.to_vessel == self.separation_vessel
                    and self.purpose == 'extract'):
                return [
                    SeparatePhases(
                        separation_vessel=self.separation_vessel,
                        lower_phase_vessel=self.waste_phase_to_vessel,
                        lower_phase_port=self.waste_phase_to_port,
                        upper_phase_vessel=self.to_vessel,
                        dead_volume_vessel=self.dead_volume_target,
                    ),
                    Transfer(
                        from_vessel=self.buffer_flasks[1],
                        to_vessel=self.separation_vessel,
                        volume='all'
                    )
                ]

            elif self.waste_phase_to_vessel == self.separation_vessel:
                return [
                    SeparatePhases(
                        separation_vessel=self.separation_vessel,
                        lower_phase_vessel=self.buffer_flasks[0],
                        upper_phase_vessel=self.to_vessel,
                        upper_phase_port=self.to_port,
                        dead_volume_vessel=self.dead_volume_target,
                        upper_phase_through=self.through_cartridge
                    ),
                    Transfer(
                        from_vessel=self.buffer_flasks[0],
                        to_vessel=self.waste_phase_to_vessel,
                        volume='all'
                    )
                ]

            return [SeparatePhases(
                separation_vessel=self.separation_vessel,
                lower_phase_vessel=self.waste_phase_to_vessel,
                lower_phase_port=self.waste_phase_to_port,
                upper_phase_vessel=self.to_vessel,
                upper_phase_port=self.to_port,
                dead_volume_vessel=self.dead_volume_target,
                upper_phase_through=self.through_cartridge
            )]

    def _get_multi_wash_loop_separate_phases(self):
        """Get CSeparatePhases in wash routine, if there is another separation
        to be performed after. Ensure product phase ends up in back in
        separator.
        """
        steps = []
        if self.product_bottom:
            if self.to_vessel != self.separation_vessel:
                steps.extend([
                    SeparatePhases(
                        separation_vessel=self.separation_vessel,
                        lower_phase_vessel=self.to_vessel,
                        lower_phase_port=self.to_port,
                        upper_phase_vessel=self.waste_phase_to_vessel,
                        upper_phase_port=self.waste_phase_to_port,
                        lower_phase_through=self.through_cartridge,
                        dead_volume_through=self.through_cartridge,
                        dead_volume_vessel=self.to_vessel,
                    ),
                    # Move to_vessel to separation_vessel
                    Transfer(
                        from_vessel=self.to_vessel,
                        to_vessel=self.separation_vessel,
                        volume='all'
                    ),
                ])
            else:
                steps.extend([
                    SeparatePhases(
                        separation_vessel=self.separation_vessel,
                        lower_phase_vessel=self.buffer_flasks[0],
                        upper_phase_vessel=self.waste_phase_to_vessel,
                        upper_phase_port=self.waste_phase_to_port,
                        dead_volume_vessel=self.buffer_flasks[0],
                    ),
                    Transfer(
                        from_vessel=self.buffer_flasks[0],
                        to_vessel=self.separation_vessel,
                        volume='all'
                    ),
                ])
        else:
            steps.append(
                SeparatePhases(
                    separation_vessel=self.separation_vessel,
                    lower_phase_vessel=self.waste_phase_to_vessel,
                    lower_phase_port=self.waste_phase_to_port,
                    upper_phase_vessel=self.separation_vessel,
                    dead_volume_vessel=self.waste_phase_to_vessel,
                )
            )
        return steps

    def _get_multi_extract_loop_separate_phases(self):
        """Get SeparatePhases in extract routine, if there is another separation
        to be performed after. Ensure waste phase ends up in back in separator.
        """
        steps = []
        if self.product_bottom:
            if self.to_vessel != self.separation_vessel:
                steps.append(
                    SeparatePhases(
                        separation_vessel=self.separation_vessel,
                        lower_phase_vessel=self.to_vessel,
                        lower_phase_port=self.to_port,
                        lower_phase_through=self.through_cartridge,
                        upper_phase_vessel=self.separation_vessel,
                        dead_volume_vessel=self.to_vessel,
                        dead_volume_through=self.through_cartridge,
                    )
                )
            else:
                steps.append(
                    SeparatePhases(
                        separation_vessel=self.separation_vessel,
                        lower_phase_vessel=self.buffer_flasks[0],
                        upper_phase_vessel=self.separation_vessel,
                        dead_volume_vessel=self.buffer_flasks[0],
                    )
                )
        else:
            if self.to_vessel != self.separation_vessel:
                steps.extend([
                    SeparatePhases(
                        separation_vessel=self.separation_vessel,
                        lower_phase_vessel=self.buffer_flasks[0],
                        upper_phase_vessel=self.to_vessel,
                        upper_phase_port=self.to_port,
                        upper_phase_through=self.through_cartridge,
                        dead_volume_vessel=self.buffer_flasks[0],
                    ),
                    # Move waste phase in buffer flask back to separation_vessel
                    Transfer(
                        from_vessel=self.buffer_flasks[0],
                        to_vessel=self.separation_vessel,
                        volume='all'
                    ),
                ])
            else:
                steps.extend([
                    SeparatePhases(
                        separation_vessel=self.separation_vessel,
                        lower_phase_vessel=self.buffer_flasks[0],
                        upper_phase_vessel=self.buffer_flasks[1],
                        dead_volume_vessel=self.buffer_flasks[0],
                    ),
                    Transfer(
                        from_vessel=self.buffer_flasks[0],
                        to_vessel=self.separation_vessel,
                        volume='all',
                    )
                ])
        return steps

    ################################
    # Complete Separation Routines #
    ################################

    def _get_single_separation_steps(self):
        """Get full separation routine for 1 wash/extraction."""
        # If necessary, Transfer from_vessel to separation_vessel
        steps = self._get_initial_reaction_mixture_transfer_step()

        steps.extend(self._get_add_solvent_step())

        # Stir separator
        steps.extend(self._get_stir_separator_before_separation_steps())

        # Separate, vessels depending on self.product_bottom
        steps.extend(self._get_final_separate_phases_step())

        return steps

    def _get_multi_wash_steps(self):
        """Get full separation routine for >1 washes."""
        # If necessary, Transfer from_vessel to separation_vessel
        steps = self._get_initial_reaction_mixture_transfer_step()

        # Add solvent
        steps.extend(self._get_add_solvent_step())

        # Stir separator
        steps.extend(self._get_stir_separator_before_separation_steps())

        for _ in range(self.n_separations - 1):
            # Separate phases, and make sure product phase ends up back in
            # separator
            steps.extend(self._get_multi_wash_loop_separate_phases())

            # Add more solvent
            steps.extend(self._get_add_solvent_step())

            # Stir
            steps.extend(self._get_stir_separator_before_separation_steps())

        steps.extend(self._get_final_separate_phases_step())
        return steps

    def _get_multi_extract_steps(self):
        """Get full separation routine for >1 extractions."""
        # If necessary, Transfer from_vessel to separation_vessel
        steps = self._get_initial_reaction_mixture_transfer_step()

        # Add solvent
        steps.extend(self._get_add_solvent_step())

        # Stir separator
        steps.extend(self._get_stir_separator_before_separation_steps())

        for _ in range(self.n_separations - 1):
            # Separate phases, and make sure waste phase ends up back in
            # separator
            steps.extend(self._get_multi_extract_loop_separate_phases())

            # Add more solvent
            steps.extend(self._get_add_solvent_step())

            # Stir
            steps.extend(self._get_stir_separator_before_separation_steps())

        steps.extend(self._get_final_separate_phases_step())
        return steps

    ####################################
    #  Abstract Method implementations #
    ####################################

    def final_sanity_check(self, graph):
        buffer_flasks = get_buffer_flasks(graph)
        try:
            assert len(buffer_flasks) >= self.buffer_flasks_required
        except AssertionError:
            raise XDLError('Not enough buffer flasks in graph. Create buffer\
 flasks as ChemputerFlask nodes with an empty chemical property.')
        assert self.to_vessel != self.waste_phase_to_vessel
        assert not self.solvent_volume or self.solvent_volume > 0
        assert self.purpose in ['extract', 'wash']
        assert self.n_separations > 0

    @property
    def buffer_flasks_required(self):
        if (self.purpose == 'extract'
                and self.n_separations > 1
                and not self.product_bottom
                and self.to_vessel == self.separation_vessel):
            return 2
        elif (
            (self.product_bottom
             and self.n_separations == 1
             and self.to_vessel == self.separation_vessel)
            or (self.n_separations > 1
                and self.product_bottom
                and self.to_vessel == self.separation_vessel
                and self.purpose == 'wash')
            or (self.purpose == 'extract'
                and self.product_bottom
                and self.to_vessel == self.separation_vessel
                and self.n_separations > 1)
            or (self.purpose == 'extract'
                and not self.product_bottom
                and self.n_separations > 1)
        ):
            return 1
        return 0

    def human_readable(self, language='en') -> str:
        props = self.formatted_properties()

        phases = ['bottom', 'top']
        # Remember True == 1 and False == 0
        props['waste_phase'] = phases[self.product_bottom]
        props['product_phase'] = phases[not self.product_bottom]

        try:
            if self.purpose == 'wash':
                s = HUMAN_READABLE_STEPS['Separate (wash)'][language].format(
                    **props)
            elif self.purpose == 'extract':
                s = HUMAN_READABLE_STEPS['Separate (extract)'][language].format(
                    **props)
            return s[0].upper() + s[1:]
        except KeyError:
            return self.name

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'separation_vessel': {
                'separator': True,
            }
        }
