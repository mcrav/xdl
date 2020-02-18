from typing import Optional
from .....step_utils.base_steps import AbstractStep
from ..steps_utility import (
    Wait, StartVacuum, StopVacuum, SwitchArgon, SwitchVacuum)
from ..steps_base import CConnect
from .....step_utils.special_steps import Repeat
from ...utils.execution import (
    get_pneumatic_controller, get_vacuum_configuration, get_vessel_type)
from .....utils.misc import SanityCheck

class Evacuate(AbstractStep):
    """Evacuate given vessel with inert gas.

    Args:
        vessel (str): Vessel to evacuate with inert gas.
        evacuations (int): Number of evacuations to perform. Defaults to 3.
        after_inert_gas_wait_time (int): Time to wait for after connecting to
            inert gas. Defaults to 1 min.
        after_vacuum_wait_time (int): Time to wait for after connecting to
            vacuum. Defaults to 1 min.
        inert_gas (str): Internal property. Inert gas flask.
        vacuum (str): Internal property. Valve connected to vacuum.
    """

    DEFAULT_PROPS = {
        'after_inert_gas_wait_time': '1 minute',
        'after_vacuum_wait_time': '1 minute',
        'evacuations': 3,
        'vacuum_pressure': '50 mbar',
    }

    INTERNAL_PROPS = [
        'inert_gas',
        'vacuum',
        'vacuum_device',
        'vessel_type',
        'pneumatic_controller',
    ]

    PROP_TYPES = {
        'vessel': str,
        'evacuations': int,
        'after_inert_gas_wait_time': float,
        'after_vacuum_wait_time': float,
        'vacuum_pressure': float,
        'inert_gas': str,
        'vacuum': str,
        'vacuum_device': str,
        'vessel_type': str,
        'pneumatic_controller': str
    }

    def __init__(
        self,
        vessel: str,
        evacuations: int = 'default',
        after_inert_gas_wait_time: Optional[float] = 'default',
        after_vacuum_wait_time: Optional[float] = 'default',
        vacuum_pressure: Optional[float] = 'default',

        # Internal properties
        inert_gas: Optional[str] = None,
        vacuum: Optional[str] = None,
        vacuum_device: Optional[str] = None,
        vessel_type: Optional[str] = None,
        pneumatic_controller: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        self.pneumatic_controller, _ = get_pneumatic_controller(
            graph, self.vessel)

        if not self.vessel_type:
            self.vessel_type = get_vessel_type(graph, self.vessel)

        vacuum_info = get_vacuum_configuration(graph, self.vessel)
        if not self.vacuum:
            self.vacuum = vacuum_info['source']
        if not self.vacuum_device:
            self.vacuum_device = vacuum_info['device']
        if not self.inert_gas:
            self.inert_gas = vacuum_info['valve_inert_gas']

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                self.pneumatic_controller or (self.vacuum and self.inert_gas),
                f'Cannot find pneumatic controller or vacuum and inert gas\
 connected to {self.vessel}. No way to perform evacuation.',
            ),
        ]

    def get_steps(self):
        if self.pneumatic_controller:
            return self.get_pneumatic_controller_steps()
        elif self.vacuum and self.inert_gas:
            return self.get_vacuum_inert_gas_valve_steps()
        else:
            return []

    def get_vacuum_inert_gas_valve_steps(self):
        vacuum_vessel = self.vacuum
        if self.vessel_type == 'rotavap':
            vacuum_vessel = self.vessel

        if self.vacuum_device:
            steps = [
                StartVacuum(
                    vessel=vacuum_vessel, pressure=self.vacuum_pressure),

                CConnect(self.vessel, self.vacuum),
                Wait(self.after_vacuum_wait_time * 2),
                CConnect(self.inert_gas, self.vessel),
                Wait(self.after_inert_gas_wait_time),

                Repeat(
                    repeats=self.evacuations - 1,
                    children=[
                        CConnect(self.vessel, self.vacuum),
                        Wait(self.after_vacuum_wait_time),
                        CConnect(self.inert_gas, self.vessel),
                        Wait(self.after_inert_gas_wait_time),
                    ]
                ),
                StopVacuum(vessel=vacuum_vessel)
            ]
        else:
            steps = [
                Repeat(
                    repeats=self.evacuations,
                    children=[
                        CConnect(self.vessel, self.vacuum),
                        Wait(self.after_vacuum_wait_time),
                        CConnect(self.inert_gas, self.vessel),
                        Wait(self.after_inert_gas_wait_time),
                    ]
                )
            ]

        return steps

    def get_pneumatic_controller_steps(self):
        steps = [
            Repeat(
                repeats=self.evacuations,
                children=[
                    SwitchVacuum(
                        vessel=self.vessel,
                        after_switch_wait=self.after_vacuum_wait_time
                    ),
                    SwitchArgon(
                        vessel=self.vessel,
                        pressure='high',
                        after_switch_wait=self.after_inert_gas_wait_time
                    )
                ]
            ),
            SwitchArgon(
                vessel=self.vessel,
                pressure='low',
            ),
        ]
        return steps

    def human_readable(self, language='en'):
        return f'Perform {self.evacuations} evacuations of {self.vessel} with\
 inert gas.'
