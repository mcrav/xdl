from .abstract_template import AbstractStepTemplate
from ...utils.prop_limits import VOLUME_PROP_LIMIT
from ...constants import VESSEL_PROP_TYPE, REAGENT_PROP_TYPE

class AbstractRunColumnStep(AbstractStepTemplate):
    """Run column.

    Name: RunColumn

    Mandatory props:
        from_vessel (vessel): Vessel to take liquid from to run through column.
        to_vessel (vessel): Vessel to send purified product from column.
        column (vessel): Column to use.
        eluting_solvent (reagent): Solvent to elute with.
        eluting_volume (float): Volume of solvent to elute with.
        elutions (int): Number of elutions to carry out.
    """
    MANDATORY_NAME = 'RunColumn'

    MANDATORY_PROP_TYPES = {
        'from_vessel': VESSEL_PROP_TYPE,
        'to_vessel': VESSEL_PROP_TYPE,
        'column': VESSEL_PROP_TYPE,
        'eluting_solvent': REAGENT_PROP_TYPE,
        'eluting_volume': float,
        'elutions': int,
    }

    MANDATORY_DEFAULT_PROPS = {
        'eluting_solvent': None,
        'eluting_volume': None,
        'elutions': None,
    }

    MANDATORY_PROP_LIMITS = {
        'eluting_volume': VOLUME_PROP_LIMIT,
    }
