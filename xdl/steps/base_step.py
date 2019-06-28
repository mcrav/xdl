# For type annotations
import logging
import copy
import sys
from abc import ABC, abstractmethod
from ..utils import initialise_logger
from ..utils.misc import format_property
from ..localisation import HUMAN_READABLE_STEPS

if False:
    from chempiler import Chempiler

from ..utils import XDLBase

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
                human_readable = HUMAN_READABLE_STEPS[self.name][language].format(
                    **self.formatted_properties())
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
        level += 1
        if not logger:
            logger = logging.getLogger('xdl_logger')
            if not logger.hasHandlers():
                logger = initialise_logger(logger)
        try:
            repeats = 1
            if 'repeat' in self.properties: repeats = int(self.repeat)
            for _ in range(repeats):
                for step in self.steps:
                    logger.info('{0}{1}'.format('  ' * level, step.name))
                    try:
                        keep_going = step.execute(chempiler, logger, level=level)
                    except Exception as e:
                        logger.info(
                            'Step failed {0} {1}'.format(type(step), step.properties))
                        raise e
                    if not keep_going:
                        return False
            return True
        except Exception as e:
            if logger:
                logger.exception(str(e), exc_info=1)
            raise(e)

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

    @abstractmethod
    def execute(self, chempiler):
        return False

class UnimplementedStep(Step):
    """Abstract base class for steps that have no implementation but are included
    either as stubs or for the purpose of showing requirements / human_readable.
    """
    def __init__(self, param_dict):
        super().__init__(param_dict)
        self.steps = []

    def execute(self, chempiler):
        raise NotImplementedError(
            f'{self.__class__.__name__} step is unimplemented.')

    @property
    def requirements(self):
        return {}