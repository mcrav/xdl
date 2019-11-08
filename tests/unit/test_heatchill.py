import os
from ..utils import generic_chempiler_test
from xdl import XDL

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_start_stop_heatchill():
    """Test that StartHeatChill and StopHeatChill work."""
    xdl_f = os.path.join(FOLDER, 'heatchill.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    generic_chempiler_test(xdl_f, graph_f)

def test_inactive_heatchill():
    xdl_f = os.path.join(FOLDER, 'inactive_heatchill.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    generic_chempiler_test(xdl_f, graph_f)

def test_heatchill_return_to_rt():
    xdl_f = os.path.join(FOLDER, 'heatchill_return_to_rt.xdl')
    graph_f = os.path.join(FOLDER, 'heatchill_return_to_rt.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    generic_chempiler_test(xdl_f, graph_f)
