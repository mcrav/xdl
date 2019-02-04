from ..steps import steps_xdl
from ..steps import steps_chasm
import copy
import inspect

BASE_STEP_OBJ_DICT = {m[0]: m[1] 
                      for m in inspect.getmembers(steps_chasm, inspect.isclass)}
XDL_STEP_OBJ_DICT = {m[0]: m[1]
                     for m in inspect.getmembers(steps_xdl, inspect.isclass)}

STEP_OBJ_DICT = copy.copy(BASE_STEP_OBJ_DICT)
STEP_OBJ_DICT.update(XDL_STEP_OBJ_DICT)

XDL_STEP_NAMESPACE = list(STEP_OBJ_DICT.keys())
XDL_HARDWARE_NAMESPACE = ['Reactor', 'Filter', 'Flask', 'Separator', 'Rotavap'] 
