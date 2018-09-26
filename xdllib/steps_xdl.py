from .chasmwriter import Chasm
from .constants import *
from .steps_generic import Step, Repeat, Comment
from .steps_chasm import (
   CMove,
    CSeparate,
    CPrime,
    CSwitchVacuum,
    CSwitchCartridge,
    CSwitchColumn,
    CStartStir,
    CStartHeat,
    CStopStir,
    CStopHeat,
    CSetTemp,
    CSetStirRpm,
    CStirrerWaitForTemp,
    CStartHeaterBath,
    CStopHeaterBath,
    CStartRotation,
    CStopRotation,
    CLiftArmUp,
    CLiftArmDown,
    CResetRotavap,
    CSetBathTemp,
    CSetRvRotationSpeed,
    CRvWaitForTemp,
    CSetInterval,
    CInitVacPump,
    CGetVacSp,
    CSetVacSp,
    CStartVac,
    CStopVac,
    CVentVac,
    CSetSpeedSp,
    CStartChiller,
    CStopChiller,
    CSetChiller,
    CChillerWaitForTemp,
    CRampChiller,
    CSwitchChiller,
    CSetCoolingPower,
    CSetRecordingSpeed,
    CWait,
    CBreakpoint,
)



class StartStir(Step):

    def __init__(self, vessel=None, stir_rpm='default', comment=''):

        self.name = 'StartStir'
        self.properties = {
            'vessel': vessel,
            'stir_rpm': stir_rpm,
            'comment': comment,
        }
        self.steps = [
            CSetStirRpm(vessel=vessel, stir_rpm='stir_rpm'),
            CStartStir(vessel=vessel),
        ]

        self.human_readable = f'Set stir rate to {stir_rpm} RPM and start stirring {vessel}.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

    @property
    def comment(self):
        return self.properties['comment']

class StartHeat(Step):

    def __init__(self, vessel=None, temp=None, comment=''):

        self.name = 'StartHeat'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'comment': comment,
        }

        self.steps = [
            CSetTemp(vessel=vessel, temp=temp),
            CStartHeat(vessel=vessel),
        ]

        self.human_readable = f'Heat {vessel} to {temp} °C'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def temp(self):
        return self.properties['temp']

    @property
    def comment(self):
        return self.properties['comment']

class StartVacuum(Step):

    def __init__(self, vessel=None, comment=''):

        self.name = 'StartVacuum'
        self.properties = {
            'vessel': vessel,
            'comment': comment,
        }

        self.steps = [
            CSwitchVacuum(vessel=vessel, destination='vacuum')
        ]

        self.human_readable = f'Start vacuum for {vessel}.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class StopVacuum(Step):

    def __init__(self, vessel=None, comment=''):

        self.name = 'StopVacuum'
        self.properties = {
            'vessel': vessel,
            'comment': comment,
        }

        self.steps = [
            CSwitchVacuum(vessel=vessel, destination='backbone')
        ]

        self.human_readable = f'Stop vacuum for {vessel}.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class CleanVessel(Step):

    def __init__(self, vessel=None, solvents=None, volumes=None, stir_rpm='default', stir_time='default', comment=''):

        self.name = 'CleanVessel'
        self.properties = {
            'vessel': vessel,
            'solvents': solvents,
            'volumes': volumes,
            'stir_rpm': stir_rpm,
            'comment': comment,
        }

        self.steps = []
        if solvents and volumes:
            for solvent, volume in zip(solvents, volumes):
                self.steps.extend([
                    CMove(from_vessel=f'flask_{solvent}', to_vessel=f"{vessel}", volume=volume),
                    StartStir(vessel=vessel, stir_rpm=stir_rpm),
                    CWait(time=60),
                    CStopStir(vessel=vessel),
                    CMove(from_vessel=vessel, to_vessel='waste_reactor', volume='all'),
                ])

        self.human_readable = ''
        if solvents and volumes:
            for solvent, volume in zip(solvents, volumes):
                self.human_readable += f'Clean {vessel} with {solvent}.\n'
        self.human_readable = self.human_readable[:-1]

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def solvents(self):
        return self.properties['solvents']

    @property
    def volumes(self):
        return self.properties['volumes']

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

    @property
    def comment(self):
        return self.properties['comment']

class CleanTubing(Step):

    def __init__(self, solvent='default', vessel=None, volume='default', comment=''):

        self.name = 'CleanTubing'
        self.properties = {
            'solvent': solvent,
            'vessel': vessel,
            'volume': volume,
            'comment': comment,
        }
        self.get_defaults()

        self.steps = [
            Repeat(2, CMove(from_vessel=f'flask_{self.solvent}', to_vessel=self.vessel,
                   volume=self.volume))
        ]

        self.human_readable = f'Clean tubing to {vessel} with {volume} mL of {solvent}.'

    @property
    def solvent(self):
        return self.properties['solvent']

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def volume(self):
        return self.properties['volume']

    @property
    def comment(self):
        return self.properties['comment']

class HeatAndReact(Step):

    def __init__(self, vessel=None, time=None, temp=None, stir_rpm='default', comment=''):

        self.name = 'HeatAndReact'
        self.properties = {
            'vessel': vessel,
            'time': time,
            'temp': temp,
            'stir_rpm': stir_rpm,
            'comment': comment,
        }

        self.steps = [
            StartStir(vessel=vessel, stir_rpm=stir_rpm),
            StartHeat(vessel=vessel, temp=temp),
            CWait(time=time),
            CStopHeat(vessel=vessel),
            ContinueStirToRT(vessel=vessel),
        ]

        self.human_readable = f'Heat {vessel} to {temp} °C under stirring and wait {float(time) / 3600} hrs.\nThen stop heating and continue stirring until {vessel} reaches room temperature.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def time(self):
        return self.properties['time']

    @property
    def temp(self):
        return self.properties['temp']

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

    @property
    def comment(self):
        return self.properties['comment']

class ContinueStirToRT(Step):
    """
    Assumes stirrer is already on.
    """
    def __init__(self, vessel=None, comment=''):

        self.name = 'StirToRT'
        self.properties = {
            'vessel': vessel,
            'comment': comment,
        }

        self.steps = [
            CSetTemp(vessel=vessel, temp=ROOM_TEMPERATURE),
            CStirrerWaitForTemp(vessel=vessel),
            CStopStir(vessel=vessel),
        ]

        self.human_readable = f'Wait for {vessel} to reach room temperature and then stop stirring.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class Chill(Step):

    def __init__(self, vessel=None, temp=None, comment=''):

        self.name = 'Chill'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'comment': comment,
        }

        self.steps = [
            CSetChiller(vessel=vessel, temp=temp),
            CChillerWaitForTemp(vessel=vessel),
            CStopChiller(vessel=vessel),
        ]

        self.human_readable = f'Chill {vessel} to {temp} °C.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def temp(self):
        return self.properties['temp']

    @property
    def comment(self):
        return self.properties['comment']

class ChillBackToRT(Step):

    def __init__(self, vessel=None, comment=''):

        self.name = 'ChillBackToRT'
        self.properties = {
            'vessel': vessel,
            'comment': comment,
        }

        self.steps = [
            CSetChiller(vessel=vessel, temp=ROOM_TEMPERATURE),
            CChillerWaitForTemp(vessel=vessel),
            CStopChiller(vessel=vessel),
        ]

        self.human_readable = f'Chill {vessel} to room temperature.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class Add(Step):

    def __init__(self, reagent=None, volume=None, vessel=None, time=None, move_speed='default', clean_tubing='default', comment=''):

        self.name = 'Add'
        self.properties = {
            'reagent': reagent,
            'volume': volume,
            'vessel': vessel,
            'time': time,
            'move_speed': move_speed,
            'clean_tubing': clean_tubing,
            'comment': comment,
        }

        self.steps = []
        if clean_tubing:
            self.steps.append(CMove(from_vessel=f"flask_{reagent}", to_vessel="waste_aqueous",
                    volume=DEFAULT_PUMP_PRIME_VOLUME, move_speed=move_speed))
        self.steps.append(CMove(from_vessel=f"flask_{reagent}", to_vessel=vessel,
                            volume=volume, move_speed=move_speed))
        if clean_tubing:
            self.steps.append(CleanTubing(solvent='default', vessel="waste_aqueous"))

        self.human_readable = f'Add {reagent} ({volume} mL) to {vessel}' # Maybe add in bit for clean tubing
        if time:
            self.human_readable += f' over {time}'
        self.human_readable += '.'

    @property
    def reagent(self):
        return self.properties['reagent']

    @property
    def volume(self):
        return self.properties['volume']

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def time(self):
        return self.properties['time']

    @property
    def move_speed(self):
        return self.properties['move_speed']

    @property
    def clean_tubing(self):
        return self.properties['clean_tubing']

    @property
    def comment(self):
        return self.properties['comment']

class StirAndTransfer(Step):

    def __init__(self, from_vessel=None, to_vessel=None, volume=None, stir_rpm='default', comment=''):

        self.name = 'StirAndTransfer'
        self.properties = {
            'from_vessel': from_vessel,
            'to_vessel': to_vessel,
            'volume': volume,
            'stir_rpm': stir_rpm,
            'comment': comment,
        }

        self.steps = [
            StartStir(vessel=from_vessel, stir_rpm=stir_rpm),
            CMove(from_vessel=from_vessel, to_vessel=to_vessel, volume=volume),
            CStopStir(vessel=from_vessel)
        ]

        self.human_readable = f'Stir {from_vessel} and transfer {volume} mL to {to_vessel}.'

    @property
    def from_vessel(self):
        return self.properties['from_vessel']

    @property
    def to_vessel(self):
        return self.properties['to_vessel']

    @property
    def volume(self):
        return self.properties['volume']

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

    @property
    def comment(self):
        return self.properties['comment']

class Wash(Step):
    """
    Wash vessel.
    Assumes vessel is being stirred.
    """
    def __init__(self, solvent=None, vessel=None, volume=None, move_speed='default',
                wait_time='default', comment=''):

        self.name = 'Wash'
        self.properties = {
            'solvent': solvent,
            'vessel': vessel,
            'volume': volume,
            'move_speed': move_speed,
            'wait_time': wait_time,
            'comment': comment,
        }

        self.steps = [
            StartStir(vessel=vessel),
            Add(reagent=solvent, volume=volume),
            CWait(time=wait_time),
            CMove(src=vessel, dest='waste_solvents',
                 volume=volume, move_speed=move_speed),
            CStopStir(vessel=vessel)
        ]

        self.human_readable = f'Wash {vessel} with {solvent} ({volume} mL).'

    @property
    def solvent(self):
        return self.properties['solvent']

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def volume(self):
        return self.properties['volume']

    @property
    def move_speed(self):
        return self.properties['move_speed']

    @property
    def wait_time(self):
        return self.properties['wait_time']

    @property
    def comment(self):
        return self.properties['comment']

class ChillReact(Step):

    def __init__(self, reagents=[], volumes=[], vessel=None, temp=None, time=None, comment=''):

        self.name = 'ChillReact'
        self.properties = {
            'reagents': reagents,
            'volumes': volumes,
            'vessel': vessel,
            'temp': temp,
            'comment': comment,
        }

        self.steps = [StartStir(vessel=vessel),]
        for reagent, volume in zip(reagents, volumes):
            self.steps.append(Add(reagent=reagent, volume=volume, vessel=vessel, clean_tubing=False, comment='Add water to filter flask bottom'))
        self.steps.extend([
            Chill(vessel=vessel, temp=temp),
            CWait(time=time),
            ChillBackToRT(vessel=vessel),
            CStopStir(vessel=vessel),
        ])

        self.human_readable = ''
        for reagent, volume in zip(reagents, volumes):
            self.human_readable += f'Add {reagent} ({volume} mL) to {vessel} under stirring.\n'
        self.human_readable += f'Chill {vessel} to {temp} °C and wait {time / 3600} hrs.\n'
        self.human_readable += f'Chill {vessel} to room temperature then stop stirring.'

    @property
    def reagents(self):
        return self.properties['reagents']

    @property
    def volumes(self):
        return self.properties['volumes']

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def temp(self):
        return self.properties['temp']

    @property
    def comment(self):
        return self.properties['comment']

class Dry(Step):

    def __init__(self, vessel=None, time='default'):

        self.name = 'Dry'
        self.properties = {
            'vessel': vessel,
            'time': time,
        }

        self.steps = [
            StartVacuum(vessel=vessel),
            CWait(time=time),
            StopVacuum(vessel=vessel)
        ]

        self.human_readable = f'Dry substance in {vessel} for {time} s.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def time(self):
        return self.properties['time']

class Filter(Step):

    def __init__(self, from_vessel=None, vessel=None, time='default'):

        self.name = 'Filter'
        self.properties = {
            'from_vessel': from_vessel,
            'vessel': vessel,
            'time': time,
        }

        self.steps = [
            StartVacuum(vessel),
        ]
        if from_vessel != vessel:
            self.steps.append(StirAndTransfer(from_vessel=from_vessel, to_vessel=vessel))
        self.steps.append(CWait(time))
        self.steps.append(StopVacuum(vessel))

        self.human_readable = f'Filter contents of {from_vessel} in {vessel} for {time} s.'

    @property
    def from_vessel(self):
        return self.properties['from_vessel']

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def time(self):
        return self.properties['time']

class MakeSolution(Step):

    def __init__(self, solute=None, solvent=None, solute_mass=None, solvent_volume=None, vessel=None, comment=''):

        self.name = 'MakeSolution'
        self.properties = {
            'solute': solute,
            'solvent': solvent,
            'solute_mass': solute_mass,
            'solvent_volume': solvent_volume,
            'vessel': vessel,
            'comment': comment,
        }

        self.steps = []
        if not isinstance(solute, list):
            solute = [solute]
        if not isinstance(solute_mass, list):
            solute_mass = [solute_mass]
        # for s, m in zip(solute, solute_mass):
        #     self.steps.append(AddSolid(reagent=s, mass=m, vessel=vessel)),
        # self.steps.append(Add(reagent=solvent, volume=solvent_volume, vessel=vessel))
        self.steps.append(Comment('WARNING: SOLID HANDLING UNIMPLENTED. MAKE SOLUTION MANUALLY.'))

        self.human_readable = f'Make solution of '
        for s, m in zip(solute, solute_mass):
            self.human_readable += f'{s} ({m}), '
        self.human_readable = self.human_readable[:-2] + f' in {solvent} ({solvent_volume} mL).'

    @property
    def solute(self):
        return self.properties['solute']

    @property
    def solvent(self):
        return self.properties['solvent']

    @property
    def solute_mass(self):
        return self.properties['solute_mass']

    @property
    def solvent_volume(self):
        return self.properties['solvent_volume']

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class AddSolid(Step):
    """UNIMPLEMENTED"""
    def __init__(self, reagent=None, mass=None, vessel=None, comment=''):

        self.name = 'AddSolid'
        self.properties = {
            'reagent': reagent,
            'mass': mass,
            'vessel': vessel,
            'comment': comment,
        }

        self.steps = []

        self.human_readable = f'UNIMPLEMENTED: Add {reagent} ({mass} g) to {vessel}.'

    @property
    def reagent(self):
        return self.properties['reagent']

    @property
    def mass(self):
        return self.properties['mass']

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class Reflux(Step):

    def __init__(self, vessel=None, temp=None, time=None, comment=''):

        self.name = 'Reflux'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'time': time,
            'comment': comment,
        }

        self.steps = [
            StartStir(vessel=vessel),
            StartHeat(vessel=vessel, temp=temp),
            CWait(time=time),
            CStopHeat(vessel=vessel),
            CStopStir(vessel=vessel),
        ]

        self.human_readable = f'Heat {vessel} to {temp} °C and reflux for {time}'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def temp(self):
        return self.properties['temp']

    @property
    def time(self):
        return self.properties['time']

    @property
    def comment(self):
        return self.properties['comment']

class Rotavap(Step):

    def __init__(self, vessel=None, temp=None, pressure=None, time=None):

        self.name = 'Rotavap'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'pressure': pressure,
            'time': time,
        }

        # Steps incomplete
        self.steps = [
            SwitchCartridge('rotavap', 0),
            LiftArmDown('rotavap'),
            SetRotation('rotavap', 'default'),
            StartRotation('rotavap'),
            SetVacSp('rotavap', 'default'),
            StartVacuum('rotavap'),
            SetBathTemp('rotavap', temp),
            StartHeaterBath('rotavap'),
            Wait(300),
            SetVacSp('rotavap', 'default'),
            Wait(time),
            StopVacuum('rotavap'),
            VentVac('rotavap'),
            Move('flask_rv_bottom', 'waste_rotary', )
        ]

        self.human_readable = f'Rotavap contents of {vessel} at {temp} °C for {time}.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def temp(self):
        return self.properties['temp']

    @property
    def pressure(self):
        return self.properties['pressure']

    @property
    def time(self):
        return self.properties['time']

class Extract(Step):

    def __init__(self, from_vessel=None, separation_vessel=None, solvent=None, solvent_volume=None, n_separations=1):

        self.name = 'Extract'
        self.properties = {
            'from_vessel': from_vessel,
            'solvent': solvent,
            'solvent_volume': solvent_volume,
            'n_separations': n_separations,
        }

        self.steps = [
            Move(from_vessel=from_vessel, to_vessel=separation_vessel, ),
        ]

        self.human_readable = f'Extract contents of {from_vessel} with {n_separations}x{solvent_volume}'
    @property
    def from_vessel(self):
        return self.properties['from_vessel']

    @property
    def solvent(self):
        return self.properties['solvent']

    @property
    def solvent_volume(self):
        return self.properties['solvent_volume']

    @property
    def n_separations(self):
        return self.properties['n_separations']
