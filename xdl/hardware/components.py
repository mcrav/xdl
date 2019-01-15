from ..utils.xdl_base import XDLBase 
from ..constants import *

class Component(XDLBase):
    """Base component class. At moment does nothing more than XDLBase."""
    def __init__(self):
        super().__init__()


class Reactor(Component):
    """Reactor class."""
    def __init__(self, cid=None, volume_ml=None, reactor_type='default', atmosphere=None):
        """
        Keyword Arguments:
            cid {str} -- Component ID i.e. 'reactor1'
            volume_ml {float} -- Volume of vessel in mL.
            reactor_type {str} -- i.e. 'RoundBottomFlask'
            atmosphere {str} -- None or 'inert'
        """
        self.name = 'Reactor'
        self.properties = {
            'cid': cid,
            'volume_ml': volume_ml,
            'reactor_type': reactor_type,
            'atmosphere': atmosphere,
        }
        self.get_defaults()

    @property
    def cid(self):
        return self.properties['cid']

    @cid.setter
    def cid(self, val):
        self.properties['cid'] = val
        self.update()

    @property
    def volume_ml(self):
        return self.properties['volume_ml']

    @volume_ml.setter
    def volume_ml(self, val):
        self.properties['volume_ml'] = val
        self.update()

    @property
    def reactor_type(self):
        return self.properties['reactor_type']

    @reactor_type.setter
    def reactor_type(self, val):
        self.properties['reactor_type'] = val
        self.update()

    @property
    def atmosphere(self):
        return self.properties['atmosphere']

    @atmosphere.setter
    def atmosphere(self, val):
        self.properties['atmosphere'] = val
        self.update()

class SeparatingFunnel(Component):

    def __init__(self, cid=None, volume_ml=None,):

        self.name = 'SeparatingFunnel'
        self.properties = {
            'cid': cid,
            'volume_ml': volume_ml,
        }

    @property
    def cid(self):
        return self.properties['cid']

    @cid.setter
    def cid(self, val):
        self.properties['cid'] = val
        self.update()

    @property
    def volume_ml(self):
        return self.properties['volume_ml']

    @volume_ml.setter
    def volume_ml(self, val):
        self.properties['volume_ml'] = val
        self.update()

class FilterFlask(Component):

    def __init__(self, cid=None, volume_ml=None, dead_volume=None):

        self.name = 'FilterFlask'
        self.properties = {
            'cid': cid,
            'volume_ml': volume_ml,
            'dead_volume': dead_volume,
        }

    @property
    def cid(self):
        return self.properties['cid']

    @cid.setter
    def cid(self, val):
        self.properties['cid'] = val
        self.update()

    @property
    def volume_ml(self):
        return self.properties['volume_ml']

    @volume_ml.setter
    def volume_ml(self, val):
        self.properties['volume_ml'] = val
        self.update()

    @property
    def dead_volume(self):
        return self.properties['dead_volume']

    @dead_volume.setter
    def dead_volume(self, val):
        self.properties['dead_volume'] = val
        self.update()

class Flask(Component):

    def __init__(self, cid=None, volume_ml=None):

        self.name = 'Flask'
        self.properties = {
            'cid': cid,
            'volume_ml': volume_ml,
        }

    @property
    def cid(self):
        return self.properties['cid']

    @cid.setter
    def cid(self, val):
        self.properties['cid'] = val
        self.update()

    @property
    def volume_ml(self):
        return self.properties['volume_ml']

    @volume_ml.setter
    def volume_ml(self, val):
        self.properties['volume_ml'] = val
        self.update()

class Waste(Component):

    def __init__(self, cid=None, volume_ml=None):

        self.name = 'Waste'
        self.properties = {
            'cid': cid,
            'volume_ml': volume_ml,
        }

    @property
    def cid(self):
        return self.properties['cid']

    @cid.setter
    def cid(self, val):
        self.properties['cid'] = val
        self.update()

    @property
    def volume_ml(self):
        return self.properties['volume_ml']

    @volume_ml.setter
    def volume_ml(self, val):
        self.properties['volume_ml'] = val
        self.update()

class Hardware(object):
    """
    Object describing entire setup. The only purpose is easily accessible lists
    of reactors, flasks, filters, wastes etc.
    """
    def __init__(self, components):

        self.components = components
        self.component_ids = [item.cid for item in self.components]
        self.reactors = []
        self.flasks = []
        self.wastes = []
        self.filters = []
        self.separators = []
        for component in self.components:
            if component.cid.startswith('reactor'):
                self.reactors.append(component)
            elif component.cid.startswith(('separator', 'flask_separator')):
                self.separators.append(component)
            elif component.cid.startswith(('filter')):
                self.filters.append(component)
            elif component.cid.startswith('flask'):
                self.flasks.append(component)
            elif component.cid.startswith('waste'):
                self.wastes.append(component)


        self.waste_cids = [item.cid for item in self.wastes]
        for component_list in [self.filters, self.separators]:
            for i in reversed(range(len(component_list))):
                component = component_list[i]
                if '_' in component.cid:
                    new_id = component.cid.split('_')[1]
                    if 'bottom' in component.cid:
                        component.cid = new_id
                    else:
                        component_list.pop(i)

    def __getitem__(self, item):
        """
        Get components like graphml_hardware['filter'].
        """
        if 'filter' in item and ('top' in item or 'bottom' in item):
            item = item.split('_')[1] # get 'filter' from 'filter_filter_bottom'
        for component in self.components:
            if component.cid == item:
                return component
        return None

    def __iter__(self):
        return self.components