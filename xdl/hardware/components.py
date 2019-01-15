from ..utils.xdl_base import XDLBase 
from ..constants import *

class Component(XDLBase):
    """Base component class. At moment does nothing more than XDLBase."""
    def __init__(self):
        super().__init__()


class Reactor(Component):

    def __init__(self, xid, volume):
        """        
        Args:
            xid (str): Unique identifier for reactor i.e. 'reactor1'
            volume_ml (float): Reactor volume in mL.
        """
        self.properties = {
            'xid': xid,
            'volume': volume,
        }

class SeparatingFunnel(Component):

    def __init__(self, xid, volume):
        """        
        Args:
            xid (str): Unique identifier for vessel i.e. 'separator1'
            volume_ml (float): Vesesel volume in mL.
        """
        self.properties = {
            'xid': xid,
            'volume': volume,
        }

class FilterFlask(Component):

    def __init__(self, xid, volume, dead_volume):
        """        
        Args:
            xid (str): Unique identifier for vessel i.e. 'filter1'
            volume (float): Vessel volume in mL.
            dead_volume (float): Volume of space below filter in mL.
        """
        self.properties = {
            'xid': xid,
            'volume': volume,
            'dead_volume': dead_volume,
        }

class Flask(Component):

    def __init__(self, xid, volume):
        """        
        Args:
            xid (str): Unique identifier for vessel i.e. 'flask1'
            volume (float): Vessel volume in mL.
        """
        self.properties = {
            'xid': xid,
            'volume': volume,
        }

class Waste(Component):

    def __init__(self, xid, volume):
        """        
        Args:
            xid (str): Unique identifier for vessel i.e. 'waste1'
            volume (float): Vessel volume in mL.
        """
        self.properties = {
            'xid': xid,
            'volume': volume,
        }

class Hardware(object):
    """
    Object describing entire setup. The only purpose is easily accessible lists
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
            if type(component) == Reactor:
                self.reactors.append(component)
            elif type(component) == SeparatingFunnel:
                self.separators.append(component)
            elif type(component) == FilterFlask:
                self.filters.append(component)
            elif type(component) == Flask:
                self.flasks.append(component)
            elif type(component) == Waste:
                self.wastes.append(component)

        self.waste_xids = [item.xid for item in self.wastes]
        for component_list in [self.filters, self.separators]:
            for i in reversed(range(len(component_list))):
                component = component_list[i]
                if '_' in component.xid:
                    new_id = component.xid.split('_')[1]
                    if 'bottom' in component.xid:
                        component.xid = new_id
                    else:
                        component_list.pop(i)

    def __getitem__(self, item):
        """
        Get components like graphml_hardware['filter'].
        """
        if 'filter' in item and ('top' in item or 'bottom' in item):
            item = item.split('_')[1] # get 'filter' from 'filter_filter_bottom'
        for component in self.components:
            if component.xid == item:
                return component
        return None

    def __iter__(self):
        return self.components