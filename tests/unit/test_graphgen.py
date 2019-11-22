import os
from xdl import XDL
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')
OUTPUT_FOLDER = os.path.join(HERE, 'test_output')

GRAPHGEN_TESTS = [
    ('orgsyn_v81p0262.xdl'),
    ('orgsyn_v80p0129.xdl'),
    ('orgsyn_v87p0016.xdl'),
    ('orgsyn_v83p0193.xdl'),
]

TEST_FOLDER = os.path.dirname(HERE)
ROOT_FOLDER = os.path.dirname(TEST_FOLDER)
TEMPLATE_GRAPH = os.path.join(ROOT_FOLDER, 'xdl', 'graphgen', 'template.json')

def test_graphgen():
    for xdl_f in GRAPHGEN_TESTS:
        x = XDL(os.path.join(FOLDER, xdl_f))
        save_path = os.path.join(OUTPUT_FOLDER, xdl_f.split('.')[0] + '.json')
        x.graph(graph_template=TEMPLATE_GRAPH, save=save_path)
        print('\n')
        generic_chempiler_test(os.path.join(FOLDER, xdl_f), save_path)
