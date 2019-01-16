from ..steps import *
from ..hardware.components import *
import copy

BASE_STEP_OBJ_DICT = {
    'Move': CMove,
    'Separate': CSeparate,
    'Prime': CPrime,
    'SwitchVacuum': CSwitchVacuum,
    'SwitchCartridge': CSwitchCartridge,
    'SwitchColumn': CSwitchColumn,
    'StartStir': CStartStir,
    'StartHeat': CStartHeat,
    'StopStir': CStopStir,
    'StopHeat': CStopHeat,
    'SetTemp': CSetTemp,
    'SetStirRpm': CSetStirRpm,
    'StirrerWaitForTemp': CStirrerWaitForTemp,
    'StartHeaterBath': CStartHeaterBath,
    'StopHeaterBath': CStopHeaterBath,
    'StartRotation': CStartRotation,
    'StopRotation': CStopRotation,
    'LiftArmUp': CLiftArmUp,
    'LiftArmDown': CLiftArmDown,
    'ResetRotavap': CResetRotavap,
    'SetBathTemp': CSetBathTemp,
    'SetRvRotationSpeed': CSetRvRotationSpeed,
    'RvWaitForTemp': CRvWaitForTemp,
    'SetInterval': CSetInterval,
    'InitVacPump': CInitVacPump,
    'GetVacSp': CGetVacSp,
    'SetVacSp': CSetVacSp,
    'StartVac': CStartVac,
    'StopVac': CStopVac,
    'VentVac': CVentVac,
    'SetSpeedSp': CSetSpeedSp,
    'StartChiller': CStartChiller,
    'CStopChiller': CStopChiller,
    'SetChiller': CSetChiller,
    'ChillerWaitForTemp': CChillerWaitForTemp,
    'RampChiller': CRampChiller,
    'SwitchChiller': CSwitchChiller,
    'SetCoolingPower': CSetCoolingPower,
    'SetRecordingSpeed': CSetRecordingSpeed,
    'CWait': CWait,
    'Breakpoint': CBreakpoint,
    'Confirm': Confirm,
}

XDL_STEP_OBJ_DICT = {
    'StartVacuum': StartVacuum,
    'StopVacuum': StopVacuum,
    'StartHeat': StartHeat,
    'StopChiller': StopChiller,
    'CleanVessel': CleanVessel,
    'ContinueStirToRT': ContinueStirToRT,
    'Chill': Chill,
    'ChillBackToRT': ChillBackToRT,
    'Add': Add,
    'Filter': Filter,
    'Dry': Dry,
    'Wait': Wait,
    'Extract': Extract,
    'WashFilterCake': WashFilterCake,
    'Transfer': Transfer,
    'Wash': WashSolution,
    'MakeSolution': MakeSolution,
    'Reflux': Reflux,
    'PrimePumpForAdd': PrimePumpForAdd,
    'PrepareFilter': PrepareFilter,
    'RemoveFilterDeadVolume': RemoveFilterDeadVolume,
}

STEP_OBJ_DICT = copy.copy(BASE_STEP_OBJ_DICT)
STEP_OBJ_DICT.update(XDL_STEP_OBJ_DICT)

XDL_STEP_NAMESPACE = list(STEP_OBJ_DICT.keys())
XDL_HARDWARE_NAMESPACE = ['Reactor', 'Filter', 'Flask', 'Separator', 'Rotavap'] 
