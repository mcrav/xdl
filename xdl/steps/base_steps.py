# Std
from typing import List, Dict, Any, Tuple
import logging
import threading
import copy
import uuid
from abc import ABC, abstractmethod
import tabulate

# Other
from networkx import MultiDiGraph
import termcolor

# Relative
from .utils import FTNDuration
from ..localisation import LOCALISATIONS
from ..utils import XDLBase
from ..utils.localisation import conditional_human_readable
from ..utils.misc import format_property, SanityCheck
from ..utils.graph import get_graph
from ..utils.logging import get_logger, log_duration
from ..utils.vessels import VesselSpec
from ..errors import (
    XDLError,
    XDLUndeclaredDefaultPropError,
    XDLUndeclaredAlwaysWriteError,
    XDLUndeclaredInternalPropError,
    XDLUndeclaredPropLimitError
)
if False:
    from ..execution import AbstractXDLExecutor

class Step(XDLBase):
    """Base class for all step objects.

    Attributes:
        properties (dict): Dictionary of step properties. Should be implemented
            in step ``__init__`` method.
        uuid (str): Step unique universal identifier, generated automatically.
        localisation: Dict[str, str]: Provides localisation for all steps
            specified by the XDL cross platform templates. Can be overridden if
            localisation needed for other steps or steps do not conform to cross
            platform standard.

    Args:
        param_dict (Dict[str, Any]): Step properties dict to initialize step
            with.
    """

    # This provides localisation for all steps specified by the XDL cross
    # platform templates. Can be overridden if localisation needed for other
    # steps or steps do not conform to cross platform standard.
    localisation: Dict[str, str] = LOCALISATIONS

    def __init__(self, param_dict: Dict[str, Any]) -> None:
        super().__init__(param_dict)

        self.uuid = str(uuid.uuid4())

        # Validate prop types
        self._validate_prop_types()
        self._validated_prop_types = True

    def _validate_prop_types(self):
        """Make sure that all props specified in ``DEFAULT_PROPS``, ``INTERNAL_PROPS``,
        ``ALWAYS_WRITE`` and ``PROP_LIMITS`` are specified in ``PROP_TYPES``.

        Raises:
            XDLUndeclaredDefaultPropError: Prop used in ``DEFAULT_PROPS`` that
                is not in ``PROP_TYPES``.
            XDLUndeclaredInternalPropError: Prop used in ``INTERNAL_PROPS`` that
                is not in ``PROP_TYPES``.
            XDLUndeclaredPropLimitError: Prop used in ``PROP_LIMITS`` that is
                not in ``PROP_TYPES``.
            XDLUndeclaredAlwaysWriteError: Prop used in ``ALWAYS_WRITE`` that is
                not used in ``PROP_TYPES``.
        """
        # Default Props
        for default_prop in self.DEFAULT_PROPS:
            if default_prop not in self.PROP_TYPES:
                raise XDLUndeclaredDefaultPropError(self.name, default_prop)

        # Internal Props
        for internal_prop in self.INTERNAL_PROPS:
            if internal_prop not in self.PROP_TYPES:
                raise XDLUndeclaredInternalPropError(self.name, internal_prop)

        # Prop Limits
        for prop_limit in self.PROP_LIMITS:
            if prop_limit not in self.PROP_TYPES:
                raise XDLUndeclaredPropLimitError(self.name, prop_limit)

        # Always Write
        for always_write in self.ALWAYS_WRITE:
            if always_write not in self.PROP_TYPES:
                raise XDLUndeclaredAlwaysWriteError(self.name, always_write)

    def on_prepare_for_execution(self, graph: MultiDiGraph) -> None:
        """Abstract method to be overridden with logic to set internal
        properties during procedure compilation. Doesn't use ``@abstractmethod``
        decorator as it's okay to leave this blank if there are no internal
        properties.

        This method is called during procedure compilation. Sanity checks are
        called after this method, and are there to validate the internal
        properties added during this stage.

        Args:
            graph (MultiDiGraph): networkx MultiDiGraph of graph that procedure
                is compiling to.
        """
        pass

    def sanity_checks(self, graph: MultiDiGraph) -> List[SanityCheck]:
        """Abstract methods that should return a list of ``SanityCheck`` objects
        to be checked by final_sanity_check. Not compulsory so not using
        ``@abstractmethod`` decorator.
        """
        return []

    def final_sanity_check(self, graph: MultiDiGraph) -> None:
        """Run all ``SanityCheck`` objects returned by ``sanity_checks``. Can be
        extended if necessary but ``super().final_sanity_check()`` should always
        be called.
        """
        for sanity_check in self.sanity_checks(graph):
            sanity_check.run(self)

    def formatted_properties(self) -> Dict[str, str]:
        """Return properties as dictionary of ``{ prop: formatted_val }``.
        Used when generating human readables.
        """
        # Copy properties dict
        formatted_props = copy.deepcopy(self.properties)

        # Add formatted properties for all properties
        for prop, val in formatted_props.items():

            # Ignore children
            if prop != 'children':
                formatted_props[prop] = format_property(
                    prop,
                    val,
                    self.PROP_TYPES[prop],
                    self.PROP_LIMITS.get(prop, None),
                )

            # Convert None properties to empty string
            if formatted_props[prop] == 'None':
                formatted_props[prop] = ''

        return formatted_props

    def human_readable(self, language: str = 'en') -> str:
        """Return human readable sentence describing step.

        Args:
            language (str): Language code for human readable sentence. Defaults
                to ``'en'``.

        Returns:
            str: Human readable sentence describing actions taken by step.
        """
        # Look for step name in localisation dict
        if self.name in self.localisation:

            # Get human readable template from localisation dict
            step_human_readables = self.localisation[self.name]
            if language in step_human_readables:
                language_human_readable = step_human_readables[language]

                # Traditional human readable template strings
                if type(language_human_readable) == str:

                    # If step has a comment add comment to template.
                    if self.comment:
                        language_human_readable += '. {comment}'

                    return language_human_readable.format(
                        **self.formatted_properties())

                # New conditional JSON object human readable format
                else:
                    # If step has a comment add comment to template.
                    if self.comment:
                        language_human_readable['full'] += '. {comment}'

                    return conditional_human_readable(
                        self, language_human_readable)

        # Return step name as a fallback if step not in localisation dict
        return self.name

    def scale(self, scale: float) -> None:
        """Method to override to handle scaling if procedure is scaled.
        Should update step properties accordingly with given scale. Doesn't
        need to do/return anything.

        Args:
            scale (float): Scale factor to scale step by.
        """
        return

    def reagents_consumed(self, graph: MultiDiGraph) -> Dict[str, float]:
        """Method to override if step consumes reagents. Used to recursively
        calculate volume of reagents consumed by procedure.

        Args:
            graph (MultiDiGraph): Graph to use when calculating volume of
                reagents consumed by step.

        Returns:
            Dict[str, float]: Dict of volumes of reagents consumed in format
            ``{ reagent_id: volume_consumed... }``.
        """
        return {}

    def duration(self, graph: MultiDiGraph) -> int:
        """Method to override to give approximate duration of step. Used to
        recursively determine duration of procedure.

        Args:
            graph (MultiDiGraph): Graph to use when calculating step duration.

        Returns:
            FTNDuration: Estimated duration of step in seconds as FTN.
        """
        # Default duration for steps that don't override this method. Duration
        # used is an estimate of the duration of steps that are virtually
        # instantaneous, such as starting stirring.
        return FTNDuration(0.5, 1, 2)

    def locks(self, platform_controller: Any) -> Tuple[List]:
        """WIP: Abstract method used by parallelisation.

        Returns locks, ongoing_locks and unlocks. Locks are nodes that are used
        while the step is executing. Ongoing locks are nodes that will be in use
        indefinitely after the step has finished (e.g. a vessel that the
        reaction mixture has been added to). Unlocks are nodes that are no
        longer being used after the step has finished (e.g. a vessel that the
        reaction mixture has been removed from).

        Args:
            platform_controller (Any): Platform controller to use for
                calculating which nodes in graph are used by step.

        Returns:
            Tuple[List]: Tuple of step lock changes in format
            ``(locks, ongoing_locks, unlocks)``.
        """
        return [], [], []

    @property
    def vessel_specs(self) -> Dict[str, VesselSpec]:
        """Return dictionary of required specifications of vessels used by the
        step. ``{ prop_name: vessel_spec... }``

        Returns:
            Dict[str, VesselSpec]: Dict of required specification of vessels
            used by the step. Should be overridden if the step has any special
            requirement on a vessel used.
        """
        return {}

    @property
    def requirements(self) -> Dict:
        """Return dictionary of requirements of vessels used by the step.
        Currently only used bySynthReader. This will soon be deprecated and
        completely replaced by ``vessel_specs``.
        """
        return {}

    def __eq__(self, other: Any) -> bool:
        """Allow ``step == other_step`` comparisons."""

        # Different type, not equal
        if type(other) != type(self):
            return False

        # Different name, not equal
        if other.name != self.name:
            return False

        # Different length of properties, not equal
        if len(self.properties) != len(other.properties):
            return False

        # Compare properties
        for k, v in other.properties.items():

            # Compare children
            if k == 'children':

                # Different length of children, not equal
                if len(v) != len(self.children):
                    return False

                # Compare individual children
                for i, other_child in enumerate(v):

                    # Children are different, not equal
                    if other_child != self.children[i]:
                        return False

            # Property key is not in self.properties, not equal
            elif k not in self.properties:
                return False

            # Different values for property, not equal
            elif v != self.properties[k]:
                return False

        # Passed all equality tests, steps are equal
        return True

    def __ne__(self, other: Any) -> bool:
        """Recommended to include this just to show that non equality has been
        considered and it is simply ``not __eq__(other)``.
        """
        return not self.__eq__(other)

    def __deepcopy__(self, memo):
        """Allow ``copy.deepcopy(step)`` to be called. Default deepcopy works,
        but not on Python 3.6, so that is what this is for. When Python 3.6 is
        not supported this can go.
        """
        # Copy children
        children = []
        if 'children' in self.properties and self.children:
            for child in self.children:
                children.append(child.__deepcopy__(memo))

        # Copy properties
        copy_props = {}
        for k, v in self.properties.items():
            if k != 'children':
                copy_props[k] = v

        if children:
            copy_props['children'] = children

        # Make new self
        copied_self = type(self)(**copy_props)

        return copied_self

class AbstractBaseStep(Step, ABC):
    """Abstract base class for all steps that do not contain other steps and
    instead have an execute method that takes a ``platform_controller`` object.

    Subclasses must implement execute.

    Args:
        param_dict (Dict[str, Any]): Step properties dict to initialize step
            with.
    """
    def __init__(self, param_dict: Dict[str, Any]) -> None:
        super().__init__(param_dict)
        self.steps = []

    @abstractmethod
    def execute(self, platform_controller) -> bool:
        """Execute method to be overridden for all base steps. Take platform
        controller and use it to execute the step. Return ``True`` if procedure
        should continue after the step is completed, return ``False`` if the
        procedure should break for some reason.
        """
        return False

    @property
    def base_steps(self):
        """Just return self as the base_steps. Used by recursive ``base_steps``
        method of ``AbstractStep``. No need to override this.
        """
        return [self]

    def request_lock(self, platform_controller: Any, locking_pid: str) -> bool:
        """WIP: Used by parallelisation to find out if the nodes required by
        the step are available.

        Args:
            platform_controller (Any): Platform controller object to request
                lock from.
            locking_pid (str): Locking pid to use when requesting lock.

        Returns:
            bool: ``True`` if can aquire lock, otherwise ``False``. Lock is not
            aquired even if the return is ``True``.
        """
        locks, ongoing_locks, _ = self.locks(platform_controller)
        return platform_controller.request_lock(
            locks + ongoing_locks, locking_pid)

    def acquire_lock(self, platform_controller: Any, locking_pid: str) -> None:
        """WIP: Used by parallelisation to let platform controller know what
        nodes are in use by the step.

        Args:
            platform_controller (Any): Platform controller object to aquire
                lock from.
            locking_pid (str): Locking pid to use when aquiring lock.
        """
        locks, ongoing_locks, _ = self.locks(platform_controller)
        platform_controller.acquire_lock(locks + ongoing_locks, locking_pid)

    def release_lock(self, platform_controller: Any, locking_pid: str) -> None:
        """WIP: Used by parallelisation to let platform controller know what
        nodes are no longer in use by the step.

        Args:
            platform_controller (Any): Platform controller object to request
                lock release from.
            locking_pid (str): Locking pid to use when releasing lock.
        """
        locks, _, unlocks = self.locks(platform_controller)
        platform_controller.release_lock(locks + unlocks, locking_pid)

class AbstractStep(Step, ABC):
    """Abstract base class for all steps that contain other steps.
    Subclasses must implement steps and human_readable, and can also override
    vessel_specs if necessary.

    Attributes:
        properties (dict): Dictionary of step properties.
        human_readable (str): Description of actions taken by step.

    Args:
        param_dict (Dict[str, Any]): Step properties dict to initialize step
            with.
    """

    _steps = []

    def __init__(self, param_dict: Dict[str, Any]) -> None:
        super().__init__(param_dict)

        # Initialise internal steps list and properties associated with this
        # steps list.
        self._steps = self.get_steps()
        self._last_props = self._copy_props()

    @property
    def steps(self):
        """The internal steps list is calculated only when it is asked for, and
        only when ``self.properties`` different to the last time steps was asked
        for. This is for performance reasons since during
        ``prepare_for_execution`` the amount of updates to ``self.properties``
        is pretty large.

        ::

            # steps updated
            step = Step(**props)

            # self.properties updated but steps not updated
            step.volume = 15

            # steps updated and returned
            print(step.steps)

            # steps not updated and returned, since properties haven't change
            # since last steps update
            print(step.steps)
        """
        # Only update self._steps if self.properties has changed.
        #
        # Optimization note: This may seem long winded compared to
        # self.properties != self._last_props but in Python 3.7 at least this is
        # faster.
        should_update = False
        for k, v in self.properties.items():
            if self._last_props[k] != v:
                should_update = True
                break

        # If self.properties has changed, update self._steps
        if should_update:
            self._steps = self.get_steps()
            self._last_props = self._copy_props()

        return self._steps

    def _copy_props(self) -> Dict[str, Any]:
        """Return deep copy of ``self.properties`` for use when deciding whether
        to use cached :py:attr:`_steps` or not.

        Returns:
            Dict[str, Any]: Deep copy of ``self.properties`` for use when
                deciding whether to use cached :py:attr:`_steps` or not.
        """
        copy_props = {}
        for k, v in self.properties.items():
            # Don't copy callable. For example, if this is a class method,
            # copying will copy the entire object, meaning that any comparison
            # with the previous method will show them to be unequal, even if
            # the method hasn't actually changed.
            if callable(v):
                copy_props[k] = v
            else:
                copy_props[k] = copy.deepcopy(v)
        return copy_props

    @abstractmethod
    def get_steps(self) -> List[Step]:
        """Abstract method that must be overridden when creating non base steps.
        Should return a list of steps to be sequentially executed when the step
        is executed. No properties should be changed during this method. This is
        a one way street to return a list of steps based on the current
        properties of the step.

        Returns:
            List[Step]: List of steps to be sequentially executed when the step
                is executed.
        """
        return []

    def request_lock(self, platform_controller: Any, locking_pid: str) -> bool:
        """WIP: Used by parallelisation to find out if the nodes required by
        the step are available.

        Args:
            platform_controller (Any): Platform controller object to request
                lock from.
            locking_pid (str): Locking pid to use when requesting lock.

        Returns:
            bool: ``True`` if can aquire lock, otherwise ``False``. Lock is not
            aquired even if the return is ``True``.
        """
        can_lock = True
        for step in self.base_steps:
            if not step.request_lock(platform_controller, locking_pid):
                can_lock = False
                break
        return can_lock

    def acquire_lock(self, platform_controller: Any, locking_pid: str) -> None:
        """WIP: Used by parallelisation to let platform controller know what
        nodes are in use by the step.

        Args:
            platform_controller (Any): Platform controller object to aquire
                lock from.
            locking_pid (str): Locking pid to use when aquiring lock.
        """
        for step in self.base_steps:
            step.acquire_lock(platform_controller, locking_pid)

    def release_lock(self, platform_controller: Any, locking_pid: str) -> None:
        """WIP: Used by parallelisation to let platform controller know what
        nodes are no longer in use by the step.

        Args:
            platform_controller (Any): Platform controller object to request
                lock release from.
            locking_pid (str): Locking pid to use when releasing lock.
        """
        for step in self.base_steps:
            step.release_lock(platform_controller, locking_pid)

    def execute(
        self,
        platform_controller,
        logger: logging.Logger = None,
        level: int = 0,
        async_steps: List[str] = [],
        step_indexes: List[int] = None,
    ) -> bool:
        """
        Execute self with given platform controller object.

        Args:
            platform_controller (platform_controller): Initialised platform
                controller object.
            logger (logging.Logger): Logger to handle output step output.
            level (int): Level of recursion in step execution.
            async_steps  (List[str]): List of currently executing async steps.
                Used by any ``Await`` steps encountered.
            step_indexes (List[int]): Indexes into steps list and substeps
                lists.

        Returns:
            bool: ``True`` if execution should continue, ``False`` if execution
            should stop.
        """
        if logger is None:
            logger = get_logger()

        # Log step start timestamp
        log_duration(self, 'start')

        # This is necessary if a step is being executed outside the context of
        # a XDL object.
        if not step_indexes:
            step_indexes = [0]
        self_step_indexes = copy.copy(step_indexes)

        # If step is at recursion level 0 logging must be done here as it won't
        # be done inside the for loop below.
        if level == 0:
            logger.info(
                execution_log_str(
                    self, step_indexes=step_indexes))

        # Bump recursion level
        level += 1

        # Add a placeholder for the next index so that it can be assigned to
        # using `step_indexes[level]`
        step_indexes.append(0)

        for i, step in enumerate(self.steps):
            # Update step indexes for current sub step
            step_indexes[level] = i
            step_indexes = step_indexes[:level + 1]

            # Log step execution
            logger.info(
                execution_log_str(
                    step, step_indexes=step_indexes))

            # Execute step
            try:
                # Await async step finishing
                if step.name == 'Await':
                    keep_going = step.execute(
                        async_steps,
                        logger=self.logger,
                        level=level,
                        step_indexes=step_indexes
                    )

                # Execute normal step
                else:
                    step_is_base_step = isinstance(step, AbstractBaseStep)

                    # Log base step start timestamp here, as it is easier than
                    # adding to all base step `execute` methods. Only base step
                    # logged here as normal step start / end timestamps logged
                    # at start / end of this method.
                    if step_is_base_step:
                        log_duration(step, 'start')

                    # Execute step, don't pass `step_indexes` to base step, and
                    # log step completion here. Step completion isn't needed to
                    # be logged for normal steps as it is done recursively at
                    # the end of this function.
                    if step_is_base_step:
                        # Execute step
                        keep_going = step.execute(
                            platform_controller, self.logger, level=level)

                        # Log step completion
                        logger.info(
                            finished_executing_step_msg(step, step_indexes))
                    else:
                        keep_going = step.execute(
                            platform_controller,
                            self.logger,
                            level=level,
                            step_indexes=step_indexes
                        )

                    # Log base step  end timestamp here, as it is easier than
                    # adding to all base step `execute` methods.
                    if step_is_base_step:
                        log_duration(step, 'end')

            # It is disgusting to use except Exception, but the only reason
            # here is just to provide a bit of debug information if a step
            # crashes. Might want to remove this in future.
            except Exception as e:
                step_failed_msg = termcolor.colored(
                    'Step failed', color='red', attrs=['bold'])
                step_name = termcolor.colored(
                    step.name, color='cyan', attrs=['bold'])
                props_table = termcolor.colored(
                    pretty_props_table(step.properties), color='cyan')
                logger.exception(
                    f'{step_failed_msg} {step_name}\n\
{step.human_readable()}\n{props_table}'
                )
                raise e

            # If keep_going is False break execution. This is used by the
            # Confirm step to stop execution if the user doesn't wish to
            # continue.
            if not keep_going:
                return False

        # Log step end timestamp
        log_duration(self, 'end')
        logger.info(finished_executing_step_msg(self, self_step_indexes))

        # Return `keep_going` flag as `True`.
        return True

    @property
    def base_steps(self) -> List[AbstractBaseStep]:
        """Return list of step's base steps.

        Returns:
            List[AbstractBaseStep]: Step's base steps.
        """
        base_steps = []
        for step in self.steps:
            if isinstance(step, AbstractBaseStep):
                base_steps.append(step)
            else:
                base_steps.extend(get_base_steps(step))
        return base_steps

    def duration(self, graph: MultiDiGraph) -> int:
        """Return approximate duration in seconds of step calculated as sum of
        durations of all substeps. This method should be overridden where an
        exact or near exact duration is known. The fallback duration for base
        steps is 1 second.

        Args:
            graph (MultiDiGraph): Graph to use when calculating step duration.

        Returns:
            int: Estimated duration of step in seconds.
        """
        duration = FTNDuration(0, 0, 0)
        for step in self.steps:
            duration += step.duration(graph)
        return duration

    def reagents_consumed(self, graph: MultiDiGraph) -> Dict[str, float]:
        """Return dictionary of reagents and volumes consumed in mL like this:
        ``{ reagent: volume... }``. Can be overridden otherwise just recursively
        adds up volumes used by base steps.

        Args:
            graph (MultiDiGraph): Graph to use when calculating volumes of
                reagents consumed by step.

        Returns:
            Dict[str, float]: Dict of reagents volumes consumed by step in
            format ``{reagent_id: reagent_volume...}``.
        """
        reagents_consumed = {}
        for substep in self.steps:
            step_reagents_consumed = substep.reagents_consumed(graph)
            for reagent, volume in step_reagents_consumed.items():
                if reagent in reagents_consumed:
                    reagents_consumed[reagent] += volume
                else:
                    reagents_consumed[reagent] = volume
        return reagents_consumed

class AbstractAsyncStep(Step):
    """For executing code asynchronously. Can only be used programmatically,
    no way of encoding this in XDL files.

    ``async_execute`` method is executed asynchronously when this step executes.
    Recommended use is to have callback functions in properties when making
    subclasses.

    Args:
        param_dict (Dict[str, Any]): Step properties dict to initialize step
            with.
    """
    def __init__(self, param_dict: Dict[str, Any]) -> None:
        super().__init__(param_dict)
        self._should_end = False

    def execute(
        self,
        platform_controller: Any,
        logger: logging.Logger = None,
        level: int = 0,
        async_steps: List[str] = [],
        step_indexes: List[int] = None,
    ) -> bool:
        """Execute step in new thread.

        Args:
            platform_controller (Any): Platform controller to execute step with.
            logger (logging.Logger): Logger for logging execution info.
            level (int): Level of execution recursion.
            async_steps (List[str]): List of currently executing async step
                pids.
            step_indexes (List[int]): Indexes into steps list and substeps
                lists.

        Returns:
            bool: ``True`` if execution should continue, ``False`` if execution
            should stop.
        """
        self.thread = threading.Thread(
            target=self.async_execute, args=(
                platform_controller, logger, level, step_indexes))
        self.thread.start()
        return True

    @abstractmethod
    def async_execute(
        self, platform_controller: Any,
        logger: logging.Logger = None,
        level: int = 0,
        step_indexes: List[int] = None,
    ) -> bool:
        """Abstract method. Should contain the execution logic that will be
        executed in a separate thread. Equivalent to
        :py:meth:`AbstractBaseStep.execute`, and similarly should return
        ``True`` if the procedure should continue after the step has finished
        executing and ``False`` if the procedure should break after the step has
        finished executing.

        Not called execute like ``AbstractBaseStep`` to keep ``step.execute``
        logic in other places consistent and simple.

        Args:
            platform_controller (Any): Platform controller to execute step with.
            logger (logging.Logger): Logger for logging execution info.

        Returns:
            bool: ``True`` if execution should continue, ``False`` if execution
            should stop.
        """
        return True

    def kill(self) -> None:
        """Flick :py:attr:`self._should_end` killswitch to let
        :py:meth:`async_execute` know that it should return to allow the thread
        to join. This relies on ``async_execute`` having been implemented in a
        way that takes notice of this variable.
        """
        self._should_end = True

    def reagents_consumed(self, graph: MultiDiGraph) -> Dict[str, float]:
        """Return dictionary of reagents and volumes consumed in mL like this:
        ``{ reagent: volume... }``. Can be overridden otherwise just recursively
        adds up volumes used by base steps.

        Args:
            graph (MultiDiGraph): Graph to use when calculating volumes of
                reagents consumed by step.

        Returns:
            Dict[str, float]: Dict of reagents volumes consumed by step in
            format ``{reagent_id: reagent_volume...}``.
        """
        reagents_consumed = {}
        # Get reagents consumed from children (Async step)
        for substep in self.children:
            step_reagents_consumed = substep.reagents_consumed(graph)
            for reagent, volume in step_reagents_consumed.items():
                if reagent in reagents_consumed:
                    reagents_consumed[reagent] += volume
                else:
                    reagents_consumed[reagent] = volume
        return reagents_consumed

    def duration(self, graph: MultiDiGraph):
        """Return duration of child steps (Async step).

        Args:
            graph (MultiDiGraph): Graph to use when calculating step duration.

        Returns:
            int: Estimated duration of step in seconds.
        """
        duration = FTNDuration(0, 0, 0)
        for step in self.children:
            duration += step.duration(graph)
        return duration

class AbstractDynamicStep(Step):
    """Step for containing dynamic experiments in which feedback from analytical
    equipment controls the flow of the experiment.

    Provides abstract methods :py:meth:`on_start`, :py:meth:`on_continue` and
    :py:meth:`on_finish` that each return lists of steps to be performed at
    different stages of the experiment. :py:meth:`on_continue` is called
    repeatedly until it returns an empty list.

    What steps are to be returned should be decided base on the state attribute.
    The state can be updated from any of the three lifecycle methods or from
    :py:class:`AbstractAsyncStep` callback functions.

    Args:
        param_dict (Dict[str, Any]): Step properties dict to initialize step
            with.
    """
    def __init__(self, param_dict: Dict[str, Any]) -> None:
        super().__init__(param_dict)
        self.state = {}
        self.async_steps = []
        self.steps = []

        # None instead of empty list so that you can tell if its been
        # intialized or not. Start block can just be [].
        self.start_block = None
        self.started = False

    @abstractmethod
    def on_start(self) -> List[Step]:
        """Returns list of steps to be executed once at start of step.

        Returns:
            List[Step]: List of  steps to be executed once at start of step.
        """
        return []

    @abstractmethod
    def on_continue(self) -> List[Step]:
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
    def on_finish(self) -> List[Step]:
        """Returns list of steps to be executed once at end of step.

        Returns:
            List[Step]: List of steps to be executed once at end of step.
        """
        return []

    def reset(self) -> None:
        """Reset state of step. Should be overridden but doesn't have to be."""
        return

    def resume(
        self,
        platform_controller: Any,
        logger: logging.Logger = None,
        level: int = 0
    ) -> None:
        """Resume execution after a pause.

        Args:
            platform_controller (Any): Platform controller to execute step with.
            logger (logging.Logger): Logger to log execution info with.
            level (int): Recursion level of step execution.
        """
        self.started = False  # Hack to avoid reset.
        self.start_block = []  # Go straight to on_continue
        self.execute(platform_controller, logger=logger, level=level)

    def _post_finish(self) -> None:
        """Called after steps returned by :py:meth:`on_finish` have finished
        executing to try to join all threads.
        """
        for async_step in self.async_steps:
            async_step.kill()

    def prepare_for_execution(
            self, graph: MultiDiGraph, executor: 'AbstractXDLExecutor') -> None:
        """Prepare step for execution.

        Args:
            graph (MultiDiGraph): Graph to use when preparing step for
                execution.
            executor (AbstractXDLExecutor): Executor to compile
                :py:attr:`start_block` with.
        """
        self.executor = executor
        self.graph = graph
        self.on_prepare_for_execution(get_graph(graph))
        self.start_block = self.on_start()
        self.executor.prepare_block_for_execution(self.graph, self.start_block)

    def execute(
        self,
        platform_controller: Any,
        logger: logging.Logger = None,
        level: int = 0,
        step_indexes: List[int] = None,
    ) -> None:
        """Execute step lifecycle. :py:meth:`on_start`, followed by
        :py:meth:`on_continue` repeatedly until an empty list is returned,
        followed by :py:meth:`on_finish`, after which all threads are joined as
        fast as possible.

        Args:
            platform_controller (Any): Platform controller object to use for
                executing steps.
            logger (Logger): Logger object.
            level (int): Level of recursion in step execution.
            step_indexes (List[int]): Indexes into steps list and substeps
                lists.

        Returns:
            bool: ``True`` if execution should continue, ``False`` if execution
            should stop.
        """
        if logger is None:
            logger = get_logger()

        # Not simulation, execute as normal
        if self.started:
            self.reset()

        # For case that step is executed outside of XDL context.
        if not step_indexes:
            step_indexes = [0]

        # Take copy of step indexes for logging once step as finished as the
        # list will be altered by substeps
        self_step_indexes = copy.copy(step_indexes)

        self.started = True

        if self.start_block is None:
            raise XDLError('Dynamic step has not been prepared for execution.\
 if executing steps individually, please use\
 `xdl_obj.execute(platform_controller, step_index)` rather than\
 `xdl_obj.steps[step_index].execute(platform_controller)`.')

        # If platform controller simulation flag is True, run simulation steps
        if platform_controller.simulation is True:

            # Run simulation steps
            self.simulate(
                platform_controller,
                logger=logger,
                step_indexes=step_indexes,
                level=level + 1
            )

            # Log step completion and return
            logger.info(finished_executing_step_msg(self, self_step_indexes))
            return True

        # Log step start timestamp
        log_duration(self, 'start')

        substep_index = 0

        # Execute steps from on_start
        for step in self.start_block:
            step_indexes.append(0)
            step_indexes[level + 1] = substep_index
            step_indexes = step_indexes[:level + 2]
            logger.info(execution_log_str(step, step_indexes))
            self.executor.execute_step(
                platform_controller,
                step,
                async_steps=self.async_steps,
                step_indexes=step_indexes,
                level=level + 1,
            )
            if isinstance(step, AbstractAsyncStep):
                self.async_steps.append(step)
            substep_index += 1

        # Repeatedly execute steps from on_continue until empty list returned
        continue_block = self.on_continue()
        self.executor.prepare_block_for_execution(self.graph, continue_block)

        while continue_block:
            for step in continue_block:
                step_indexes.append(0)
                step_indexes[level + 1] = substep_index
                step_indexes = step_indexes[:level + 2]
                logger.info(execution_log_str(step, step_indexes))
                if isinstance(step, AbstractAsyncStep):
                    self.async_steps.append(step)
                self.executor.execute_step(
                    platform_controller,
                    step,
                    async_steps=self.async_steps,
                    step_indexes=step_indexes,
                    level=level + 1,
                )
                substep_index += 1

            continue_block = self.on_continue()
            self.executor.prepare_block_for_execution(
                self.graph, continue_block)

        # Execute steps from on_finish
        finish_block = self.on_finish()
        self.executor.prepare_block_for_execution(self.graph, finish_block)

        for step in finish_block:
            step_indexes.append(0)
            step_indexes[level + 1] = substep_index
            step_indexes = step_indexes[:level + 2]
            logger.info(execution_log_str(step, step_indexes))
            self.executor.execute_step(
                platform_controller,
                step,
                async_steps=self.async_steps,
                step_indexes=step_indexes
            )
            if isinstance(step, AbstractAsyncStep):
                self.async_steps.append(step)
            substep_index += 1

        # Kill all threads
        self._post_finish()

        # Log step end timestamp
        log_duration(self, 'end')
        logger.info(finished_executing_step_msg(self, self_step_indexes))

        return True

    def simulate(
        self,
        platform_controller: Any,
        logger: logging.Logger = None,
        level: int = 0,
        step_indexes: List[int] = None
    ) -> str:
        """Run simulation steps to catch any errors that may occur during
        execution.

        Args:
            platform_controller (Any): Platform controller to use to run
                simulation steps. Should be in simulation mode.
            logger (logging.Logger): XDL logger object.
            level (int): Recursion level of step.
            step_indexes (List[int]): Indexes into steps list and substeps
                lists.
        """
        simulation_steps = self.get_simulation_steps()
        step_indexes.append(0)
        for i, step in enumerate(simulation_steps):
            step_indexes[level] = i
            step_indexes = step_indexes[:level + 1]
            logger.info(
                execution_log_str(step, step_indexes=step_indexes))
            step.execute(
                platform_controller,
                logger=logger,
                level=level,
                step_indexes=step_indexes
            )

    @abstractmethod
    def get_simulation_steps(self) -> List[Step]:
        """Should return all steps that it is possible for the step to run when
        it actually executes. The point of this is that due to the fact the
        steps list is not known ahead of time in a dynamic step, normal
        simulation cannot be done. So this is here to provide a means of
        specifying steps that should pass simulation.

        Returns:
            List[Step]: List of all steps that it is possible for the dynamic
            step to execute.
        """
        return []

    def reagents_consumed(self, graph: MultiDiGraph) -> Dict[str, float]:
        """Return dictionary of reagents and volumes consumed in mL like this:
        ``{ reagent: volume... }``. Can be overridden otherwise just recursively
        adds up volumes used by base steps.

        Args:
            graph (MultiDiGraph): Graph to use when calculating volumes of
                reagents consumed by step.

        Returns:
            Dict[str, float]: Dict of reagents volumes consumed by step in
            format ``{reagent_id: reagent_volume...}``.
        """
        reagents_consumed = {}
        for substep in self.start_block:
            step_reagents_consumed = substep.reagents_consumed(graph)
            for reagent, volume in step_reagents_consumed.items():
                if reagent in reagents_consumed:
                    reagents_consumed[reagent] += volume
                else:
                    reagents_consumed[reagent] = volume
        return reagents_consumed

    def duration(self, graph: MultiDiGraph) -> int:
        """Return duration of start block, since duration after that is unknown.

        Returns:
            int: Estimated duration of step in seconds.
        """
        duration = FTNDuration(0, 0, 0)
        for step in self.start_block:
            duration += step.duration(graph)
        return duration

class UnimplementedStep(Step):
    """Abstract base class for steps that have no implementation but are
    included either as stubs or for the purpose of showing requirements or
    ``human_readable``.

    Args:
        param_dict (Dict[str, Any]): Step properties dict to initialize step
            with.
    """
    def __init__(self, param_dict: Dict[str, Any]) -> None:
        super().__init__(param_dict)
        self.steps = []

    def execute(self, platform_controller, logger=None, level=0):
        raise NotImplementedError(
            f'{self.__class__.__name__} step is unimplemented.')

def get_base_steps(step: Step) -> List[AbstractBaseStep]:
    """Return list of given step's base steps. Recursively descends step tree
    to find base steps. Here rather than in utils as uses ``AbstractBaseStep``
    type so would cause circular import.

    Args:
        step (Step): Step to get base steps from.

    Returns:
        List[AbstractBaseStep]: List of step's base steps.
    """
    base_steps = []
    for step in step.steps:
        if isinstance(step, AbstractBaseStep):
            base_steps.append(step)
        else:
            base_steps.extend(get_base_steps(step))
    return base_steps

def pretty_props_table(props: Dict[str, Any]) -> str:
    """Make neat props table for printing to terminal. Has no table lines but
    aligns items neatly.

    Args:
        props (Dict[str, Any]): Step properties dict

    Returns:
        str: Step properties table neatly formatted.
    """
    return tabulate.tabulate(
        [
            [k, str(v)]
            for k, v in props.items()
            if k != 'children'
        ],
        tablefmt='plain',
    )

def execution_log_str(
        step: Step, step_indexes: List[int] = []) -> str:
    """Return strings to log when step begins executing.

    Args:
        step (Step): Step beginning execution.
        step_indexes (List[int]): Indexes into steps list and substeps lists.

    Returns:
        str: Log message for when the step begins executing.
    """
    # First line, e.g. "Executing step 2.3.1"
    step_index_str = '.'.join([str(idx + 1) for idx in step_indexes])
    first_line = termcolor.colored(
        f'Executing step {step_index_str}:', color='green', attrs=['bold'])

    # Step human readable description
    human_readable = termcolor.colored(
        f'{step.human_readable()}.', attrs=['bold'])

    # Step name
    step_name = termcolor.colored(step.name, color='cyan', attrs=['bold'])

    # Step properties table
    prop_table = termcolor.colored(
        pretty_props_table(step.properties), color='cyan')

    # Combine all message parts and return
    return f'{first_line}\n{human_readable}\n{step_name}\n{prop_table}\n'

def finished_executing_step_msg(step: Step, step_indexes: List[int]) -> str:
    """Message to log when step finishes executing.

    Args:
        step (Step): Step that has finished executing.
        step_indexes (List[int]): Indexes into steps list and substeps lists.

    Returns:
        str: Log message for when step finishes executing.
    """
    step_index_str = '.'.join([
        str(idx + 1) for idx in step_indexes])
    return termcolor.colored(
        f'Finished executing step {step_index_str} ',
        color='green', attrs=['bold'],
    ) + termcolor.colored(step.name, color='cyan', attrs=['bold']) + '\n'
