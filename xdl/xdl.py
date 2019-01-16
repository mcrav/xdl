from .constants import *
from .steps import *
from .utils.namespace import BASE_STEP_OBJ_DICT
from .readwrite.interpreter import xdl_file_to_objs, xdl_str_to_objs
from .readwrite import XDLGenerator
from .safety import procedure_is_safe
import os
import re
import copy

class XDL(object):
    """
    Interpets XDL (file or str) and provides the following public methods:.
    
    Public Methods:
        as_human_readable -- Returns human readable description of the procedure.
        print_human_readable -- Prints human readable description of the procedure.
        print_full_xdl_tree -- Prints reasonably human readable visualisation of 
                               the nested XDL steps.
        as_string -- Return XDL as XML string.
        save -- Save XDL as XML.
        save_chempiler_script -- Save XDL base steps as Python chempiler script.
        as_literal_chempiler_code -- Return XDL base steps as Python chempiler script.
        iter_vessel_contents -- Return iterator of vessel_contents at each step.
    """
    def __init__(
        self, xdl_file=None, xdl_str=None, steps=[], hardware=None, reagents=[]):
        """Init method for XDL object.
        One of xdl_file, xdl_str or (steps, hardware and reagents) must be given.
        
        Args:
            xdl_file(str, optional): Path to XDL file.
            xdl_str(str, optional): XDL str. 
            steps (List[Step], optional): List of Step objects.
            hardware (Hardware, optional): Hardware object containing all 
                components in XDL.
            reagents (List[Reagent], optional): List of Reagent objects.
        """
        self._xdl_file = None
        if xdl_file:
            self._xdl_file = xdl_file
            self.steps, self.hardware, self.reagents = xdl_file_to_objs(xdl_file)
        elif xdl_str:
            self.steps, self.hardware, self.reagents = xdl_str_to_objs(xdl_str)
        elif steps and hardware and reagents:
            self.steps, self.hardware, self.reagents = steps, hardware, reagents
        else:
            print("Can't create XDL object. Insufficient args given to __init__ method.")
        if self.steps:
            self._xdlgenerator = XDLGenerator(
                steps=self.steps, hardware=self.hardware, reagents=self.reagents)

    def _get_exp_id(self, default='xdl_exp'):
        """Get experiment ID name to give to the Chempiler."""
        if self._xdl_file:
            return os.path.splitext(os.path.split(self._xdl_file)[-1])[0]
        else:
            return default

    def iter_vessel_contents(self, additions=False):
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
        for i, step in enumerate(self.steps):
            additions_l = []
            if type(step) == Add:
                additions_l.append((step.reagent, step.volume))
                vessel_contents.setdefault(step.vessel, []).append(
                    (step.reagent, step.volume))

            elif type(step) == MakeSolution:
                additions_l.append((step.solvent, step.solvent_volume))
                vessel_contents.setdefault(step.vessel, []).append(
                    (step.solvent, step.solvent_volume))
                for solute in step.solutes:
                    additions_l.append((solute, 0))
                    vessel_contents[step.vessel].append((solute, 0))

            elif type(step) == Extract:
                if step.from_vessel != step.separation_vessel:
                    vessel_contents[step.from_vessel].clear()
                    additions_l.extend(vessel_contents[step.from_vessel])
                vessel_contents.setdefault(step.to_vessel, []).append(
                    (step.solvent, step.solvent_volume))
                # vessel_contents.setdefault(step.waste_vessel, []).extend(
                #   vessel_contents[step.from_vessel])
                additions_l.append((step.solvent, step.solvent_volume))

            elif type(step) == WashSolution:
                additions_l.extend(vessel_contents[step.from_vessel])
                additions_l.append((step.solvent, step.solvent_volume))
                vessel_contents[step.to_vessel] = copy.copy(
                    vessel_contents[step.from_vessel])
                if not step.from_vessel == step.to_vessel:
                    vessel_contents[step.from_vessel].clear()

            elif type(step) == WashFilterCake:
                additions_l.append((step.solvent, step.volume))

            elif type(step) == Filter:
                vessel_contents.setdefault(step.filter_vessel, []).clear()

            elif type(step) == CMove:
                additions_l.extend(vessel_contents[step.from_vessel])
                vessel_contents.setdefault(step.to_vessel, []).extend(
                    vessel_contents[step.from_vessel])
                vessel_contents[step.from_vessel].clear()

            elif type(step) == Transfer:
                from_vessel = step.from_vessel
                if ('filter' in from_vessel and ('top' in from_vessel or 
                    'bottom' in from_vessel)):
                    from_vessel = from_vessel.split('_')[1]
                additions_l.extend(vessel_contents[from_vessel])
                vessel_contents.setdefault(step.to_vessel, []).extend(
                    vessel_contents[from_vessel])
                vessel_contents[from_vessel].clear()

            if additions_l:
                for vessel in list(vessel_contents.keys()):
                    if 'filter' in vessel and 'top' in vessel:
                        bottom_vessel = vessel.split('_')[1]
                        if bottom_vessel in vessel_contents:
                            vessel_contents[bottom_vessel].extend(
                                vessel_contents[vessel])
                        else:
                            vessel_contents[bottom_vessel] = vessel_contents[vessel]
                        vessel_contents[vessel] = []

            if additions:
                yield (i, step, copy.deepcopy(vessel_contents), additions_l)
            else:
                yield (i, step, copy.deepcopy(vessel_contents))

    def _get_full_xdl_tree(self):
        """
        Return list of all steps after unpacking nested steps.
        Root steps are included followed by all their children in order, 
        recursively.

        Returns:
            List[Step]
        """
        tree = []
        for step in self.steps:
            tree.extend(climb_down_tree(step))
        return tree

    def print_full_xdl_tree(self):
        """Print nested structure of all steps in XDL procedure."""
        print('\n')
        print('Operation Tree\n--------------\n')
        for step in self.steps:
            climb_down_tree(step, print_tree=True)
        print('\n')

    def as_literal_chempiler_code(self, dry_run=False):
        """
        Returns string of literal chempiler code built from steps.

        Args:
            dry_run (bool, optional): Defaults to False. 
                Don't include Wait steps in dry run.
        """
        s = f'from chempiler import Chempiler\n\nchempiler = Chempiler(r"{self._get_exp_id(default="xdl_simulation")}", "{self.graphml_file}", "output_dir", False)\n\nchempiler.start_recording()\nchempiler.camera.change_recording_speed(14)\n'
        full_tree = self._get_full_xdl_tree()
        base_steps = list(BASE_STEP_OBJ_DICT.values())
        for step in full_tree:
            if step in self.steps:
                s += f'\n# {step.human_readable}\n'
            if type(step) in base_steps:
                if dry_run and type(step) == CWait:
                    new_step = copy.deepcopy(step)
                    new_step.time = 2
                    step = new_step
                s += re.sub(r'([a-zA-Z][a-z|A-Z|_|0-9]+)([\,|\)])', 
                            r"'\1'\2", 
                            step.literal_code) + '\n'
        return s

    def save_chempiler_script(self, save_path, dry_run=False):
        """Save a chempiler script from the given steps."""
        with open(save_path, 'w') as fileobj:
            fileobj.write(self.as_literal_chempiler_code(dry_run=dry_run))

    def as_human_readable(self):
        """Return human-readable English description of XDL procedure.
        
        Returns:
            str: Human readable description of procedure.
        """
        s = ''
        for step in self.steps:
            s += f'{step.human_readable}\n'
        return s

    def print_full_human_readable(self):
        """Print human-readable English description of XDL procedure."""
        print('Synthesis Description\n---------------------\n')
        print(self.as_human_readable())
        print('\n')

    def as_string(self):
        return self._xdlgenerator.as_string()

    def save(self, save_file):
        self._xdlgenerator.save(save_file)


def climb_down_tree(step, print_tree=False, lvl=0):
    """Go through given step's sub steps recursively until base steps are reached.
    Return list containing the step, all sub steps and all base steps.
    
    Args:
        step (Step): step to find all sub steps for.
        print_tree (bool, optional): Defaults to False.
            Print tree as well as returning it.
        lvl (int, optional): Level of recursion. Defaults to 0. 
            Used to determine indent level when print_tree=True.
    
    Returns:
        List[Step]: List of all Steps involved with given step. 
                    Includes given step, and all sub steps all the way down to 
                    base steps.
    """
    indent = '  '
    base_steps = list(BASE_STEP_OBJ_DICT.values())
    tree = [step]
    if print_tree:
        print(f'{indent*lvl}{step.name}' + ' {')
    if type(step) in base_steps:
        return tree
    else:
        lvl += 1
        for step in step.steps:
            if type(step) in base_steps:
                if print_tree:
                    print(f'{indent*lvl}{step.name}')
                tree.append(step)
                continue
            else:
                tree.extend(
                    climb_down_tree(step, print_tree=print_tree, lvl=lvl))
        if print_tree:
            print(f'{indent*(lvl-1)}' + '}')
    return tree