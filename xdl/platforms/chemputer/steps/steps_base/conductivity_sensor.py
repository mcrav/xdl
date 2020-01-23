from typing import Callable
from .....step_utils.base_steps import AbstractBaseStep

class ReadConductivitySensor(AbstractBaseStep):

    def __init__(self, sensor: str, on_reading: Callable):
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        if chempiler.simulation:
            self.on_reading(-1)
        else:
            self.on_reading(chempiler[self.sensor].conductivity)
        return True

    def human_readable(self, language='en'):
        return 'Read conductivity sensor.'

    def locks(self, chempiler):
        return [self.sensor], [], []
