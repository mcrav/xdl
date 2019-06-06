import os
from ..utils import generic_chempiler_test
from xdl import XDL
from xdl.steps import Filter, StopStir, StartStir

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_filter_with_stirring():
    """Test that Filter step works with stirring."""
    xdl_f = os.path.join(FOLDER, 'filter_with_stirring.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f)
    for step in x.steps:
        if type(step) == Filter:
            assert type(step.steps[0]) == StartStir
            assert type(step.steps[2]) == StopStir
    generic_chempiler_test(xdl_f, graph_f)

def test_filter_without_stirring():
    """Test that Filter step stir works without stirring."""
    xdl_f = os.path.join(FOLDER, 'filter_without_stirring.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f)
    for step in x.steps:
        if type(step) == Filter:
            assert type(step.steps[0]) == StopStir
    generic_chempiler_test(xdl_f, graph_f)