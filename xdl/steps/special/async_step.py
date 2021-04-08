from typing import Union, List, Callable
import logging

from ..core import (
    Step,
    AbstractAsyncStep,
)
from ..logging import execution_log_str, finished_executing_step_msg

if False:
    from chempiler import Chempiler


class Async(AbstractAsyncStep):
    """Wrapper to execute a step or sequence of steps asynchronously.

    Use like this:

    ``async_stir_step = Async(Stir(vessel=filter, time=3600))``

    Can be stopped in between steps by calling ``async_stir_step.kill()``

    Args:
        children (Union[Step, List[Step]]): Step object or list of Step objects
            to execute asynchronously.
        pid (str): Process ID. Optional, but must be given if using
            :py:class:``Await`` later in procedure.
        on_finish (Callable): Callback function to call after execution of steps
            has finished.
    """

    PROP_TYPES = {
        'children': Union[Step, List[Step]],
        'pid': str,
        'on_finish': Callable,
    }

    def __init__(
        self,
        children: Union[Step, List[Step]],
        pid: str = None,
        on_finish: Callable = None,
        **kwargs
    ):
        super().__init__(locals())

        if type(children) != list:
            self.children = [children]

        self.steps = self.children

        self._should_end = False
        self.finished = False

    def async_execute(
        self, chempiler: 'Chempiler',
        logger: logging.Logger = None,
        level: int = 0,
        step_indexes: List[int] = None,
    ) -> None:
        # Get logger if not passed
        if not logger:
            logger = logging.getLogger('xdl')

        # Get default step indexes if they are not passed
        if step_indexes is None:
            step_indexes = [0]

        # Log step start if it is executed by itself (level == 0), as there will
        # be no other context logging the step start.
        if level == 0:
            logger.info(execution_log_str(self, step_indexes))

        # Get message for end before step_indexes are changed by substeps
        finish_msg = finished_executing_step_msg(self, step_indexes)

        # Execute async children steps
        for i, step in enumerate(self.children):
            # Update step indexes
            step_indexes.append(0)
            step_indexes[level + 1] = i
            step_indexes = step_indexes[:level + 2]

            # Log step start
            logger.info(execution_log_str(step, step_indexes))

            # Execute step
            keep_going = step.execute(
                chempiler, logger, level=level + 1, step_indexes=step_indexes)

            # Break out of loop if either stop flag is ``True``
            if not keep_going or self._should_end:
                self.finished = True
                logger.info(finish_msg)
                return

        # Finish and log step finish
        self.finished = True
        if self.on_finish:
            self.on_finish()
        logger.info(finish_msg)
        return True

    def human_readable(self, language='en'):
        human_readable = 'Asynchronous:\n'
        for step in self.children:
            human_readable += f'    {step.human_readable()}\n'
        return human_readable
