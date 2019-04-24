import os
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_dissolve_in_rotavap():
    """Test that dissolving a solid in the rotavap works."""
    xdl_f = os.path.join(FOLDER, 'dissolve_in_rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'rotavap_reactor_cartridge.json')
    generic_chempiler_test(xdl_f, graph_f)

def test_wash_in_rotavap():
    """Test that washing a solid in the rotavap works."""
    xdl_f = os.path.join(FOLDER, 'wash_in_rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'rotavap_reactor_cartridge.json')
    generic_chempiler_test(xdl_f, graph_f)

def test_rotavap():
    """Test rotavap evaporate step."""
    xdl_f = os.path.join(FOLDER, 'rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'rotavap_reactor_cartridge.json')
    generic_chempiler_test(xdl_f, graph_f)