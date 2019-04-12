import os
import pytest

from xdl import XDL

HERE = os.path.abspath(os.path.dirname(__file__))

def test_prepare_for_execution():
    """Test by instantiating XDL objects on files known to work
    and calling prepare_for_execution on graph known to work.
    """
    folder = os.path.join(HERE, 'files')
    files = [os.path.join(folder, f) for f in sorted(os.listdir(folder))]
    i = 0
    while i + 1 < len(files):
        x = XDL(files[i])
        x.prepare_for_execution(files[i+1]) 
        i += 2
