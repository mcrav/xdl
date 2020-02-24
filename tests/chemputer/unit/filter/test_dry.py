import os
import pytest
from ...utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, '..', 'files')

@pytest.mark.unit
def test_dry_in_filter():
    """Test that dry step at specific pressure works in filter."""
    xdl_f = os.path.join(FOLDER, 'dry_in_filter.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

@pytest.mark.unit
def test_dry_in_reactor():
    """Test that dry step at specific pressure works in reactor."""
    xdl_f = os.path.join(FOLDER, 'dry_in_reactor.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

@pytest.mark.unit
def test_dry_in_rotavap():
    """Test that dry step at specific pressure works in reactor."""
    xdl_f = os.path.join(FOLDER, 'dry_in_rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

@pytest.mark.unit
def test_dry_inert_gas_connection():
    """Test confirms issue #112 fixed during reworking of Dry."""
    from xdl import XDL
    from xdl.platforms.chemputer.steps.steps_base.general import CConnect

    xdl_f = os.path.join(FOLDER, 'dry.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig_no_vacuum_device.json')
    generic_chempiler_test(xdl_f, graph_f)

    x = XDL(xdl_f)
    x.prepare_for_execution(
        graph_f,
        testing=True,
    )
    for step in x.steps:
        if step.name == 'Dry':
            for substep in step.steps:
                if type(substep) == CConnect:
                    assert substep.from_vessel == 'flask_nitrogen'
