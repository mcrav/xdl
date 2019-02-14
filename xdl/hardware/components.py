from typing import Union, Generator
from ..utils.xdl_base import XDLBase 
from ..constants import *

class Component(XDLBase):
    """Base component class. At moment does nothing more than XDLBase.

    Args:
        xid (str): ID for the component.
        properties (dict): Property dict of the component.
        type (str): Type of the component i.e. 'ChemputerFlask'
    """
    def __init__(
        self, xid: str = None, properties: Dict[str, Any] = {}, type: str = None
    ) -> None:

        self.properties = {'xid': xid, 'type': type}
        self.properties.update(properties)

class Hardware(object):
    """
    Object describing entire setup. The purpose is easily accessible lists
    of reactors, flasks, filters, wastes etc.

    Args:
        components (List[Component]): List of Component objects.
    """
    def __init__(self, components: List[Component]) -> None:

        self.components = components
        self.component_ids = [item.xid for item in self.components]
        self.reactors = []
        self.flasks = []
        self.wastes = []
        self.filters = []
        self.separators = []
        for component in self.components:
            if component.type == CHEMPUTER_REACTOR_CLASS_NAME:
                self.reactors.append(component)
            elif component.type == CHEMPUTER_SEPARATOR_CLASS_NAME:
                self.separators.append(component)
            elif component.type == CHEMPUTER_FILTER_CLASS_NAME:
                self.filters.append(component)
            elif component.type == CHEMPUTER_FLASK_CLASS_NAME:
                self.flasks.append(component)
            elif component.type == CHEMPUTER_WASTE_CLASS_NAME:
                self.wastes.append(component)
        self.waste_xids = [waste.xid for waste in self.wastes]

    def __getitem__(self, item: str) -> Union[Component, None]:
        """
        Get components like this: graph_hardware['filter'].
        """
        for component in self.components:
            if component.xid == item:
                return component
        return None

    def __iter__(self) -> Generator[Component]:
        for item in self.components:
            yield item 