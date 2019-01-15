
from ..utils.xdl_base import XDLBase

class Step(XDLBase):
    """Base class for all step objects."""
    
    def __init__(self):
        self.name = ''
        self.properties = {}
        self.steps = []
        self.human_readable = ''

    @property
    def name(self):
        return type(self).__name__

    def execute(self, chempiler):
        """
        Execute self with given Chempiler object.
        
        Arguments:
            chempiler {chempiler.Chempiler} -- Initialised Chempiler object.
        """
        for step in self.steps:
            keep_going = step.execute(chempiler)
            if not keep_going:
                return False
        return True
