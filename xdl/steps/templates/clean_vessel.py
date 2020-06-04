from .abstract_template import AbstractStepTemplate
from ...utils.prop_limits import VOLUME_PROP_LIMIT, TEMP_PROP_LIMIT
from ...constants import VESSEL_PROP_TYPE, REAGENT_PROP_TYPE

class AbstractCleanVesselStep(AbstractStepTemplate):
    """Clean vessel.

    Name: CleanVessel

    Mandatory props:
        vessel (vessel): Vessel to clean.
        solvent (reagent): Solvent to clean vessel with.
        volume (float): Volume of solvent to clean vessel with.
        temp (float): Temperature to heat vessel to while cleaning.
    """
    MANDATORY_NAME = 'CleanVessel'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'solvent': REAGENT_PROP_TYPE,
        'volume': float,
        'temp': float,
    }

    MANDATORY_DEFAULT_PROPS = {
        'volume': None,
        'temp': None
    }

    MANDATORY_PROP_LIMITS = {
        'volume': VOLUME_PROP_LIMIT,
        'temp': TEMP_PROP_LIMIT,
    }
