from typing import Union, List, Callable, Dict, Any
import logging
import time
from ..utils.prop_limits import TIME_PROP_LIMIT
from .base_steps import (
    Step,
    AbstractAsyncStep,
    AbstractStep,
    AbstractBaseStep,
    AbstractDynamicStep,
    execution_log_str,
    finished_executing_step_msg,
)
from .utils import FTNDuration

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

class Await(AbstractBaseStep):
    """Wait for Async step with given pid to finish executing.

    Args:
        pid (str): pid of :py:class:``Async`` step to wait for.
    """

    PROP_TYPES = {
        'pid': str,
    }

    def __init__(self, pid: str, **kwargs):
        super().__init__(locals())
        self.steps = []

    def execute(
        self,
        async_steps: List[Async],
        logger: logging.Logger = None,
        level: int = 0,
        step_indexes: List[int] = None,
    ) -> None:
        # Log step start if it is executed by itself (level == 0), as there will
        # be no other context logging the step start.
        if level == 0:
            logger.info(execution_log_str(self, step_indexes))

        # Await async step with self.pid
        for async_step in async_steps:
            if async_step.pid == self.pid:
                while not async_step.finished:
                    time.sleep(1)
                # Reset async step so it can be used again, for example in
                # Repeat step.
                async_step.finished = False

        # Log step finish
        logger.info(finished_executing_step_msg(self, step_indexes))
        return True

    def locks(self, chempiler):
        return [], [], []

class Repeat(AbstractStep):
    """Repeat children of this step ``self.repeats`` times.

    Args:
        repeats (int): Number of times to repeat children.
        children (List[Step]): Child steps to repeat.
    """

    PROP_TYPES = {
        'repeats': int,
        'children': Union[Step, List[Step]]
    }

    def __init__(
        self, repeats: int, children: Union[Step, List[Step]], **kwargs
    ) -> None:
        super().__init__(locals())

        if type(children) != list:
            self.children = [children]

    def get_steps(self):
        steps = []
        for _ in range(self.repeats):
            steps.extend(self.children)
        return steps

    def human_readable(self, language='en'):
        human_readable = f'Repeat {self.repeats} times:\n'
        for step in self.children:
            human_readable += f'    {step.human_readable()}\n'
        return human_readable

class Loop(AbstractDynamicStep):
    """Repeat children of this step indefinitely.

    Args:
        children (List[Step]): Child steps to repeat.

    """

    PROP_TYPES = {
        'children': Union[Step, List[Step]]
    }

    def __init__(
        self, children: Union[Step, List[Step]], **kwargs
    ) -> None:
        super().__init__(locals())

        if type(children) != list:
            self.children = [children]

    def on_start(self):
        """Nothing to be done."""
        return []

    def on_continue(self):
        """Perform child steps"""
        return self.children

    def on_finish(self):
        """Nothing to be done."""
        return []

class Wait(AbstractBaseStep):
    """Wait for given time.

    Args:
        time (int): Time in seconds
    """

    PROP_TYPES = {
        'time': float,
    }

    PROP_LIMITS = {
        'time': TIME_PROP_LIMIT,
    }

    def __init__(self, time: float, **kwargs) -> None:
        super().__init__(locals())

    def execute(
        self,
        platform_controller: Any,
        logger: logging.Logger = None,
        level: int = 0
    ) -> bool:
        # Don't wait if platform_controller is in simulation mode.
        if (hasattr(platform_controller, 'simulation')
                and platform_controller.simulation is True):
            return True

        time.sleep(self.time)
        return True

    def duration(self):
        return FTNDuration(self.time, self.time, self.time)

class Callback(AbstractBaseStep):
    """Call ``fn`` when this step is executed with given args.

    Args:
        AbstractBaseStep ([type]): [description]
    """
    PROP_TYPES = {
        'fn': Callable,
        'args': List[Any],
        'keyword_args': Dict[str, Any]
    }

    def __init__(
        self,
        fn: Callable,
        args: List[Any] = [],
        keyword_args: Dict[str, Any] = {}
    ) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger, level=0):
        self.fn(*self.args, **self.keyword_args)

    def locks(self, chempiler):
        return [], [], []
