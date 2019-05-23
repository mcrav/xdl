from typing import Optional, List, Dict

from ..base_step import AbstractStep, Step
from ..steps_base import CMove
from ...utils.misc import get_port_str

class PrimePumpForAdd(AbstractStep):
    """Prime pump attached to given reagent flask in anticipation of Add step.

    Args:
        reagent (str): Reagent to prime pump for addition.
        move_speed (str): Speed to move reagent at. (optional)
    """
    def __init__(
        self,
        reagent: str,
        volume: Optional[float] = 'default',
        reagent_vessel: Optional[str] = None,
        waste_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())
    
    def get_steps(self) -> List[Step]:
        return [CMove(from_vessel=self.reagent_vessel,
                      to_vessel=self.waste_vessel,
                      volume=self.volume)]

    def get_human_readable(self) -> Dict[str, str]:
        en = 'Move {volume} mL of {reagent} to waste to prime pump'.format(
            **self.properties)
        return {
            'en': en,
        }

class Transfer(AbstractStep):
    """Transfer contents of one vessel to another.

    Args:
        from_vessel (str): Vessel name to transfer from.
        to_vessel (str): Vessel name to transfer to.
        volume (float): Volume to transfer in mL.
        from_port (str): Port on from_vessel to transfer from.
        to_port (str): Port on to_vessel to transfer from.
        through (str): Node name to transfer to.
        aspiration_speed (float): Speed in mL / min to pull liquid out of
            from_vessel.
        move_speed (float): Speed in mL / min to move liquid at.
        dispense_speed (float): Speed in mL / min to push liquid out of pump
            into to_vessel.
    """
    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
        volume: float,
        from_port: Optional[str] = None, 
        to_port: Optional[str] = None, 
        through: Optional[str] = None,
        aspiration_speed: Optional[float] = 'default',
        move_speed: Optional[float] = 'default',
        dispense_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [CMove(from_vessel=self.from_vessel,
                      from_port=self.from_port,
                      to_vessel=self.to_vessel,
                      to_port=self.to_port, 
                      volume=self.volume,
                      through=self.through,
                      aspiration_speed=self.aspiration_speed,
                      move_speed=self.move_speed,
                      dispense_speed=self.dispense_speed)]

    def get_human_readable(self) -> Dict[str, str]:
        en = 'Transfer {0} mL from {1} {2} to {3} {4}.'.format(
            self.volume, self.from_vessel, get_port_str(self.from_port),
            self.to_vessel, get_port_str(self.to_port))
        return {
            'en': en,
        }