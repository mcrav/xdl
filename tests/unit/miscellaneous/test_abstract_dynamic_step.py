import os
import time
import pytest

from chemputerxdl.steps import Wait, Add
from xdl import XDL
from xdl.steps import AbstractDynamicStep
from chemputerxdl.executor import ChemputerExecutor

import ChemputerAPI
from chempiler import Chempiler

from ...utils import remove_confirm_steps

HERE = os.path.abspath(os.path.dirname(__file__))

class TestDynamicStep(AbstractDynamicStep):

    __test__ = False

    PROP_TYPES = {}

    def __init__(self):
        super().__init__(locals())
        self.state = {'i': 0}
        self.done = False

    def on_start(self):
        return [Add(reagent='ether', vessel='filter', volume=5), Wait(0.5)]

    def on_continue(self):
        if self.state['i'] > 3:
            return []
        self.state['i'] += 1
        return [Wait(0.5)]

    def on_finish(self):
        self.done = True
        return [Wait(0.5)]


@pytest.mark.unit
def test_abstract_dynamic_step():
    step = TestDynamicStep()
    executor = ChemputerExecutor(None)
    step.prepare_for_execution(
        os.path.join(HERE, '..', 'files', 'bigrig.json'), executor)
    assert step.start_block[-2].reagent_vessel == 'flask_ether'

    chempiler = Chempiler(
        experiment_code='dynamic_step_test',
        output_dir=os.path.join(HERE, 'chempiler_output'),
        simulation=True,
        graph_file=os.path.join(HERE, '..', 'files', 'bigrig.json'),
        device_modules=[ChemputerAPI]
    )

    # Nasty hack to make this execute blocks rather than simulation steps.
    chempiler.simulation = False

    executor.execute_step(
        chempiler, step, async_steps=[], step_indexes=[0], level=0)

    time.sleep(2)

    assert step.state['i'] == 4
    assert step.done is True

def test_log_file_step_indexes():
    """This test was just run manually to verify that step indexes were logged
    correctly for dynamic steps. It is annoying automated because all the wait
    steps actually wait.
    """
    xdl_f = os.path.join(
        HERE, '..', '..', 'integration', 'files', 'orgsyn_v81p0262.xdlexe')
    graph_f = os.path.join(
        HERE, '..', '..', 'integration', 'files', 'orgsyn_v81p0262_graph.json')
    info_log_file = os.path.join(
        HERE, 'chempiler_output', 'log_files', 'dynamic_step_test_info.log')
    if os.path.isfile(info_log_file):
        os.remove(info_log_file)
    chempiler = Chempiler(
        experiment_code='dynamic_step_test',
        output_dir=os.path.join(HERE, 'chempiler_output'),
        simulation=True,
        graph_file=graph_f,
        device_modules=[ChemputerAPI]
    )
    chempiler.simulation = False
    x = XDL(xdl_f)
    remove_confirm_steps(x)
    x.execute(chempiler, 6)
