from typing import Any, Union, Dict, List
import hashlib
import appdirs
import os
from abc import ABC, abstractmethod
from networkx.readwrite import node_link_data
from networkx import MultiDiGraph

from .utils import do_sanity_check
from ..steps.special_steps import Async, Await
from ..steps.base_steps import (
    Step, AbstractDynamicStep, AbstractAsyncStep, AbstractBaseStep)
from ..steps import NON_RECURSIVE_ABSTRACT_STEPS
from ..readwrite import xdl_to_xml_string
from ..errors import XDLError
from ..utils import get_logger
if False:
    from ..xdl import XDL

class AbstractXDLExecutor(ABC):
    _prepared_for_execution = False
    _xdl = None
    _warnings = []  # TODO: Remove this, no longer needed
    _graph = None
    logger = None

    def __init__(self, xdl: 'XDL' = None) -> None:
        if xdl:
            self.logger = xdl.logger
            self._xdl = xdl
        else:
            self.logger = get_logger()
        self._graph = None
        self._prepared_for_execution = False

    @abstractmethod
    def prepare_for_execution(
        self,
        graph_file: Union[str, Dict],
        **kwargs
    ) -> None:
        return

    def _graph_hash(self, graph=None):
        """Get SHA 256 hash of graph."""
        if not graph:
            graph = self._graph
        return hashlib.sha256(
            str(node_link_data(graph)).encode('utf-8')
        ).hexdigest()

    def perform_sanity_checks(self, steps: List[Step] = None) -> None:
        """Recursively perform sanity checks on every step in list."""
        if steps is None:
            steps = self._xdl.steps
        for step in steps:
            do_sanity_check(self._graph, step)

    def save_execution_script(self, save_path: str = '') -> None:
        """Generate and save execution script. Called at the end of
        prepare_for_execution.
        """
        # Generate execution script

        exescript = xdl_to_xml_string(
            self._xdl,
            graph_hash=self._graph_hash(),
            full_properties=True,
            full_tree=True
        )

        # Generate file in user data dir using hash of execution script
        # as file name.
        if not save_path:
            save_folder = appdirs.user_data_dir('xdl', 'croninlab')
            exescript_hash = hashlib.sha256(
                bytes(exescript, encoding='utf-8')).hexdigest()
            self.exe_save_path = os.path.join(
                save_folder,
                f'{exescript_hash}.xdlexe'
            )

        # Save execution script file path for later
        else:
            self.exe_save_path = save_path

        try:
            # Save execution script
            with open(self.exe_save_path, 'w') as fd:
                fd.write(exescript)
        except FileNotFoundError:
            self.logger.warning(
                f'Unable to save execution script in {save_folder}.')

    def add_internal_properties(
        self, graph: MultiDiGraph, steps: List[Step]
    ) -> None:
        """Recursively add internal properties to all steps and substeps in
        given list of steps.

        Args:
            steps (List[Step]): List of steps to add internal properties to.
        """

        # Iterate through each step
        for step in steps:

            # Prepare the step for execution
            step.on_prepare_for_execution(graph)

            # Special case for Dynamic steps
            if isinstance(step, AbstractDynamicStep):
                step.prepare_for_execution(graph, self)

            # If the step has children, add internal properties to all children
            if 'children' in step.properties:
                self.add_internal_properties(graph, step.children)

            # Recursive steps, add internal proerties to all substeps
            if not isinstance(step, NON_RECURSIVE_ABSTRACT_STEPS):
                self.add_internal_properties(graph, step.steps)

    def prepare_dynamic_steps_for_execution(self, step, graph):
        if isinstance(step, AbstractDynamicStep):
            if not hasattr(step, 'start_block'):
                step.prepare_for_execution(graph, self)
            for substep in step.start_block:
                self.prepare_dynamic_steps_for_execution(substep, graph)
        elif not isinstance(step, (AbstractAsyncStep, AbstractBaseStep)):
            for substep in step.steps:
                self.prepare_dynamic_steps_for_execution(substep, graph)

    def execute_step(self, platform_controller, step, async_steps=None):
        if hasattr(platform_controller, 'graph') and platform_controller.graph:
            self.prepare_dynamic_steps_for_execution(
                step, platform_controller.graph.graph)

        self.logger.info(step.name)

        try:
            # Wait for async step to finish executing
            if type(step) == Await:
                keep_going = step.execute(async_steps, self.logger)

            # Normal step execution
            else:
                keep_going = step.execute(
                    platform_controller, self.logger)

        # Raise any errors during step execution.
        except Exception as e:
            self.logger.info(
                'Step failed {0} {1}'.format(
                    type(step), step.properties))
            raise e

        return keep_going

    def execute(self, platform_controller: Any) -> None:
        """Execute XDL procedure with given chempiler. The same graph must be
        passed to the chempiler and to prepare_for_execution.

        Args:
            chempiler (chempiler.Chempiler): Chempiler object to execute XDL
                                             with.
        """
        # XDLEXE, check graph hashes match
        if (not self._prepared_for_execution and self._xdl.compiled):
            # Currently, this check only performed for Chemputer
            if hasattr(platform_controller, 'graph'):
                if self._xdl.graph_sha256 == self._graph_hash(
                        platform_controller.graph.graph):
                    self.logger.info('Executing xdlexe, graph hashes match.')
                    self._prepared_for_execution = True
                else:
                    raise XDLError(
                        'Trying to execute xdlexe on different graph than it\
 was made with.')

        if self._prepared_for_execution:
            self.logger.info(
                f'Procedure\n---------\n\n{self._xdl.human_readable()}')
            self.logger.info('Execution\n---------\n')
            async_steps = []

            for step in self._xdl.steps:

                # Store all Async steps so that they can be awaited.
                if type(step) == Async:
                    async_steps.append(step)

                keep_going = self.execute_step(
                    platform_controller, step, async_steps=async_steps)

                if not keep_going:
                    return
        else:
            self.logger.error(
                'Not prepared for execution. Prepare by calling\
 xdlexecutor.prepare_for_execution with your graph.')
