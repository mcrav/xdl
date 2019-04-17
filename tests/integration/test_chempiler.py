import os

import pytest

from xdl import XDL
import ChemputerAPI
import SerialLabware
from chempiler import Chempiler

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
        print('xdl', files[i])
        print('graph', files[i+1])
        x.prepare_for_execution(files[i+1], interactive=False) 
        chempiler = Chempiler(
            experiment_code='test',
            output_dir=os.path.join(HERE, 'logs'),
            simulation=True,
            graph_file=files[i+1],
            device_modules=[ChemputerAPI, SerialLabware])
        x.execute(chempiler)
        i += 2
