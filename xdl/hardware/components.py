from ..utils.xdl_base import XDLBase 
from ..constants import *

class Component(XDLBase):
    """Base component class. At moment does nothing more than XDLBase."""
    def __init__(self, xid=None, properties={}):
        self.properties = {'xid': xid}
        self.properties.update(properties)

class Hardware(object):
    """
    Object describing entire setup. The purpose is easily accessible lists
    of reactors, flasks, filters, wastes etc.
    """
    def __init__(self, components):
        """Sort components into categories.
        
        Args:
            components (List[Component]): List of Component objects.
        """
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

    def __getitem__(self, item):
        """
        Get components like this: graph_hardware['filter'].
        """
        for component in self.components:
            if component.xid == item:
                return component
        return None

    def __iter__(self):
        for item in self.components:
            yield item 