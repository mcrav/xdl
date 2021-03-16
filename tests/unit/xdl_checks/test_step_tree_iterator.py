import pytest
from chemputerxdl.steps import (
    Stir,
    StartStir,
    CStirringControllerSetSpeed,
    CStirringControllerStart,
    Wait,
    CSetRecordingSpeed,
    CWait,
    StopStir,
    CStirringControllerStop
)

@pytest.mark.unit
def test_step_tree_iterator():
    """Test step tree iterator goes through step tree in a depth first
    manner.
    """
    step = Stir(vessel='reactor', time='60 min', stir_speed=250)
    expected_step_tree = [
        StartStir,
        CStirringControllerSetSpeed,
        CStirringControllerStart,
        Wait,
        CSetRecordingSpeed,
        CWait,
        CSetRecordingSpeed,
        StopStir,
        CStirringControllerStop,
    ]
    for i, substep in enumerate(step.step_tree):
        assert type(substep) == expected_step_tree[i]
