import abc

class AbstractPlatform(object):
    """Container class to hold everything necessary for a platform to be used
    with the XDL framework.

    Args:
        executor (AbstractXDLExecutor): Implementation of
            abstract class AbstractXDLExecutor.
        step_library (Dict[str, Step]): Dictionary of step names and
            corresponding step classes.
    """
    def __init__(self):
        pass

    @property
    @abc.abstractmethod
    def executor(self):
        return None

    @property
    @abc.abstractmethod
    def step_library(self):
        return None
