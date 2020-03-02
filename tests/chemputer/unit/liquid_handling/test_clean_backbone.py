import os
import pytest
from ...utils import generic_chempiler_test

from xdl import XDL
from chemputerxdl.steps import CleanBackbone

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, '..', 'files')

#####################
# Cleaning Schedule #
#####################

ALKYL_FLUOR_STEP4_CLEANING_SCHEDULE = [
    'acetonitrile',
    # Dry
    'acetonitrile',
    # AddFilterDeadVolume acetonitrile
    # 'acetonitrile',
    # Add acetonitrile
    # 'acetonitrile',
    # Dissolve acetonitrile
    # 'acetonitrile',
    # Transfer
    'acetonitrile',
    # CleanVessel
    'acetonitrile',
    'dcm',
    # HeatChill, HeatChillReturnToRT
    # FilterThrough
    'dcm',
    # Evaporate
    # Dissolve DCM
    # 'dcm',
    # FilterThrough DCM
    'dcm',
    # CleanVessel
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

EXPENSIVE_SOLVENTS = [
    "ethyl vinyl ether"
]

@pytest.mark.unit
def test_cleaning_schedule():
    """Test that cleaning scheduling algorithm works correctly."""
    xdl_f = os.path.join(FOLDER, 'alkyl_fluor_step4.xdl')
    graph_f = os.path.join(FOLDER, 'alkyl_fluor_step4.graphml')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    cleaning_solvents = [
        step.solvent for step in x.steps if type(step) == CleanBackbone]
    for solvent in cleaning_solvents:
        print(solvent)
    for i in range(len(cleaning_solvents)):
        assert (ALKYL_FLUOR_STEP4_CLEANING_SCHEDULE[i].lower()
                == cleaning_solvents[i].lower())

@pytest.mark.unit
def test_cleaning_no_solvents():
    """Test that having no solvents available doesn't cause an error."""
    xdl_f = os.path.join(FOLDER, 'no_cleaning_solvents.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

@pytest.mark.unit
def test_cleaning_no_preserved_solvents():
    """ Tests that this routine does not use the expensive solvent
    ethyl vinyl ether
    """

    xdl_f = os.path.join(FOLDER, "no_expensive_solvents.xdl")
    graph_f = os.path.join(FOLDER, "no_expensive_solvents.json")
    generic_chempiler_test(xdl_f, graph_f)

    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)

    for step in x.steps:
        if isinstance(step, CleanBackbone):
            assert step.solvent not in EXPENSIVE_SOLVENTS

@pytest.mark.unit
def test_incompatible_solvents_reagents_dcm():
    """
    Tests whether solvents incompatible with specific reagents are ruled out
    of cleaning (if otherwise appropriate). In this case, cleaning solvent
    should be dcm for all CleanBackbone steps.
    """

    xdl_f_dcm = os.path.join(
        FOLDER,
        "incompatible_reagent_solvents_clean_dcm.xdl")
    graph_f_dcm = os.path.join(FOLDER, "reagent_solvents_graph.json")
    generic_chempiler_test(xdl_f_dcm, graph_f_dcm)

    x_dcm = XDL(xdl_f_dcm)
    x_dcm.prepare_for_execution(graph_f_dcm, interactive=False)

    for step in x_dcm.steps:
        if type(step) == CleanBackbone:
            assert step.solvent == "dcm"

@pytest.mark.unit
def test_incompatible_solvents_reagents_ether():
    """
    Tests whether solvents incompatible with specific reagents are ruled out
    of cleaning (if otherwise appropriate). In this case, the cleaning solvent
    should be ether for all CleanBackbone steps.
    """

    xdl_f_ether = os.path.join(
        FOLDER,
        "incompatible_reagent_solvents_clean_ether.xdl"
    )
    graph_f_ether = os.path.join(FOLDER, "reagent_solvents_graph.json")
    generic_chempiler_test(xdl_f_ether, graph_f_ether)

    x_ether = XDL(xdl_f_ether)
    x_ether.prepare_for_execution(graph_f_ether, interactive=False)

    for step in x_ether.steps:
        if type(step) == CleanBackbone:
            assert step.solvent == "ether"
