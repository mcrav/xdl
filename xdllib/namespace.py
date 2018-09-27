from .steps import *
from .components import *
import copy

BASE_STEP_OBJ_DICT = {
    'Move': CMove,
    'Separate': CSeparate,
    'Prime': CPrime,
    'SwitchVacuum': CSwitchVacuum,
    'SwitchCartridge': CSwitchCartridge,
    'SwitchColumn': CSwitchColumn,
    'StartStir': StartStir,
    'StartHeat': StartHeat,
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
    'StopChiller': CStopChiller,
    'SetChiller': CSetChiller,
    'ChillerWaitForTemp': CChillerWaitForTemp,
    'RampChiller': CRampChiller,
    'SwitchChiller': CSwitchChiller,
    'SetCoolingPower': CSetCoolingPower,
    'SetRecordingSpeed': CSetRecordingSpeed,
    'Wait': CWait,
    'Breakpoint': CBreakpoint,
}

XDL_STEP_OBJ_DICT = {
    'StartVacuum': StartVacuum,
    'StopVacuum': StopVacuum,
    'StartHeat': StartHeat,
    'CleanVessel': CleanVessel,
    'CleanTubing': CleanTubing,
    'HeatAndReact': HeatAndReact,
    'ContinueStirToRT': ContinueStirToRT,
    'Chill': Chill,
    'ChillBackToRT': ChillBackToRT,
    'Add': Add,
    'StirAndTransfer': StirAndTransfer,
    'Wash': WashFilterCake,
    'ChillReact': ChillReact,
    'MakeSolution': MakeSolution,
    'Reflux': Reflux,
    'PrimePumpForAdd': PrimePumpForAdd,
}

STEP_OBJ_DICT = copy.copy(BASE_STEP_OBJ_DICT)
STEP_OBJ_DICT.update(XDL_STEP_OBJ_DICT)

COMPONENT_OBJ_DICT = {
    'Reactor': Reactor,
    'FilterFlask': FilterFlask,
    'Flask': Flask,
    'Waste': Waste,
}

XDL_STEP_NAMESPACE = list(STEP_OBJ_DICT.keys())
XDL_HARDWARE_NAMESPACE = list(COMPONENT_OBJ_DICT.keys())
