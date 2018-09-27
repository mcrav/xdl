from .constants import *
from .utils import XDLElement

class Reagent(XDLElement):

    def __init__(self, id_word=None, cas=None, waste=None):

        self.properties = {
            'id': id_word,
            'cas': cas,
            'waste': waste,
        }
    @property
    def id_word(self):
        return self.properties['id']

    @property
    def cas(self):
        return self.properties['cas']

    @property
    def waste(self):
        return self.properties['waste']
