from typing import Optional
from ...base_steps import AbstractStep
from ..steps_utility import Wait, StartVacuum, StopVacuum
from ..steps_base import CConnect
from ...special_steps import Repeat

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
    def __init__(
        self,
        vessel: str,
        evacuations: int = 'default',
        after_inert_gas_wait_time: Optional[int] = 'default',
        after_vacuum_wait_time: Optional[int] = 'default',
        inert_gas: Optional[str] = None,
        vacuum: Optional[str] = None,
        vacuum_device: Optional[str] = None,
        vacuum_pressure: Optional[float] = 'default',
        vessel_type: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self):
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


    def human_readable(self, language='en'):
        return f'Perform {self.evacuations} evacuations of {self.vessel} with inert gas.'
