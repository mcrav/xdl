from typing import Optional, List, Dict, Any
from ..steps_utility import PrimePumpForAdd, Wait, StopStir, StartStir
from ..steps_base import CMove, Confirm
from ..base_step import Step, AbstractStep
from ...utils.misc import get_port_str
from ...constants import (
    DEFAULT_AFTER_ADD_WAIT_TIME,
    DEFAULT_AIR_FLUSH_TUBE_VOLUME,
    TOP_PORT,
    EVAPORATE_PORT
)

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
            if self.time:
                # dispense_speed (mL / min) = volume (mL) / time (min)
                dispense_speed = self.volume / (self.time / 60)
            else:
                dispense_speed = self.dispense_speed

            # Liquid addition
            steps = [
                PrimePumpForAdd(
                    reagent=self.reagent,
                    volume='default',
                    waste_vessel=self.waste_vessel),
                CMove(
                    from_vessel=self.reagent_vessel,
                    to_vessel=self.vessel, 
                    to_port=port,
                    volume=self.volume,
                    move_speed=self.move_speed,
                    aspiration_speed=self.aspiration_speed,
                    dispense_speed=dispense_speed),
                Wait(time=DEFAULT_AFTER_ADD_WAIT_TIME)
            ]

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

    def get_human_readable(self) -> Dict[str, str]:
        # Solid addition
        if self.mass != None:
            en = 'Add {0} ({1} g) to {2} {3}.'.format(
                self.reagent, self.mass, self.vessel, get_port_str(self.port))
        en = 'Add {0} ({1} mL) to {2} {3}.'.format(
            self.reagent, self.volume, self.vessel, get_port_str(self.port))
        return {
            'en': en,
        }

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