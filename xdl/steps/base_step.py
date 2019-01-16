from ..utils import XDLBase

class Step(XDLBase):
    """Base class for all step objects."""
    
    def __init__(self):
        self.name = ''
        self.properties = {}
        self.steps = []
        self.human_readable = ''

    def execute(self, chempiler):
        """
        Execute self with given Chempiler object.
        
        Args:
            chempiler {chempiler.Chempiler} -- Initialised Chempiler object.
        """
        for step in self.steps:
            keep_going = step.execute(chempiler)
            if not keep_going:
                return False
        return True
