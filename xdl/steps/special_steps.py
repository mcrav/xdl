from typing import Union, List, Callable
import logging
import time

from .base_steps import Step, AbstractAsyncStep, AbstractStep, AbstractBaseStep

class Async(AbstractAsyncStep):
    """Wrapper to execute a step or sequence of steps asynchronously.

    Use like this:

    async_stir_step = Async(Stir(vessel=filter, time=3600))

    Can be stopped in between steps by calling async_stir_step.kill()

    Args:
        children (Union[Step, List[Step]]): Step object or list of Step objects
            to execute asynchronously.
        pid (str): Process ID. Optional, but must be given if using Await later
            in procedure.
        on_finish (Callable): Callback function to call after execution of steps
            has finished.
    """
    def __init__(
        self,
        children: Union[Step, List[Step]],
        pid: str = None,
        on_finish: Callable = None,
    ):
        super().__init__(locals())

        if type(children) != list:
            self.children = [children]

        self.steps = self.children

        self._should_end = False
        self.finished = False

    def async_execute(
        self, chempiler: 'Chempiler', logger: logging.Logger = None) -> None:
        for step in self.children:
            keep_going = step.execute(chempiler, logger)
            if not keep_going or self._should_end:
                self.finished = True
                return

        self.finished = True
        if self.on_finish:
            self.on_finish()
        return True

    def human_readable(self, language='en'):
        human_readable = f'Asynchronous:\n'
        for step in self.children:
            human_readable += f'    {step.human_readable()}\n'
        return human_readable

class Await(AbstractBaseStep):
    """Wait for Async step with given pid to finish executing.

    Args:
        pid (str): pid of Async step to wait for.
    """
    def __init__(self, pid: str, **kwargs):
        super().__init__(locals())
        self.steps = []

    def execute(
        self,
        async_steps: List[Async],
        logger: logging.Logger = None
    ) -> None:
        for async_step in async_steps:
            if async_step.pid == self.pid:
                while not async_step.finished:
                    time.sleep(1)
        return True

class Repeat(AbstractStep):
    """Repeat children of this step self.repeats times.

    Args:
        repeats (int): Number of times to repeat children.
        children (List[Step]): Child steps to repeat.
    """
    def __init__(
        self, repeats: int, children: Union[Step, List[Step]])  -> None:
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
