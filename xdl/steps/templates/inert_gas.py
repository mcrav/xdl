from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE
from ...utils.prop_limits import TIME_PROP_LIMIT

class AbstractEvacuateAndRefillStep(AbstractStepTemplate):
    """Evacuate vessel and refill with inert gas.

    Name: Evacuate

    Mandatory props:
        vessel (vessel): Vessel to evacuate and refill.
        repeats (int): Number of evacuation/refill cycles to perform.
    """
    MANDATORY_NAME = 'EvacuateAndRefill'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'repeats': int,
    }

class AbstractPurgeStep(AbstractStepTemplate):
    """Purge liquid by bubbling inert gas through it.

    Name: Purge

    Mandatory props:
        vessel (vessel): Vessel containing liquid to purge with inert gas.
        time (float): Time to bubble inert gas through vessel.
    """
    MANDATORY_NAME = 'Purge'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'time': float,
    }

    MANDATORY_DEFAULT_PROPS = {
        'time': None,
    }

    MANDATORY_PROP_LIMITS = {
        'time': TIME_PROP_LIMIT,
    }

class AbstractStartPurgeStep(AbstractStepTemplate):
    """Start purging liquid by bubbling inert gas through it.

    Mandatory props:
        vessel (vessel): Vessel containing liquid to purge with inert gas.
    """
    MANDATORY_NAME = 'StartPurge'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
    }

class AbstractStopPurgeStep(AbstractStepTemplate):
    """Stop bubbling inert gas through vessel.

    Mandatory props:
        vessel (vessel): Vessel to stop bubbling inert gas through.
    """
    MANDATORY_NAME = 'StopPurge'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
    }
