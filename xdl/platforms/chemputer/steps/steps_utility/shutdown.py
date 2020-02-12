from typing import List
from itertools import chain
from .....constants import (
    CHILLER_CLASSES,
    HEATER_CLASSES,
    ROTAVAP_CLASSES,
    VACUUM_CLASSES,
    STIRRER_CLASSES
)
from .....step_utils import AbstractStep
from ..steps_base import (
    CRotavapLiftUp,
    CStopChiller,
    CStopHeat,
    CStopVacuum,
    CVentVacuum,
    CStopStir,
    CRotavapStopHeater,
    CRotavapStopRotation
)

from .....graphgen.utils import undirected_neighbors

class Shutdown(AbstractStep):
    """XDL step to enact a Shutdown on the platform.
    Will iterate through all devices which can switch off.

    Inherits:
        AbstractStep
    """
    def __init__(
        self,
        vacuums: List[str] = [],
        heaters: List[str] = [],
        stirrers: List[str] = [],
        rotavaps: List[str] = [],
        chillers: List[str] = [],
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_rotavap_steps(self) -> list:
        stop_rots = [
            CRotavapStopRotation(rot)
            for rot in self.rotavaps
        ]

        stop_heats = [
            CRotavapStopHeater(rot)
            for rot in self.rotavaps
        ]

        lifts = [
            CRotavapLiftUp(rot)
            for rot in self.rotavaps
        ]

        return list(
            chain(stop_rots, stop_heats, lifts)
        )

    def get_stirrer_steps(self) -> list:
        return [
            CStopStir(stir)
            for stir in self.stirrers
        ]

    def get_heater_steps(self) -> list:
        return [
            CStopHeat(heat)
            for heat in self.heaters
        ]

    def get_vacuum_steps(self) -> list:
        steps = []
        for vac in self.vacuums:
            steps.extend([
                CStopVacuum(vac),
                CVentVacuum(vac)
            ])
        return steps

    def get_chiller_steps(self) -> list:
        return [
            CStopChiller(chill)
            for chill in self.chillers
        ]

    def on_prepare_for_execution(self, graph):
        chillers, stirrers, heaters, rotavaps, vacuums = [], [], [], [], []

        for node, data in graph.nodes(data=True):
            vessel = [i for i in undirected_neighbors(graph, node)][0]

            if data["class"] in CHILLER_CLASSES:
                chillers.append(vessel)
            elif data["class"] in HEATER_CLASSES:
                heaters.append(vessel)
            elif data["class"] in STIRRER_CLASSES:
                stirrers.append(vessel)
            elif data["class"] in ROTAVAP_CLASSES:
                rotavaps.append(node)
            elif data["class"] in VACUUM_CLASSES:
                vacuums.append(vessel)

        self.chillers = chillers
        self.rotavaps = rotavaps
        self.vacuums = vacuums
        self.heaters = heaters
        self.stirrers = stirrers

    def get_steps(self) -> list:
        return list(
            chain(
                self.get_rotavap_steps(),
                self.get_stirrer_steps(),
                self.get_heater_steps(),
                self.get_vacuum_steps(),
                self.get_chiller_steps(),
            )
        )
