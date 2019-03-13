# For type annotations
import logging
import copy
import sys

if False:
    from chempiler import Chempiler

from ..utils import XDLBase

class Step(XDLBase):
    """Base class for all step objects.
    
    Attributes:
        properties (dict): Dictionary of step properties. Should be implemented
            in step __init__.
        steps (list): List of step objects. Should be implemented in step
            __init__.
        human_readable (str): Description of actions taken by step. Should be
            implemented in step __init__.
    """
    def __init__(self, param_dict):
        super().__init__(param_dict)
        if 'kwargs' in param_dict:
            kwargs = ['repeat']
            for kwarg in kwargs:
                if kwarg in param_dict['kwargs']:
                    self.properties[kwarg] = param_dict['kwargs'][kwarg]
        self.steps = []
        self.human_readable = ''
        self.requirements = {}
        self.vessel_chain = []

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
            logging.basicConfig(
                stream=sys.stdout, level=logging.DEBUG, format='%(message)s')
            logger = logging.getLogger('xdl_logger')
        try:
            for step in self.steps:
                logger.info('{0}{1}'.format('  ' * level, step.name))
                repeats = 1
                if 'repeat' in step.properties: repeats = step.repeats
                for _ in range(repeats):
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