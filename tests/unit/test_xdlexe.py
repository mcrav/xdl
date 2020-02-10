import os
import pytest
from xdl import XDL
from xdl.steps.base_steps import AbstractBaseStep, AbstractDynamicStep
from xdl.utils.errors import XDLError
from ..utils import get_chempiler, generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')
INTEGRATION_FOLDER = os.path.join(os.path.dirname(HERE), 'integration', 'files')

TESTS = [
    (os.path.join(INTEGRATION_FOLDER, 'lidocaine.xdl'),
     os.path.join(INTEGRATION_FOLDER, 'lidocaine_graph.json')),

    (os.path.join(INTEGRATION_FOLDER, 'DMP.xdl'),
     os.path.join(INTEGRATION_FOLDER, 'DMP_graph.json')),

    (os.path.join(INTEGRATION_FOLDER, 'AlkylFluor.xdl'),
     os.path.join(INTEGRATION_FOLDER, 'AlkylFluor_graph.graphml')),
]

@pytest.mark.unit
def test_xdlexe():
    for test_xdl_f, test_graph_f in TESTS:
        x = XDL(test_xdl_f)
        x.prepare_for_execution(
            test_graph_f, interactive=False, save_path=test_xdl_f + 'exe')
        xexe = XDL(test_xdl_f + 'exe')
        assert len(x.steps) == len(xexe.steps)
        for i, step in enumerate(x.steps):
            test_steps_identical(step, xexe.steps[i])
    generic_chempiler_test(test_xdl_f, test_graph_f)

def test_steps_identical(step1, step2):
    assert type(step1) == type(step2)
    for prop, val in step1.properties.items():
        if val or step2.properties[prop]:
            try:
                if type(val) == float:
                    assert f'{step2.properties[prop]:.4f}' == f'{val:.4f}'
                else:
                    assert step2.properties[prop] == val
            except AssertionError:
                raise AssertionError(
                    f'Property "{prop}": {val} != {step2.properties[prop]}')
    if not isinstance(step1, (AbstractBaseStep, AbstractDynamicStep)):
        assert len(step1.steps) == len(step2.steps)
        for j, step in enumerate(step1.steps):
            test_steps_identical(step, step2.steps[j])

@pytest.mark.unit
def test_xdlexe_execute_wrong_graph():
    for test_xdl_f, test_graph_f in TESTS:
        with pytest.raises(XDLError):
            x = XDL(test_xdl_f)
            x.prepare_for_execution(test_graph_f, interactive=False)
            x = XDL(test_xdl_f + 'exe')
            c = get_chempiler(os.path.join(FOLDER, 'bigrig.json'))
            x.execute(c)

        x = XDL(test_xdl_f)
        x.prepare_for_execution(test_graph_f, interactive=False)
        x = XDL(test_xdl_f + 'exe')
        c = get_chempiler(test_graph_f)
        x.execute(c)

@pytest.mark.unit
def test_xdlexe_decodes_symbols():
    test_path = os.path.join(FOLDER, "V60P0014_A.xdlexe")
    XDL(test_path)
