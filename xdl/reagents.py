from .constants import *
from .utils import XDLElement

class Reagent(XDLElement):
    """Reagent class."""
    def __init__(self, rid=None, cas=None, waste=None):
        """
        Keyword Arguments:
            rid {str} -- Reagent ID (containing only letters and underscore).
            cas {int} -- CAS number as int.
            waste {str} -- Type of waste reagent should go to.
                           'aqueous', 'organic', 'chlorinated_organic', or 'metal'.
        """
        self.properties = {
            'rid': rid,
            'cas': cas,
            'waste': waste,
        }
    @property
    def rid(self):
        return self.properties['rid']

    @property
    def cas(self):
        return self.properties['cas']

    @property
    def waste(self):
        return self.properties['waste']
