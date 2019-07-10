import os
from xdl import XDL
from xdl.steps import StartStir, StopStir, StartHeatChill, StopHeatChill
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

def test_temp_controlled_reagents():
    """Test reagent flasks needing stirring work."""
    xdl_f = os.path.join(FOLDER, 'temp_controlled_reagents.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f)
    assert type(x.steps[0]) == StartHeatChill
    assert x.steps[0].vessel == 'flask_water'
    assert x.steps[0].temp == 5
    assert type(x.steps[-1]) == StopHeatChill
