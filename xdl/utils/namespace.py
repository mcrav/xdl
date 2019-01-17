from ..steps import *
from ..hardware.components import *
import copy

BASE_STEP_OBJ_DICT = {
    'CMove': CMove,
    'CSeparate': CSeparatePhases,
    'CPrime': CPrime,
    'CSwitchVacuum': CSwitchVacuum,
    'CSwitchCartridge': CSwitchCartridge,
    'CSwitchColumn': CSwitchColumn,
    'CStartStir': CStartStir,
    'CStartHeat': CStartHeat,
    'CStopStir': CStopStir,
    'CStopHeat': CStopHeat,
    'CSetTemp': CSetTemp,
    'CSetStirRpm': CSetStirRpm,
    'CStirrerWaitForTemp': CStirrerWaitForTemp,
    'CStartHeaterBath': CStartHeaterBath,
    'CStopHeaterBath': CStopHeaterBath,
    'CStartRotation': CStartRotation,
    'CStopRotation': CStopRotation,
    'CLiftArmUp': CLiftArmUp,
    'CLiftArmDown': CLiftArmDown,
    'CResetRotavap': CResetRotavap,
    'CSetBathTemp': CSetBathTemp,
    'CSetRvRotationSpeed': CSetRvRotationSpeed,
    'CRvWaitForTemp': CRvWaitForTemp,
    'CSetInterval': CSetInterval,
    'CInitVacPump': CInitVacPump,
    'CGetVacSp': CGetVacSp,
    'CSetVacSp': CSetVacSp,
    'CStartVac': CStartVac,
    'CStopVac': CStopVac,
    'CVentVac': CVentVac,
    'CSetSpeedSp': CSetSpeedSp,
    'CStartChiller': CStartChiller,
    'CStopChiller': CStopChiller,
    'CSetChiller': CSetChiller,
    'CChillerWaitForTemp': CChillerWaitForTemp,
    'CRampChiller': CRampChiller,
    'CSwitchChiller': CSwitchChiller,
    'CSetCoolingPower': CSetCoolingPower,
    'CSetRecordingSpeed': CSetRecordingSpeed,
    'CWait': CWait,
    'CBreakpoint': CBreakpoint,
}

XDL_STEP_OBJ_DICT = {
    'StartVacuum': StartVacuum,
    'StopVacuum': StopVacuum,
    'StartHeat': StartHeat,
    'StartStir': StartStir,

    'Chill': Chill,
    'Reflux': Reflux,

    'CleanVessel': CleanVessel,
    'CleanBackbone': CleanBackbone,


    'Filter': Filter,
    'WashFilterCake': WashFilterCake,
    'Dry': Dry,

    'Wait': Wait,

    'Separate': Separate,

    'Add': Add,
    'PrimePumpForAdd': PrimePumpForAdd,
    'Transfer': Transfer,
    'MakeSolution': MakeSolution,
    
    'StirAtRT': StirAtRT,
    'PrepareFilter': PrepareFilter,
    'RemoveFilterDeadVolume': RemoveFilterDeadVolume,
    'Confirm': Confirm,
}

STEP_OBJ_DICT = copy.copy(BASE_STEP_OBJ_DICT)
STEP_OBJ_DICT.update(XDL_STEP_OBJ_DICT)

XDL_STEP_NAMESPACE = list(STEP_OBJ_DICT.keys())
XDL_HARDWARE_NAMESPACE = ['Reactor', 'Filter', 'Flask', 'Separator', 'Rotavap'] 
