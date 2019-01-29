from ..utils import XDLBase

class Step(XDLBase):
    """Base class for all step objects."""
    
    def __init__(self):
        self.name = ''
        self.properties = {}
        self.steps = []
        self.human_readable = ''

    def execute(self, chempiler, logger=None):
        """
        Execute self with given Chempiler object.
        
        Args:
            chempiler {chempiler.Chempiler} -- Initialised Chempiler object.
        """
        try:
            for step in self.steps:
                if logger:
                    logger.info(step.name)
                keep_going = step.execute(chempiler, logger)
                if not keep_going:
                    return False
            return True
        except Exception as e:
            if logger:
                logger.exception(str(e), exc_info=1)
            raise(e)
