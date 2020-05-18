from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE
from ...utils.prop_limits import (
    TEMP_PROP_LIMIT, TIME_PROP_LIMIT, ROTATION_SPEED_PROP_LIMIT
)

class AbstractHeatChillStep(AbstractStepTemplate):
    """Heat or chill vessel to given temp for given time.

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

class AbstractHeatChillToTempStep(AbstractStepTemplate):
    """Heat or chill vessel to given temperature.

    Name: HeatChillToTemp

    Mandatory props:
        vessel (vessel): Vessel to heat or chill.
        temp (float): Temperature to heat or chill vessel to.
        active (bool): If True, actively heat or chill to temp. If False, allow
            vessel to warm or cool to temp.
        continue_heatchill (bool): If True, leave heating or chilling on after
            steps finishes. If False, stop heating/chilling at end of step.
        stir (bool): If True, stir while heating or chilling.
        stir_speed (float): Speed in RPM at which to stir at if stir is True.
    """
    MANDATORY_NAME = 'HeatChillToTemp'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'temp': float,
        'active': bool,
        'continue_heatchill': bool,
        'stir': bool,
        'stir_speed': float,
    }

    MANDATORY_DEFAULT_PROPS = {
        'stir': True,
        'stir_speed': None,
        'active': True,
        'continue_heatchill': True,
    }

    MANDATORY_PROP_LIMITS = {
        'temp': TEMP_PROP_LIMIT,
        'stir_speed': ROTATION_SPEED_PROP_LIMIT,
    }

class AbstractStartHeatChillStep(AbstractStepTemplate):
    """Start heating/chilling vessel.

    Name: StartHeatChill

    Mandatory props:
        vessel (vessel): Vessel to start heating/chilling.
        temp (float): Temperature to heat or chill vessel to.
    """
    MANDATORY_NAME = 'StartHeatChill'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'temp': float,
    }

    MANDATORY_PROP_LIMITS = {
        'temp': TEMP_PROP_LIMIT,
    }

class AbstractStopHeatChillStep(AbstractStepTemplate):
    """Heat or chill vessel.

    Name: StopHeatChill

    Mandatory props:
        vessel (vessel): Vessel to stop heating/chilling.
    """
    MANDATORY_NAME = 'StopHeatChill'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'temp': float,
    }

    MANDATORY_PROP_LIMITS = {
        'temp': TEMP_PROP_LIMIT,
    }
