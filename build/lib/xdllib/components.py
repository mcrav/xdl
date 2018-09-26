from .utils import XDLElement
from .constants import *

class Component(XDLElement):

    def __init__(self):
        super().__init__()


class Reactor(Component):
    
    def __init__(self, id_word=None, volume_ml=None, reactor_type='default', atmosphere=None):
        
        self.name = 'Reactor'
        self.properties = {
            'id': id_word,
            'volume_ml': volume_ml,
            'reactor_type': reactor_type,
            'atmosphere': atmosphere,
        }
        self.get_defaults()

class FilterFlask(Component):
    
    def __init__(self, id_word=None, volume_ml=None,):

        self.name = 'FilterFlask'    
        self.properties = {
            'id': id_word,
            'volume_ml': volume_ml,
        }

class Flask(Component):
    
    def __init__(self, id_word=None, volume_ml=None):
        
        self.properties = {
            'id': id_word,
            'volume_ml': volume_ml,
        }

class Waste(Component):
    
    def __init__(self, id_word=None, volume_ml=None):
        
        self.properties = {
            'id': id_word,
            'volume_ml': volume_ml,
        }

class Hardware(object):

    def __init__(self, components):

        self.components = components
        self.component_ids = [item.properties['id'] for item in self.components]
        self.reactors = []
        self.flasks = []
        self.wastes = []
        self.filters = []
        for component in self.components:
            if component.properties['id'].startswith('reactor'):
                self.reactors.append(component)
            elif component.properties['id'].startswith('flask'):
                self.flasks.append(component)
            elif component.properties['id'].startswith('waste'):
                self.wastes.append(component)
            elif component.properties['id'].startswith('filter'):
                self.filters.append(component)