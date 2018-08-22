from constants import *
from steps_generic import XDLElement

class Reagent(XDLElement):

    def __init__(self, id_word=None, cas=None,):

        self.properties = {
            'id': id_word,
            'cas': cas,
        }