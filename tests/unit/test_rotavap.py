import os
from xdl import XDL
from xdl.steps import Rotavap, CRotavapAutoEvaporation
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_dissolve_in_rotavap():
    """Test that dissolving a solid in the rotavap works."""
    xdl_f = os.path.join(FOLDER, 'dissolve_in_rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

def test_wash_in_rotavap():
    """Test that washing a solid in the rotavap works."""
    xdl_f = os.path.join(FOLDER, 'wash_in_rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

def test_rotavap():
    """Test rotavap evaporate step."""
    xdl_f = os.path.join(FOLDER, 'rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

def test_rotavap_auto_mode():
    """Test rotavap auto evaporate mode."""
    xdl_f = os.path.join(FOLDER, 'rotavap_auto.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    for step in x.steps:
        if type(step) == Rotavap:
            assert type(step.steps[0]) == CRotavapAutoEvaporation
            break
    generic_chempiler_test(xdl_f, graph_f)

def test_rotavap_collection_volume():
    """Test rotavap withdraws correct amount after evaporation."""
    xdl_f = os.path.join(FOLDER, 'rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    for step in x.steps:
        if type(step) == Rotavap:
            # collection_flask_volume in graph
            assert step.steps[-1].volume == 50

def test_rotavap_rotation_speed():
    xdl_f = os.path.join(FOLDER, 'alkyl_fluor_step4.xdl')
    graph_f = os.path.join(FOLDER, 'alkyl_fluor_step4.graphml')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    for step in x.base_steps:
        if step.name == 'CRotavapSetRotationSpeed':
            assert step.rotation_speed <= 300