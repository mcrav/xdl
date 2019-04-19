import os
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_clean_vessel():
    """Test that dissolving a solid in the rotavap works."""
    xdl_f = os.path.join(FOLDER, 'clean_reactor_rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'rotavap_reactor.json')
    generic_chempiler_test(xdl_f, graph_f)
