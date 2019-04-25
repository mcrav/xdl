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
        vessel_is_filter (bool): Given internally. True if vessel is a filter,
            otherwise False. Determines drying method.
        vessel_is_rotavap (bool): Given internally. True if vessel is a rotavap,
            otherwise False.
        vessel_has_stirrer (bool): Given internally. True if vessel is connected
            to a stirrer.
    """
    def __init__(
        self,
        vessel: str,
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
        vessel_is_filter: Optional[bool] = True,
        vessel_is_rotavap: Optional[bool] = False,
        vessel_has_stirrer: Optional[bool] = True,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        steps = []
        if self.vessel_has_stirrer or self.vessel_is_rotavap:
            steps.append(StopStir(vessel=self.vessel))
        # Normally vacuum is a vacuum flask, but in the case of the rotavap,
        # the node attached to the vacuum is the rotavap itself.
        vacuum_vessel = self.vacuum
        from_port = None
        if self.vessel_is_rotavap:
            vacuum_vessel = self.vessel
            from_port='collect'
        # from_port should be None unless drying is in a filter in which case
        # use bottom port, or for a rotavap port 'collect' is used.
        if self.vessel_is_filter:
            from_port = BOTTOM_PORT
            
        steps.extend([
            # Move bulk of liquid to waste.
            CMove(from_vessel=self.vessel,
                  from_port=from_port,
                  to_vessel=self.waste_vessel,
                  volume=DEFAULT_DRY_WASTE_VOLUME,
                  aspiration_speed=self.aspiration_speed),

            StartVacuum(vessel=vacuum_vessel, pressure=self.vacuum_pressure),
            # Connect the vacuum.
        ])
        # If using rotavap CConnect not needed.
        if vacuum_vessel != self.vessel:
            steps.append(
                CConnect(from_vessel=self.vessel,
                        to_vessel=vacuum_vessel,
                        from_port=from_port))

        steps.append(Wait(self.time))
        
        # If vacuum is just from vacuum line not device remove Start/Stop vacuum
        # steps.
        if not self.vacuum_device:
            steps.pop(-3)

        if self.temp != None:
            steps.insert(0, HeatChillToTemp(
                vessel=self.vessel,
                temp=self.temp,
                vessel_type='ChemputerFilter',
                stir=False))

        if not self.vessel_is_rotavap:
            steps.extend(get_vacuum_valve_reconnect_steps(
                inert_gas=self.inert_gas,
                vacuum_valve=self.vacuum_valve,
                valve_unused_port=self.valve_unused_port,
                vessel=self.vessel))

        if self.vacuum_device:
            steps.extend([
                StopVacuum(vessel=vacuum_vessel),
                CVentVacuum(vessel=vacuum_vessel),
                CSetVacuumSetPoint(
                    vessel=vacuum_vessel,
                    vacuum_pressure=DEFAULT_FILTER_VACUUM_PRESSURE)
            ])

        return steps

    @property
    def human_readable(self) -> str:
        return 'Dry substance in {vessel} for {time} s.'.format(
            **self.properties)
