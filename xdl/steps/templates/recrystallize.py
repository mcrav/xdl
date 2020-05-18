from .abstract_template import AbstractStepTemplate
from ...constants import VESSEL_PROP_TYPE, REAGENT_PROP_TYPE
from ...utils.prop_limits import (
    TEMP_PROP_LIMIT,
    TIME_PROP_LIMIT,
    VOLUME_PROP_LIMIT,
)

class AbstractRecrystallizeStep(AbstractStepTemplate):
    """Recrystallize.

    Name: Recrystallize

    Mandatory props:
        vessel (vessel): Vessel to recrystallize.
        time (float): Time to wait for crystallization to occur.
        crystallize_temp (float): Temp to heat/chill vessel to while waiting for
            crystallization.
        solvent (str): Solvent to dissolve contents of vessel in before
            recrystallizing. Optional.
        solvent_volume (float): Volume of solvent to give. Ignored if solvent
            not given.
        dissolve_temp (float): Temp to heat/chill vessel to while dissolving in
            solvent. Ignored if solvent not given.
    """
    MANDATORY_NAME = 'Recrystallize'

    MANDATORY_PROP_TYPES = {
        'vessel': VESSEL_PROP_TYPE,
        'time': float,
        'crystallize_temp': float,
        'solvent': REAGENT_PROP_TYPE,
        'solvent_volume': float,
        'dissolve_temp': float,
    }

    DEFAULT_PROPS = {
        'time': None,
        'crystallize_temp': None,
        'solvent': None,
        'solvent_volume': None,
        'dissolve_temp': None,
    }

    MANDATORY_PROP_LIMITS = {
        'time': TIME_PROP_LIMIT,
        'crystallize_temp': TEMP_PROP_LIMIT,
        'dissolve_temp': TEMP_PROP_LIMIT,
        'solvent_volume': VOLUME_PROP_LIMIT,
    }
