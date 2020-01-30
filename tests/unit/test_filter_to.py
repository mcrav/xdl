import pytest
import os
from xdl.utils.errors import XDLError

from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_filter_to():
    xdl_f = os.path.join(FOLDER, 'filter_to.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)
    with pytest.raises(XDLError):
        xdl_f = os.path.join(FOLDER, 'filter_to_error.xdl')
        generic_chempiler_test(xdl_f, graph_f)
    with pytest.raises(XDLError):
        xdl_f = os.path.join(FOLDER, 'filter_to_error2.xdl')
        generic_chempiler_test(xdl_f, graph_f)
