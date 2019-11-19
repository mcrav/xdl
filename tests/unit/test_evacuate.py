import os
from ..utils import generic_chempiler_test, test_step
from xdl.constants import (
    DEFAULT_EVACUATE_AFTER_INERT_GAS_WAIT_TIME,
    DEFAULT_EVACUATE_AFTER_VACUUM_WAIT_TIME,
    DEFAULT_EVACUATE_N_EVACUTIONS
)
from xdl import XDL
from xdl.steps import Evacuate, CConnect, Wait, Repeat, StartVacuum, StopVacuum

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

correct_steps = [
    (CConnect, {'from_vessel': 'filter', 'to_vessel': 'vacuum_flask'}),
    (Wait, {'time': 60}),
    (CConnect, {'from_vessel': 'flask_nitrogen', 'to_vessel': 'filter'}),
    (Wait, {'time': 60}),
]

def test_evacuate():
    xdl_f = os.path.join(FOLDER, 'evacuate.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f)
    for step in x.steps:
        if type(step) == Evacuate:
            assert len(step.steps) == 7
            assert type(step.steps[0]) == StartVacuum
            assert step.steps[0].vessel == 'vacuum_flask'
            assert type(step.steps[1]) == CConnect
            assert type(step.steps[2]) == Wait
            assert step.steps[2].time == DEFAULT_EVACUATE_AFTER_VACUUM_WAIT_TIME * 2
            assert type(step.steps[3]) == CConnect
            assert type(step.steps[4]) == Wait
            assert type(step.steps[-2]) == Repeat
            assert type(step.steps[-1]) == StopVacuum
            assert step.steps[-1].vessel == 'vacuum_flask'
            assert step.steps[-2].repeats == DEFAULT_EVACUATE_N_EVACUTIONS - 1

            for i, substep in enumerate(step.steps[-2].children):
                test_step(substep, correct_steps[i])
