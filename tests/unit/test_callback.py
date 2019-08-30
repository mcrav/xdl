from xdl.steps.base_steps import AbstractStep
from xdl.steps.special_steps import Callback
from xdl.steps.steps_utility import Wait
from ..utils import get_chempiler

import os
from typing import Callable

HERE = os.path.abspath(os.path.dirname(__file__))

class TestStep(AbstractStep):
    def __init__(self, on_finish: Callable):
        super().__init__(locals())

    def get_steps(self):
        return [
            Wait(50),
            Callback(self.on_finish, args=[0], keyword_args={'result': 1}),
        ]

def test_callback():
    c = get_chempiler(os.path.join(HERE, 'files', 'bigrig.json'))
    step = TestStep(on_finish)
    step.execute(c)

def on_finish(item, result=None):
    assert item == 0
    assert result == 1
