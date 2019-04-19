from typing import Optional
from ..base_step import Step
from .add import Add
from ..steps_utility import Stir, Transfer

class WashSolid(Step):
    """Wash a solid in vessel with given solvent by adding solvent, stirring,
    then removing solvent through a filter. Assumes vessel outlet is fitted with
    a filter.
    
    Args:
        vessel (str): Vessel containing solid to wash.
        solvent (str): Solvent to wash solid with.
        volume (float): Volume of solvent to wash solid with.
        stir_time (float): Time to stir for.
        stir_rpm (float): Speed to stir at.
        solvent_vessel (str): Given internally. Vessel containing solvent.
        waste_vessel (str): Given internally. Vessel to send solvent to after
            washing.
    """
    def __init__(
        self,
        vessel: str,
        solvent: str,
        volume: float,
        stir_time: Optional[float] = 'default',
        stir_rpm: Optional[float] = 'default',
        solvent_vessel: Optional[str] = None,
        waste_vessel: Optional[str] = None,
    ) -> None:
        super().__init__(locals())

        self.steps = [
            Add(vessel=self.vessel, reagent=self.solvent, volume=self.volume),
            Stir(vessel=self.vessel,
                 time=self.stir_time,
                 stir_rpm=self.stir_rpm),
            Transfer(from_vessel=self.vessel,
                     to_vessel=self.waste_vessel,
                     volume='all'),
        ]

        self.human_readable = 'Wash solid in {vessel} with {solvent} ({volume} mL) stirring for {stir_time} s at {stir_rpm} RPM.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'stir': True,
            }
        }