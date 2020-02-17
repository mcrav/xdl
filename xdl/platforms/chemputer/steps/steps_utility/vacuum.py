from typing import List
from .....step_utils.base_steps import Step, AbstractStep
from ..steps_base import (
    CStartVacuum,
    CStopVacuum,
    CSetVacuumSetPoint,
    CConnect,
    CValveMoveToPosition,
    CVentVacuum
)
from .pneumatic_controller import SwitchArgon, SwitchVacuum
from .general import Wait
from ...utils.execution import (
    get_pneumatic_controller,
    get_vacuum_configuration,
)
from .....utils.misc import SanityCheck

class StartVacuum(AbstractStep):
    """Start vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to start vacuum on.
    """

    DEFAULT_PROPS = {
        'pressure': '400 mbar',
    }

    def __init__(
        self, vessel: str, pressure: float = 'default', **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [
            CSetVacuumSetPoint(
                vessel=self.vessel, vacuum_pressure=self.pressure),
            CStartVacuum(vessel=self.vessel)
        ]

class StopVacuum(AbstractStep):
    """Stop vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to stop vacuum on.
    """
    def __init__(self, vessel: str, **kwargs) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [CStopVacuum(vessel=self.vessel)]

class ApplyVacuum(AbstractStep):
    """Apply vacuum to given vessel for given amount of time.
    Assumes one of following hardware setups:
        (Optional CVC3000) -> ChemputerVacuum <- ChemputerValve <-> vessel
        OR
        pneumatic_controller <-> vessel
    """

    DEFAULT_PROPS = {
        'pressure': '400 mbar',
    }

    INTERNAL_PROPS = [
        'vacuum_valve',
        'vacuum_source',
        'vacuum_device',
        'vacuum_valve_inert_gas',
        'vacuum_valve_unused_port',
        'pneumatic_controller'
    ]

    def __init__(
        self,
        vessel: str,
        time: float,
        pressure: float = 'default',
        port: str = None,

        # Internal properties
        vacuum_valve: str = None,
        vacuum_source: str = None,
        vacuum_device: str = None,
        vacuum_valve_inert_gas: str = None,
        vacuum_valve_unused_port: str = None,
        pneumatic_controller: str = None,
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        self.pneumatic_controller, _ = get_pneumatic_controller(
            graph, self.vessel)
        if not self.pneumatic_controller:
            vacuum_info = get_vacuum_configuration(graph, self.vessel)
            self.vacuum_valve = vacuum_info['valve']
            self.vacuum_source = vacuum_info['source']
            self.vacuum_device = vacuum_info['device']
            self.vacuum_valve_inert_gas_ = vacuum_info['valve_inert_gas']
            self.vacuum_valve_unused_port = vacuum_info['valve_unused_port']

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=self.vessel in graph.nodes(),
                error_msg=f'vessel {self.vessel} not found in graph.',
            ),

            SanityCheck(
                condition=(
                    self.pneumatic_controller
                    or (self.vacuum_valve and self.vacuum_source)
                ),
                error_msg=f'Neither of valid hardware setups found.\n\
 Option 1: vessel <-> pneumatic controller\n\
 Option 2: vessel <-> valve -> vacuum <- (Optional vacuum device)',
            ),

            SanityCheck(
                condition=(
                    self.pneumatic_controller
                    or (self.vacuum_valve_inert_gas is not None
                        or self.vacuum_valve_unused_port is not None)
                ),
                error_msg=f'Using vacuum valve, but cannot find inert gas or an unused\
 port to connect to after applying vacuum.',
            ),

            SanityCheck(
                condition=self.time > 0,
                error_msg=f'time property must be > 0',
            )
        ]

    def get_steps(self) -> List[Step]:
        if self.pneumatic_controller:
            return self.get_pneumatic_controller_steps()

        else:
            return self.get_vacuum_valve_steps()

    def get_pneumatic_controller_steps(self):
        return [
            SwitchVacuum(self.vessel),
            Wait(self.time),
            SwitchArgon(self.vessel, pressure='low'),
        ]

    def get_vacuum_valve_steps(self):
        return (
            self.get_start_vacuum_step()
            + self.get_connect_vacuum_step()
            + self.get_wait_step()
            + self.get_vacuum_valve_reconnect_step()
            + self.get_stop_vacuum_step()
            + self.get_vent_vacuum_step()
        )

    def get_start_vacuum_step(self):
        if self.vacuum_device:
            return [
                StartVacuum(
                    vessel=self.vacuum_source,
                    pressure=self.pressure
                )
            ]
        return []

    def get_connect_vacuum_step(self):
        return [
            CConnect(
                from_vessel=self.vessel,
                to_vessel=self.vacuum_source,
                from_port=self.port
            )
        ]

    def get_wait_step(self):
        return [
            Wait(self.time),
        ]

    def get_vacuum_valve_reconnect_step(self):
        if self.vacuum_valve_inert_gas:
            return [
                CConnect(
                    from_vessel=self.vacuum_valve_inert_gas,
                    to_vessel=self.vessel
                )
            ]
        elif self.vacuum_valve_unused_port is not None:
            return [
                CValveMoveToPosition(
                    valve_name=self.vacuum_valve,
                    position=self.vacuum_valve_unused_port
                )
            ]
        return []

    def get_stop_vacuum_step(self):
        if self.vacuum_device:
            return [
                StopVacuum(vessel=self.vacuum_source)
            ]
        return []

    def get_vent_vacuum_step(self):
        if self.vacuum_device:
            return [
                CVentVacuum(vessel=self.vacuum_source)
            ]
        return []
