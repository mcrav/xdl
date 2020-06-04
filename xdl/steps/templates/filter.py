from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE
from ...utils.prop_limits import ROTATION_SPEED_PROP_LIMIT, TIME_PROP_LIMIT

class AbstractFilterStep(AbstractStepTemplate):
    """Filter mixture.

    Name: Filter

    Mandatory props:
        vessel (vessel): Vessel containing mixture to filter.
        filtrate_vessel (vessel): Vessel to send filtrate to. If not given,
            filtrate is sent to waste.
        stir (bool): Stir vessel while adding reagent.
        stir_speed (float): Speed in RPM at which to stir at if stir is True.
        vacuum_time (float): Time to apply vacuum for after filtrate has been
            removed.
    """
    MANDATORY_NAME = 'Filter'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'filtrate_vessel': VESSEL_PROP_TYPE,
        'stir': bool,
        'stir_speed': float,
        'vacuum_time': float,
    }

    MANDATORY_DEFAULT_PROPS = {
        'filtrate_vessel': None,
        'stir': False,
        'stir_speed': None,
        'vacuum_time': None
    }

    MANDATORY_PROP_LIMITS = {
        'vacuum_time': TIME_PROP_LIMIT,
        'stir_speed': ROTATION_SPEED_PROP_LIMIT,
    }
