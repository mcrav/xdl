from typing import Optional, List, Dict, Any
import copy

from ..steps_utility import PrimePumpForAdd, Wait, StopStir, StartStir
from ..steps_base import CMove, Confirm
from ..base_steps import Step, AbstractStep
from ...utils.misc import get_port_str, format_property
from ...constants import (
    DEFAULT_AFTER_ADD_WAIT_TIME,
    DEFAULT_AIR_FLUSH_TUBE_VOLUME,
    TOP_PORT,
    EVAPORATE_PORT
)
from ...localisation import HUMAN_READABLE_STEPS

class Add(AbstractStep):
    """Add given volume of given reagent to given vessel.

    Args:
        reagent (str): Reagent to add.
        volume (float): Volume of reagent to add.
        vessel (str): Vessel name to add reagent to.
        port (str): vessel port to use.
        move_speed (float): Speed in mL / min to move liquid at. (optional)
        aspiration_speed (float): Aspiration speed (speed at which liquid is
            pulled out of reagent_vessel).
        dispense_speed (float): Dispense speed (speed at which liquid is pushed
            from pump into vessel).
        time (float): Time to spend dispensing liquid. Works by changing
            dispense_speed. Note: The time given here will not be the total step
            execution time, it will be the total time spent dispensing from the
            pump into self.vessel during the addition.
        stir (bool): If True, stirring will be started before addition.
        stir_speed (float): RPM to stir at, only relevant if stir = True.

        anticlogging (bool): If True, a technique will be used to avoid clogging
            where reagent is added in small portions, each one followed by a
            small portion of solvent.
        anticlogging_solvent (str): Solvent to add between reagent additions
            during anticlogging routine.
        anticlogging_solvent_volume (float): Optional. Portion of solvent to add
            in each cycle of anticlogging add routine.
        anticlogging_reagent_volume (float): Optional. Portion of reagent to add
            in each cycle of anticlogging add routine.
        anticlogging_solvent_vessel (str): Given internally. Vessel containing
            anticlogging solvent.

        reagent_vessel (str): Given internally. Vessel containing reagent.
        waste_vessel (str): Given internally. Vessel to send waste to.
        flush_tube_vessel (str): Given internally. Air/nitrogen vessel to use to
            flush liquid out of the valve -> vessel tube.
    """
    def __init__(
        self,
        reagent: str,
        vessel: str,
        volume: Optional[float] = None,
        mass: Optional[float] = None,
        port: Optional[str] = None,
        move_speed: Optional[float] = 'default',
        aspiration_speed: Optional[float] = 'default',
        dispense_speed: Optional[float] = 'default',
        time: Optional[float] = None,
        stir: Optional[bool] = False,
        stir_speed: Optional[float] = 'default',

        anticlogging: Optional[bool] = 'default',
        anticlogging_solvent: Optional[str] = None,
        anticlogging_solvent_volume: Optional[float] = 'default',
        anticlogging_reagent_volume: Optional[float] = 'default',
        anticlogging_solvent_vessel: Optional[str] = None,

        reagent_vessel: Optional[str] = None,
        waste_vessel: Optional[str] = None,
        flush_tube_vessel: Optional[str] = None,
        vessel_type: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        port = self.get_port()
        steps = []
        # Solid addition
        if self.mass != None:
            steps = [Confirm('Is {reagent} ({mass} g) in {vessel}?'.format(
                **self.properties))]
        # Liquid addition
        else:
            if self.anticlogging:
                return self.get_anticlogging_add_steps()

            else:
                return self.get_add_steps()

            if self.flush_tube_vessel:
                steps.append(CMove(
                    from_vessel=self.flush_tube_vessel,
                    to_vessel=self.vessel,
                    to_port=port,
                    volume=DEFAULT_AIR_FLUSH_TUBE_VOLUME))

            if self.stir:
                steps.insert(0, StartStir(vessel=self.vessel,
                                          vessel_type=self.vessel_type,
                                          stir_speed=self.stir_speed))
            else:
                steps.insert(0, StopStir(vessel=self.vessel))
        return steps

    def get_add_steps(self):
        return [
            PrimePumpForAdd(
                reagent=self.reagent,
                volume='default',
                waste_vessel=self.waste_vessel),
            CMove(
                from_vessel=self.reagent_vessel,
                to_vessel=self.vessel,
                to_port=self.get_port(),
                volume=self.volume,
                move_speed=self.move_speed,
                aspiration_speed=self.aspiration_speed,
                dispense_speed=self.get_dispense_speed()),
            Wait(time=DEFAULT_AFTER_ADD_WAIT_TIME)
        ]

    def get_anticlogging_add_steps(self):
        dispense_speed = self.get_dispense_speed()
        port = self.get_port()
        steps = [
            PrimePumpForAdd(
                reagent=self.reagent,
                volume='default',
                waste_vessel=self.waste_vessel
            )
        ]
        n_adds = int(self.volume / self.anticlogging_reagent_volume) + 1
        for _ in range(n_adds):
            steps.extend([
                CMove(
                    from_vessel=self.reagent_vessel,
                    to_vessel=self.vessel,
                    to_port=port,
                    volume=self.anticlogging_reagent_volume,
                    move_speed=self.move_speed,
                    aspiration_speed=self.aspiration_speed,
                    dispense_speed=dispense_speed),
                CMove(
                    from_vessel=self.anticlogging_solvent_vessel,
                    to_vessel=self.vessel,
                    to_port=port,
                    volume=self.anticlogging_solvent_volume,
                    move_speed=self.move_speed,
                    aspiration_speed=self.aspiration_speed,
                    dispense_speed=dispense_speed),
            ])
        steps.append(Wait(time=DEFAULT_AFTER_ADD_WAIT_TIME))
        return steps


    def human_readable(self, language: str = 'en') -> str:
        try:
            if self.mass != None:
                return HUMAN_READABLE_STEPS['Add (mass)'][language].format(
                    **self.formatted_properties())
            elif self.volume != None:
                return HUMAN_READABLE_STEPS['Add (volume)'][language].format(
                    **self.formatted_properties())
            else:
                return self.name
        except KeyError:
            return self.name

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        return {
            'vessel': {
                'stir': self.stir,
            }
        }

    def get_port(self) -> str:
        """If self.port is None, return default port for different vessel types.

        Returns:
            str: Vessel port to add to.
        """
        if self.port:
            return self.port
        elif self.vessel_type == 'filter':
            return TOP_PORT
        elif self.vessel_type == 'separator':
            return TOP_PORT
        elif self.vessel_type == 'rotavap':
            return EVAPORATE_PORT
        return None

    def get_dispense_speed(self) -> float:
        if self.time:
            # dispense_speed (mL / min) = volume (mL) / time (min)
            return self.volume / (self.time / 60)
        return self.dispense_speed
