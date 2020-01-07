from typing import List
from .base_steps import CBSetStirRate, CBWait
from ....step_utils.base_steps import Step, AbstractStep

class StartStir(AbstractStep):
    def __init__(self, stir_speed: int, children = []):
        super().__init__(locals())


    def get_steps(self) -> List[Step]:
        return [
            CBSetStirRate(self.stir_speed)
        ]


class StopStir(AbstractStep):
    def __init__(self, children = []):
        super().__init__(locals())


    def get_steps(self) -> List[Step]:
        return [
            CBSetStirRate(0)
        ]

class Stir(AbstractStep):
    def __init__(self, stir_speed: int, time: int, children = []) -> None:
        super().__init__(locals())

    def get_steps(self) -> List[Step]:
        return [
            StartStir(self.stir_speed),
            CBWait(self.time),
            StopStir()
        ]
