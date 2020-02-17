from typing import Optional, Union, List, Dict, Any
from .....step_utils.base_steps import Step, AbstractStep
from .add import Add
from ..utils import get_vacuum_valve_reconnect_steps
from .....localisation import HUMAN_READABLE_STEPS
from ..steps_utility import (
    Wait,
    StartStir,
    StopStir,
    StartVacuum,
    StopVacuum,
    Stir,
    Transfer,
    HeatChillToTemp,
    StopHeatChill,
)
from ..steps_base import CMove, CConnect, CVentVacuum
from .....constants import (
    BOTTOM_PORT,
    TOP_PORT,
    DEFAULT_FILTER_EXCESS_REMOVE_FACTOR,
    DEFAULT_FILTER_VACUUM_PRESSURE,
    DEFAULT_FILTER_ANTICLOGGING_ASPIRATION_SPEED,
    CHEMPUTER_WASTE,
)
from ...utils.execution import get_nearest_node

class WashSolid(AbstractStep):
    """Wash filter cake with given volume of given solvent.

    Args:
        vessel (str): Vessel containing contents to wash.
        solvent (str): Solvent to wash with.
        volume (float): Volume of solvent to wash with.
        temp (float): Optional. Temperature to perform wash at.
        vacuum_time (float): Time to wait after vacuum connected.
        stir (Union[float, str]): True, 'solvent' or False. True means stir from
            the start until the solvent has been removed. 'solvent' means stir
            after the solvent has been added and stop before it is removed.
            False means don't stir.
        stir_time (float): Time to stir for after solvent has been added. Only
            relevant if stir is True or 'solvent'.
        stir_speed (float): Speed to stir at in RPM. Only relevant if stir is
            True or 'solvent'.
        waste_vessel (str): Given internally. Vessel to send waste to.
        filtrate_vessel (str): Optional. Vessel to send filtrate to. Defaults to
            waste_vessel.
        aspiration_speed (float): Speed to remove solvent from filter_vessel.
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
        vessel_type (str): Given internally. 'reactor', 'filter', 'rotavap',
            'flask' or 'separator'.
        filter_dead_volume (float): Given internally. Dead volume of filter if
            vessel_type == 'filter' otherwise None.
    """

    DEFAULT_PROPS = {
        'volume': '20 mL',
        'vacuum_time': '10 seconds',
        'stir': True,
        'stir_time': '30 seconds',
        'stir_speed': '500 RPM',
        'aspiration_speed': 5,  # mL / min
        'anticlogging': False,
    }

    def __init__(
        self,
        vessel: str,
        solvent: str,
        volume: Optional[float] = 'default',
        temp: Optional[float] = None,
        vacuum_time: Optional[float] = 'default',
        stir: Optional[Union[bool, str]] = 'default',
        stir_time: Optional[float] = 'default',
        stir_speed: Optional[float] = 'default',
        waste_vessel: Optional[str] = None,
        filtrate_vessel: Optional[str] = None,
        aspiration_speed: Optional[float] = 'default',
        vacuum: Optional[str] = None,
        vacuum_device: Optional[str] = None,
        inert_gas: Optional[str] = None,
        vacuum_valve: Optional[str] = None,
        valve_unused_port: Optional[Union[str, int]] = None,
        vessel_type: Optional[str] = None,
        filter_dead_volume: Optional[float] = None,
        anticlogging: Optional[bool] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.waste_vessel:
            self.waste_vessel = get_nearest_node(
                graph, self.vessel, CHEMPUTER_WASTE)

        if not self.filter_dead_volume:
            vessel = graph.nodes[self.vessel]
            if 'dead_volume' in vessel:
                self.filter_dead_volume = vessel['dead_volume']

    def get_steps(self) -> List[Step]:
        steps = []
        # Volume to withdraw after solvent is added.
        withdraw_volume = self.volume * DEFAULT_FILTER_EXCESS_REMOVE_FACTOR

        # If filter dead volume given internally, add it to withdraw volume
        if self.filter_dead_volume:
            withdraw_volume += self.filter_dead_volume

        aspiration_speed = self.aspiration_speed
        if self.anticlogging:
            aspiration_speed = DEFAULT_FILTER_ANTICLOGGING_ASPIRATION_SPEED

        # Rotavap/reactor WashSolid steps
        if not self.vessel_type == 'filter':
            steps.extend([
                Add(vessel=self.vessel,
                    reagent=self.solvent,
                    volume=self.volume),
                Stir(vessel=self.vessel,
                     time=self.stir_time,
                     stir_speed=self.stir_speed),
                Transfer(from_vessel=self.vessel,
                         to_vessel=self.waste_vessel,
                         volume='all',
                         aspiration_speed=aspiration_speed),
            ])
        # Filter WashSolid steps
        else:
            filtrate_vessel = self.filtrate_vessel
            if not filtrate_vessel:
                filtrate_vessel = self.waste_vessel

            steps.extend([
                # Add solvent
                Add(reagent=self.solvent, volume=self.volume,
                    vessel=self.vessel, port=TOP_PORT,
                    waste_vessel=self.waste_vessel,
                    stir=self.stir is True,
                    stir_speed=self.stir_speed),
                # Stir (or not if stir=False) filter cake and solvent briefly.
                Wait(self.stir_time),
                # Remove solvent.
                CMove(
                    from_vessel=self.vessel,
                    from_port=BOTTOM_PORT,
                    to_vessel=filtrate_vessel,
                    volume=withdraw_volume,
                    aspiration_speed=aspiration_speed),
                # Briefly dry under vacuum.
                StartVacuum(
                    vessel=self.vacuum,
                    pressure=DEFAULT_FILTER_VACUUM_PRESSURE
                ),
                CConnect(from_vessel=self.vessel, to_vessel=self.vacuum,
                         from_port=BOTTOM_PORT),
                Wait(self.vacuum_time),
            ])

            # If vacuum is just from vacuum line not device remove Start/Stop
            # vacuum steps.
            if not self.vacuum_device:
                steps.pop(-3)

            # Start stirring before the solvent is added and stop stirring after
            # the solvent has been removed but before the vacuum is connected.
            if self.stir is True:
                steps.insert(
                    0, StartStir(vessel=self.vessel,
                                 vessel_type=self.vessel_type,
                                 stir_speed=self.stir_speed))
                steps.insert(-2, StopStir(vessel=self.vessel))
            # Only stir after solvent is added and stop stirring before it is
            # removed.
            elif self.stir == 'solvent':
                steps.insert(
                    1, StartStir(vessel=self.vessel,
                                 vessel_type=self.vessel_type,
                                 stir_speed=self.stir_speed))
                steps.insert(-3, StopStir(vessel=self.vessel))

            steps.extend(get_vacuum_valve_reconnect_steps(
                inert_gas=self.inert_gas,
                vacuum_valve=self.vacuum_valve,
                valve_unused_port=self.valve_unused_port,
                vessel=self.vessel))

            if self.vacuum_device:
                steps.extend([
                    StopVacuum(vessel=self.vacuum),
                    CVentVacuum(vessel=self.vacuum)
                ])

            # If self.temp isn't None add HeatChill steps at beginning and end.
            if self.temp is not None:
                steps.insert(
                    0, HeatChillToTemp(vessel=self.vessel, temp=self.temp))
                steps.append(StopHeatChill(vessel=self.vessel))

        return steps

    def human_readable(self, language='en'):
        """Show repeats in solvent volume like 'ethanol (3 × 50 mL)'."""
        props = self.formatted_properties()
        if 'repeat' in props and int(self.repeat) > 1:
            props['volume'] = f"{self.repeat} × {props['volume']}"
        try:
            return HUMAN_READABLE_STEPS['WashSolid'][language].format(**props)
        except KeyError:
            return self.name

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'stir': self.stir is False,
            }
        }
