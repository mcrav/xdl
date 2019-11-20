import pytest
from xdl.utils.errors import XDLError
from xdl.reagents import Reagent

def test_reagent_roles():
    with pytest.raises(XDLError):
        Reagent(id="irnbru", role="juice")
    Reagent(id="DCM", role="solvent")
    Reagent(id="Pd(DBA)2", role="catalyst")
    Reagent(id="2-aminophenethyl alcohol", role="reactant")
