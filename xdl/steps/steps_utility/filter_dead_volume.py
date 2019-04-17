from typing import Optional

from ..utils import get_vacuum_valve_reconnect_steps
from ..base_step import Step
from ..steps_base import CMove, CValveMoveToPosition
from ...constants import BOTTOM_PORT

class AddFilterDeadVolume(Step):
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
    def __init__(
        self,
        filter_vessel: str,
        solvent: str,
        volume: float, 
        waste_vessel: Optional[str] = None,
        solvent_vessel: Optional[str] = None,
        vacuum: Optional[str] = None,
        inert_gas: Optional[str] = None,
        vacuum_valve: Optional[str] = None,
        valve_unused_port: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            CMove(from_vessel=self.solvent_vessel, volume=self.volume,
                to_vessel=self.filter_vessel, to_port=BOTTOM_PORT)
        ]

        # Reconnect vacuum valve to inert gas or unconnected port after done
        self.steps.extend(get_vacuum_valve_reconnect_steps(
            inert_gas=self.inert_gas,
            vacuum_valve=self.vacuum_valve,
            valve_unused_port=self.valve_unused_port,
            filter_vessel=self.filter_vessel))

        self.human_readable = 'Fill bottom of {filter_vessel} with {solvent} ({volume} mL).'.format(
            **self.properties)

        self.requirements = {
            'filter_vessel': {
                'filter': True
            }
        }

class RemoveFilterDeadVolume(Step):
    """Remove dead volume (volume below filter) from filter vessel.
    
    Args:
        filter_vessel (str): Filter vessel to remove dead volume from.
        dead_volume (float): Volume in mL to remove from bottom of filter vessel.
        waste_vessel (str): Given internally. Waste vessel to send solvent to.
        vacuum (str): Given internally. Name of vacuum flask.
        inert_gas (str): Given internally. Name of node supplying inert gas.
            Only used if inert gas filter dead volume method is being used.
        vacuum_valve (str): Given internally. Name of valve connecting filter
            bottom to vacuum.
        valve_unused_port (str): Given internally. Random unused position on
            valve.
    """
    def __init__(
        self,
        filter_vessel: str,
        dead_volume: Optional[float] = 0,
        waste_vessel: Optional[str] = None,
        vacuum: Optional[str] = None,
        vacuum_valve: Optional[str] = None,
        valve_unused_port: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            CMove(from_vessel=self.filter_vessel, from_port=BOTTOM_PORT,
                  to_vessel=self.waste_vessel, volume=self.dead_volume)
        ]

        if self.vacuum_valve and self.valve_unused_port != None:
            self.steps.append(
                CValveMoveToPosition(valve_name=self.vacuum_valve,
                                     position=self.valve_unused_port))

        self.human_readable = 'Remove dead volume ({dead_volume} mL) from bottom of {filter_vessel}'.format(
            **self.properties)
