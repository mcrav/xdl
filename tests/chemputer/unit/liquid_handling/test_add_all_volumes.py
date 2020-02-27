import os
import pytest
from xdl import XDL
from xdl.steps import Transfer
from xdl.platforms.chemputer.executor.constants import (
    TRANSFER_ALL_VOLUME_FACTOR)

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, '..', 'files')

@pytest.mark.unit
def test_add_all_volumes():
    x = XDL(os.path.join(FOLDER, 'add_all_volumes.xdl'))
    x.prepare_for_execution(os.path.join(FOLDER, 'bigrig.json'), testing=True)
    volumes = [
        15 * TRANSFER_ALL_VOLUME_FACTOR,
        15 * TRANSFER_ALL_VOLUME_FACTOR,
        100
    ]
    i = 0
    for step in x.steps:
        if type(step) == Transfer:
            assert volumes[i] == step.volume
            i += 1
