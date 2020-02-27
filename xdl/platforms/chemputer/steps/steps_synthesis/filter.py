from typing import Optional, List, Dict, Any
from .....step_utils.base_steps import Step, AbstractStep
from ..steps_base import CMove
from ..steps_utility import (
    StopStir, StartStir, Transfer, ApplyVacuum)
from .....constants import (
    BOTTOM_PORT,
    DEFAULT_FILTER_EXCESS_REMOVE_FACTOR,
    DEFAULT_FILTER_ANTICLOGGING_ASPIRATION_SPEED,
)
from .....utils.misc import SanityCheck
from ...utils.execution import get_vacuum_configuration, get_nearest_node
from .....constants import CHEMPUTER_WASTE

class Filter(AbstractStep):
    """Filter contents of filter vessel. Apply vacuum for given time.
    Assumes liquid is already in the top of the filter vessel.

    Args:
        filter_vessel (str): Filter vessel.
        filter_top_volume (float): Volume (mL) of contents of filter top.
        wait_time (float): Time to leave vacuum on filter vessel after contents
            have been moved. (optional)
        aspiration_speed (float): Speed in mL / min to draw liquid from
            filter_vessel.
        stir (bool): True to stir, False to stop stirring.
        stir_speed (float): Speed to stir at in RPM.
        waste_vessel (float): Given internally. Vessel to move waste material
            to.
        filtrate_vessel (str): Optional. Vessel to send filtrate to. Defaults to
            waste_vessel.
        vacuum (str): Given internally. Name of vacuum flask.
        vacuum_device (str): Given internally. Name of vacuum device attached to
            vacuum flask. Can be None if vacuum is just from fumehood vacuum
            line.
        vacuum_valve (str): Given internally. Name of valve connecting filter
            bottom to vacuum.
        valve_unused_port (str): Given internally. Random unused position on
            valve.
    """

    DEFAULT_PROPS = {
        'wait_time': '2 minutes',
        'aspiration_speed': 5,  # mL / min
        'stir': True,
        'stir_speed': '500 RPM',
        'anticlogging': False,
    }

    PROP_TYPES = {
        'filter_vessel': str,
        'wait_time': float,
        'aspiration_speed': float,
        'stir': bool,
        'stir_speed': float,
        'filtrate_vessel': str,
        'anticlogging': bool,
        'waste_vessel': str,
        'filter_top_volume': float,
        'inline_filter': bool,
        'vacuum_attached': bool
    }

    INTERNAL_PROPS = [
        'waste_vessel',
        'filter_top_volume',
        'inline_filter',
        'vacuum_attached',
    ]

    def __init__(
        self,
        filter_vessel: str,
        wait_time: Optional[float] = 'default',
        aspiration_speed: Optional[float] = 'default',
        stir: Optional[bool] = 'default',
        stir_speed: Optional[float] = 'default',
        filtrate_vessel: Optional[str] = None,
        anticlogging: Optional[bool] = 'default',

        # Internal properties
        waste_vessel: Optional[str] = None,
        filter_top_volume: Optional[float] = 0,
        inline_filter: Optional[bool] = False,
        vacuum_attached: Optional[bool] = False,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.waste_vessel:
            self.waste_vessel = get_nearest_node(
                graph, self.filter_vessel, CHEMPUTER_WASTE)

        filter_vessel = graph.nodes[self.filter_vessel]
        if (filter_vessel['class'] != 'ChemputerFilter'
                and ('can_filter' in filter_vessel
                     and filter_vessel['can_filter'] is True)):
            self.inline_filter = True

        if get_vacuum_configuration(graph, self.filter_vessel)['source']:
            self.vacuum_attached = True

    def get_steps(self) -> List[Step]:
        # Normal filtering in ChemputerFilter
        if not self.inline_filter:
            return self.get_normal_filtering_steps()

        else:
            # Inline filtering in reactor or rotavap with vacuum
            if self.vacuum_attached:
                return self.get_inline_filtering_with_vacuum_steps()

            else:
                # Inline filtering in reactor or rotavap without vacuum
                return self.get_inline_filtering_without_vacuum_steps()

    def get_normal_filtering_steps(self):
        """ChemputerFilter attached to vacuum."""
        return (
            self.get_initial_stir()
            + self.get_normal_filter_liquid_transfer()
            + self.get_vacuum_stop_stir()
            + self.apply_vacuum(port=BOTTOM_PORT)
        )

    def get_inline_filtering_with_vacuum_steps(self):
        """Reactor or rotavap attached to vacuum."""
        return (
            self.get_initial_stir()
            + self.get_inline_filter_to()
            + self.get_vacuum_stop_stir()
            + self.apply_vacuum()
        )

    def get_inline_filtering_without_vacuum_steps(self):
        """Reactor or rotavap with no vacuum."""
        return (
            self.get_initial_stir()
            + self.get_inline_filter_to()
        )

    def get_normal_filter_liquid_transfer(self):
        return [
            CMove(
                from_vessel=self.filter_vessel,
                to_vessel=self.get_filtrate_vessel(),
                from_port=BOTTOM_PORT,
                volume=(self.filter_top_volume
                        * DEFAULT_FILTER_EXCESS_REMOVE_FACTOR),
                aspiration_speed=self.get_aspiration_speed()
            )
        ]

    def get_inline_filter_to(self):
        return [FilterTo(
            from_vessel=self.filter_vessel,
            to_vessel=self.filtrate_vessel
        )]

    def get_start_stir(self):
        return StartStir(vessel=self.filter_vessel, stir_speed=self.stir_speed)

    def get_stop_stir(self):
        return StopStir(vessel=self.filter_vessel)

    def get_initial_stir(self):
        if self.stir is True:
            return [self.get_start_stir()]
        else:
            return [self.get_stop_stir()]

    def get_vacuum_stop_stir(self):
        # Stirring already stopped at start of step
        if self.stir is False:
            return []

        # Using filtrate so no point drying solid.
        elif (self.filtrate_vessel is not None
                and self.filtrate_vessel != self.waste_vessel):
            return []

        else:
            return [self.get_stop_stir()]

    def apply_vacuum(self, port=None):
        # Using filtrate so no point drying solid.
        if (self.filtrate_vessel is not None
                and self.filtrate_vessel != self.waste_vessel):
            return []
        else:
            return [
                ApplyVacuum(
                    vessel=self.filter_vessel,
                    time=self.wait_time,
                    port=port
                )
            ]

    def get_aspiration_speed(self):
        aspiration_speed = self.aspiration_speed
        if self.anticlogging:
            aspiration_speed = DEFAULT_FILTER_ANTICLOGGING_ASPIRATION_SPEED
        return aspiration_speed

    def get_filtrate_vessel(self):
        filtrate_vessel = self.filtrate_vessel
        if not filtrate_vessel:
            filtrate_vessel = self.waste_vessel
        return filtrate_vessel

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'filter_vessel': {
                'filter': True
            }
        }

class FilterTo(AbstractStep):

    PROP_TYPES = {
        'from_vessel': str,
        'to_vessel': str,
    }

    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
    ):
        super().__init__(locals())

    def get_steps(self):
        return [
            Transfer(
                from_vessel=self.from_vessel,
                to_vessel=self.to_vessel,
                volume='all',
            )
        ]

    def sanity_checks(self, graph):
        full_node = graph.nodes[self.from_vessel]
        return [
            SanityCheck(
                condition='can_filter' in full_node and full_node['can_filter'],
                error_msg=f"from_vessel ({self.from_vessel}) doesn't have\
 can_filter property == True"
            ),

            SanityCheck(
                condition=self.from_vessel != self.to_vessel,
                error_msg=f"from_vessel and to_vessel can't be the same node\
 ({self.from_vessel})."
            )
        ]
