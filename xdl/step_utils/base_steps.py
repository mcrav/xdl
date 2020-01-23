from ..utils import XDLBase
from ..constants import DEFAULT_INSTANT_DURATION
import logging
import threading
import copy
from abc import ABC, abstractmethod
from ..utils.misc import format_property
from ..localisation import HUMAN_READABLE_STEPS

if False:
    from chempiler import Chempiler

class Step(XDLBase):
    """Base class for all step objects.

    Attributes:
        properties (dict): Dictionary of step properties. Should be implemented
            in step __init__.
    """
    def __init__(self, param_dict):
        super().__init__(param_dict)
        if 'kwargs' in param_dict:
            kwargs = ['repeat']
            for kwarg in kwargs:
                if kwarg in param_dict['kwargs']:
                    self.properties[kwarg] = param_dict['kwargs'][kwarg]

    def formatted_properties(self):
        formatted_props = copy.deepcopy(self.properties)
        for prop, val in formatted_props.items():
            formatted_props[prop] = format_property(prop, val)
        return formatted_props

    def human_readable(self, language='en'):
        if self.name in HUMAN_READABLE_STEPS:
            step_human_readables = HUMAN_READABLE_STEPS[self.name]
            if language in step_human_readables:
                human_readable = HUMAN_READABLE_STEPS[
                    self.name][language].format(**self.formatted_properties())
            else:
                human_readable = self.name
        else:
            human_readable = self.name
        return human_readable

class AbstractStep(Step, ABC):
    """Abstract base class for all steps that contain other steps.
    Subclasses must implement steps and human_readable, and can also override
    requirements if necessary.

    Attributes:
        properties (dict): Dictionary of step properties.
        steps (list): List of Step objects.
        human_readable (str): Description of actions taken by step.
    """
    def __init__(self, param_dict):
        super().__init__(param_dict)
        self.steps = self.get_steps()

    @abstractmethod
    def get_steps(self):
        return []

    @property
    def requirements(self):
        return {}

    def request_lock(self, chempiler, locking_pid):
        can_lock = True
        for step in self.base_steps:
            if not step.request_lock(chempiler, locking_pid):
                can_lock = False
                break
        return can_lock

    def acquire_lock(self, chempiler, locking_pid):
        for step in self.base_steps:
            step.acquire_lock(chempiler, locking_pid)

    def release_lock(self, chempiler, locking_pid):
        for step in self.base_steps:
            step.release_lock(chempiler, locking_pid)

    def final_sanity_check(self, graph):
        pass

    def on_prepare_for_execution(self, graph):
        pass

    def execute(
        self,
        chempiler: 'Chempiler',
        logger: logging.Logger = None,
        level: int = 0
    ) -> bool:
        """
        Execute self with given Chempiler object.

        Args:
            chempiler (chempiler.Chempiler): Initialised Chempiler object.
            logger (logging.Logger): Logger to handle output step output.
            level (int): Level of recursion in step execution.
        """
        self.final_sanity_check(chempiler.graph.graph)
        level += 1
        if not logger:
            logger = logging.getLogger('xdl')

        try:
            repeats = 1
            if 'repeat' in self.properties:
                repeats = int(self.repeat)
            for _ in range(repeats):
                for step in self.steps:
                    prop_str = ''
                    for k, v in step.properties.items():
                        prop_str += f'{"  " * level}  {k}: {v}\n'
                    logger.info(
                        'Executing:\n{0}{1}\n{2}'.format(
                            '  ' * level, step.name, prop_str))
                    try:
                        keep_going = step.execute(
                            chempiler, logger, level=level)
                    except Exception as e:
                        logger.info(
                            'Step failed {0} {1}'.format(
                                type(step), step.properties))
                        raise e
                    if not keep_going:
                        return False
            return True
        except Exception as e:
            if logger:
                logger.exception(str(e), exc_info=1)
            raise(e)

    @property
    def base_steps(self):
        base_steps = []
        for step in self.steps:
            if isinstance(step, AbstractBaseStep):
                base_steps.append(step)
            else:
                base_steps.extend(self.get_base_steps(step))
        return base_steps

    def get_base_steps(self, step):
        base_steps = []
        for step in step.steps:
            if isinstance(step, AbstractBaseStep):
                base_steps.append(step)
            else:
                base_steps.extend(self.get_base_steps(step))
        return base_steps

    def duration(self, chempiler):
        duration = 0
        for step in self.base_steps:
            print(step)
            duration += step.duration(chempiler)
        return duration

class AbstractBaseStep(Step, ABC):
    """Abstract base class for all steps that do not contain other steps and
    instead have an execute method that takes a chempiler object.

    Subclasses must implement execute.
    """
    def __init__(self, param_dict):
        super().__init__(param_dict)
        self.steps = []

    def human_readable(self, language='en'):
        return self.__class__.__name__

    def on_prepare_for_execution(self, graph):
        pass

    def final_sanity_check(self, graph):
        pass

    @property
    def requirements(self):
        return {}

    @abstractmethod
    def execute(self, chempiler: 'Chempiler'):
        return False

    @property
    def base_steps(self):
        return [self]

    def duration(self, chempiler):
        return DEFAULT_INSTANT_DURATION

    @abstractmethod
    def locks(self, chempiler):
        return [], [], []

    def request_lock(self, chempiler, locking_pid):
        locks, ongoing_locks, _ = self.locks(chempiler)
        return chempiler.request_lock(locks + ongoing_locks, locking_pid)

    def acquire_lock(self, chempiler, locking_pid):
        locks, ongoing_locks, _ = self.locks(chempiler)
        chempiler.acquire_lock(locks + ongoing_locks, locking_pid)

    def release_lock(self, chempiler, locking_pid):
        locks, _, unlocks = self.locks(chempiler)
        chempiler.release_lock(locks + unlocks, locking_pid)

class AbstractAsyncStep(XDLBase):
    """For executing code asynchronously. Can only be used programtically,
    no way of encoding this in XDL files.

    async_execute method is executed asynchronously when this step executes.
    Recommended use is to have callback functions in properties when making
    subclasses.
    """
    def __init__(self, param_dict):
        super().__init__(param_dict)
        self._should_end = False

    def execute(self, chempiler, logger=None, level=0):
        self.thread = threading.Thread(
            target=self.async_execute, args=(chempiler, logger))
        self.thread.start()
        return True

    @abstractmethod
    def async_execute(
        self, chempiler: 'Chempiler', logger: logging.Logger = None
    ) -> bool:
        return True

    def kill(self):
        self._should_end = True


class AbstractDynamicStep(XDLBase):
    """Step for containing dynamic experiments in which feedback from analytical
    equipment controls the flow of the experiment.

    Provides abstract methods on_start, on_continue and on_finish that each
    return lists of steps to be performed at different stages of the experiment.
    on_continue is called repeatedly until it returns an empty list.

    What steps are to be returned should be decided base on the state attribute.
    The state can be updated from any of the three lifecycle methods or from
    AbstractAsyncStep callback functions.
    """
    def __init__(self, param_dict):
        super().__init__(param_dict)
        self.state = {}
        self.async_steps = []

    @abstractmethod
    def on_start(self):
        """Returns list of steps to be executed once at start of step.

        Returns:
            List[Step]: List of  steps to be executed once at start of step.
        """
        return []

    @abstractmethod
    def on_continue(self):
        """Returns list of steps to be executed in main loop of step, after
        on_start and before on_finish. Is called repeatedly until empty list is
        returned at which point the steps returned by on_finish are executed
        and the step ends.

        Returns:
            List[Step]: List of steps to execute in main loop based on
                self.state.
        """
        return []

    @abstractmethod
    def on_finish(self):
        """Returns list of steps to be executed once at end of step.

        Returns:
            List[Step]: List of steps to be executed once at end of step.
        """
        return []

    def _post_finish(self):
        """Called after steps returned by on_finish have finished executing to
        try to join all threads.
        """
        for async_step in self.async_steps:
            async_step.kill()

    def prepare_for_execution(self, graph, executor):
        self.executor = executor
        self.graph = graph
        self.start_block = self.on_start()
        self.executor.prepare_block_for_execution(self.graph, self.start_block)

    def execute(self, chempiler, logger=None, level=0):
        """Execute step lifecycle. on_start, followed by on_continue repeatedly
        until an empty list is returned, followed by on_finish, after which all
        threads are joined as fast as possible.

        Args:
            chempiler (Chempiler): Chempiler object to use for executing steps.
            logger (Logger): Logger object.
            level (int): Level of recursion in step execution.

        Returns:
            True: bool to indicate execution should continue after this step.
        """
        # Execute steps from on_start
        for step in self.start_block:
            step.execute(chempiler, logger=logger, level=level)
            if isinstance(step, AbstractAsyncStep):
                self.async_steps.append(step)

        # Repeatedly execute steps from on_continue until empty list returned
        continue_block = self.on_continue()
        self.executor.prepare_block_for_execution(self.graph, continue_block)

        while continue_block:
            for step in continue_block:
                if isinstance(step, AbstractAsyncStep):
                    self.async_steps.append(step)
                step.execute(chempiler, logger=logger, level=level)

            continue_block = self.on_continue()
            self.executor.prepare_block_for_execution(
                self.graph, continue_block)

        # Execute steps from on_finish
        finish_block = self.on_finish()
        self.executor.prepare_block_for_execution(self.graph, finish_block)

        for step in finish_block:
            step.execute(chempiler, logger=logger, level=level)
            if isinstance(step, AbstractAsyncStep):
                self.async_steps.append(step)

        # Kill all threads
        self._post_finish()

        return True

class UnimplementedStep(Step):
    """Abstract base class for steps that have no implementation but are
    included either as stubs or for the purpose of showing requirements or
    human_readable.
    """
    def __init__(self, param_dict):
        super().__init__(param_dict)
        self.steps = []

    def execute(self, chempiler, logger=None, level=0):
        raise NotImplementedError(
            f'{self.__class__.__name__} step is unimplemented.')

    @property
    def requirements(self):
        return {}

    def final_sanity_check(self, graph):
        pass

    def on_prepare_for_execution(self, graph):
        pass