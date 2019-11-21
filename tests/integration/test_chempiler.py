import os
import pytest

from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

@pytest.mark.integration
def test_lidocaine():
    generic_chempiler_test(
        os.path.join(FOLDER, 'lidocaine.xdl'),
        os.path.join(FOLDER, 'lidocaine_graph.json')
    )

@pytest.mark.integration
def test_dmp():
    generic_chempiler_test(
        os.path.join(FOLDER, 'DMP.xdl'),
        os.path.join(FOLDER, 'DMP_graph.json')
    )

@pytest.mark.integration
def test_alkyl_fluor():
    generic_chempiler_test(
        os.path.join(FOLDER, 'AlkylFluor.xdl'),
        os.path.join(FOLDER, 'AlkylFluor_graph.graphml')
    )

@pytest.mark.integration
def test_orgsyn_v83p0184a():
    generic_chempiler_test(
        os.path.join(FOLDER, 'orgsyn_v83p0184a.xdl'),
        os.path.join(FOLDER, 'orgsyn_v83p0184a_graph.json')
    )

@pytest.mark.integration
def test_orgsyn_v83p0193():
    generic_chempiler_test(
        os.path.join(FOLDER, 'orgsyn_v83p0193.xdl'),
        os.path.join(FOLDER, 'orgsyn_v83p0193_graph.json')
    )
