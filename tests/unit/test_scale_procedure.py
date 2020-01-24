import os
from xdl import XDL

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_dry_in_filter():
    """Test that dry step at specific pressure works in filter."""
    xdl_f = os.path.join(FOLDER, 'scale_procedure.xdl')
    x = XDL(xdl_f)
    x.scale_procedure(0.5)
    assert x.steps[0].volume == 10  # Add step changed
    assert x.steps[1].volume == 10  # CleanVessel unchanged
