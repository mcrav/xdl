from .abstract_template import AbstractStepTemplate
from ...utils.prop_limits import VOLUME_PROP_LIMIT
from ...constants import VESSEL_PROP_TYPE, REAGENT_PROP_TYPE

class AbstractCleanVesselStep(AbstractStepTemplate):
    """Clean vessel.

    Name: CleanVessel

    Mandatory props:
        vessel (vessel): Vessel to clean.
        solvent (reagent): Solvent to clean vessel with.
        volume (float): Volume of solvent to clean vessel with.
    """
    MANDATORY_NAME = 'CleanVessel'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'solvent': REAGENT_PROP_TYPE,
        'volume': float,
    }

    MANDATORY_DEFAULT_PROPS = {
        'volume': None,
    }

    MANDATORY_PROP_LIMITS = {
        'volume': VOLUME_PROP_LIMIT,
    }
