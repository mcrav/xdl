from ..constants import *
from ..utils.xdl_base import XDLBase

class Reagent(XDLBase):
    """Base reagent class.

    Args:
        xid (str): Unique identifier containing only letters, numbers and _
        clean_type (str): 'organic' or 'aqueous'. Used by XDLExecutor to decide
            what solvent to use in CleanBackbone steps.
        cas (int, optional): Defaults to None. CAS number of reagent as int.
    """
    def __init__(
        self,
        id: str,
        cleaning_solvent: str = None,
        use_for_cleaning: str = False,
        stir: bool = False,
        cas: int = None,
        temp: float = None,
        last_minute_addition: str = None,
        last_minute_addition_volume: float = None,
    ) -> None:
        super().__init__(locals())
