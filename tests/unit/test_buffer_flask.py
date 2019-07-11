import os
from ..utils import generic_chempiler_test
from xdl import XDL

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_buffer_flask():
    """Test that buffer flask works."""
    xdl_f = os.path.join(FOLDER, 'buffer_flask.xdl')
    graph_f = os.path.join(FOLDER, 'AF-4-Tr-RBF.graphml')
    generic_chempiler_test(xdl_f, graph_f)
