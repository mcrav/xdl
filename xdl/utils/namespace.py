from ..steps import steps_xdl
from ..steps import steps_chasm
import copy
import inspect
from ..constants import *

BASE_STEP_OBJ_DICT = {m[0]: m[1] 
                      for m in inspect.getmembers(steps_chasm, inspect.isclass)}
XDL_STEP_OBJ_DICT = {m[0]: m[1]
                     for m in inspect.getmembers(steps_xdl, inspect.isclass)}

STEP_OBJ_DICT = copy.copy(BASE_STEP_OBJ_DICT)
STEP_OBJ_DICT.update(XDL_STEP_OBJ_DICT)

XDL_STEP_NAMESPACE = list(STEP_OBJ_DICT.keys())
XDL_HARDWARE_NAMESPACE = [
    CHEMPUTER_REACTOR_CLASS_NAME,
    CHEMPUTER_SEPARATOR_CLASS_NAME,
    CHEMPUTER_FILTER_CLASS_NAME,
    CHEMPUTER_FLASK_CLASS_NAME,
    CHEMPUTER_WASTE_CLASS_NAME,
    CHEMPUTER_VACUUM_CLASS_NAME,
    CHEMPUTER_PUMP_CLASS_NAME,
    CHEMPUTER_VALVE_CLASS_NAME,
] 
