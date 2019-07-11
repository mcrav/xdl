import os
from xdl import XDL
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_pneumatic_controller():
    """Test pneumatic controller works correctly."""
    xdl_f = os.path.join(FOLDER, 'pneumatic_controller.xdl')
    graph_f = os.path.join(FOLDER, 'pneumatic_controller.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f)

    for step in x.steps:
        assert step.pneumatic_controller == 'pneumatic_controller'

        if step.vessel == 'flask':
            assert str(step.pneumatic_controller_port) == '1'

        elif step.vessel == 'filter':

            if step.port == 'bottom':
                assert str(step.pneumatic_controller_port) == '0'

            elif step.port == 'top':
                assert str(step.pneumatic_controller_port) == '2'

    generic_chempiler_test(xdl_f, graph_f)
