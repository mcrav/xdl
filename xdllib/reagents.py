from .constants import *
from .utils import XDLElement

class Reagent(XDLElement):
    """Reagent class."""
    def __init__(self, id_word=None, cas=None, waste=None):
        """
        Keyword Arguments:
            id_word {str} -- Name of the reagent containing only letters and underscore.
            cas {int} -- CAS number as int.
            waste {str} -- Type of waste reagent should go to.
                           'aqueous', 'organic', 'chlorinated_organic', or 'metal'.
        """
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
