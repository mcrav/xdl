from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE
from ...utils.prop_limits import (
    TEMP_PROP_LIMIT,
    TIME_PROP_LIMIT,
    ROTATION_SPEED_PROP_LIMIT
)

class AbstractPrecipitateStep(AbstractStepTemplate):
    """Cause precipitation by changing temperature and stirring.

    Name: Precipitate

    Mandatory props:
        vessel (vessel): Vessel to heat/chill and stir to cause precipitation.
        temp (float): Temperature to heat/chill vessel to.
        time (float): Time to stir vessel for at given temp.
        stir_speed (float): Speed in RPM at which to stir.
    """
    MANDATORY_NAME = 'Precipitate'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'temp': float,
        'time': float,
        'stir_speed': float,
    }

    DEFAULT_PROPS = {
        'temp': None,
        'time': None,
        'stir_speed': None,
    }

    MANDATORY_PROP_LIMITS = {
        'temp': TEMP_PROP_LIMIT,
        'time': TIME_PROP_LIMIT,
        'stir_speed': ROTATION_SPEED_PROP_LIMIT,
    }
