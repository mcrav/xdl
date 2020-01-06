from typing import Any
import hashlib
import appdirs
import os
from abc import ABC, abstractmethod
from networkx.readwrite import node_link_data
from ..steps.special_steps import Async, Await
from ..readwrite.generator import XDLGenerator
from ..utils.errors import XDLError
from ..utils import get_logger

class AbstractXDLExecutor(ABC):
    _prepared_for_execution = False
    _xdl = None
    logger = None

    def __init__(self, xdl: 'XDL' = None) -> None:
        if xdl:
            self.logger = xdl.logger
            self._xdl = xdl
        else:
            self.logger = get_logger()
        self._warnings = []
        self._raw_graph = None
        self._graph = None
        self._prepared_for_execution = False

    @abstractmethod
    def prepare_for_execution(self, graph):
        return

    def _graph_hash(self, graph=None):
        """Get SHA 256 hash of graph."""
        if not graph: graph = self._raw_graph
        return hashlib.sha256(
            str(node_link_data(graph)).encode('utf-8')
        ).hexdigest()

    def save_execution_script(self, save_path: str = '') -> None:
        """Generate and save execution script. Called at the end of
        prepare_for_execution.
        """
        # Generate execution script

        exescript = XDLGenerator(
            self._xdl.steps,
            self._xdl.hardware,
            self._xdl.reagents,
            graph_hash=self._graph_hash(),
            full_properties=True,
            full_tree=True
        ).as_string()

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
        else: self.exe_save_path = save_path

        try:
            # Save execution script
            with open(self.exe_save_path, 'w')  as fd:
                fd.write(exescript)
        except FileNotFoundError:
            self.logger.warning(f'Unable to save execution script in {save_folder}.')

    def call_on_prepare_for_execution(self, step):
        step.on_prepare_for_execution(self._graph)
        for substep in step.steps:
            self.call_on_prepare_for_execution(substep)

    def execute(self, platform_controller: Any) -> None:
        """Execute XDL procedure with given chempiler. The same graph must be
        passed to the chempiler and to prepare_for_execution.

        Args:
            chempiler (chempiler.Chempiler): Chempiler object to execute XDL
                                             with.
        """
        if not self._prepared_for_execution and hasattr(self._xdl, 'graph_sha256'):
            # Currently, this check only performed for Chemputer
            if hasattr(platform_controller, 'graph'):
                if self._xdl.graph_sha256 == self._graph_hash(
                    platform_controller.graph.raw_graph):
                    self.logger.info('Executing xdlexe, graph hashes match.')
                    self._prepared_for_execution = True
                else:
                    raise XDLError(
                'Trying to execute xdlexe on different graph than it was made with.')

        if self._prepared_for_execution:
            self._xdl.print_full_xdl_tree()
            self._xdl.log_human_readable()
            self.logger.info('Execution\n---------\n')
            async_steps = []

            for step in self._xdl.steps:

                # Store all Async steps so that they can be awaited.
                if type(step) == Async:
                    async_steps.append(step)

                self.logger.info(step.name)
                try:
                    # Wait for async step to finish executing
                    if type(step) == Await:
                        keep_going = step.execute(async_steps, self.logger)

                    # Normal step execution
                    else:
                        keep_going = step.execute(platform_controller, self.logger)

                # Raise any errors during step execution.
                except Exception as e:
                    self.logger.info(
                        'Step failed {0} {1}'.format(
                            type(step), step.properties))
                    raise e
                if not keep_going:
                    return
        else:
            self.logger.error(
                'Not prepared for execution. Prepare by calling xdlexecutor.prepare_for_execution with your graph.')
