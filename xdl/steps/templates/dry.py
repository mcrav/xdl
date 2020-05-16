from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE
from ...utils.prop_limits import (
    TEMP_PROP_LIMIT, TIME_PROP_LIMIT, PRESSURE_PROP_LIMIT
)

class AbstractDryStep(AbstractStepTemplate):
    """Dry solid.

    Name: Dry

    Mandatory props:
        vessel (vessel): Vessel containing solid to dry.
        time (float): Time to apply vacuum for.
        pressure (float): Vacuum pressure to use for drying.
        temp (float): Temp to heat vessel to while drying.
        continue_heatchill (bool): If True, continue heating after step has
            finished. If False, stop heating at end of step.
    """
    MANDATORY_NAME = 'Dry'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'time': float,
        'pressure': float,
        'temp': float,
        'continue_heatchill': bool,
    }

    MANDATORY_DEFAULT_PROPS = {
        'time': None,
        'temp': None,
        'pressure': None,
        'continue_heatchill': False,
    }

    MANDATORY_PROP_LIMITS = {
        'time': TIME_PROP_LIMIT,
        'temp': TEMP_PROP_LIMIT,
        'pressure': PRESSURE_PROP_LIMIT,
    }
