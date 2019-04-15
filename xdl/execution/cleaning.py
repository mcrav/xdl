from typing import List, Tuple
if False: # For type annotations
    from ..xdl import XDL
import re
import time

from chemdata.synonyms import SOLVENT_SYNONYM_CAS_DICT

from .constants import *
from .tracking import iter_vessel_contents
from ..steps import *
from ..hardware import Hardware
from ..reagents import Reagent

'''
Backbone Cleaning Rules
-----------------------
If a step contains a common solvent then that solvent is used for backbone
cleaning after that step. If the last clean didn't also use that solvent, a
backbone clean using the solvent is also performed before the step. If no
common solvent is used in a step the last encountered common solvent is used.
e.g.
Add( acetone )
CleanBackbone( acetone )
Add( acetic anhydride )
CleanBackbone( acetone )
CleanBackbone( water )
Add( aqueous_oxone_solution )
CleanBackbone( water )
CleanBackbone( ether )
Add( ether )
CleanBackbone( ether )
...
'''

def get_available_solvents(reagents: List[Reagent]) -> List[str]:
    """Get list of common available solvents in list of Reagent objects given. 
    
    Args:
        reagents (List[Reagent]): List of reagent objects.
    
    Returns:
        List[str]: List of common solvents contained in reagents.
    """
    solvents = []
    for reagent in reagents:
        for solvent in SOLVENT_SYNONYM_CAS_DICT:
            # Look for stuff like 'X in THF' as well as plain 'THF'.
            if (re.match(r'[ _]?' + solvent, reagent.id.lower())
                or re.match(r'[ _]?' + solvent, reagent.id.lower())):
                # Don't want to use solvents that damage parts of Chemputer.
                if not reagent.id.lower() in CLEANING_SOLVENT_BLACKLIST:
                    solvents.append(reagent.id)
    return solvents

def get_cleaning_schedule(xdl_obj: 'XDL') -> List[str]:
    """Get list of what solvent should be used to clean at every step.
    
    Args:
        xdl_obj (XDL): XDL object to get cleaning schedule for.
    
    Returns:
        List[str]: List of organic cleaning solvents to use with every step.
            Solvents are selected for every step regardless of whether an
            organic clean should be performed at that step.
    """
    available_solvents = get_available_solvents(xdl_obj.reagents)
    schedule = [None for step in xdl_obj.steps]
    # Add solvents to schedule at solvent addition steps.
    for i, _, _, additions in iter_vessel_contents(
        xdl_obj.steps, xdl_obj.executor._graph_hardware, additions=True):
        for reagent in additions:
            cleaning_solvent = get_reagent_cleaning_solvent(
                reagent, xdl_obj.reagents, available_solvents)
            if cleaning_solvent:
                schedule[i] = cleaning_solvent

    # Fill in blanks in schedule.
    # 1) Treat consecutive SOLVENT_CONTAINING_STEPS as groups and if one step in
    #    group has a solvent apply that to all steps in the group.
    i = 0
    while i < len(schedule):
        reagent = schedule[i]
        j = i
        if reagent:
            while (j >= 0
                and type(xdl_obj.steps[j]) in SOLVENT_CONTAINING_STEPS
                and not schedule[j]):
                j -= 1
                schedule[j] = reagent
            j = i
            while (j < len(xdl_obj.steps)
                and type(xdl_obj.steps[j]) in SOLVENT_CONTAINING_STEPS
                and not schedule[j]):
                j += 1
                schedule[j] = reagent
        i = max(j, i + 1)
    # 2) Go forward applying last encountered solvent to every step in schedule.
    current_reagent = None
    for i, reagent in enumerate(schedule):
        if reagent:
            if reagent != 'water':
                current_reagent = reagent
        else:
            schedule[i] = current_reagent
    return schedule

def get_reagent_cleaning_solvent(
    reagent_name: str, xdl_reagents: List[Reagent], available_solvents) -> bool:
    """Return True if reagent_name is an aqueous reagent, otherwise False.
    
    Args:
        reagent_name (str): Name of reagent.
    
    Returns:
        bool: True if reagent_name is aqueous, otherwise False.
    """
    # See if any of available solvents are added.
    if reagent_name in available_solvents:
        return reagent_name

    # Look for stuff like 'X in THF'
    for solvent in available_solvents:
        if (re.match(r'[ ]?' + solvent, reagent_name)
            or re.match(r'[ ]?' + solvent, reagent_name)):
            return reagent_name
                
    for xdl_reagent in xdl_reagents:
        if xdl_reagent.id == reagent_name and xdl_reagent.clean_type:
            return xdl_reagent.clean_type
    for word in AQUEOUS_KEYWORDS:
        if word in reagent_name:
            return 'water'
    return None

def get_clean_backbone_steps(steps: List[Step]) -> List[int]:
    """Get list of steps after which backbone should be cleaned.
    
    Returns:
        List[int]: List of indexes for steps after which the backbone should
            be cleaned.
    """
    clean_backbone_steps = []
    for i, step in enumerate(steps):
        if type(step) in CLEAN_BACKBONE_AFTER_STEPS:
            clean_backbone_steps.append(i)
    return clean_backbone_steps

def get_clean_backbone_sequence(xdl_obj) -> List[Tuple[int, str]]:
    """Get sequence of backbone cleans required. Cleans are given as tuples like
    this (step_index, cleaning_solvent).
    
    Returns:
        List[int, str]: List of Tuples like this
            [(step_to_insert_backbone_clean, cleaning_solvent)...]
    """
    step_solvents = get_cleaning_schedule(xdl_obj)
    clean_backbone_steps = get_clean_backbone_steps(xdl_obj.steps)
    cleans = []
    for i, step_i in enumerate(clean_backbone_steps):
        # Get after_type and before_type
        if step_i + 1 < len(step_solvents):
            if i + 1 < len(clean_backbone_steps):
                next_step_i = clean_backbone_steps[i+1]
                after_solvent = step_solvents[next_step_i]
        else:
            after_solvent = xdl_obj.organic_cleaning_solvent 
        before_solvent = step_solvents[step_i] 

        if before_solvent == after_solvent:
            cleans.append((step_i+1, before_solvent))
        elif before_solvent != after_solvent:
            cleans.append((step_i+1, before_solvent))
            cleans.append((step_i+1, after_solvent))
    return cleans

def add_cleaning_steps(xdl_obj: 'XDL') -> 'XDL':
    """Add cleaning steps to XDL object with appropriate cleaning solvents.
    
    Args:
       xdl_obj (XDL): XDL object to add cleaning steps to.

    Returns:
        XDL: xdl_obj with cleaning steps added.
    """
    for i, solvent in reversed(get_clean_backbone_sequence(
        xdl_obj)):
        if not solvent:
            solvent = xdl_obj.organic_cleaning_solvent
        xdl_obj.steps.insert(i, CleanBackbone(solvent=solvent))
    verify = None
    while verify not in ['y', 'n', '']:
        verify = input('Verify solvents used in backbone cleaning? (y, [n])')
    if verify == 'y':
        verify_cleaning_steps(xdl_obj)
    return xdl_obj

def verify_cleaning_steps(xdl_obj: 'XDL') -> 'XDL':
    """Allow user to see cleaning steps being added and make changes to what
    solvents are used.

    Args:
        xdl_obj (XDL): XDL object to verify cleaning steps.

    Returns:
        xdl_obj (XDL): XDL object with cleaning steps amended according to user
            input.
    """
    available_solvents = get_available_solvents(xdl_obj.reagents)
    print('Available cleaning solvents:', '\n'.join(available_solvents))
    step_i = 0
    for step in xdl_obj.steps:
        # If step is CleanBackbone give user option to change solvent.
        if type(step) == CleanBackbone:
            print(f'\nCleanBackbone {step.solvent}')
            answer = None
            # Get appropriate answer.
            while answer not in ['', 'y', 'n']:
                answer = input(
                    f'Is {step.solvent} an appropriate cleaning solvent? ([y], n)\n')
            # Leave solvent as is. Move onto next steps.
            if not answer or answer == 'y':
                continue
            # Get user to select new solvent.
            else:
                new_solvent_index = None
                # Wait for user to give appropriate input.
                while new_solvent_index not in list(
                    range(len(available_solvents))):
                    input_msg = f'Select new solvent by number\n'
                    input_msg += '\n'.join(
                        [f'{solvent} ({i})'
                         for i, solvent in enumerate(available_solvents)]
                    ) + '\n'
                    new_solvent_index = input(input_msg)
                    try:
                        new_solvent_index = int(new_solvent_index)
                    except ValueError:
                        print('Input must be number corresponding to solvent.')
                # Change CleanBackbone step solvent.
                step.solvent = available_solvents[new_solvent_index]
                print(f'Solvent changed to {step.solvent}\n')
                time.sleep(1)
        # Print step to show user context of CleanBackbone step.
        else:
            print(f'{step_i + 1}) {step.human_readable}')
            step_i += 1
                    