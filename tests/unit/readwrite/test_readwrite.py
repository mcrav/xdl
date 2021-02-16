from xdl import XDL
import os
import shutil
import pytest

HERE = os.path.abspath(os.path.dirname(__file__))
INTEGRATION_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(HERE)), 'integration', 'files')
UNIT_FOLDER = os.path.join(os.path.dirname(HERE), 'files')
TEST_OUTPUT = os.path.join(HERE, 'test_output')
os.makedirs(TEST_OUTPUT, exist_ok=True)

@pytest.mark.unit
def test_readwrite():
    for f in os.listdir(INTEGRATION_FOLDER):
        if f.endswith('.xdl'):
            f_path = os.path.join(INTEGRATION_FOLDER, f)
            if not f.startswith('AlkylFluor'):
                # AlkylFluor weird as writes internal props
                x = XDL(f_path)
                os.makedirs('test_output', exist_ok=True)
                save_xml_path = os.path.join('test_output', f)
                save_json_path = os.path.join('test_output', f[:-3] + 'json')
                x.save(save_xml_path)
                x.save(save_json_path, file_format='json')
                x_xml = XDL(save_xml_path)
                x_json = XDL(save_json_path)
                shutil.rmtree('test_output')
                assert x_xml == x_json == x

@pytest.mark.unit
def test_readwrite_procedure_sections():
    xdl_f = os.path.join(UNIT_FOLDER, 'procedure-sections.xdl')
    x1 = XDL(xdl_f)
    output_file = os.path.join(HERE, 'test_output', 'procedure-section.xdl')
    x1.save(output_file)
    x2 = XDL(output_file)
    assert x1 == x2
    assert len(x1.prep_steps) == len(x2.prep_steps) > 0
    assert len(x1.reaction_steps) == len(x2.reaction_steps) > 0
    assert len(x1.workup_steps) == len(x2.workup_steps) > 0
    assert len(x1.purification_steps) == len(x2.purification_steps) > 0

@pytest.mark.unit
def test_readwrite_procedure_sections_json():
    xdl_f = os.path.join(UNIT_FOLDER, 'procedure-sections.xdl')
    x1 = XDL(xdl_f)
    output_file = os.path.join(HERE, 'test_output', 'procedure-section.json')
    x1.save(output_file, file_format='json')
    x2 = XDL(output_file)
    assert x1 == x2
    assert len(x1.prep_steps) == len(x2.prep_steps) > 0
    assert len(x1.reaction_steps) == len(x2.reaction_steps) > 0
    assert len(x1.workup_steps) == len(x2.workup_steps) > 0
    assert len(x1.purification_steps) == len(x2.purification_steps) > 0
