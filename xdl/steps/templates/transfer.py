from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE
from ...utils.prop_limits import VOLUME_PROP_LIMIT, TIME_PROP_LIMIT

class AbstractTransferStep(AbstractStepTemplate):
    """Transfer liquid from one vessel to another.

    Name: Transfer

    Mandatory props:
        from_vessel (vessel): Vessel to transfer liquid from.
        to_vessel (vessel): Vessel to transfer liquid to.
        volume (float): Volume of liquid to transfer from from_vessel to
            to_vessel.
        time (float): Time over which to transfer liquid.
        viscous (bool): If True, adapt process to handle viscous liquid, e.g.
            use slower move speed.
    """
    MANDATORY_NAME = 'Transfer'

    MANDATORY_PROP_TYPES = {
        'from_vessel': VESSEL_PROP_TYPE,
        'to_vessel': VESSEL_PROP_TYPE,
        'volume': float,
        'time': float,
        'viscous': bool,
    }

    MANDATORY_DEFAULT_PROPS = {
        'viscous': False,
        'time': None,
    }

    MANDATORY_PROP_LIMITS = {
        'volume': VOLUME_PROP_LIMIT,
        'time': TIME_PROP_LIMIT,
    }
