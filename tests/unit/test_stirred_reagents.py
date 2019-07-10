import os
from xdl import XDL
from xdl.steps import StartStir, StopStir
from xdl.constants import DEFAULT_STIR_REAGENT_FLASK_SPEED
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_stirred_reagents():
    """Test reagent flasks needing stirring work."""
    xdl_f = os.path.join(FOLDER, 'stirred_reagents.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f)
    assert type(x.steps[1]) == StartStir
    assert x.steps[1].vessel == 'flask_water'
    assert x.steps[1].stir_speed == DEFAULT_STIR_REAGENT_FLASK_SPEED
    assert type(x.steps[-1]) == StopStir
