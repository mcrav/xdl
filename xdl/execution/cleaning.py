from typing import List, Tuple
if False: # For type annotations
    from ..xdl import XDL
import re
import time

from .constants import *
from .tracking import iter_vessel_contents
from ..steps import *
from ..hardware import Hardware
from ..reagents import Reagent
from ..constants import AQUEOUS_KEYWORDS

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
        for solvent in COMMON_SOLVENT_NAMES:
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
    if not available_solvents:
        return None
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
    try:
        current_reagent = [item for item in schedule if item][0]
    except IndexError:
        current_reagent = available_solvents[0]
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
        if xdl_reagent.id == reagent_name and xdl_reagent.cleaning_solvent:
            return xdl_reagent.cleaning_solvent
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
    if step_solvents == None:
        return []
    clean_backbone_steps = get_clean_backbone_steps(xdl_obj.steps)
    cleans = []
    for i, step_i in enumerate(clean_backbone_steps):
        # Get after_type and before_type
        after_solvent = None
        if i + 1 < len(clean_backbone_steps):
            next_step_i = clean_backbone_steps[i+1]
            if next_step_i < len(step_solvents):
                after_solvent = step_solvents[next_step_i]

        before_solvent = step_solvents[step_i] 
        # If on last clean backbone step then there will be no after solvent.
        if not after_solvent:
            after_solvent = before_solvent

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
    clean_backbone_sequence = get_clean_backbone_sequence(xdl_obj)
    if clean_backbone_sequence:
        for i, solvent in reversed(clean_backbone_sequence):
            # If organic_cleaning_solvent is given use it otherwise use solvent in
            # synthesis.
            if solvent != 'water' and xdl_obj.organic_cleaning_solvent:
                solvent = xdl_obj.organic_cleaning_solvent
            xdl_obj.steps.insert(i, CleanBackbone(solvent=solvent))
        xdl_obj = add_cleaning_steps_at_beginning_and_end(xdl_obj)
    return xdl_obj

def add_cleaning_steps_at_beginning_and_end(xdl_obj: 'XDL') -> 'XDL':
    """Add CleanBackbone steps at beginning and end of procedure with
    appropriate solvents.

    Args:
        xdl_obj (XDL): XDL object to add CleanBackbone steps to.
    
    Returns:
        XDL: xdl_obj with CleanBackbone steps added at beginning and end with
            appropriate solvents.
    """
    # Set default solvents to use if nothing better found.
    available_solvents = get_available_solvents(xdl_obj.reagents)
    start_solvent, end_solvent = None, None
    if len(available_solvents) > 0:
        start_solvent, end_solvent = (
            available_solvents[0], available_solvents[0])
    cleaning_solvents = [
        step.solvent for step in xdl_obj.steps if type(step) == CleanBackbone]
    # Set start solvent and end solvent to first used and last used cleaning
    # solvent if they exist.
    if len(cleaning_solvents) > 0:
        start_solvent = cleaning_solvents[0]
        end_solvent = cleaning_solvents[-1]
    # If end solvent is in blacklist look for a better solvent in available
    # solvents.
    if end_solvent in CLEANING_SOLVENT_PREFER_NOT_TO_USE:
        # Do it like this as probably prefer to use solvent from procedure
        # rather than random one available.
        potential_solvents = cleaning_solvents + available_solvents
        for solvent in potential_solvents:
            if not solvent in CLEANING_SOLVENT_PREFER_NOT_TO_USE:
                end_solvent = solvent
                break
    # Add cleaning steps.
    if start_solvent:
        xdl_obj.steps.insert(0, CleanBackbone(solvent=start_solvent))
    else:
        xdl_obj.steps.append(CleanBackbone(solvent=end_solvent))
    return xdl_obj


########################################
### Interactive Solvent Verification ###
########################################

def verify_cleaning_steps(xdl_obj: 'XDL') -> 'XDL':
    """Allow user to see cleaning steps being added and make changes to what
    solvents are used.

    Args:
        xdl_obj (XDL): XDL object to verify cleaning steps.

    Returns:
        xdl_obj (XDL): XDL object with cleaning steps amended according to user
            input.
    """
    print('\nVerifying Cleaning Steps\n------------------------\n')
    print('* CleanBackbone solvent indicates the step which is being verified. Other steps are shown for context.\n\n')
    available_solvents = get_available_solvents(xdl_obj.reagents)
    chunks = get_cleaning_chunks(xdl_obj)
    print('Procedure Start')
    for chunk in chunks:
        for i in range(len(chunk)):
            if type(chunk[i]) == CleanBackbone:
                print('---------------\n')
                for j, step in enumerate(chunk):
                    if j == i:
                        print(f'* CleanBackbone {step.solvent}')
                    elif type(step) == CleanBackbone:
                        print(f'CleanBackbone {step.solvent}')
                    else:
                        print(step.human_readable)
                answer = None
                # Get appropriate answer.
                while answer not in ['', 'y', 'n']:
                    answer = input(
                        f'\nIs {chunk[i].solvent} an appropriate cleaning solvent? ([y], n)\n')
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
                    chunk[i].solvent = available_solvents[new_solvent_index]
                    print(f'Solvent changed to {chunk[i].solvent}\n')
                    time.sleep(1)
                    
def get_cleaning_chunks(xdl_obj: 'XDL') -> List[List[Step]]:
    """Takes slices out of xdl_obj steps showing context of cleaning. Chunks
    are the step before a set of CleanBackbone steps, the CleanBackbone steps,
    and the step immediately after, e.g. [Add, CleanBackbone, CleanBackbone, Add]
    
    Arguments:
        xdl_obj (XDL): XDL object to get cleaning chunks from.
    
    Returns:
        List[List[Step]]: List of slices from xdl_obj steps showing immediate 
            context of all CleanBackbone steps.
    """
    chunks = []
    steps = xdl_obj.steps
    i = 0
    while i < len(steps):
        if type(steps[i]) == CleanBackbone:
            chunk_start = i
            if i > 0:
                chunk_start = i-1
            chunk_end = i
            while (chunk_end < len(steps)
                   and type(steps[chunk_end]) == CleanBackbone):
                chunk_end += 1
            chunks.append(steps[chunk_start:chunk_end+1])
            i = chunk_end
        i += 1
    return chunks

