import os
import pytest
from xdl import XDL
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

@pytest.mark.integration
def test_lidocaine_prepare_for_execution():
    xdl_f = os.path.join(FOLDER, 'lidocaine.xdl')
    graph_f = os.path.join(FOLDER, 'lidocaine_graph.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)

@pytest.mark.integration
def test_dmp_prepare_for_execution():
    xdl_f = os.path.join(FOLDER, 'DMP.xdl')
    graph_f = os.path.join(FOLDER, 'DMP_graph.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)

@pytest.mark.integration
def test_alkyl_fluor_prepare_for_execution():
    xdl_f = os.path.join(FOLDER, 'AlkylFluor.xdl')
    graph_f = os.path.join(FOLDER, 'AlkylFluor_graph.graphml')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
