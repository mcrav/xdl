import pytest
from xdl.errors import XDLValueError
from xdl.reagents import Reagent

@pytest.mark.unit
def test_reagent_roles():
    with pytest.raises(XDLValueError):
        Reagent(name="irnbru", role="juice")
    Reagent(name="DCM", role="solvent")
    Reagent(name="Pd(DBA)2", role="catalyst")
    Reagent(name="2-aminophenethyl alcohol", role="reagent")
    Reagent(name="compound 2", role="substrate")
