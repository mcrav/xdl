from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE

class AbstractRunColumnStep(AbstractStepTemplate):
    """Placeholder. Needs done properly in future.
    """
    MANDATORY_NAME = 'RunColumn'

    MANDATORY_PROP_TYPES = {
        'from_vessel': VESSEL_PROP_TYPE,
        'to_vessel': VESSEL_PROP_TYPE,
        'column': str,
    }
