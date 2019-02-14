from typing import Dict, List

from ..steps import steps_synthesis
from ..steps import steps_utility
from ..steps import steps_base
from ..steps import Step
import copy
import inspect
from ..constants import *

#: Dictionary of base step name keys and step class values.
BASE_STEP_OBJ_DICT: Dict[str, type] = {
    m[0]: m[1] for m in inspect.getmembers(steps_base, inspect.isclass)}

#: Dictionary of utility step name keys and step class values.
UTILITY_STEP_OBJ_DICT: Dict[str, type] = {
    m[0]: m[1] for m in inspect.getmembers(steps_utility, inspect.isclass)}

#: Dictionary of synthesis step name keys and step class values.
SYNTHESIS_STEP_OBJ_DICT: Dict[str, type] = {
    m[0]: m[1] for m in inspect.getmembers(steps_synthesis, inspect.isclass)}

#: Dictionary of all step name keys and step class values.
STEP_OBJ_DICT: Dict[str, type] = copy.copy(BASE_STEP_OBJ_DICT)
STEP_OBJ_DICT.update(UTILITY_STEP_OBJ_DICT)
STEP_OBJ_DICT.update(SYNTHESIS_STEP_OBJ_DICT)

#: List of all step names.
XDL_STEP_NAMESPACE: List[str] = list(STEP_OBJ_DICT.keys())

#: List of all component class names.
XDL_HARDWARE_NAMESPACE: List[str] = [
    CHEMPUTER_REACTOR_CLASS_NAME,
    CHEMPUTER_SEPARATOR_CLASS_NAME,
    CHEMPUTER_FILTER_CLASS_NAME,
    CHEMPUTER_FLASK_CLASS_NAME,
    CHEMPUTER_WASTE_CLASS_NAME,
    CHEMPUTER_VACUUM_CLASS_NAME,
    CHEMPUTER_PUMP_CLASS_NAME,
    CHEMPUTER_VALVE_CLASS_NAME,
] 
