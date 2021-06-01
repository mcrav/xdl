import os
import json
from xdl.blueprints.chasm2 import Chasm2

HERE = os.path.abspath(os.path.dirname(__file__))
FILES = os.path.join(HERE, 'files')
TEST_OUTPUT = os.path.join(HERE, 'test_output')
os.makedirs(TEST_OUTPUT, exist_ok=True)

def test_chasm2():
    with open(os.path.join(FILES, 'chasm2.json')) as fd:
        chasm2_procedure = json.load(fd)
    x = Chasm2(chasm2_procedure).build_xdl()
    for step in x.steps:
        print(step.name, step.properties, '\n')
    x.save(os.path.join(TEST_OUTPUT, 'chasm2.xdl'))
