from typing import Optional, List, Dict, Any, Union

from ..utils import get_vacuum_valve_reconnect_steps
from .....step_utils.base_steps import AbstractStep, Step
from ..base_step import ChemputerStep
from ..steps_base import CMove
from ...constants import BOTTOM_PORT, CHEMPUTER_WASTE
from ...utils.execution import (
    get_nearest_node, get_reagent_vessel, get_vacuum_configuration)

class AddFilterDeadVolume(ChemputerStep, AbstractStep):
    """Fill bottom of filter vessel with solvent in anticipation of the filter
    top being used.

    Args:
        filter_vessel (str): Filter vessel to fill dead volume with solvent.
        solvent (str): Solvent to fill filter bottom with.
        volume (int): Volume of filter bottom.
        waste_vessel (str): Given internally. Vessel to put waste material.
        solvent_vessel (str): Given internally. Vessel to take solvent from.
        vacuum (str): Given internally. Name of vacuum flask.
        inert_gas (str): Given internally. Name of node supplying inert gas.
            Only used if inert gas filter dead volume method is being used.
        vacuum_valve (str): Given internally. Name of valve connecting filter
            bottom to vacuum.
        valve_unused_port (str): Given internally. Random unused position on
            valve.
    """

    INTERNAL_PROPS = [
        'waste_vessel',
        'solvent_vessel',
        'vacuum',
        'inert_gas',
        'vacuum_valve',
        'valve_unused_port',
    ]

    PROP_TYPES = {
        'filter_vessel': str,
        'solvent': str,
        'volume': float,
        'waste_vessel': str,
        'solvent_vessel': str,
        'vacuum': str,
        'inert_gas': str,
        'vacuum_valve': str,
        'valve_unused_port': Union[str, int]
    }

    DO_NOT_SCALE = True

    def __init__(
        self,
        filter_vessel: str,
        solvent: str,
        volume: float,

        # Internal properties
        waste_vessel: Optional[str] = None,
        solvent_vessel: Optional[str] = None,
        vacuum: Optional[str] = None,
        inert_gas: Optional[str] = None,
        vacuum_valve: Optional[str] = None,
        valve_unused_port: Optional[Union[str, int]] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.waste_vessel:
            self.waste_vessel = get_nearest_node(
                graph, self.filter_vessel, CHEMPUTER_WASTE)

        if not self.solvent_vessel:
            self.solvent_vessel = get_reagent_vessel(graph, self.solvent)

        vacuum_info = get_vacuum_configuration(graph, self.filter_vessel)
        if not self.vacuum:
            self.vacuum = vacuum_info['source']
        if not self.inert_gas:
            self.inert_gas = vacuum_info['valve_inert_gas']
        if not self.vacuum_valve:
            self.vacuum_valve = vacuum_info['valve']
        if not self.valve_unused_port:
            self.valve_unused_port = vacuum_info['valve_unused_port']

    def get_steps(self) -> List[Step]:
        steps = [CMove(from_vessel=self.solvent_vessel,
                       volume=self.volume,
                       to_vessel=self.filter_vessel,
                       to_port=BOTTOM_PORT)]
        # Reconnect vacuum valve to inert gas or unconnected port after done
        steps.extend(get_vacuum_valve_reconnect_steps(
            inert_gas=None,
            vacuum_valve=self.vacuum_valve,
            valve_unused_port=self.valve_unused_port,
            vessel=self.filter_vessel))
        return steps

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'filter_vessel': {
                'filter': True,
            }
        }

class RemoveFilterDeadVolume(ChemputerStep, AbstractStep):
    """Remove dead volume (volume below filter) from filter vessel.

    Args:
        filter_vessel (str): Filter vessel to remove dead volume from.
        dead_volume (float): Volume in mL to remove from bottom of filter
            vessel.
        waste_vessel (str): Given internally. Waste vessel to send solvent to.
        vacuum (str): Given internally. Name of vacuum flask.
        inert_gas (str): Given internally. Name of node supplying inert gas.
            Only used if inert gas filter dead volume method is being used.
        vacuum_valve (str): Given internally. Name of valve connecting filter
            bottom to vacuum.
        valve_unused_port (str): Given internally. Random unused position on
            valve.
    """

    INTERNAL_PROPS = [
        'waste_vessel',
        'vacuum',
        'vacuum_valve',
        'valve_unused_port'
    ]

    PROP_TYPES = {
        'filter_vessel': str,
        'dead_volume': float,
        'waste_vessel': str,
        'vacuum': str,
        'vacuum_valve': str,
        'valve_unused_port': Union[str, int]
    }

    DO_NOT_SCALE = True

    def __init__(
        self,
        filter_vessel: str,
        dead_volume: Optional[float] = 0,

        # Internal properties
        waste_vessel: Optional[str] = None,
        vacuum: Optional[str] = None,
        vacuum_valve: Optional[str] = None,
        valve_unused_port: Optional[Union[str, int]] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        self.waste_vessel = get_nearest_node(
            graph, self.filter_vessel, CHEMPUTER_WASTE)

        vacuum_info = get_vacuum_configuration(graph, self.filter_vessel)
        if not self.vacuum:
            self.vacuum = vacuum_info['source']
        if not self.vacuum_valve:
            self.vacuum_valve = vacuum_info['valve']
        if not self.valve_unused_port:
            self.valve_unused_port = vacuum_info['valve_unused_port']

    def get_steps(self) -> List[Step]:
        steps = [CMove(from_vessel=self.filter_vessel,
                       from_port=BOTTOM_PORT,
                       to_vessel=self.waste_vessel,
                       volume=self.dead_volume)]
        # Reconnect vacuum valve to inert gas or unconnected port after done
        steps.extend(get_vacuum_valve_reconnect_steps(
            inert_gas=None,
            vacuum_valve=self.vacuum_valve,
            valve_unused_port=self.valve_unused_port,
            vessel=self.filter_vessel))
        return steps

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'filter_vessel': {
                'filter': True,
            }
        }
