import os
import pytest
from xdl import XDL
from xdl.steps import Repeat
from ...utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, '..', 'files')

@pytest.mark.unit
def test_repeat():
    """Test Repeat step works correctly."""
    xdl_f = os.path.join(FOLDER, 'repeat_parent.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f)

    for step in x.steps:
        if type(step) == Repeat:
            assert len(step.steps) == 4
            assert step.steps[0].time == 5
            assert step.steps[1].time == 10
            assert step.steps[2].time == 5
            assert step.steps[3].time == 10
    generic_chempiler_test(xdl_f, graph_f)
