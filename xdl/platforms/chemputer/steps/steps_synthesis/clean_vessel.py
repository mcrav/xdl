from typing import Optional
from .....step_utils.base_steps import AbstractStep
from ..steps_utility import (
    StartStir, StopStir, Wait, HeatChillToTemp, HeatChillReturnToRT)
from ..steps_base import CMove
from .dry import Dry
from .....utils.misc import SanityCheck
from ...utils.execution import (
    get_vacuum_configuration,
    get_nearest_node,
    get_reagent_vessel,
    get_heater_chiller,
    get_vessel_type,
)
from .....constants import CHEMPUTER_WASTE

class CleanVessel(AbstractStep):
    """Clean given vessel with given solvent.

    Args:
        vessel (str): Vessel to clean.
        solvent (str): Solvent to clean vessel with.
        stir_time (float): Time to stir for after solvent is added.
        stir_speed (float): Speed to stir at in RPM.
        volume (float): Volume of solvent to use. If not supplied will be
            given internally according to vessel max volume.
        cleans (int): Number of cleans to do.
        solvent_vessel (str): Given internally. Flask containing solvent.
        waste_vessel (str): Given internally. Vessel to send waste solvent
            to.
        vacuum (str): Internal property. Used to tell if drying is possible.
    """

    DEFAULT_PROPS = {
        'stir_time': '1 minute',
        'stir_speed': '500 RPM',
    }

    #: Fraction of vessel max volume to use as solvent volume in CleanVessel
    # step.
    CLEAN_VESSEL_VOLUME_FRACTION: float = 0.5

    def __init__(
        self,
        vessel: str,
        solvent: str,
        stir_time: Optional[float] = 'default',
        stir_speed: Optional[float] = 'default',
        temp: Optional[float] = None,
        dry: Optional[bool] = False,
        volume: Optional[float] = None,
        cleans: Optional[int] = 2,
        solvent_vessel: Optional[str] = None,
        waste_vessel: Optional[str] = None,
        vacuum: Optional[str] = None,
        vessel_type: Optional[str] = None,
        heater: Optional[str] = None,
        chiller: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):

        if self.volume is None:
            self.volume = (
                graph.nodes[self.vessel]['max_volume']
                * self.CLEAN_VESSEL_VOLUME_FRACTION
            )

        if not self.vessel_type:
            self.vessel_type = get_vessel_type(graph, self.vessel)

        self.heater, self.chiller = get_heater_chiller(graph, self.vessel)

        if not self.waste_vessel:
            self.waste_vessel = get_nearest_node(
                graph, self.vessel, CHEMPUTER_WASTE)

        if not self.solvent_vessel:
            self.solvent_vessel = get_reagent_vessel(graph, self.solvent)

        vacuum_info = get_vacuum_configuration(graph, self.vessel)
        if vacuum_info['source']:
            self.dry = True
            if not self.vacuum:
                self.vacuum = vacuum_info['source']

        for node in graph.nodes():
            if graph.nodes[node]['class'] == 'ChemputerFlask':
                if graph.nodes[node]['chemical'] == self.solvent:
                    self.solvent_vessel = node
                    break
        self.check_for_heater()

    def check_for_heater(self):
        if (self.temp is not None
            and not (self.heater or self.chiller
                     or self.vessel_type == 'rotavap')):
            self.temp = None

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=self.solvent_vessel,
                error_msg=f'No solvent vessel found in graph for {self.solvent}'
            ),

            SanityCheck(
                condition=self.waste_vessel,
                error_msg=f'No waste vessel found for "{self.vessel}".'
            ),

            SanityCheck(
                condition=self.cleans > 0,
                error_msg=f'`cleans` property must be > 0. {self.cleans} is an\
 invalid value.'
            ),

            SanityCheck(
                condition=self.volume and self.volume > 0,
                error_msg=f'`volume` must be > 0. {self.volume} is an invalid\
 value.'
            ),
        ]

    def get_steps(self):
        steps = []
        for _ in range(self.cleans):
            steps.extend([
                StartStir(vessel=self.vessel),
                CMove(from_vessel=self.solvent_vessel,
                      to_vessel=self.vessel,
                      volume=self.volume),
                Wait(time=self.stir_time),
                CMove(from_vessel=self.vessel,
                      to_vessel=self.waste_vessel,
                      volume=self.volume),
                StopStir(vessel=self.vessel),
            ])
        if self.dry:
            steps.append(Dry(vessel=self.vessel))
        if self.temp is not None and (self.temp < 20 or self.temp > 25):
            steps.insert(
                1, HeatChillToTemp(vessel=self.vessel, temp=self.temp))
            steps.append(HeatChillReturnToRT(vessel=self.vessel, stir=False))
        return steps
