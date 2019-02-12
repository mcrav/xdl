from .constants import *
from .steps import *
from .utils.namespace import BASE_STEP_OBJ_DICT
from .utils import parse_bool
from .readwrite.interpreter import xdl_file_to_objs, xdl_str_to_objs
from .readwrite import XDLGenerator
from .safety import procedure_is_safe
from .execution import XDLExecutor
import os
import re
import logging
import copy

class XDL(object):
    """
    Interpets XDL (file or str) and provides an object for further use.
    """
    def __init__(self, xdl=None, steps=None, hardware=None, reagents=None,
                       logger=None):
        """Init method for XDL object.
        One of xdl or (steps, hardware and reagents) must be given.
        
        Args:
            xdl(str, optional): Path to XDL file or XDL str.
            steps (List[Step], optional): List of Step objects.
            hardware (Hardware, optional): Hardware object containing all 
                components in XDL.
            reagents (List[Reagent], optional): List of Reagent objects.

        Raises:
            ValueError: If insufficient args provided to instantiate object.
        """
        self.logger = logger
        if not logger:
            self.logger = logging.getLogger('xdl_logger')
        self._xdl_file = None
        self.auto_clean = DEFAULT_AUTO_CLEAN
        self.organic_cleaning_reagent = DEFAULT_ORGANIC_CLEANING_SOLVENT
        self.aqueous_cleaning_reagent = DEFAULT_AQUEOUS_CLEANING_SOLVENT
        self.dry_run = False
        if xdl:
            parsed_xdl = {}
            if os.path.exists(xdl):
                self._xdl_file = xdl
                parsed_xdl = xdl_file_to_objs(xdl, self.logger)
            else:
                parsed_xdl = xdl_str_to_objs(xdl, self.logger)
            if parsed_xdl:
                self.steps = parsed_xdl['steps']
                self.hardware = parsed_xdl['hardware']
                self.reagents = parsed_xdl['reagents']
                # Get attrs from <Synthesis> tag.
                for camelAttr, snakeAttr in [
                    ('autoClean', 'auto_clean'),
                    ('organicCleaningReagent', 'organic_cleaning_reagent'),
                    ('aqueousCleaningReagent', 'aqueous_cleaning_reagent'),
                    ('dryRun', 'dry_run'),
                ]:
                    if camelAttr in parsed_xdl:
                        self.__setattr__(snakeAttr, parsed_xdl[camelAttr])
                
        elif (steps is not None
              and reagents is not None
              and hardware is not None):
            self.steps, self.hardware, self.reagents = steps, hardware, reagents
        else:
            raise ValueError(
                "Can't create XDL object. Insufficient args given to __init__ method.")

    def _get_exp_id(self, default='xdl_exp'):
        """Get experiment ID name to give to the Chempiler."""
        if self._xdl_file:
            return os.path.splitext(os.path.split(self._xdl_file)[-1])[0]
        else:
            return default

    def climb_down_tree(self, step, print_tree=False, lvl=0):
        """Go through given step's sub steps recursively until base steps are
        reached. Return list containing the step, all sub steps and all base
        steps.
        
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
            self.logger.info('{0}{1}'.format(indent*lvl, step.name))
        if type(step) in base_steps:
            return tree
        else:
            lvl += 1
            for step in step.steps:
                if type(step) in base_steps:
                    if print_tree:
                        self.logger.info('{0}{1}'.format(indent*lvl, step.name))
                    tree.append(step)
                    continue
                else:
                    tree.extend(
                        self.climb_down_tree(
                            step, print_tree=print_tree, lvl=lvl))
        return tree

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
            tree.extend(self.climb_down_tree(step))
        return tree

    def print_full_xdl_tree(self):
        """Print nested structure of all steps in XDL procedure."""
        self.logger.info('\nOperation Tree\n--------------\n')
        for step in self.steps:
            self.climb_down_tree(step, print_tree=True)
        self.logger.info('\n')

    def as_literal_chempiler_code(self, dry_run=False):
        """
        Returns string of literal chempiler code built from steps.

        Args:
            dry_run (bool, optional): Defaults to False. 
                Don't include Wait steps in dry run.
        """
        s = 'from chempiler import Chempiler\n\nchempiler = Chempiler(r"{self._get_exp_id(default="xdl_simulation")}", "{self.graphml_file}", "output_dir", False)\n\nchempiler.start_recording()\nchempiler.camera.change_recording_speed(14)\n'
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
                            step.literal_code)
                s += '\n'
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
        for i, step in enumerate(self.steps):
            s += f'{i+1}) {step.human_readable}\n'
        return s

    def print_full_human_readable(self):
        """Print human-readable English description of XDL procedure."""
        self.logger.info('Synthesis Description\n---------------------\n')
        self.logger.info('{0}\n'.format(self.as_human_readable()))

    def save_human_readable(self, save_file):
        """Save human readable description of procedure to given path."""
        with open(save_file, 'w') as fileobj:
            fileobj.write(self.as_human_readable())

    def as_string(self):
        """Return XDL str of procedure."""
        self._xdlgenerator = XDLGenerator(steps=self.steps,
                                          hardware=self.hardware,
                                          reagents=self.reagents)
        return self._xdlgenerator.as_string()

    def save(self, save_file):
        """Save as XDL file.
        
        Args:
            save_file (str): File path to save XDL to.
        """
        self._xdlgenerator = XDLGenerator(steps=self.steps,
                                          hardware=self.hardware,
                                          reagents=self.reagents)
        self._xdlgenerator.save(save_file)

    def scale_procedure(self, scale):
        """Scale all volumes in procedure.

        Args:
            scale (float): Number to scale all volumes by.
        """
        for step in self.steps:
            for prop in step.properties:
                if 'volume' in prop:
                    val = step.properties[prop]
                    if val:
                        step.properties[prop] = float(val) * scale
                        print(step.properties[prop])
                        print(val)
                        print('------')
        for step in self.steps:
            print(step.properties)

    def prepare_for_execution(self, graph_file):
        """Check hardware compatibility and prepare XDL for execution on given 
        setup.
        
        Args:
            graph_file (str, optional): Path to graph file. May be GraphML file,
                                        JSON file with graph in node link format,
                                        or dict containing graph in same format
                                        as JSON file.
        """
        self.executor = XDLExecutor(self)
        self.executor.prepare_for_execution(graph_file)

    def execute(self, chempiler):
        """Execute XDL using given Chempiler object. self.prepare_for_execution
        must have been called before calling thie method.
        
        Args:
            chempiler (chempiler.Chempiler): Chempiler object instantiated with
                modules and graph to run XDL on.
        """
        if self.executor:
            self.executor.execute(chempiler)
        else:
            raise RuntimeError(
                'XDL executor not available. Call prepare_for_execution before trying to execute.')