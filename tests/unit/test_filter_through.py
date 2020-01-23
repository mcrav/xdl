import os
from ..utils import generic_chempiler_test
from xdl import XDL
from xdl.steps import FilterThrough, CMove

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
            assert step.buffer_flask == 'buffer_flask2'
            last_transfer = step.steps[-1]
            assert last_transfer.from_vessel == 'buffer_flask2'
            assert last_transfer.to_vessel == 'rotavap'
    generic_chempiler_test(xdl_f, graph_f)

def test_filter_eluting_with_more_than_max_volume():
    xdl_f = os.path.join(FOLDER, 'filter_through_elute_more_than_max_volume.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f)
    total_vol_added = 0
    total_elutes = 0
    tests = [
        (10,  1000),
        (20, 2000),
        (3, 75),
        (3, 150)
    ]
    i = 0
    for step in x.steps:
        if type(step) == FilterThrough:
            for substep in step.base_steps:
                if type(substep) == CMove:
                    if substep.from_vessel == 'flask_ether' and substep.to_vessel == 'reactor':
                        total_vol_added += substep.volume
                        total_elutes += 1
            assert total_elutes == tests[i][0]
            assert total_vol_added == tests[i][1]
            total_elutes = 0
            total_vol_added = 0
            i += 1
    assert i == len(tests)
