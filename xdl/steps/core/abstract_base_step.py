# Std
from typing import Dict, Any
from abc import ABC, abstractmethod

# Relative
from .step import Step


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
