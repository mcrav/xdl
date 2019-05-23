from typing import Optional, Dict, Any, List
from ..base_step import Step, AbstractStep
from .add import Add
from ..steps_utility import Transfer, Wait, Stir
from ..steps_base import CSeparatePhases, CMove
from ...utils.misc import get_port_str
from ...constants import (
    BOTTOM_PORT,
    TOP_PORT,
    DEFAULT_SEPARATION_FAST_STIR_TIME,
    DEFAULT_SEPARATION_FAST_STIR_RPM,
    DEFAULT_SEPARATION_SLOW_STIR_TIME,
    DEFAULT_SEPARATION_SLOW_STIR_RPM,
    DEFAULT_SEPARATION_SETTLE_TIME,
)

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
        through (str): Optional. Cartridge to transfer product phrase through
            on way to to_vessel.
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
        solvent: str,
        product_bottom: bool,
        through: Optional[str] = None,
        from_port: Optional[str] = None,
        to_port: Optional[str] = None,
        solvent_volume: Optional[float] = 'default',
        n_separations: Optional[float] = 1,
        waste_phase_to_vessel: Optional[str] = None,
        waste_phase_to_port: Optional[str] = None,
        waste_vessel: Optional[str] = None,
        remove_dead_volume: Optional[bool] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        if not self.waste_phase_to_vessel and self.waste_vessel:
            self.waste_phase_to_vessel = self.waste_vessel

        if not self.n_separations:
            n_separations = 1
        else:
            n_separations = int(self.n_separations)

        dead_volume_target = None
        if self.remove_dead_volume:
            dead_volume_target = self.waste_vessel

        steps = []
        steps.extend([
            # Move from from_vessel to separation_vessel
            Transfer(
                from_vessel=self.from_vessel, from_port=self.from_port, 
                to_vessel=self.separation_vessel, to_port=TOP_PORT, 
                volume='all'),
            # Move solvent to separation_vessel.
            Add(reagent=self.solvent, volume=self.solvent_volume, 
                vessel=self.separation_vessel, port=BOTTOM_PORT, 
                waste_vessel=self.waste_vessel),
            # Stir separation_vessel
            Stir(vessel=self.separation_vessel, 
                 time=DEFAULT_SEPARATION_FAST_STIR_TIME, 
                 stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
            Stir(vessel=self.separation_vessel, 
                 time=DEFAULT_SEPARATION_SLOW_STIR_TIME, 
                 stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
            # Wait for phases to separate
            Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
        ])

        if self.from_vessel == self.separation_vessel:
            steps.pop(0)

        remove_volume = 2

        # If product in bottom phase
        if self.product_bottom:
            if n_separations > 1:
                for _ in range(n_separations - 1):
                    steps.extend([
                        Transfer(from_vessel=self.separation_vessel, 
                                 from_port=BOTTOM_PORT, 
                                 to_vessel=self.waste_vessel, 
                                 volume=remove_volume),
                        # dead_volume_target is None as there is no point wasting
                        # when there is still solvent to come.
                        CSeparatePhases(lower_phase_vessel=self.to_vessel, 
                                        lower_phase_port=self.to_port,
                                        upper_phase_vessel=self.waste_phase_to_vessel,
                                        upper_phase_port=self.waste_phase_to_port,
                                        separation_vessel=self.separation_vessel, 
                                        dead_volume_target=None,
                                        lower_phase_through=self.through),
                        # Move to_vessel to separation_vessel
                        CMove(from_vessel=self.to_vessel, 
                              to_vessel=self.separation_vessel, volume='all'),
                        # Move solvent to separation_vessel. 
                        # Bottom port as washes any reagent from previous 
                        # separation back into funnel.
                        Add(reagent=self.solvent, volume=self.solvent_volume, 
                            vessel=self.separation_vessel, port=BOTTOM_PORT, 
                            waste_vessel=self.waste_vessel),
                        # Stir separation_vessel
                        Stir(vessel=self.separation_vessel, 
                             time=DEFAULT_SEPARATION_FAST_STIR_TIME, 
                             stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
                        Stir(vessel=self.separation_vessel, 
                             time=DEFAULT_SEPARATION_SLOW_STIR_TIME, 
                             stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
                        # Wait for phases to separate
                        Wait(time=DEFAULT_SEPARATION_SETTLE_TIME)
                    ])


            steps.extend([
                Transfer(from_vessel=self.separation_vessel, 
                         from_port=BOTTOM_PORT, to_vessel=self.waste_vessel, 
                         volume=remove_volume),
                CSeparatePhases(
                    separation_vessel=self.separation_vessel,
                    lower_phase_vessel=self.to_vessel,
                    lower_phase_port=self.to_port,
                    upper_phase_vessel=self.waste_phase_to_vessel,
                    upper_phase_port=self.waste_phase_to_port,
                    dead_volume_target=dead_volume_target,
                    lower_phase_through=self.through),
            ])
        else:
            if n_separations > 1:
                for _ in range(n_separations - 1):
                    steps.extend([
                        Transfer(from_vessel=self.separation_vessel, 
                                 from_port=BOTTOM_PORT, 
                                 to_vessel=self.waste_vessel,
                                 volume=remove_volume),
                        # dead_volume_target is None as there is no point wasting
                        # when there is still solvent to come.
                        CSeparatePhases(
                            lower_phase_vessel=self.waste_phase_to_vessel,
                            lower_phase_port=self.waste_phase_to_port,
                            upper_phase_vessel=self.separation_vessel,
                            separation_vessel=self.separation_vessel,
                            dead_volume_target=None),
                        # Move solvent to separation_vessel
                        Add(reagent=self.solvent, vessel=self.separation_vessel, 
                            port=BOTTOM_PORT, volume=self.solvent_volume, 
                            waste_vessel=self.waste_vessel),
                        # Stir separation_vessel
                        Stir(vessel=self.separation_vessel, 
                             time=DEFAULT_SEPARATION_FAST_STIR_TIME, 
                             stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
                        Stir(vessel=self.separation_vessel, 
                             time=DEFAULT_SEPARATION_SLOW_STIR_TIME, 
                             stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
                        # Wait for phases to separate
                        Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
                    ])

            steps.extend([
                Transfer(from_vessel=self.separation_vessel, 
                         from_port=BOTTOM_PORT, to_vessel=self.waste_vessel, 
                         volume=remove_volume),
                CSeparatePhases(lower_phase_vessel=self.waste_phase_to_vessel, 
                                lower_phase_port=self.waste_phase_to_port, 
                                upper_phase_vessel=self.to_vessel,
                                upper_phase_port=self.to_port,
                                separation_vessel=self.separation_vessel,
                                dead_volume_target=dead_volume_target,
                                upper_phase_through=self.through)
            ])
        return steps

    @property
    def human_readable(self) -> str:
        return 'Separate contents of {0} {1} with {2} ({3}x{4} mL). Transfer waste phase to {5} {6} and product phase to {7} {8}.'.format(
            self.from_vessel,
            get_port_str(self.from_port),
            self.solvent,
            self.n_separations,
            self.solvent_volume,
            self.waste_phase_to_vessel,
            get_port_str(self.waste_phase_to_port),
            self.to_vessel,
            self.to_port)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'separation_vessel': {
                'separator': True,
            }
        }