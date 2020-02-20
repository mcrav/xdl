import os
from ..utils import generic_chempiler_test
from xdl import XDL

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_transfer_through():
    """Test that transfering through a cartridge works."""
    xdl_f = os.path.join(FOLDER, 'transfer_through.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')

    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f)
    generic_chempiler_test(xdl_f, graph_f)
