
import os
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_dry_in_filter():
    """Test that dry step at specific pressure works in filter."""
    xdl_f = os.path.join(FOLDER, 'dry_in_filter.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

def test_dry_in_reactor():
    """Test that dry step at specific pressure works in reactor."""
    xdl_f = os.path.join(FOLDER, 'dry_in_reactor.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

def test_dry_in_rotavap():
    """Test that dry step at specific pressure works in reactor."""
    xdl_f = os.path.join(FOLDER, 'dry_in_rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)