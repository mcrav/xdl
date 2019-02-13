from ..constants import *
from ..utils.xdl_base import XDLBase

class Reagent(XDLBase):
    """Base reagent class.

    Args:
        xid (str): Unique identifier containing only letters, numbers and _
        cas (int, optional): Defaults to None. CAS number of reagent as int.
    """
    def __init__(self, xid=None, cas=None):
        
        self.properties = {
            'xid': xid,
            'cas': cas,
        }