from typing import Callable
import time
import os

from xdl.steps.base_steps import AsyncStep
from xdl.steps.special_steps import Async
from xdl.steps import Wait

import ChemputerAPI
from chempiler import Chempiler

HERE = os.path.abspath(os.path.dirname(__file__))

class TestAsyncStep(AsyncStep):
    def __init__(self, callback: Callable, on_finish: Callable):
        super().__init__(locals())

    def async_execute(self, chempiler, logger=None, level=0):
        for i in range(5):
            time.sleep(1)
            self.callback(i)
        self.on_finish()

class TestAsyncStepManager(object):
    def __init__(self):
        self.async_step = TestAsyncStep(
            self.test_async_step_callback, self.test_async_step_on_finish)
        self.vals = []

    def test_async_step_callback(self, i):
        self.vals.append(i)

    def test_async_step_on_finish(self):
        assert tuple(self.vals) == (0, 1, 2, 3, 4)
        self.vals = 'donedone'

    def execute(self):
        self.async_step.execute(None, None)

def test_async_step():
    mgr = TestAsyncStepManager()
    mgr.execute()
    waits = 0
    while len(mgr.vals) < 5:
        time.sleep(1)
        waits += 1
        assert waits < 7
    assert mgr.vals == 'donedone'

class TestAsyncWrapperManager(object):
    def __init__(self, steps):
        self.async_steps = Async(steps, self.on_finish)
        self.done = False

    def execute(self, chempiler):
        self.async_steps.execute(chempiler, None)

    def on_finish(self):
        self.done = True

def test_async_wrapper():
    chempiler = Chempiler(
        experiment_code='test',
        output_dir=os.path.join(HERE, 'chempiler_output'),
        simulation=True,
        graph_file=os.path.join(HERE, 'files', 'bigrig.json'),
        device_modules=[ChemputerAPI])

    mgr = TestAsyncWrapperManager(Wait(5))
    mgr.execute(chempiler)
    time.sleep(2)
    assert mgr.done == True

    mgr = TestAsyncWrapperManager([Wait(5)])
    mgr.execute(chempiler)
    time.sleep(2)
    assert mgr.done == True
