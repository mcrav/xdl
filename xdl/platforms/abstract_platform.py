from typing import Optional
import abc
from ..utils.schema import generate_schema

class AbstractPlatform(object):
    """Container class to hold everything necessary for a platform to be used
    with the XDL framework.
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

    @abc.abstractmethod
    def graph(
        self,
        graph_template: Optional[str] = None,
        save: Optional[str] = None,
        **kwargs
    ):
        return

    @property
    def schema(self):
        return generate_schema(self.step_library)

    @property
    def localisation(self):
        return {}
