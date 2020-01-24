from ..steps_utility.pneumatic_controller import SwitchArgon
from .general import Wait
from ..steps_base import CConnect, CValveMoveToPosition
from ...utils.execution import get_unused_valve_port
from .....step_utils.base_steps import AbstractStep
from .....utils.graph import undirected_neighbors
from .....constants import INERT_GAS_SYNONYMS

def get_pneumatic_controller(graph, vessel):
    for node, data in undirected_neighbors(graph, vessel, data=True):
        if data['class'] == 'PneumaticController':
            return node
    return None

def get_inert_gas(graph, vessel):
    for node, data in undirected_neighbors(graph, vessel, data=True):
        if data['class'] == 'ChemputerValve':
            for valve_node, valve_data in undirected_neighbors(
                    graph, node, data=True):
                if (valve_data['class'] == 'ChemputerFlask'
                        and valve_data['chemical'] in INERT_GAS_SYNONYMS):
                    return node, valve_node
    return None, None

def assert_node_in_graph(graph, node):
    assert node in list(graph.nodes())

class StartPurge(AbstractStep):
    def __init__(
        self,
        vessel: str,
        pneumatic_controller: str = None,
        inert_gas: str = None,
        **kwargs,
    ):
        super().__init__(locals())

    def final_sanity_check(self, graph):
        assert self.pneumatic_controller or self.inert_gas

    def on_prepare_for_execution(self, graph):
        self.pneumatic_controller = self.inert_gas = None
        self.pneumatic_controller = get_pneumatic_controller(graph, self.vessel)
        if not self.pneumatic_controller:
            _, self.inert_gas = get_inert_gas(graph, self.vessel)

    def get_steps(self):
        if self.pneumatic_controller:
            return [
                SwitchArgon(
                    vessel=self.vessel,
                    pressure='high',
                    after_switch_wait=None,
                ),
            ]
        elif self.inert_gas:
            return [
                CConnect(
                    from_vessel=self.inert_gas,
                    to_vessel=self.vessel,
                ),
            ]
        else:
            return []

class StopPurge(AbstractStep):
    def __init__(
        self,
        vessel: str,
        pneumatic_controller: str = None,
        inert_gas: str = None,
        inert_gas_valve: str = None,
        inert_gas_valve_unused_port: str = None,
        **kwargs,
    ):
        super().__init__(locals())

    def final_sanity_check(self, graph):
        assert self.pneumatic_controller or self.inert_gas
        assert_node_in_graph(graph, self.vessel)

    def on_prepare_for_execution(self, graph):
        self.pneumatic_controller = self.inert_gas = None
        self.pneumatic_controller = get_pneumatic_controller(graph, self.vessel)
        if not self.pneumatic_controller:
            self.inert_gas_valve, self.inert_gas = get_inert_gas(
                graph, self.vessel)
            if self.inert_gas:
                self.inert_gas_valve_unused_port =\
                    get_unused_valve_port(
                        graph, self.inert_gas_valve)

    def get_steps(self):
        if self.pneumatic_controller:
            return [
                SwitchArgon(
                    vessel=self.vessel,
                    pressure='low',
                    after_switch_wait=None,
                )
            ]
        elif self.inert_gas:
            return [
                CValveMoveToPosition(
                    valve_name=self.inert_gas_valve,
                    position=self.inert_gas_valve_unused_port
                )
            ]
        else:
            return []

class Purge(AbstractStep):
    def __init__(
        self,
        vessel: str,
        time: float = 'default',
        **kwargs,
    ):
        super().__init__(locals())

    def final_sanity_check(self, graph):
        assert_node_in_graph(graph, self.vessel)
        assert self.time >= 0

    def on_prepare_for_execution(self, graph):
        return

    def get_steps(self):
        return [
            StartPurge(vessel=self.vessel),
            Wait(time=self.time),
            StopPurge(vessel=self.vessel)
        ]
