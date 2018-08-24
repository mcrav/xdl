from chasmwriter import Chasm
from constants import *
from steps_generic import Step, Repeat
from steps_chasm import *

class SetRpmAndStartStir(Step):

    def __init__(self, vessel=None, stir_rpm=DEFAULT_STIR_RPM, comment=''):

        self.name = 'StartStir'
        self.properties = {
            'vessel': vessel,
            'stir_rpm': stir_rpm,
            'comment': comment,
        }

        self.steps = [
            SetStirRpm(name='vessel', rpm='stir_rpm'),
            StartStir(name=vessel),
        ]

        self.human_readable = f'Set stir rate to {stir_rpm} RPM and start stirring {vessel}.'

class StartVacuum(Step):

    def __init__(self, vessel=None, comment=''):

        self.name = 'StartVacuum'
        self.properties = {
            'vessel': vessel,
            'comment': comment,
        }

        self.steps = [
            SwitchVacuum(flask=vessel, destination='vacuum')
        ]

        self.human_readable = f'Start vacuum for {vessel}.'


class StopVacuum(Step):

    def __init__(self, vessel=None, comment=''):

        self.name = 'StopVacuum'
        self.properties = {
            'vessel': vessel,
            'comment': comment,
        }

        self.steps = [
            SwitchVacuum(flask=vessel, destination='backbone')
        ]

        self.human_readable = f'Stop vacuum for {vessel}.'

class SetTempAndStartHeat(Step):

    def __init__(self, vessel=None, temp=None, comment=''):
        
        self.name = 'StartHeat'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'comment': comment,
        }

        self.steps = [
            SetTemp(name=vessel, temp=temp),
            StartHeat(name=vessel),
        ]

        self.human_readable = f'Heat {vessel} to {temp} °C'

class CleanVessel(Step):

    def __init__(self, vessel=None, solvents=None, volumes=None, stir_rpm=DEFAULT_STIR_RPM, stir_time=DEFAULT_CLEAN_STIR_TIME, comment=''):

        self.name = 'CleanVessel'
        self.properties = {
            'vessel': vessel,
            'solvents': solvents,
            'volumes': volumes,
            'stir_rpm': stir_rpm,
            'comment': comment,
        }

        self.steps = []
        for solvent, volume in zip(solvents, volumes):
            self.steps.extend([
                Move(src=f'flask_{solvent}', dest=f"{vessel}", volume=volume),
                SetRpmAndStartStir(vessel=vessel, stir_rpm=stir_rpm),
                Wait(time=60),
                StopStir(name=vessel),
                Move(src=vessel, dest='waste_reactor', volume='all'),
            ])

        self.human_readable = ''
        for solvent, volume in zip(solvents, volumes):
            self.human_readable += f'Clean {vessel} with {solvent}.\n'
        self.human_readable = self.human_readable[:-1]

class CleanTubing(Step):

    def __init__(self, solvent=None, vessel=None, volume=DEFAULT_CLEAN_TUBING_VOLUME, comment=''):

        self.name = 'CleanTubing'
        self.properties = {
            'solvent': solvent,
            'vessel': vessel,
            'volume': volume,
            'comment': comment,
        }

        self.steps = [
            Repeat(2, Move(src=f'flask_{self.properties["solvent"]}', dest=self.properties['vessel'], volume=self.properties['volume']))
        ]

        self.human_readable = f'Clean tubing to {vessel} with {volume} mL of {solvent}.'

class HeatAndReact(Step):
    
    def __init__(self, vessel=None, time=None, temp=None, stir_rpm=DEFAULT_STIR_RPM, comment=''):

        self.name = 'HeatAndReact'
        self.properties = {
            'vessel': vessel,
            'time': time,
            'temp': temp,
            'stir_rpm': stir_rpm,
            'comment': comment,
        }

        self.steps = [
            SetRpmAndStartStir(vessel=vessel, stir_rpm=stir_rpm),
            SetTempAndStartHeat(vessel=vessel, temp=temp),
            Wait(time=time),
            StopHeat(name=vessel),
            ContinueStirToRT(vessel=vessel),
        ]

        self.human_readable = f'Heat {vessel} to {temp} °C under stirring and wait {float(time) / 3600} hrs.\nThen stop heating and continue stirring until {vessel} reaches room temperature.'

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
            SetTemp(name=vessel, temp=ROOM_TEMPERATURE),
            StirrerWaitForTemp(name=vessel),
            StopStir(name=vessel),
        ]

        self.human_readable = f'Wait for {vessel} to reach room temperature and then stop stirring.'

class Chill(Step):

    def __init__(self, vessel=None, temp=None, comment=''):

        self.name = 'Chill'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'comment': comment,
        }

        self.steps = [
            SetChiller(name=vessel, setpoint=temp),
            ChillerWaitForTemp(name=vessel),
            StopChiller(name=vessel),
        ]

        self.human_readable = f'Chill {vessel} to {temp} °C.'

class ChillBackToRT(Step):

    def __init__(self, vessel=None, comment=''):

        self.name = 'ChillBackToRT'
        self.properties = {
            'vessel': vessel,
            'comment': comment,
        }

        self.steps = [
            SetChiller(name=vessel, setpoint=ROOM_TEMPERATURE),
            ChillerWaitForTemp(name=vessel),
            StopChiller(name=vessel),
        ]

    self.human_readable = f'Chill {vessel} to room temperature.'

class Add(Step):

    def __init__(self, reagent=None, volume=None, vessel=None, move_speed=DEFAULT_MOVE_SPEED, clean_tubing=True, comment=''):

        self.name = 'Add'
        self.properties = {
            'reagent': reagent,
            'volume': volume,
            'vessel': vessel,
            'move_speed': move_speed,
            'clean_tubing': clean_tubing,
            'comment': comment,
        }

        self.steps = []
        if clean_tubing:
            self.steps.append(Move(src=f"flask_{reagent}", dest="waste_aqueous", 
                    volume=DEFAULT_PUMP_PRIME_VOLUME, move_speed=move_speed))
        self.steps.append(Move(src=f"flask_{reagent}", dest=vessel, 
                            volume=volume, move_speed=move_speed))
        if clean_tubing:
            self.steps.append(CleanTubing(solvent=DEFAULT_CLEAN_TUBING_SOLVENT, vessel=vessel))

        self.human_readable = f'Add {reagent} ({volume} mL) to {vessel}.' # Maybe add in bit for clean tubing

class StirAndTransfer(Step):

    def __init__(self, from_vessel=None, to_vessel=None, volume=None, stir_rpm=DEFAULT_STIR_RPM, comment=''):

        self.name = 'StirAndTransfer'
        self.properties = {
            'from_vessel': from_vessel,
            'to_vessel': to_vessel,
            'volume': volume,
            'stir_rpm': stir_rpm,
            'comment': comment,
        }

        self.steps = [
            SetRpmAndStartStir(vessel=from_vessel, stir_rpm=stir_rpm),
            Move(src=from_vessel, dest=to_vessel, volume=volume),
            StopStir(name=from_vessel)
        ]

        self.human_readable = f'Stir {from_vessel} and transfer {volume} mL to {to_vessel}.'

class Wash(Step):
    """
    Wash vessel.
    Assumes vessel is being stirred.
    """
    def __init__(self, solvent=None, vessel=None, volume=None, move_speed=DEFAULT_MOVE_SPEED, 
                wait_time=600, comment=''):

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
            StartStir(name=vessel)
            Add(reagent=solvent, volume=volume),
            Wait(time=wait_time),
            Move(src=vessel, dest='waste_solvents', 
                 volume=volume, move_speed=move_speed)
            StopStir(name=vessel)
        ]

        self.human_readable = f'Wash {vessel} with {solvent} ({volume} mL).'

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

        self.steps = [StartStir(name=vessel),]
        for reagent, volume in zip(reagents, volumes):
            self.steps.append(Add(reagent=reagent, volume=volume, vessel=vessel, clean_tubing=False, comment='Add water to filter flask bottom'))
        self.steps.extend([
            Chill(vessel=vessel, temp=temp),
            Wait(time=time),
            ChillBackToRT(vessel=vessel),
            StopStir(name=vessel),
        ])

        self.human_readable = ''
        for reagent, volume in zip(reagents, volumes):
            self.human_readable += f'Add {reagent} ({volume} mL) to {vessel} under stirring.\n'
        self.human_readable += f'Chill {vessel} to {temp} °C and wait {time / 3600} hrs.\n'
        self.human_readable += f'Chill {vessel} to room temperature then stop stirring.'