from typing import List, Tuple
if False: # For type annotations
    from ..xdl import XDL
import re
import time

from .constants import *
from .tracking import iter_vessel_contents, VesselContents
from ..steps import *
from ..hardware import Hardware
from ..reagents import Reagent
from ..constants import AQUEOUS_KEYWORDS

GENERIC_ORGANIC = 0

"""
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

Vessel Cleaning Rules
---------------------
Vessels are cleaned after emptying steps if the step preceding the emptying step
was a dissolve step. This is to make sure that no vessels are cleaned after
emptying steps when they actually still contain solids.
e.g.
...
Evaporate rotavap
Dissolve rotavap
Transfer rotavap -> reactor
CleanVessel rotavap
...

"""

def get_available_solvents(xdl_obj: 'XDL') -> List[str]:
    """Get list of common available solvents in XDL object.
    Reagents list and graph are searched for available solvents. 
    
    Args:
        reagents (XDL): XDL object to get available solvents from.
    
    Returns:
        List[str]: List of common solvents contained in reagents.
    """
    solvents = []
    reagents = [reagent.id for reagent in xdl_obj.reagents]
    graph_hardware = xdl_obj.executor._graph_hardware
    reagents.extend([flask.chemical for flask in graph_hardware.flasks])
    reagents = list(set(reagents))
    for reagent in reagents:
        for solvent in COMMON_SOLVENT_NAMES:
            # Look for stuff like 'X in THF' as well as plain 'THF'.
            if (re.match(r'[ _]?' + solvent, reagent.lower())
                or re.match(r'[ _]?' + solvent, reagent.lower())):
                # Don't want to use solvents that damage parts of Chemputer.
                if not reagent.lower() in CLEANING_SOLVENT_BLACKLIST:
                    solvents.append(reagent)
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
    graph_hardware = xdl_obj.executor._graph_hardware
    available_solvents = get_available_solvents(xdl_obj)
    if not available_solvents:
        return None
    schedule = [None for step in xdl_obj.steps]
    # Add solvents to schedule at solvent addition steps.
    for i, _, _, additions in iter_vessel_contents(
        xdl_obj.steps, graph_hardware, additions=True):
        for reagent in additions:
            cleaning_solvent = get_reagent_cleaning_solvent(
                reagent, xdl_obj.reagents, available_solvents)
            # Explicit None check as cleaning_solvent can be GENERIC_ORGANIC (0)
            if cleaning_solvent != None:
                schedule[i] = cleaning_solvent
    
    # Fill in blanks in schedule.
    # 1) Add organic solvents to steps that add a solvent blacklisted for
    # cleaning.
    organic_solvents = [(i, item)
                        for i, item in enumerate(schedule)
                        if item and item != 'water']
    for i in range(len(schedule)):
        if schedule[i] == GENERIC_ORGANIC:
            if organic_solvents:
                # Get closest organic solvent in schedule
                schedule[i] = sorted(
                    organic_solvents, key=lambda x: abs(x[0] - i))[0][1]
            else:
                # Choose random organic solvent.
                for solvent in available_solvents:
                    if solvent != 'water':
                        schedule[i] = solvent

    # 2) Treat consecutive SOLVENT_CONTAINING_STEPS as groups and if one step in
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

    # 3) Go forward applying last encountered solvent to every step in schedule.
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

    if reagent_name in CLEANING_SOLVENT_BLACKLIST:
        return GENERIC_ORGANIC
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
            # Don't clean after solid additions
            if not (type(step) == Add and step.mass):
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
            if i-1 >= 0:
                prev_step = xdl_obj.steps[i-1]
                clean = True
                # Don't clean certain steps if the solvent used for cleaning
                # is the same as the solvent being added.
                for step_type in NO_DUPLICATE_CLEAN_STEPS:
                    if type(prev_step) == step_type:
                        for item in ['reagent', 'solvent']:
                            if item in prev_step.properties:
                                if prev_step.properties[item] == solvent:
                                    clean = False
                if not clean:
                    continue
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
    available_solvents = get_available_solvents(xdl_obj)
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

#######################
### Vessel Cleaning ###
#######################

def get_vessel_emptying_steps(
    steps: List[Step], hardware: Hardware
) -> List[Tuple[int, str, Dict[str, VesselContents]]]:
    """Get steps at which a filter vessel is emptied. Also return full
    list of vessel contents dict at every step.
    
    Returns:
        List[Tuple[int, str, Dict[str, VesselContents]]]: List of tuples,
            format:
            [(step_index,
                filter_vessel_name,
                {vessel: VesselContents, ...},
                ...]
    """
    vessel_emptying_steps = []
    full_vessel_contents = []
    prev_vessel_contents = {}
    for i, _, vessel_contents in iter_vessel_contents(steps, hardware):
        full_vessel_contents.append(vessel_contents)
        for vessel, contents in vessel_contents.items():
            # If target vessel has just been emptied, append to vessel
            # emptying steps.
            if vessel in prev_vessel_contents:
                if (not contents.reagents
                    and prev_vessel_contents[vessel].reagents):
                    vessel_emptying_steps.append((i, vessel))
                    
        prev_vessel_contents = vessel_contents
    return vessel_emptying_steps

def get_clean_vessel_sequence(
    xdl_obj: 'XDL', hardware: Hardware) -> List[Tuple[int, str, str]]:
    """Get list of places where CleanVessel steps need to be added along with
    vessel name and solvent to use.
    
    Args:
        xdl_obj (XDL): XDL object to get vessel cleaning sequence for.
        hardware (Hardware): Hardware to use when finding emptying steps.
    
    Returns:
        List[Tuple[int, str, str]]: List of tuples like below.
            [(index_to_insert_clean_vessel_step, vessel, solvent_to_use)...]
    """
    # Get all solvents available for cleaning.
    available_solvents = get_available_solvents(xdl_obj)
    steps = xdl_obj.steps
    cleaning_sequence = []
    prev_vessel_contents = {}
    # Go through and find conditions where CleanVessel steps should be added.
    # Find solvents to clean with as well.
    for i, step, vessel_contents in iter_vessel_contents(steps, hardware):
        cleaning_solvents = []
        # Clean separation from_vessel
        if (type(step) == Separate
            and step.from_vessel not in [step.separation_vessel, step.to_vessel]):
            cleaning_solvents = get_clean_vessel_solvents(xdl_obj,
                                                          step.from_vessel,
                                                          prev_vessel_contents,
                                                          available_solvents)
        # Clean if vessel is empty the step after a dissolve step. This rule is
        # used as it guarantees that any solid is also gone from the vessel.
        elif (i > 0 and type(steps[i-1]) == Dissolve
              and not vessel_contents[steps[i-1].vessel].reagents):
            cleaning_solvents = get_clean_vessel_solvents(xdl_obj,
                                                          steps[i-1].vessel,
                                                          prev_vessel_contents,
                                                          available_solvents)
        # For all cleaning solvents found add them to the sequence along with
        # the vessel and position in procedure.
        for cleaning_solvent in cleaning_solvents:
            cleaning_sequence.append((
                i+1, step.from_vessel, cleaning_solvent))
        prev_vessel_contents = vessel_contents
    return cleaning_sequence
        
def get_clean_vessel_solvents(
    xdl_obj: 'XDL',
    vessel: str,
    prev_vessel_contents: Dict[str, VesselContents],
    available_solvents: List[str]
) -> List[str]:
    """Given empty vessel name and previous step vessel contents find what
    solvents should be used to clean the vessel.

    Args:
        xdl_obj (XDL): XDL object. Needed to access reagents list and check if
            any reagents have a specified cleaning reagent.
        vessel (str): Vessel to be cleaned.
        prev_vessel_contents (Dict[str, VesselContents]): All vessel contents at
            step before vessel is emptied and should be cleaned.
        available_solvents (List[str]): Solvents available for cleaning the
            vessel.

    Returns:
        List[str]: List of solvents that the vessel should be cleaned with.
    """
    solvents = []
    # Only clean vessel if it has had previous contents.
    if vessel in prev_vessel_contents:
        # Get all cleaning solvents associated with reagents that were in vessel.
        cleaning_solvents = [
            get_reagent_cleaning_solvent(
                reagent, xdl_obj.reagents, available_solvents)
            for reagent in prev_vessel_contents[vessel]
        ]
        for cleaning_solvent in cleaning_solvents:
            # If solvent found add it
            if cleaning_solvent:
                solvents.append(cleaning_solvent)
            # If unknown organic solvent found
            elif cleaning_solvent == GENERIC_ORGANIC:
                organic_solvents = [solvent
                                    for solvent in cleaning_solvents
                                    if solvent and solvent != 'water']
                # If there is another organic solvent associated with another
                # reagent from vessel contents, use this.
                if organic_solvents:
                    solvents.append(organic_solvents[0])
                # If there are no other organic solvents associated with the
                # reagents in vessel contents, use a random organic solvent.
                else:
                    organic_solvents = [solvent
                                        for solvent in  available_solvents
                                        if solvent != 'water']
                    if organic_solvents:
                        solvents.append(organic_solvents[0])
    return solvents

def add_vessel_cleaning_steps(xdl_obj: 'XDL', hardware: Hardware) -> 'XDL':
    """Add CleanVessel steps to xdl_obj at appropriate places. Rule is that a
    CleanVessel step should be added after a vessel has been emptied only if the
    step before the emptying step was a Dissolve step. This ensures that any
    solids in the vessel have also been removed before cleaning.
    
    Args:
        xdl_obj (XDL): XDL object to add CleanVessel steps to.

    Returns:
        XDL: XDL object with CleanVessel steps added at appropriate places.
    """
    clean_vessel_sequence = get_clean_vessel_sequence(xdl_obj, hardware)
    if clean_vessel_sequence:
        for i, vessel, solvent in reversed(clean_vessel_sequence):
            # If organic_cleaning_solvent is given use it otherwise use solvent
            # in synthesis.
            if solvent != 'water' and xdl_obj.organic_cleaning_solvent:
                solvent = xdl_obj.organic_cleaning_solvent
            xdl_obj.steps.insert(i, CleanVessel(vessel=vessel, solvent=solvent))
    xdl_obj.steps = add_clean_vessel_temps(xdl_obj.steps)
    return xdl_obj

def add_clean_vessel_temps(steps: List[List[Step]]) -> List[List[Step]]:
    """Add temperatures to CleanVessel steps. Priority is:
    1) Use explicitly given temperature.
    2) If solvent boiling point known use 80% of the boiling point.
    3) Use 30°C.
    
    Args:
        steps (List[List[Step]]): List of steps to add temperatures to
            CleanVessel steps
    
    Returns:
        List[List[Step]]: List of steps with temperatures added to CleanVessel
            steps.
    """
    for step in steps:
        if type(step) == CleanVessel:
            if step.temp == None:
                solvent = step.solvent.lower()
                if solvent in SOLVENT_BOILING_POINTS:
                    step.temp = (SOLVENT_BOILING_POINTS[solvent]
                                 * CLEAN_VESSEL_BOILING_POINT_FACTOR)
                else:
                    step.temp = 30
    return steps


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
    available_solvents = get_available_solvents(xdl_obj)
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
                        print(step.human_readable())
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
