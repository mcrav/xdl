import os
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))

def test_dissolve_in_rotavap():
    """Test by instantiating XDL objects on files known to work
    and calling prepare_for_execution on graph known to work.
    """
    folder = os.path.join(HERE, 'files')
    xdl_f = os.path.join(folder, 'dissolve_in_rotavap.xdl')
    graph_f = os.path.join(folder, 'dissolve_in_rotavap.json')
    generic_chempiler_test(xdl_f, graph_f)