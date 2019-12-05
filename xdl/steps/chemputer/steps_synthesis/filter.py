from typing import Optional, List, Dict, Any, Union
from ..utils import get_vacuum_valve_reconnect_steps
from ...base_steps import Step, AbstractStep
from ..steps_base import CMove, CConnect, CVentVacuum
from ..steps_utility import (
    StopStir, StartStir, Wait, StartVacuum, StopVacuum, Transfer)
from ....constants import (
    BOTTOM_PORT,
    DEFAULT_FILTER_EXCESS_REMOVE_FACTOR,
    DEFAULT_FILTER_VACUUM_PRESSURE,
    DEFAULT_FILTER_ANTICLOGGING_ASPIRATION_SPEED,
)
from ....utils.errors import XDLError

class Filter(AbstractStep):
    """Filter contents of filter vessel. Apply vacuum for given time.
    Assumes liquid is already in the top of the filter vessel.

    Args:
        filter_vessel (str): Filter vessel.
        filter_top_volume (float): Volume (mL) of contents of filter top.
        wait_time (float): Time to leave vacuum on filter vessel after contents
            have been moved. (optional)
        aspiration_speed (float): Speed in mL / min to draw liquid from
            filter_vessel.
        stir (bool): True to stir, False to stop stirring.
        stir_speed (float): Speed to stir at in RPM.
        waste_vessel (float): Given internally. Vessel to move waste material to.
        filtrate_vessel (str): Optional. Vessel to send filtrate to. Defaults to
            waste_vessel.
        vacuum (str): Given internally. Name of vacuum flask.
        vacuum_device (str): Given internally. Name of vacuum device attached to
            vacuum flask. Can be None if vacuum is just from fumehood vacuum
            line.
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
        filter_top_volume: Optional[float] = 0,
        wait_time: Optional[float] = 'default',
        aspiration_speed: Optional[float] = 'default',
        stir: Optional[bool] = 'default',
        stir_speed: Optional[float] = 'default',
        waste_vessel: Optional[str] = None,
        filtrate_vessel: Optional[str] = None,
        vacuum: Optional[str] = None,
        vacuum_device: Optional[str] = None,
        inert_gas: Optional[str] = None,
        vacuum_valve: Optional[str] = None,
        valve_unused_port: Optional[Union[str, int]] = None,
        anticlogging: Optional[bool] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        filtrate_vessel = self.filtrate_vessel
        if not filtrate_vessel:
            filtrate_vessel = self.waste_vessel

        aspiration_speed = self.aspiration_speed
        if self.anticlogging:
            aspiration_speed = DEFAULT_FILTER_ANTICLOGGING_ASPIRATION_SPEED

        steps = [
            # Move the filter top volume from the bottom to the waste.
            CMove(
                from_vessel=self.filter_vessel,
                to_vessel=filtrate_vessel,
                from_port=BOTTOM_PORT,
                volume=(self.filter_top_volume
                        * DEFAULT_FILTER_EXCESS_REMOVE_FACTOR),
                aspiration_speed=aspiration_speed),
            StartVacuum(
                vessel=self.vacuum, pressure=DEFAULT_FILTER_VACUUM_PRESSURE),
            # Connect the vacuum.
            CConnect(from_vessel=self.filter_vessel, to_vessel=self.vacuum,
                     from_port=BOTTOM_PORT),
            Wait(time=self.wait_time),
        ]

        if not self.stir:
            steps.insert(0, StopStir(vessel=self.filter_vessel))
        else:
            steps.insert(1, StopStir(vessel=self.filter_vessel))
            steps.insert(0, StartStir(
                vessel=self.filter_vessel, stir_speed=self.stir_speed))

        # If vacuum is just from vacuum line not device remove Start/Stop vacuum
        # steps.
        if not self.vacuum_device:
            steps.pop(-3)

        # Reconnect vacuum valve to inert gas or unconnected port after done
        # with vacuum.
        steps.extend(get_vacuum_valve_reconnect_steps(
            inert_gas=self.inert_gas,
            vacuum_valve=self.vacuum_valve,
            valve_unused_port=self.valve_unused_port,
            vessel=self.filter_vessel))

        if self.vacuum_device:
            steps.extend([
                StopVacuum(vessel=self.vacuum),
                CVentVacuum(vessel=self.vacuum)])
        return steps

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'filter_vessel': {
                'filter': True
            }
        }

    def syntext(self) -> str:
        s = 'The reaction mixture was filtered.'
        return s


class FilterTo(AbstractStep):
    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
    ):
        super().__init__(locals())

    def get_steps(self):
        return [
            Transfer(
                from_vessel=self.from_vessel,
                to_vessel=self.to_vessel,
                volume='all',
            )
        ]

    def final_sanity_check(self, graph):
        try:
            full_node = graph.node[self.from_vessel]
            assert 'can_filter' in full_node and full_node['can_filter']
        except AssertionError:
            raise XDLError(f"from_vessel ({self.from_vessel}) doesn't have can_filter property == True")

        try:
            assert self.from_vessel != self.to_vessel
        except AssertionError:
            raise XDLError(f"from_vessel and to_vessel can't be the same node ({self.from_vessel}).")
