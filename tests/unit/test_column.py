import os
from ..utils import generic_chempiler_test
from xdl import XDL
from xdl.steps import FilterThrough

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_column():
    """Test that RunColumn step works."""
    xdl_f = os.path.join(FOLDER, 'column.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)
