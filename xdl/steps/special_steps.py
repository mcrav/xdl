from typing import Union, List, Callable
import logging

from .base_steps import Step, AsyncStep

class Async(AsyncStep):
    """Wrapper to execute a step or sequence of steps asynchronously.

    Use like this:

    async_stir_step = Async(Stir(vessel=filter, time=3600))

    Can be stopped in between steps by calling async_stir_step.kill()

    Args:
        steps (Union[Step, List[Step]]): Step object or list of Step objects to
            execute asynchronously.
        on_finish (Callable): Callback function to call after execution of steps
            has finished.
    """
    def __init__(
        self,
        steps: Union[Step, List[Step]],
        on_finish: Callable = None,
    ):
        super().__init__(locals())

        if type(steps) != list:
            self.steps = [steps]

        self._should_end = False

    def async_execute(
        self, chempiler: 'Chempiler', logger: logging.Logger = None) -> None:
        for step in self.steps:
            keep_going = step.execute(chempiler, logger)
            if not keep_going or self._should_end:
                return
        if self.on_finish:
            self.on_finish()
