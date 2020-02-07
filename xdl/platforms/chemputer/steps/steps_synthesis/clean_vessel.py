from typing import Optional
from .....step_utils.base_steps import AbstractStep
from ..steps_utility import (
    StartStir, StopStir, Wait, HeatChillToTemp, HeatChillReturnToRT)
from ..steps_base import CMove
from .dry import Dry
from .....utils.errors import XDLError
from ...utils.execution import get_neighboring_vacuum

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

    def __init__(
        self,
        vessel: str,
        solvent: str,
        stir_time: Optional[float] = 'default',
        stir_speed: Optional[float] = 'default',
        temp: Optional[float] = None,
        dry: Optional[bool] = True,
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

    def final_sanity_check(self, graph):
        try:
            assert self.solvent_vessel
        except AssertionError:
            raise XDLError(
                f'No solvent vessel found in graph for {self.solvent}')

        try:
            assert self.waste_vessel
        except AssertionError:
            raise XDLError(
                f'No waste vessel found for "{self.vessel}".')

        try:
            assert self.cleans > 0
        except AssertionError:
            raise XDLError(
                f'`cleans` property must be > 0. {self.cleans} is an invalid\
 value.')

        try:
            assert self.volume and self.volume > 0
        except AssertionError:
            raise XDLError(
                f'`volume` must be > 0. {self.volume} is an invalid value.')

    def on_prepare_for_execution(self, graph):
        for node in graph.nodes():
            if graph.nodes[node]['class'] == 'ChemputerFlask':
                if graph.nodes[node]['chemical'] == self.solvent:
                    self.solvent_vessel = node
                    break
        self.check_for_vacuum_pump(graph)
        self.check_for_heater()

    def check_for_vacuum_pump(self, graph):
        if self.dry and not self.vessel_type == 'rotavap':
            if not get_neighboring_vacuum(graph, self.vessel):
                self.dry = False

    def check_for_heater(self):
        if (self.temp is not None
            and not (self.heater or self.chiller
                     or self.vessel_type == 'rotavap')):
            self.temp = None

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
