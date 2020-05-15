from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE, REAGENT_PROP_TYPE
from ...utils.prop_limits import (
    VOLUME_PROP_LIMIT, ROTATION_SPEED_PROP_LIMIT, TIME_PROP_LIMIT)

class AbstractAddStep(AbstractStepTemplate):
    """Add liquid reagent.

    Name: Add

    Mandatory props:
        vessel (vessel): Vessel to add reagent to. vessel prop type used as must
            declared in Hardware section of XDL.
        reagent (reagent): Reagent to add. reagent prop type used as must be
            declared in Reagents section of XDL.
        volume (float): Volume of reagent to add.
        time (float): Time to add reagent over.
        stir (bool): Stir vessel while adding reagent.
        stir_speed (float): Speed in RPM at which to stir at if stir is True.
        viscous (bool): If True, adapt process to handle viscous reagent,
            e.g. use slower addition speeds.
    """
    MANDATORY_NAME = 'Add'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'reagent': REAGENT_PROP_TYPE,
        'volume': float,
        'time': float,
        'stir': bool,
        'stir_speed': float,
        'viscous': bool,
    }

    MANDATORY_DEFAULT_PROPS = {
        'stir': False,
        'viscous': False,
        'time': None,
        'stir_speed': None
    }

    MANDATORY_PROP_LIMITS = {
        'volume': VOLUME_PROP_LIMIT,
        'time': TIME_PROP_LIMIT,
        'stir_speed': ROTATION_SPEED_PROP_LIMIT,
    }
