from typing import Optional, List, Dict, Any

from ..steps_utility import PrimePumpForAdd, Wait, StopStir, StartStir
from ..steps_base import CMove, Confirm
from .....step_utils.base_steps import Step, AbstractStep
from .....constants import (
    DEFAULT_AFTER_ADD_WAIT_TIME,
    DEFAULT_AIR_FLUSH_TUBE_VOLUME,
    DEFAULT_VISCOUS_ASPIRATION_SPEED,
)
from .....localisation import HUMAN_READABLE_STEPS
from .....utils.misc import SanityCheck
from .....constants import CHEMPUTER_WASTE
from ...utils.execution import (
    get_nearest_node, get_reagent_vessel, get_flush_tube_vessel, get_cartridge)

class Add(AbstractStep):
    """Add given volume of given reagent to given vessel.

    Args:
        reagent (str): Reagent to add.
        volume (float): Volume of reagent to add.
        vessel (str): Vessel name to add reagent to.
        port (str): vessel port to use.
        through (str): Substrate to pass reagent through on way to vessel
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
        through_cartridge (str): Internal property. Node name of cartridge to
            pass reagent through on way to vessel.

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

    DEFAULT_PROPS = {
        'move_speed': 40,  # mL / min
        'aspiration_speed': 10,  # mL / min
        'dispense_speed': 40,  # mL / min
        'viscous': False,
        'stir_speed': '250 RPM',
        'anticlogging': False,
        'anticlogging_solvent_volume': '2 mL',
        'anticlogging_reagent_volume': '10 mL',
    }

    def __init__(
        self,
        reagent: str,
        vessel: str,
        volume: Optional[float] = None,
        mass: Optional[float] = None,
        port: Optional[str] = None,
        through: Optional[str] = None,
        move_speed: Optional[float] = 'default',
        aspiration_speed: Optional[float] = 'default',
        dispense_speed: Optional[float] = 'default',
        viscous: Optional[bool] = 'default',
        time: Optional[float] = None,
        stir: Optional[bool] = False,
        stir_speed: Optional[float] = 'default',
        through_cartridge: Optional[str] = None,

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

    def on_prepare_for_execution(self, graph):
        if not self.waste_vessel:
            self.waste_vessel = get_nearest_node(
                graph, self.vessel, CHEMPUTER_WASTE)

        if not self.reagent_vessel:
            self.reagent_vessel = get_reagent_vessel(graph, self.reagent)

        if self.anticlogging_solvent and not self.anticlogging_solvent_vessel:
            self.anticlogging_solvent_vessel = get_reagent_vessel(
                graph, self.anticlogging_solvent)

        if not self.flush_tube_vessel:
            self.flush_tube_vessel = get_flush_tube_vessel(graph)

        if not self.through_cartridge and self.through:
            self.through_cartridge = get_cartridge(graph, self.through)

    def get_steps(self) -> List[Step]:
        steps = []
        # Solid addition
        if self.volume is None and self.mass is not None:
            steps = [Confirm('Is {reagent} ({mass} g) in {vessel}?'.format(
                **self.properties))]
        # Liquid addition
        else:
            if self.anticlogging:
                steps = self.get_anticlogging_add_steps()

            else:
                steps = self.get_add_steps()

            if self.flush_tube_vessel:
                steps.append(CMove(
                    from_vessel=self.flush_tube_vessel,
                    to_vessel=self.vessel,
                    to_port=self.port,
                    volume=DEFAULT_AIR_FLUSH_TUBE_VOLUME))

            if self.stir:
                steps.insert(0, StartStir(vessel=self.vessel,
                                          vessel_type=self.vessel_type,
                                          stir_speed=self.stir_speed))
            else:
                steps.insert(0, StopStir(vessel=self.vessel))
        return steps

    def get_add_steps(self):
        aspiration_speed = self.aspiration_speed
        if self.viscous:
            aspiration_speed = DEFAULT_VISCOUS_ASPIRATION_SPEED
        return [
            PrimePumpForAdd(
                reagent=self.reagent,
                volume='default',
                waste_vessel=self.waste_vessel),
            CMove(
                from_vessel=self.reagent_vessel,
                to_vessel=self.vessel,
                to_port=self.port,
                volume=self.volume,
                through=self.through_cartridge,
                move_speed=self.move_speed,
                aspiration_speed=aspiration_speed,
                dispense_speed=self.get_dispense_speed()),
            Wait(time=DEFAULT_AFTER_ADD_WAIT_TIME)
        ]

    def get_anticlogging_add_steps(self):
        dispense_speed = self.get_dispense_speed()
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
                    to_port=self.port,
                    volume=self.anticlogging_reagent_volume,
                    move_speed=self.move_speed,
                    aspiration_speed=self.aspiration_speed,
                    dispense_speed=dispense_speed),
                CMove(
                    from_vessel=self.anticlogging_solvent_vessel,
                    to_vessel=self.vessel,
                    to_port=self.port,
                    volume=self.anticlogging_solvent_volume,
                    move_speed=self.move_speed,
                    aspiration_speed=self.aspiration_speed,
                    dispense_speed=dispense_speed),
            ])
        steps.append(Wait(time=DEFAULT_AFTER_ADD_WAIT_TIME))
        return steps

    def human_readable(self, language: str = 'en') -> str:
        try:
            if self.mass is not None:
                return HUMAN_READABLE_STEPS['Add (mass)'][language].format(
                    **self.formatted_properties())
            elif self.volume is not None:
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

    def get_dispense_speed(self) -> float:
        if self.time:
            # dispense_speed (mL / min) = volume (mL) / time (min)
            return self.volume / (self.time / 60)
        return self.dispense_speed

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=not self.through or self.through_cartridge,
                error_msg=f'Trying to add through "{self.through}" but cannot\
 find cartridge containing {self.through}.'
            )
        ]
