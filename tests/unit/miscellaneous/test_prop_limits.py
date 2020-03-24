import pytest
from xdl.errors import XDLError
from chemputerxdl.steps import Add

@pytest.mark.unit
def test_volume_prop_limit():
    Add(
        reagent="water",
        vessel="reactor",
        volume="10 mL"
    )
    with pytest.raises(XDLError):
        Add(
            reagent="water",
            vessel="reactor",
            volume="10 mg"
        )
    with pytest.raises(XDLError):
        Add(
            reagent="water",
            vessel="reactor",
            volume="-10 mL"
        )
