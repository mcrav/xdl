from .....step_utils.base_steps import AbstractStep
from ..base_step import ChemputerStep
from .heatchill import HeatChill
from .dissolve import Dissolve

class Recrystallize(ChemputerStep, AbstractStep):

    DEFAULT_PROPS = {
        'time': '2 hrs',
        'crystallize_temp': '25°C',
    }

    PROP_TYPES = {
        'vessel': str,
        'time': float,
        'dissolve_temp': float,
        'crystallize_temp': float,
        'solvent': str,
        'solvent_volume': float
    }

    def __init__(
        self,
        vessel: str,
        time: float = 'default',
        dissolve_temp: float = None,
        crystallize_temp: float = 'default',
        solvent: str = None,
        solvent_volume: float = None,
        **kwargs
    ):
        super().__init__(locals())

    def get_steps(self):
        steps = []
        if self.solvent:
            steps.append(self.get_dissolve_step())

        steps.append(self.get_crystallize_steps())
        return steps

    def get_dissolve_step(self):
        return Dissolve(
            vessel=self.vessel,
            solvent=self.solvent,
            volume=self.solvent_volume,
            temp=self.dissolve_temp,
        )

    def get_crystallize_steps(self):
        return HeatChill(
            vessel=self.vessel,
            temp=self.crystallize_temp,
            time=self.time,
            stir=True,
        )

    @property
    def requirements(self):
        temps = []
        if self.crystallize_temp:
            temps.append(self.crystallize_temp)
        if self.dissolve_temp:
            temps.append(self.dissolve_temp)
        return {
            'vessel': {
                'heatchill': True,
                'temp': temps
            }
        }
