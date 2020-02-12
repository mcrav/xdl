import os
from xdl import XDL
from xdl.steps import (
    Evaporate,
    CStopChiller,
    CStartChiller,
    CRotavapAutoEvaporation,
    RotavapHeatToTemp,
    RotavapStopEverything
)
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
        if type(step) == Evaporate:
            assert type(step.steps[-3]) == RotavapStopEverything
            assert type(step.steps[-4]) == CRotavapAutoEvaporation
            assert type(step.steps[-5]) == RotavapHeatToTemp
            break
    generic_chempiler_test(xdl_f, graph_f)

def test_rotavap_collection_volume():
    """Test rotavap withdraws correct amount after evaporation."""
    xdl_f = os.path.join(FOLDER, 'rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    for step in x.steps:
        if type(step) == Evaporate:
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

def test_rotavap_has_chiller():
    """Test rotavap has a chiller attached."""
    xdl_f = os.path.join(FOLDER, 'rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)

    step_types = {
        "CStartChiller": CStartChiller,
        "CStopChiller": CStopChiller
    }

    for step in x.steps:
        if type(step) == Evaporate:
            assert step.properties["has_chiller"] is True
            for s in step.steps:
                if type(s) in step_types.values():
                    step_types.pop(s.name)

            assert len(step_types) == 0
