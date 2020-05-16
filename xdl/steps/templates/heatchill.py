from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE
from ...utils.prop_limits import (
    TEMP_PROP_LIMIT, TIME_PROP_LIMIT, ROTATION_SPEED_PROP_LIMIT
)

class AbstractHeatChillStep(AbstractStepTemplate):
    """Heat or chill vessel.

    Name: HeatChill

    Mandatory props:
        vessel (vessel): Vessel to heat or chill.
        temp (float): Temperature to heat or chill vessel to.
        time (float): Time to heat or chill vessel for.
        stir (bool): If True, stir while heating or chilling.
        stir_speed (float): Speed in RPM at which to stir at if stir is True.
    """
    MANDATORY_NAME = 'HeatChill'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'time': float,
        'temp': float,
        'stir': bool,
        'stir_speed': float,
    }

    MANDATORY_DEFAULT_PROPS = {
        'stir': True,
        'stir_speed': None,
    }

    MANDATORY_PROP_LIMITS = {
        'time': TIME_PROP_LIMIT,
        'temp': TEMP_PROP_LIMIT,
        'stir_speed': ROTATION_SPEED_PROP_LIMIT,
    }
