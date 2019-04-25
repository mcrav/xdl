import os
from ..utils import generic_chempiler_test

from xdl import XDL
from xdl.steps import CleanBackbone

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_clean_vessel():
    """Test that dissolving a solid in the rotavap works."""
    xdl_f = os.path.join(FOLDER, 'clean_reactor_rotavap.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)


#########################
### Cleaning Schedule ###
#########################

ALKYL_FLUOR_STEP4_CLEANING_SCHEDULE = [
    'acetonitrile',
    # Dry
    'acetonitrile',
    # AddFilterDeadVolume acetonitrile
    'acetonitrile',
    # Add acetonitrile
    'acetonitrile',
    # Dissolve acetonitrile
    'acetonitrile',
    # Transfer
    'acetonitrile',
    # Clean vessel acetonitrile
    'acetonitrile',
    # HeatChill, HeatChillReturnToRT
    # RemoveFilterDeadVolume
    'acetonitrile',
    'dcm',
    # FilterThrough
    'dcm',
    # Rotavap
    # Dissolve DCM
    'dcm',
    # FilterThrough DCM
    'dcm',
    # CleanVessel DCM
    'dcm',
    # Transfer
    'dcm',
    'ether',
    # WashSolid
    'ether',
    # Dry
    'ether',
    'acetonitrile'
]

def test_cleaning_schedule():
    """Test that cleaning scheduling algorithm works correctly."""
    xdl_f = os.path.join(FOLDER, 'alkyl_fluor_step4.xdl')
    graph_f = os.path.join(FOLDER, 'alkyl_fluor_step4.graphml')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    cleaning_solvents = [
        step.solvent for step in x.steps if type(step) == CleanBackbone]
    for i in range(len(cleaning_solvents)):
        assert (ALKYL_FLUOR_STEP4_CLEANING_SCHEDULE[i].lower()
                == cleaning_solvents[i].lower())