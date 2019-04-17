from typing import Optional
from ..steps_utility import PrimePumpForAdd, Wait
from ..steps_base import CMove, CSetStirRate, CStopStir, CStir, Confirm
from ..base_step import Step
from ...utils.misc import get_port_str
from ...constants import (
    DEFAULT_AFTER_ADD_WAIT_TIME, DEFAULT_AIR_FLUSH_TUBE_VOLUME)

class Add(Step):
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
        stir_rpm (float): RPM to stir at, only relevant if stir = True.
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
        stir_rpm: Optional[float] = None,
        reagent_vessel: Optional[str] = None, 
        waste_vessel: Optional[str] = None,
        flush_tube_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        # Solid addition
        if self.mass:
            self.steps = [Confirm(f'Is {reagent} ({mass} g) in {vessel}?')]
            self.human_readable = 'Add {0} ({1} g) to {2} {3}.'.format(
                self.reagent, self.mass, self.vessel, get_port_str(self.port))
        
        else:

            if self.time:
                time = self.time
                # dispense_speed (mL / min) = volume (mL) / time (min)
                dispense_speed = self.volume / (self.time / 60)
            else:
                dispense_speed = self.dispense_speed

            # Liquid addition
            self.steps = [
                PrimePumpForAdd(
                    reagent=self.reagent,
                    volume='default',
                    waste_vessel=self.waste_vessel),
                CMove(
                    from_vessel=self.reagent_vessel,
                    to_vessel=self.vessel, 
                    to_port=self.port,
                    volume=self.volume,
                    move_speed=self.move_speed,
                    aspiration_speed=self.aspiration_speed,
                    dispense_speed=dispense_speed),
                Wait(time=DEFAULT_AFTER_ADD_WAIT_TIME)
            ]

            if self.flush_tube_vessel:
                self.steps.append(CMove(
                    from_vessel=self.flush_tube_vessel,
                    to_vessel=self.vessel,
                    to_port=self.port,
                    volume=DEFAULT_AIR_FLUSH_TUBE_VOLUME,))

            if self.stir:
                self.steps.insert(0, CStir(vessel=self.vessel))
                if self.stir_rpm:
                    self.steps.insert(
                        0, CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm))
                else:
                    self.steps.insert(
                        0, CSetStirRate(vessel=self.vessel, stir_rpm='default'))
            else:
                self.steps.insert(0, CStopStir(vessel=self.vessel))

            self.human_readable = 'Add {0} ({1} mL) to {2} {3}.'.format(
                self.reagent, self.volume, self.vessel, get_port_str(self.port))

        self.requirements = {
            'vessel': {
                'stir': self.stir,
            }
        }