from typing import Optional
from .utils import get_vacuum_valve_reconnect_steps
from ..base_step import Step
from ..steps_utility import (
    StopStir, HeatChillToTemp, Wait, StartVacuum, StopVacuum)
from ..steps_base import CMove, CConnect, CVentVacuum
from ...constants import (
    BOTTOM_PORT, DEFAULT_DRY_WASTE_VOLUME, DEFAULT_FILTER_VACUUM_PRESSURE)

class Dry(Step):
    """Dry given vessel by applying vacuum for given time.

    Args:
        filter_vessel (str): Vessel name to dry.
        time (float): Time to dry vessel for in seconds. (optional)
        temp (float): Temperature to dry at.
        waste_vessel (str): Given internally. Vessel to send waste to.
        vacuum (str): Given internally. Vacuum flask.
        inert_gas (str): Given internally. Name of node supplying inert gas.
            Only used if inert gas filter dead volume method is being used.
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
        inert_gas: Optional[str] = None,
        vacuum_valve: Optional[str] = None,
        valve_unused_port: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            StopStir(vessel=self.filter_vessel),
            # Move bulk of liquid to waste.
            CMove(
                from_vessel=self.filter_vessel,
                from_port=BOTTOM_PORT,
                to_vessel=self.waste_vessel,
                volume=DEFAULT_DRY_WASTE_VOLUME,
                aspiration_speed=self.aspiration_speed),
            StartVacuum(
                vessel=self.vacuum, pressure=DEFAULT_FILTER_VACUUM_PRESSURE),
            # Connect the vacuum.
            CConnect(from_vessel=self.filter_vessel, to_vessel=self.vacuum,
                     from_port=BOTTOM_PORT),
            Wait(self.time),
            StopVacuum(vessel=self.vacuum),
            CVentVacuum(vessel=self.vacuum),
        ]

        # If vacuum is just from vacuum line not device remove Start/Stop vacuum
        # steps.
        if not self.vacuum_device:
            self.steps.pop()
            self.steps.pop()
            self.steps.pop(-3)

        if self.temp != None:
            self.steps.insert(0, HeatChillToTemp(
                vessel=self.filter_vessel,
                temp=self.temp,
                vessel_type='ChemputerFilter'))

        self.steps.extend(get_vacuum_valve_reconnect_steps(
            inert_gas=self.inert_gas,
            vacuum_valve=self.vacuum_valve,
            valve_unused_port=self.valve_unused_port,
            filter_vessel=self.filter_vessel))

        self.human_readable = 'Dry substance in {filter_vessel} for {time} s.'.format(
            **self.properties)

        self.requirements = {
            'filter_vessel': {
                'filter': True
            }
        }
