from .steps_xdl import *
from .steps_chasm import *
from .steps_generic import *
from .components import *

STEP_OBJ_DICT = {
    'Step': Step,
    'Comment': Comment,
    'Repeat': Repeat,
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
    'SetRotation': CSetRvRotationSpeed,
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
    'StartVacuum': StartVacuum,
    'StopVacuum': StopVacuum,
    'SetTempAndStartHeat': StartHeat,
    'CleanVessel': CleanVessel,
    'CleanTubing': CleanTubing,
    'HeatAndReact': HeatAndReact,
    'ContinueStirToRT': ContinueStirToRT,
    'Chill': Chill,
    'ChillBackToRT': ChillBackToRT,
    'Add': Add,
    'StirAndTransfer': StirAndTransfer,
    'Wash': Wash,
    'ChillReact': ChillReact,
    'MakeSolution': MakeSolution,
    'AddSolid': AddSolid,
    'Reflux': Reflux,
}

COMPONENT_OBJ_DICT = {
    'Reactor': Reactor,
    'FilterFlask': FilterFlask,
    'Flask': Flask,
    'Waste': Waste,
}
