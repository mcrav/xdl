from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE
from ...utils.prop_limits import TIME_PROP_LIMIT, ROTATION_SPEED_PROP_LIMIT

class AbstractStirStep(AbstractStepTemplate):
    """Stir vessel for given time.

    Name: Stir

    Mandatory props:
        vessel (vessel): Vessel to stir.
        time (float): Time to stir vessel for.
        stir_speed (float): Speed in RPM at which to stir at.
    """
    MANDATORY_NAME = 'Stir'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'time': float,
        'stir_speed': float,
    }

    MANDATORY_DEFAULT_PROPS = {
        'stir_speed': None,
    }

    MANDATORY_PROP_LIMITS = {
        'time': TIME_PROP_LIMIT,
        'stir_speed': ROTATION_SPEED_PROP_LIMIT,
    }

class AbstractStartStirStep(AbstractStepTemplate):
    """Start stirring vessel.

    Name: StartStir

    Mandatory props:
        vessel (vessel): Vessel to start stirring.
        stir_speed (float): Speed in RPM at which to stir at.
    """
    MANDATORY_NAME = 'StartStir'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'stir_speed': float,
    }

    MANDATORY_DEFAULT_PROPS = {
        'stir_speed': None,
    }

    MANDATORY_PROP_LIMITS = {
        'stir_speed': ROTATION_SPEED_PROP_LIMIT
    }

class AbstractStopStirStep(AbstractStepTemplate):
    """Stop stirring given vessel.

    Name: StopStir

    Mandatory props:
        vessel (vessel): Vessel to stop stirring.
    """
    MANDATORY_NAME = 'StopStir'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
    }
