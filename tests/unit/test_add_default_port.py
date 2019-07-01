import os
from xdl import XDL
from xdl.steps import Add, CMove

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_dry_in_filter():
    """Test that dry step at specific pressure works in filter."""
    xdl_f = os.path.join(FOLDER, 'add_default_port.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    correct_ports = [
        'top', # filter default
        None, # reactor default
        'evaporate', # rotavap default
        'top', # separator default
        'bottom', # separator explicit
    ]
    for step in x.steps:
        if type(step) == Add:
            correct_port = correct_ports.pop(0)
            for substep in step.steps:
                if type(substep) == CMove:
                    assert substep.to_port == correct_port
