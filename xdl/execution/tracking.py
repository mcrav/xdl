from typing import List, Dict, Generator, Optional, Union, Tuple
import copy
from .utils import VesselContents
from ..steps import Step, Filter, WashFilterCake, Dry, Separate, CMove
from ..hardware import Hardware

def iter_vessel_contents(
    steps: List[Step], hardware: Hardware, additions: bool = False
) -> Generator[
    Tuple[
        int,
        Step,
        Dict[str, VesselContents],
        Optional[List[str]]],
    None, None]:
    """Iterator. Allows you to track vessel contents as they change
    throughout the steps.

    Args:
        additions (bool, optional): Defaults to False. 
            If True, list of what contents were added that step is yielded.
    
    Yields:
        Tuple: (i, step, contents, {additions})
                i -- Index of step.
                step -- Step object of step.
                contents -- Dict of contents of all vessels after step.
                additions (optional) -- List of contents added during step.
    """
    vessel_contents = {}
    for flask in hardware.flasks:
        vessel_contents[flask.id] = VesselContents(
            [flask.chemical], flask.current_volume)
    for i, step in enumerate(steps):
        additions_l = []

        # Handle separate step differently.
        if type(step) == Separate:
            # Add vessels to vessel_contents if they aren't there.
            for vessel in [step.from_vessel, step.to_vessel,
                            step.waste_phase_to_vessel]:
                vessel_contents.setdefault(
                    vessel, VesselContents([], hardware[vessel].current_volume))
            # Empty from_vessel
            from_reagents = vessel_contents[step.from_vessel].reagents
            from_volume = vessel_contents[step.from_vessel].volume
            vessel_contents[step.from_vessel].reagents = []
            vessel_contents[step.from_vessel].volume = 0
            # Add from_vessel contents to to_vessel and waste_phase_to_vessel
            vessel_contents[step.to_vessel].reagents.extend(
                from_reagents)
            vessel_contents[step.waste_phase_to_vessel].reagents.extend(
                from_reagents)
            # If extraction add solvent to to_vessel
            # and from_vessel volume to waste_phase_to_vessel.
            if step.purpose == 'extract':
                vessel_contents[step.to_vessel].reagents.append(step.solvent)
                vessel_contents[step.to_vessel].volume += step.solvent_volume
                vessel_contents[
                    step.waste_phase_to_vessel].volume += from_volume
            # If wash add solvent to waste_phase_to_vessel
            # and from_vessel volume to to_vessel.
            elif step.purpose == 'wash':
                vessel_contents[
                    step.waste_phase_to_vessel].reagents.append(step.solvent)
                vessel_contents[
                    step.waste_phase_to_vessel].volume += step.solvent_volume
                vessel_contents[step.to_vessel].volume += from_volume

        elif type(step) in [Filter, WashFilterCake, Dry]:
            for vessel in [step.filter_vessel, step.waste_vessel]:
                vessel_contents.setdefault(
                    vessel, VesselContents([], hardware[vessel].current_volume))

            filter_reagents = vessel_contents[step.filter_vessel].reagents
            filter_volume = vessel_contents[step.filter_vessel].volume
            vessel_contents[step.filter_vessel].reagents = []
            vessel_contents[step.filter_vessel].volume = 0
            vessel_contents[step.waste_vessel].reagents.extend(filter_reagents)
            vessel_contents[step.waste_vessel].volume += filter_volume

        elif type(step) == Dry:
            # This is necessary to stop move command putting filter into
            # negative volume
            pass 

        # Handle normal Move steps.
        else:
            for from_vessel, to_vessel, volume in get_movements(step):
                empty_from_vessel = False
                # Add vessels to vessel_contents if they aren't there.
                for vessel in [from_vessel, to_vessel]:
                    print('VESSEL', vessel, step)
                    vessel_contents.setdefault(
                        vessel,
                        VesselContents([], hardware[vessel].current_volume))

                # Get actual volume if volume is 'all'
                if volume == 'all':
                    volume = vessel_contents[from_vessel].volume
                    empty_from_vessel = True
                # Add volume to to_vessel
                vessel_contents[to_vessel].volume += volume 
                vessel_contents[to_vessel].reagents.extend(
                    vessel_contents[from_vessel].reagents)
                additions_l.extend(vessel_contents[from_vessel].reagents)
                # Remove volume from from_vessel.
                vessel_contents[from_vessel].volume -= volume
                if vessel_contents[from_vessel].volume <= 0:
                    vessel_contents[from_vessel].reagents = []
                # Extend list of reagents added in the step.
                # Empty from_vessel if 'all' volume specified.
                if empty_from_vessel:
                    vessel_contents[from_vessel].volume = 0
                    vessel_contents[from_vessel].reagents = []
    
        if additions:
            yield (
                i,
                step,
                copy.deepcopy(vessel_contents),
                copy.deepcopy(additions_l)
            )
        else:
            yield (i, step, copy.deepcopy(vessel_contents))

def get_movements(step: Step) -> List[Tuple[str, str, float]]:
    """Get all liquid movements associated with given step. Works recursively
    going down step tree until a CMove step is encountered and then the
    liquid movement from the CMove step is added to the movements list.
    
    Args:
        step (Step): Step to get liquid movements from.
    
    Returns:
        List[Tuple]: List of tuples (from_vessel, to_vessel, volume) 
    """
    movements = []
    # All movements are obtained from CMove.
    if type(step) == CMove:
        movements.append((step.from_vessel, step.to_vessel, step.volume))
    # Recursive calls until CMove steps encountered.
    elif hasattr(step, 'steps'):
        for sub_step in step.steps:
            movements.extend(get_movements(sub_step))
    return movements