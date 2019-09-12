import os
import json
import pytest

from xdl.steps import Add, HeatChill, Transfer
from xdl.execution import XDLExecutor
from xdl.steps.special_steps import Parallelizer
from networkx.readwrite.json_graph import node_link_graph

import ChemputerAPI
from chempiler import Chempiler

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'files', 'bigrig.json')) as fd:
    graph_dict = json.load(fd)
    graph = node_link_graph(graph_dict)

chempiler = Chempiler(
    experiment_code='test',
    output_dir=os.path.join(HERE, 'chempiler_output'),
    simulation=True,
    graph_file=graph_dict,
    device_modules=[ChemputerAPI])

executor = XDLExecutor(None)
block1 = [
    Transfer(from_vessel='flask_water', to_vessel='reactor', volume=5),
    Transfer(from_vessel='flask_ether', to_vessel='reactor', volume=5),
    # HeatChill(vessel='reactor', temp=60, time='1 hr'),
    # Transfer(from_vessel='reactor', to_vessel='filter', volume=5)
]
block2 = [
    Transfer(from_vessel='flask_chloroacetyl_chloride', to_vessel='filter',
                volume=5),
]
executor.prepare_block_for_execution(graph_dict, block1)
executor.prepare_block_for_execution(graph_dict, block2)

p = Parallelizer(chempiler, graph, [block1, block2], time_step=5)

@pytest.mark.unit
def test_block_scheduling():
    assert block1[0] in p.exstream[0]
    assert block2[0] in p.exstream[0]

    p.print_lockmatrix()

@pytest.mark.unit
def test_exstream():
    p.execute()
