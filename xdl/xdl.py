import os
import sys
import re
import logging
import inspect
import copy
from typing import List

from .constants import *
from .graph.generator import GraphGenerator
from .steps import *
from .steps import steps_synthesis
from .steps import steps_utility
from .steps import steps_base
from .utils.namespace import BASE_STEP_OBJ_DICT
from .utils import parse_bool, initialise_logger
from .readwrite.interpreter import xdl_file_to_objs, xdl_str_to_objs
from .readwrite import XDLGenerator
from .safety import procedure_is_safe
from .execution import XDLExecutor
from .hardware import Hardware
from .reagents import Reagent

# For type annotations
if False:
    from chempiler import Chempiler

class XDL(object):
    """
    Interpets XDL (file or str) and provides an object for further use.
    """
    def __init__(
        self,
        xdl: str = None,
        steps: List[Step] = None,
        hardware: Hardware = None,
        reagents: List[Reagent] = None,
        logger: logging.Logger = None
    ) -> None:
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
            if not self.logger.hasHandlers():
                self.logger = initialise_logger(self.logger)
                
        self._xdl_file = None
        self.auto_clean = DEFAULT_AUTO_CLEAN
        self.organic_cleaning_solvent = None 
        self.aqueous_cleaning_solvent = DEFAULT_AQUEOUS_CLEANING_SOLVENT
        self.dry_run = False
        self.filter_dead_volume_method = 'inert_gas'
        self.filter_dead_volume_solvent = None
        self.prepared = False
        if xdl:
            parsed_xdl = {}
            if os.path.exists(xdl):
                self._xdl_file = xdl
                parsed_xdl = xdl_file_to_objs(xdl, self.logger)
            # Check XDL is XDL str and not just mistyped XDL file path.
            elif '<Synthesis>' in xdl and '<Procedure>' in xdl:
                parsed_xdl = xdl_str_to_objs(xdl, self.logger)
            else:
                raise ValueError(
                    f"Can't instantiate XDL from this: \n{xdl}"
                )
            if parsed_xdl:
                self.steps = parsed_xdl['steps']
                self.hardware = parsed_xdl['hardware']
                self.reagents = parsed_xdl['reagents']
                # Get attrs from <Synthesis> tag.
                for k, v in parsed_xdl['procedure_attrs'].items():
                    setattr(self, k, v)
                self.executor = XDLExecutor(self)
            
            else:
                self.logger.info('Invalid XDL given.')
                
        elif (steps is not None
              and reagents is not None
              and hardware is not None):
            self.steps, self.hardware, self.reagents = steps, hardware, reagents
            self.executor = XDLExecutor(self)
        else:
            raise ValueError(
                "Can't create XDL object. Insufficient args given to __init__ method.")

    def _get_exp_id(self, default: str = 'xdl_exp') -> str:
        """Get experiment ID name to give to the Chempiler."""
        if self._xdl_file:
            return os.path.splitext(os.path.split(self._xdl_file)[-1])[0]
        return default

    def climb_down_tree(
        self, step: Step, print_tree: bool = False, lvl: int = 0
    ) -> List[Step]:
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

    def _get_full_xdl_tree(self) -> List[Step]:
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

    def print_full_xdl_tree(self) -> None:
        """Print nested structure of all steps in XDL procedure."""
        self.logger.info('\nOperation Tree\n--------------\n')
        for step in self.steps:
            self.climb_down_tree(step, print_tree=True)
        self.logger.info('\n')
            
    def as_human_readable(self) -> str:
        """Return human-readable English description of XDL procedure.
        
        Returns:
            str: Human readable description of procedure.
        """
        s = ''
        for i, step in enumerate(self.steps):
            s += f'{i+1}) {step.human_readable}\n'
        return s

    def print_full_human_readable(self) -> None:
        """Print human-readable English description of XDL procedure."""
        self.logger.info('Synthesis Description\n---------------------\n')
        self.logger.info('{0}\n'.format(self.as_human_readable()))

    def save_human_readable(self, save_file: str) -> None:
        """Save human readable description of procedure to given path."""
        with open(save_file, 'w') as fileobj:
            fileobj.write(self.as_human_readable())

    def as_string(self) -> str:
        """Return XDL str of procedure."""
        self._xdlgenerator = XDLGenerator(steps=self.steps,
                                          hardware=self.hardware,
                                          reagents=self.reagents)
        return self._xdlgenerator.as_string()

    def save(self, save_file: str, full_properties: bool = False) -> str:
        """Save as XDL file.
        
        Args:
            save_file (str): File path to save XDL to.
            full_properties (bool): If True, all properties will be included.
                If False, only properties that differ from their default values
                will be included.
                Including full properties is recommended for making XDL files
                that will stand the test of time, as defaults may change in new
                versions of XDL.
        """
        self._xdlgenerator = XDLGenerator(steps=self.steps,
                                          hardware=self.hardware,
                                          reagents=self.reagents,
                                          full_properties=full_properties)
        self._xdlgenerator.save(save_file)

    def scale_procedure(self, scale: float) -> None:
        """Scale all volumes in procedure.

        Args:
            scale (float): Number to scale all volumes by.
        """
        for step in self.steps:
            if step.name not in UNSCALED_STEPS:
                for prop, val in step.properties.items():
                    if 'volume' in prop and type(val) == float:
                        if val:
                            step.properties[prop] = float(val) * scale

    def prepare_for_execution(
        self, graph_file: str, interactive: bool = True) -> None:
        """Check hardware compatibility and prepare XDL for execution on given 
        setup.
        
        Args:
            graph_file (str, optional): Path to graph file. May be GraphML file,
                                        JSON file with graph in node link format,
                                        or dict containing graph in same format
                                        as JSON file.
        """
        if not self.prepared:
            self.executor.prepare_for_execution(graph_file, interactive=interactive)
            self.prepared = True
        else:
            self.logger.warn('Cannot call prepare for execution twice on same XDL object.')

    def execute(self, chempiler: 'Chempiler') -> None:
        """Execute XDL using given Chempiler object. self.prepare_for_execution
        must have been called before calling thie method.
        
        Args:
            chempiler (chempiler.Chempiler): Chempiler object instantiated with
                modules and graph to run XDL on.
        """
        if self.prepared:
            if hasattr(self, 'executor'):
                self.executor.execute(chempiler)
            else:
                raise RuntimeError(
                    'XDL executor not available. Call prepare_for_execution before trying to execute.')
        else:
            self.logger.warn('prepare_for_execution must be called before executing.')

    @property
    def base_steps(self):
        return [step
                for step in self._get_full_xdl_tree()
                if isinstance(step, AbstractBaseStep)]
