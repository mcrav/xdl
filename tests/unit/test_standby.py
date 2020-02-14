import os
from xdl import XDL

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_standby_mode():
    """Standby mode test."""
    xdl_f = os.path.join(FOLDER, 'standby.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')

    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)

    for step in x.steps:
        if step.name == 'Standby':
            assert len(step.steps[0].children) == 2
