from xdl.execution import XDLExecutor
from xdl.steps import Add, Transfer
from xdl.utils.errors import IllegalPortError
import pytest
import os

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_port_validation():
    executor = XDLExecutor()
    bigrig = os.path.join(FOLDER, 'bigrig.json')
    with pytest.raises(IllegalPortError):
        block = [Add(reagent="water", vessel="reactor", volume=5, port="top")]
        executor.prepare_block_for_execution(bigrig, block)

    block = [Add(reagent="water", vessel="reactor", volume=5, port="0")]
    executor.prepare_block_for_execution(bigrig, block)

    with pytest.raises(IllegalPortError):
        block = [Transfer(from_vessel="rotavap", to_vessel="reactor", volume=5, from_port="top")]
        executor.prepare_block_for_execution(bigrig, block)

    block = [Transfer(from_vessel="rotavap", to_vessel="reactor", volume=5, from_port="evaporate")]
    executor.prepare_block_for_execution(bigrig, block)
    block = [Transfer(from_vessel="rotavap", to_vessel="reactor", volume=5, from_port="collect")]
    executor.prepare_block_for_execution(bigrig, block)

    with pytest.raises(IllegalPortError):
        block = [Transfer(from_vessel="rotavap", to_vessel="filter", volume=5, to_port="0")]
        executor.prepare_block_for_execution(bigrig, block)

    block = [Transfer(from_vessel="rotavap", to_vessel="filter", volume=5, to_port="top")]
    executor.prepare_block_for_execution(bigrig, block)
    block = [Transfer(from_vessel="rotavap", to_vessel="filter", volume=5, to_port="bottom")]
    executor.prepare_block_for_execution(bigrig, block)
