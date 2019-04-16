from typing import Optional
from ..base_step import Step
from ..steps_utility import Wait, HeatChillToTemp
from .add import Add

class Dissolve(Step):
    """Dissolve contents of vessel in given solvent.
    
    Args:
        vessel (str): Vessel to dissolve contents of. 
        solvent (str): Solvent to dissolve contents of vessel with.
        volume (float): Volume of solvent to use.
        port (str): Port to add solvent to.
        temp (float): Temperature to stir at. Optional.
        time (float): Time to stir for. Optional.
        solvent_vessel (str): Given internally. Flask containing solvent.
    """
    def __init__(
        self,
        vessel: str,
        solvent: str,
        volume: float,
        port: Optional[str] = None,
        temp: Optional[float] = 'default',
        time: Optional[float] = 'default',
        stir_rpm: Optional[float] = 'default',
        solvent_vessel: Optional[str] = None,
    ) -> None:
        super().__init__(locals())

        self.steps = [
            Add(reagent=self.solvent,
                volume=self.volume,
                vessel=self.vessel,
                port=self.port),
            HeatChillToTemp(
                vessel=self.vessel,
                temp=self.temp,
                stir=True,
                stir_rpm=self.stir_rpm),
            Wait(self.time),
        ]

        self.human_readable = f'Dissolve contents of {vessel} in {solvent} ({volume} mL) at {temp} °C over {time} seconds.'

        self.requirements = {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp],
                'stir': True,
            }
        }
