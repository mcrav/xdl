import os
from ..utils import generic_chempiler_test
from xdl import XDL
from xdl.steps import FilterThrough

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_filter_through():
    """Test that dissolving a solid in the rotavap works."""
    xdl_f = os.path.join(FOLDER, 'filter_through.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

def test_filter_through_buffer_flask():
    """Test that dissolving a solid in the rotavap works."""
    xdl_f = os.path.join(FOLDER, 'filter_through_buffer_flask.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    for step in x.steps:
        if type(step) == FilterThrough:
            assert step.buffer_flask == 'buffer_flask'
            last_transfer = step.steps[-1]
            assert last_transfer.from_vessel == 'buffer_flask'
            assert last_transfer.to_vessel == 'rotavap'
    generic_chempiler_test(xdl_f, graph_f)
