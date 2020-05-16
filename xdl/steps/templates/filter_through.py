from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE, REAGENT_PROP_TYPE

class AbstractFilterThroughStep(AbstractStepTemplate):
    """Filter liquid through solid, for example filtering reaction mixture
    through celite.

    Name: FilterThrough

    Mandatory props:
        from_vessel (vessel): Vessel containing liquid to be filtered through
            solid chemical.
        to_vessel (vessel): Vessel to send liquid to after it has been filtered
            through the solid chemical.
        through (reagent): Solid chemical to filter liquid through.
        eluting_solvent (reagent): Solvent to elute with.
        eluting_solvent_volume (float): Volume of eluting_solvent to use.
        n_elutions (int): Number of elutions to perform.
    """
    MANDATORY_NAME = 'FilterThrough'

    MANDATORY_PROP_TYPES = {
        'from_vessel': VESSEL_PROP_TYPE,
        'to_vessel': VESSEL_PROP_TYPE,
        'through': REAGENT_PROP_TYPE,
        'eluting_solvent': REAGENT_PROP_TYPE,
        'eluting_solvent_volume': float,
        'n_elutions': int,
    }

    MANDATORY_DEFAULT_PROPS = {
        'eluting_solvent': None,
        'eluting_solvent_volume': None,
        'n_elutions': None,
    }
