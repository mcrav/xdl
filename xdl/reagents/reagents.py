from ..constants import *
from ..utils.xdl_base import XDLBase
from ..utils.errors import XDLError

VALID_REAGENT_ROLES = [
    'catalyst',
    'reagent',
    'solvent',
    'substrate',
]

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
        role: str = None,
        last_minute_addition: str = None,
        last_minute_addition_volume: float = None,
    ) -> None:
        super().__init__(locals())
        self.validate_role()

    def validate_role(self):
        try:
            assert not self.role or self.role in VALID_REAGENT_ROLES
        except AssertionError:
            raise XDLError(f'Invalid role "{self.role}" given for reagent "{self.id}". Valid roles: {", ".join(VALID_REAGENT_ROLES)}')
