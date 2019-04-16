from typing import Optional, Union
from ..base_step import Step
from .add import Add
from ..steps_utility import Wait, StartStir, StopStir
from ..steps_base import CMove, CConnect
from ...constants import (
    BOTTOM_PORT, TOP_PORT, DEFAULT_FILTER_EXCESS_REMOVE_FACTOR)

class WashFilterCake(Step):
    """Wash filter cake with given volume of given solvent.

    Args:
        filter_vessel (str): Filter vessel name to wash.
        solvent (str): Solvent to wash with.
        volume (float): Volume of solvent to wash with.
        vacuum_time (float): Time to wait after vacuum connected.
        stir (Union[float, str]): True, 'solvent' or False. True means stir from
            the start until the solvent has been removed. 'solvent' means stir
            after the solvent has been added and stop before it is removed.
            False means don't stir.
        stir_time (float): Time to stir for after solvent has been added. Only
            relevant if stir is True or 'solvent'.
        stir_rpm (float): Speed to stir at in RPM. Only relevant if stir is True
            or 'solvent'.
        waste_vessel (str): Given internally. Vessel to send waste to.
        filtrate_vessel (str): Optional. Vessel to send filtrate to. Defaults to
            waste_vessel.
        aspiration_speed (float): Speed to remove solvent from filter_vessel.
        vacuum (str): Given internally. Name of vacuum flask.
        inert_gas (str): Given internally. Name of node supplying inert gas.
            Only used if inert gas filter dead volume method is being used.
    """
    def __init__(
        self,
        filter_vessel: str,
        solvent: str,
        volume: Optional[float] = 'default',
        vacuum_time: Optional[float] = 'default',
        stir: Optional[Union[bool, str]] = 'solvent', 
        stir_time: Optional[float] = 'default',
        stir_rpm: Optional[float] =  'default',
        waste_vessel: Optional[str] = None,
        filtrate_vessel: Optional[str] = None,
        aspiration_speed: Optional[float] = 'default',
        vacuum: Optional[str] = None,
        inert_gas: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        if not filtrate_vessel:
            filtrate_vessel = self.waste_vessel

        self.steps = [
            # Add solvent
            Add(reagent=self.solvent, volume=self.volume,
                vessel=self.filter_vessel, port=TOP_PORT, 
                waste_vessel=self.waste_vessel, stir=self.stir == True),
            # Stir (or not if stir=False) filter cake and solvent briefly.
            Wait(self.stir_time),
            # Remove solvent.
            CMove(
                from_vessel=self.filter_vessel,
                from_port=BOTTOM_PORT,
                to_vessel=filtrate_vessel,
                volume=self.volume * DEFAULT_FILTER_EXCESS_REMOVE_FACTOR,
                aspiration_speed=self.aspiration_speed),
            # Briefly dry under vacuum.
            CConnect(from_vessel=self.filter_vessel, to_vessel=self.vacuum,
                     from_port=BOTTOM_PORT),
            Wait(self.vacuum_time),
        ]
        # Start stirring before the solvent is added and stop stirring after the
        # solvent has been removed but before the vacuum is connected.
        if self.stir == True:
            self.steps.insert(
                0, StartStir(vessel=self.filter_vessel, stir_rpm=self.stir_rpm))
            self.steps.insert(-2, StopStir(vessel=self.filter_vessel))
        # Only stir after solvent is added and stop stirring before it is
        # removed.
        elif self.stir == 'solvent':
            self.steps.insert(
                1, StartStir(vessel=self.filter_vessel, stir_rpm=self.stir_rpm))
            self.steps.insert(-3, StopStir(vessel=self.filter_vessel))

        if self.inert_gas:
            self.steps.append(
                CConnect(
                    from_vessel=self.inert_gas, to_vessel=self.filter_vessel))

        self.human_readable = 'Wash {filter_vessel} with {solvent} ({volume} mL).'.format(
            **self.properties)

        self.requirements = {
            'filter_vessel': {
                'filter': True
            }
        }
