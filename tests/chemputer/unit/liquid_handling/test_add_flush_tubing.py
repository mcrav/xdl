
import pytest
import os
from xdl import XDL

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, '..', 'files')

@pytest.mark.unit
def test_add_flush_tubing():
    x = XDL(os.path.join(FOLDER, 'repeat_parent.xdl'))
    x.prepare_for_execution(
        os.path.join(FOLDER, 'bigrig.json'), interactive=False)
    for step in x.steps:
        if step.name == 'Repeat':
            for child in step.children:
                if child.name == 'Add':
                    assert child.flush_tube_vessel == 'flask_nitrogen'
                    flushing_tubing = False
                    for substep in child.steps:
                        if substep.name == 'CMove':
                            if substep.from_vessel == 'flask_nitrogen':
                                flushing_tubing = True
                                break
                    assert flushing_tubing

@pytest.mark.unit
def test_add_flush_tubing_no_backbone_inert_gas():
    x = XDL(os.path.join(FOLDER, 'repeat_parent.xdl'))
    x.prepare_for_execution(
        os.path.join(FOLDER, 'bigrig_no_backbone_inert_gas.json'),
        interactive=False,

        # Avoid diff as repeat_parent.xdlexe is not in .gitignore.
        save_path=os.path.join(FOLDER, 'repeat_parent_no_inert_gas.xdlexe')
    )
    for step in x.steps:
        if step.name == 'Repeat':
            for child in step.children:
                if child.name == 'Add':
                    assert child.flush_tube_vessel is None
                    flushing_tubing = False
                    for substep in child.steps:
                        if substep.name == 'CMove':
                            if substep.from_vessel == 'flask_nitrogen':
                                flushing_tubing = True
                                break
                    assert not flushing_tubing
