import os
import time

from xdl.steps import Wait, AbstractDynamicStep, Add
from xdl.execution import XDLExecutor

import ChemputerAPI
from chempiler import Chempiler

HERE = os.path.abspath(os.path.dirname(__file__))

class TestDynamicStep(AbstractDynamicStep):
    def __init__(self):
        super().__init__(locals())
        self.state = {'i': 0}
        self.done = False

    def on_start(self):
        return [Add(reagent='ether', vessel='filter', volume=5), Wait(1)]

    def on_continue(self):
        if self.state['i'] > 3:
            return []
        self.state['i'] += 1
        return [Wait(2)]

    def on_finish(self):
        self.done = True
        return [Wait(3)]

chempiler = Chempiler(
    experiment_code='test',
    output_dir=os.path.join(HERE, 'chempiler_output'),
    simulation=True,
    graph_file=os.path.join(HERE, 'files', 'bigrig.json'),
    device_modules=[ChemputerAPI])

def test_abstract_dynamic_step():
    step = TestDynamicStep()
    executor = XDLExecutor(None)
    step.prepare_for_execution(os.path.join(HERE, 'files', 'bigrig.json'), executor)
    assert step.start_block[-2].reagent_vessel == 'flask_ether'
    step.execute(chempiler)

    time.sleep(2)

    assert step.state['i'] == 4
    assert step.done == True