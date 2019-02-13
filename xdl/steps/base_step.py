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
    
    def __init__(self):
        self.properties = {}
        self.steps = []
        self.human_readable = ''

    def execute(self, chempiler, logger=None, level=0):
        """
        Execute self with given Chempiler object.
        
        Args:
            chempiler (chempiler.Chempiler): Initialised Chempiler object.
            logger (logging.Logger): Logger to handle output step output.
            level (int): Level of recursion in step execution.
        """
        level += 1
        try:
            for step in self.steps:
                if logger:
                    logger.info('{0}{1}'.format('  ' * level, step.name))
                keep_going = step.execute(chempiler, logger, level=level)
                if not keep_going:
                    return False
            return True
        except Exception as e:
            if logger:
                logger.exception(str(e), exc_info=1)
            raise(e)