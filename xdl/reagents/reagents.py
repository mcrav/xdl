from typing import List
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
        id (str): Unique identifier containing only letters, numbers and _
        clean_type (str): 'organic' or 'aqueous'. Used by XDLExecutor to decide
            what solvent to use in CleanBackbone steps.
        cas (int, optional): Defaults to None. CAS number of reagent as int.
        use_for_cleaning (str, optional): Defaults to False. Specifies whether
            reagent can be used as a cleaning solvent. If the reagent is
            recognised as a common solvent setting this property to False will
            NOT stop it being used for cleaning.
        stir (bool, optional): Defaults to False. Specifies whether reagent
            flask should be stirred continuously.
        temp (float, optional): Defaults to None. Specifies temperature (in
            °C) to keep reagent flask at.
        role (str, optional): Defaults to None. Specifies reagent role. NOTE:
            must be a valid reagent role if specified (catalyst, reagent,
            solvent, substrate).
        last_minute_addition (str, optional): Defaults to None. Name of reagent
            that must be added to reagent flask immediately prior to addition.
        last_minute_addition_volume (float, optional): Defaults to None. Volume
            of last minute addition.
        preserve (bool, optional): Defaults to False. True if reagent is
            expensive and should be preserved when possible; False if not.
        incompatible_reagents (list, optional): Defaults to None. List of
            reagents that are incompatible with this reagent and should never
            be mixed in the backbone.
        is_base (bool, optional): Defaults to False. Specifies whether reagent
            is a base. If True, more thorough backbone cleaning will be carried
            out after addition of this reagent.
    """

    PROP_TYPES = {
        'id': str,
        'cleaning_solvent': str,
        'use_for_cleaning': str,
        'stir': bool,
        'cas': int,
        'temp': float,
        'role': str,
        'last_minute_addition': str,
        'last_minute_addition_volume': float,
        'preserve': bool,
        'incompatible_reagents': List[str],
        'is_base': bool
    }

    DEFAULT_PROPS = {
        'is_base': False,
    }

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
        preserve: bool = False,
        incompatible_reagents: List[str] = [],
        is_base: bool = 'default'
    ) -> None:
        super().__init__(locals())
        self.validate_role()

    def validate_role(self):
        try:
            assert not self.role or self.role in VALID_REAGENT_ROLES
        except AssertionError:
            raise XDLError(f'Invalid role "{self.role}" given for reagent\
 "{self.id}". Valid roles: {", ".join(VALID_REAGENT_ROLES)}')
