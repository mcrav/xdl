
import os
from ..utils import generic_chempiler_test
from xdl import XDL

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_wash_solid():
    """Test that WashSolid step works with temperature property."""
    xdl_f = os.path.join(FOLDER, 'wash_solid.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

def test_wash_solid_stirring():
    """Test that WashSolid step stir property works."""
    xdl_f = os.path.join(FOLDER, 'wash_solid.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f)
    assert('StartStir' in [step.name for step in x.steps[-1].steps])
