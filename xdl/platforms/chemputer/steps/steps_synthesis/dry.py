from typing import Optional, List, Dict, Any, Union
from .....step_utils.base_steps import Step, AbstractStep
from ..steps_utility.vacuum import ApplyVacuum
from ..steps_utility import (
    StopStir,
    HeatChillToTemp,
)
from ..steps_base import CMove
from ...constants import (
    BOTTOM_PORT,
    DEFAULT_DRY_WASTE_VOLUME,
    CHEMPUTER_WASTE,
)
from .....constants import ROOM_TEMPERATURE
from ...utils.execution import (
    get_nearest_node,
    get_vacuum_configuration,
    get_vessel_stirrer,
    get_vessel_type,
)

class Dry(AbstractStep):
    """Dry given vessel by applying vacuum for given time.

    Args:
        vessel (str): Vessel name to dry.
        time (float): Time to dry vessel for in seconds. (optional)
        temp (float): Temperature to dry at.
        waste_vessel (str): Given internally. Vessel to send waste to.
        vacuum (str): Given internally. Name of vacuum flask.
        vacuum_device (str): Name of actual vacuum device attached to vacuum
            flask. If there is no device (i.e. vacuum line in fumehood) will be
            None.
        vacuum_pressure (float): Pressure in mbar of vacuum. Only applied if
            vacuum_device isn't None.
        inert_gas (str): Given internally. Name of node supplying inert gas.
            Only used if inert gas filter dead volume method is being used.
        vacuum_valve (str): Given internally. Name of valve connecting filter
            bottom to vacuum.
        valve_unused_port (str): Given internally. Random unused position on
            valve.
        vessel_type (str): Given internally. 'reactor', 'filter', 'rotavap',
            'flask' or 'separator'.
        vessel_has_stirrer (bool): Given internally. True if vessel is connected
            to a stirrer.
    """

    DEFAULT_PROPS = {
        'time': '1 hr',
        'aspiration_speed': 5,  # mL / min
        'vacuum_pressure': '400 mbar',
        'continue_heatchill': False,
    }

    PROP_TYPES = {
        'vessel': str,
        'time': float,
        'temp': float,
        'waste_vessel': str,
        'aspiration_speed': float,
        'continue_heatchill': bool,
        'vacuum': str,
        'vacuum_device': str,
        'vacuum_pressure': float,
        'inert_gas': str,
        'vacuum_valve': str,
        'valve_unused_port': Union[str, int],
        'vessel_type': str,
        'vessel_has_stirrer': bool
    }

    INTERNAL_PROPS = [
        'vacuum',
        'vacuum_device',
        'inert_gas',
        'vacuum_valve',
        'valve_unused_port',
        'vessel_type',
        'vessel_has_stirrer',
    ]

    def __init__(
        self,
        vessel: str,
        time: Optional[float] = 'default',
        temp: Optional[float] = None,
        waste_vessel: Optional[str] = None,
        aspiration_speed: Optional[float] = 'default',
        continue_heatchill: Optional[bool] = 'default',

        # Internal properties
        vacuum: Optional[str] = None,
        vacuum_device: Optional[str] = False,
        vacuum_pressure: Optional[float] = 'default',
        inert_gas: Optional[str] = None,
        vacuum_valve: Optional[str] = None,
        valve_unused_port: Optional[Union[str, int]] = None,
        vessel_type: Optional[str] = None,
        vessel_has_stirrer: Optional[bool] = True,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def sanity_checks(self, graph):
        return []

    def on_prepare_for_execution(self, graph):
        if not self.waste_vessel:
            self.waste_vessel = get_nearest_node(
                graph, self.vessel, CHEMPUTER_WASTE)

        if not self.vessel_type:
            self.vessel_type = get_vessel_type(graph, self.vessel)

        if get_vessel_stirrer(graph, self.vessel):
            self.vessel_has_stirrer = True
        else:
            self.vessel_has_stirrer = False

        vacuum_info = get_vacuum_configuration(graph, self.vessel)
        if not self.vacuum:
            self.vacuum = vacuum_info['source']
        if not self.inert_gas:
            self.inert_gas = vacuum_info['valve_inert_gas']
        if not self.vacuum_valve:
            self.vacuum_valve = vacuum_info['valve']
        if not self.valve_unused_port:
            self.valve_unused_port = vacuum_info['valve_unused_port']
        if not self.vacuum_device:
            self.vacuum_device = vacuum_info['device']

    def get_steps(self) -> List[Step]:
        return (
            self.get_start_heatchill_steps()
            + self.get_stop_stir_steps()
            + self.get_move_steps()
            + self.get_apply_vacuum_steps()
            + self.get_end_heatchill_steps()
        )

    def get_start_heatchill_steps(self):
        return ([
            HeatChillToTemp(
                vessel=self.vessel,
                temp=self.temp,
                stir=False
            )
        ] if self.temp is not None else [])

    def get_stop_stir_steps(self):
        return (
            [StopStir(vessel=self.vessel)]
            if self.vessel_has_stirrer or self.vessel_type == 'rotavap'
            else []
        )

    def get_move_steps(self):
        from_port = BOTTOM_PORT if self.vessel_type == 'filter' else None
        return ([
            CMove(
                from_vessel=self.vessel,
                from_port=from_port,
                to_vessel=self.waste_vessel,
                volume=DEFAULT_DRY_WASTE_VOLUME,
                aspiration_speed=self.aspiration_speed,
            )
        ] if self.vessel_type == 'filter' else [])

    def get_apply_vacuum_steps(self):
        port = BOTTOM_PORT if self.vessel_type == 'filter' else None
        return [
            ApplyVacuum(
                vessel=self.vessel,
                time=self.time,
                port=port
            )
        ]

    def get_end_heatchill_steps(self):
        return ([
            HeatChillToTemp(
                vessel=self.vessel,
                temp=ROOM_TEMPERATURE,
                continue_heatchill=False,
                stir=False
            )
        ] if self.temp and not self.continue_heatchill else [])

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'temp': [item for item in [self.temp] if item is not None],
            }
        }
