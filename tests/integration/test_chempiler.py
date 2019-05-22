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