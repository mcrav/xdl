import os
from xdl import XDL
from xdl.steps import Add, CMove, Dissolve, Transfer, Separate

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_default_ports():
    """Test that dry step at specific pressure works in filter."""
    xdl_f = os.path.join(FOLDER, 'add_default_port.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    correct_ports = [
        'top',  # filter default
        '0',  # reactor default
        'evaporate',  # rotavap default
        'bottom',  # separator default
        'top',  # separator explicit

        'top',
        '0',
        'evaporate',
        '1',

        ('0', 'bottom'),
        ('evaporate', 'top'),

        ('0', '0', 'bottom'),
        ('1', '1', 'top')
    ]
    for step in x.steps:
        if type(step) in [Add, Dissolve]:
            correct_port = correct_ports.pop(0)
            for substep in step.steps:
                if type(substep) == CMove:
                    assert str(substep.to_port) == correct_port

        elif type(step) == Transfer:
            correct_from_port, correct_to_port = correct_ports.pop(0)
            for substep in step.steps:
                if type(substep) == CMove:
                    assert str(substep.from_port) == correct_from_port
                    assert str(substep.to_port) == correct_to_port

        elif type(step) == Separate:
            correct_from_port, correct_to_port, correct_waste_phase_to_port =\
                correct_ports.pop(0)
            assert str(step.from_port) == correct_from_port
            assert str(step.to_port) == correct_to_port
            assert str(step.waste_phase_to_port) == correct_waste_phase_to_port
