import os
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_separate_phases():
    """Test that dissolving a solid in the rotavap works."""
    xdl_f = os.path.join(FOLDER, 'separate_phases.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)
