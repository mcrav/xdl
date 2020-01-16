import os
from ..utils import get_chempiler
from xdl import XDLController


HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_controller():
    """Test that XDL controller works in simulation mode."""
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    c = get_chempiler(graph_f)
    controller = XDLController(c, graph_f)
    controller.add(reagent='water', vessel='reactor', volume=10)
    