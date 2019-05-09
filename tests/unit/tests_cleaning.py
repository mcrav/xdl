import os
from ..utils import generic_chempiler_test

from xdl import XDL
from xdl.steps import CleanBackbone, Dissolve, CleanVessel

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
    # CleanVessel
    'acetonitrile',
    'dcm',
    # HeatChill, HeatChillReturnToRT
    # FilterThrough
    'dcm',
    # Rotavap
    # Dissolve DCM
    'dcm',
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

def test_cleaning_no_solvents():
    """Test that having no solvents available doesn't cause an error."""
    xdl_f = os.path.join(FOLDER, 'no_cleaning_solvents.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)

def test_clean_vessel_scheduling():
    """Test that all CleanVessel steps are added at correct places, i.e. 
    ...Dissolve, emptying_step, CleanVessel,..."""
    xdl_f = os.path.join(FOLDER, 'alkyl_fluor_step4.xdl')
    graph_f = os.path.join(FOLDER, 'alkyl_fluor_step4.graphml')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)

    # Check right number of steps with right vessel/solvent have been added.
    clean_vessel_steps = [step for step in x.steps if type(step) == CleanVessel]
    assert len(clean_vessel_steps) == 2
    assert (clean_vessel_steps[0].solvent.lower() == 'acetonitrile'
            and clean_vessel_steps[0].vessel == 'rotavap')
    assert (clean_vessel_steps[1].solvent.lower() == 'dcm'
            and clean_vessel_steps[1].vessel == 'rotavap')

    # Check all CleanVessel steps come after Dissolve + filter_emptying step.
    for i in range(len(x.steps)):
        emptying_step_passed = False
        legit = True
        if type(x.steps[i]) == CleanVessel:
            # Check default double clean is being done.
            assert (len([step
                         for step in x.steps[i].steps
                         if step.name == 'CMove']) == 2)
            legit = False
            j = i
            while j > 0:
                j -= 1
                #  Ignore CleanBackbone steps
                if type(x.steps[j]) == CleanBackbone:
                    continue
                # Dissolve steps encountered after emptying step.
                elif type(x.steps[j]) == Dissolve and emptying_step_passed:
                    legit = True
                    break
                # Found emptying step.
                elif not emptying_step_passed:
                    emptying_step_passed = True
                # Emptying step already found but next step backwards is not a
                # Dissolve step. Therefore CleanVessel is incorrectly placed.
                else:
                    legit = False
                    break
            assert legit
