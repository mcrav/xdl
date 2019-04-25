from typing import Optional, List, Dict, Any
from ..utils import get_vacuum_valve_reconnect_steps
from ..base_step import Step, AbstractStep
from ..steps_utility import (
    StopStir,
    HeatChillToTemp,
    Wait,
    StartVacuum,
    StopVacuum,
    CSetVacuumSetPoint,
)
from ..steps_base import CMove, CConnect, CVentVacuum
from ...constants import (
    BOTTOM_PORT, DEFAULT_DRY_WASTE_VOLUME, DEFAULT_FILTER_VACUUM_PRESSURE)

class Dry(AbstractStep):
    """Dry given vessel by applying vacuum for given time.

    Args:
        filter_vessel (str): Vessel name to dry.
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
    """
    def __init__(
        self,
        filter_vessel: str,
        time: Optional[float] = 'default',
        temp: Optional[float] = None,
        waste_vessel: Optional[str] = None,
        aspiration_speed: Optional[float] = 'default',
        vacuum: Optional[str] = None,
        vacuum_device: Optional[str] = False,
        vacuum_pressure: Optional[float] = 'default',
        inert_gas: Optional[str] = None,
        vacuum_valve: Optional[str] = None,
        valve_unused_port: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        steps = [
            StopStir(vessel=self.filter_vessel),
            # Move bulk of liquid to waste.
            CMove(
                from_vessel=self.filter_vessel,
                from_port=BOTTOM_PORT,
                to_vessel=self.waste_vessel,
                volume=DEFAULT_DRY_WASTE_VOLUME,
                aspiration_speed=self.aspiration_speed),
            StartVacuum(
                vessel=self.vacuum, pressure=self.vacuum_pressure),
            # Connect the vacuum.
            CConnect(from_vessel=self.filter_vessel,
                     to_vessel=self.vacuum,
                     from_port=BOTTOM_PORT),
            Wait(self.time),
        ]

        # If vacuum is just from vacuum line not device remove Start/Stop vacuum
        # steps.
        if not self.vacuum_device:
            steps.pop(-3)

        if self.temp != None:
            steps.insert(0, HeatChillToTemp(
                vessel=self.filter_vessel,
                temp=self.temp,
                vessel_type='ChemputerFilter',
                stir=False))

        steps.extend(get_vacuum_valve_reconnect_steps(
            inert_gas=self.inert_gas,
            vacuum_valve=self.vacuum_valve,
            valve_unused_port=self.valve_unused_port,
            filter_vessel=self.filter_vessel))

        if self.vacuum_device:
            steps.extend([
                StopVacuum(vessel=self.vacuum),
                CVentVacuum(vessel=self.vacuum),
                CSetVacuumSetPoint(
                    vessel=self.vacuum,
                    vacuum_pressure=DEFAULT_FILTER_VACUUM_PRESSURE)
            ])

        return steps

    @property
    def human_readable(self) -> str:
        return 'Dry substance in {filter_vessel} for {time} s.'.format(
            **self.properties)

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'filter_vessel': {
                'filter': True
            }
        }