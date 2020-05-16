from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE
from ...utils.prop_limits import (
    TEMP_PROP_LIMIT,
    ROTATION_SPEED_PROP_LIMIT,
    TIME_PROP_LIMIT,
    PRESSURE_PROP_LIMIT,
)

class AbstractEvaporateStep(AbstractStepTemplate):
    """Evaporate solvent.

    Name: Evaporate

    Mandatory props:
        vessel (vessel): Vessel to evaporate solvent from.
        pressure (float): Vacuum pressure to use for evaporation.
        temp (float): Temperature to heat contents of vessel to for evaporation.
        time (float): Time to evaporate for.
        rotation_speed (float): If using traditional rotavap, speed in RPM at
            which to rotate evaporation flask.
    """
    MANDATORY_NAME = 'Evaporate'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'pressure': float,
        'time': float,
        'temp': float,
        'rotation_speed': float,
    }

    MANDATORY_DEFAULT_PROPS = {
        'time': None,
        'temp': None,
        'pressure': None,
        'rotation_speed': None
    }

    MANDATORY_PROP_LIMITS = {
        'time': TIME_PROP_LIMIT,
        'temp': TEMP_PROP_LIMIT,
        'rotation_speed': ROTATION_SPEED_PROP_LIMIT,
        'pressure': PRESSURE_PROP_LIMIT,
    }
