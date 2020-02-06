import os
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_separate_phases():
    """Test SeparatePhases step."""
    xdl_f = os.path.join(FOLDER, 'separate_phases.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

def test_separate_phases_retry():
    """To use this test make on_conductivity_sensor_reading set
    self.done = False during simulation and see if the retries happen
    successfully."""
    xdl_f = os.path.join(FOLDER, 'separate_phases_retry.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)
