from typing import Optional, List
from ..steps_utility.pneumatic_controller import SwitchArgon
from .general import Wait
from ..steps_base import CConnect, CValveMoveToPosition
from .....step_utils.base_steps import AbstractStep
from .....constants import INERT_GAS_SYNONYMS
from .....utils.misc import SanityCheck
from ..steps_utility.cleaning import CleanBackbone
from ...utils.execution import (
    get_vacuum_configuration, get_pneumatic_controller, node_in_graph
)

class StartPurge(AbstractStep):
    def __init__(
        self,
        vessel: str,
        pneumatic_controller: str = None,
        inert_gas: str = None,
        **kwargs,
    ):
        super().__init__(locals())

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=self.pneumatic_controller or self.inert_gas,
                error_msg=f'Cannot find pneumatic controller or inert gas connected to\
 {self.vessel} so cannot purge.'
            )
        ]

    def on_prepare_for_execution(self, graph):
        self.pneumatic_controller = self.inert_gas = None
        self.pneumatic_controller, _ = get_pneumatic_controller(
            graph, self.vessel)
        if not self.pneumatic_controller:
            vacuum_info = get_vacuum_configuration(graph, self.vessel)
            if not self.pneumatic_controller and not self.inert_gas:
                self.inert_gas = vacuum_info['valve_inert_gas']

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

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=self.pneumatic_controller or self.inert_gas,
                error_msg=f'Cannot find pneumatic controller or inert gas connected to\
 {self.vessel} so cannot purge.'
            ),

            SanityCheck(
                condition=node_in_graph(graph, self.vessel),
                error_msg=f'Unable to find {self.vessel} in graph.'
            )
        ]

    def on_prepare_for_execution(self, graph):
        self.pneumatic_controller = self.inert_gas = None
        self.pneumatic_controller, _ = get_pneumatic_controller(
            graph, self.vessel)
        if not self.pneumatic_controller:
            vacuum_info = get_vacuum_configuration(graph, self.vessel)
            if not self.pneumatic_controller:
                if not self.inert_gas:
                    self.inert_gas = vacuum_info['valve_inert_gas']
                if not self.inert_gas_valve:
                    self.inert_gas_valve = vacuum_info['valve']
                if self.inert_gas_valve_unused_port is None:
                    self.inert_gas_valve_unused_port = vacuum_info[
                        'valve_unused_port']

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

    DEFAULT_PROPS = {
        'time': '5 minutes',
    }

    def __init__(
        self,
        vessel: str,
        time: float = 'default',
        **kwargs,
    ):
        super().__init__(locals())

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=node_in_graph(graph, self.vessel),
                error_msg=f'Unable to find {self.vessel} in graph.',
            ),
            SanityCheck(
                condition=self.time > 0,
                error_msg='Purge time must be > 0.'
            )
        ]

    def on_prepare_for_execution(self, graph):
        return

    def get_steps(self):
        return [
            StartPurge(vessel=self.vessel),
            Wait(time=self.time),
            StopPurge(vessel=self.vessel)
        ]

class PurgeBackbone(AbstractStep):

    def __init__(
        self,
        purge_gas: str = None,
        purge_vessel: str = None,
        waste_vessels: Optional[List[str]] = [],
        **kwargs
    ):
        super().__init__(locals())

    def sanity_checks(self, graph):
        checks = [
            SanityCheck(
                condition=self.purge_vessel,
            ),
            SanityCheck(
                condition=node_in_graph(graph, self.purge_vessel)
            )
        ]
        waste_checks = [
            SanityCheck(
                node_in_graph(graph, waste)
                for waste in self.waste_vessels
            )
        ]
        return checks + waste_checks

    def on_prepare_for_execution(self, graph):
        if self.purge_gas is None:
            for node, data in graph.nodes(data=True):
                if (data['class'] == 'ChemputerFlask'
                        and data['chemical'] in INERT_GAS_SYNONYMS):
                    self.purge_gas = data['chemical']
                    break

        elif self.purge_vessel is None:
            for node, data in graph.nodes(data=True):
                if (data['class'] == 'ChemputerFlask'
                        and data['chemical'] == self.purge_gas):
                    self.purge_vessel = node
                    break

    def get_steps(self):
        return [
            CleanBackbone(
                solvent=self.purge_gas,
                waste_vessels=self.waste_vessels,
                solvent_vessel=self.purge_vessel
            )
        ]
