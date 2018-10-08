from ..constants import *
from ..utils import Step
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
    """Start stirring given vessel.

    Keyword Arguments:
        vessel {str} -- Vessel name to stir.
        stir_rpm {int} -- Speed in RPM to stir at. (optional)
    """
    def __init__(self, vessel=None, stir_rpm='default'):

        self.name = 'StartStir'
        self.properties = {
            'vessel': vessel,
            'stir_rpm': stir_rpm,
        }
        self.steps = [
            CSetStirRpm(vessel=vessel, stir_rpm=stir_rpm),
            CStartStir(vessel=vessel),
        ]

        self.human_readable = f'Set stir rate to {stir_rpm} RPM and start stirring {vessel}.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

    @stir_rpm.setter
    def stir_rpm(self, val):
        self.properties['stir_rpm'] = val
        self.update()

class StartHeat(Step):
    """Start heating given vessel at given temperature.

    Keyword Arguments:
        vessel {str} -- Vessel name to heat.
        temp {float} -- Temperature to heat to in °C.
    """
    def __init__(self, vessel=None, temp=None):

        self.name = 'StartHeat'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
        }

        self.steps = [
            CSetTemp(vessel=vessel, temp=temp),
            CStartHeat(vessel=vessel),
        ]

        self.human_readable = f'Heat {vessel} to {temp} °C'

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def temp(self):
        return self.properties['temp']

    @temp.setter
    def temp(self, val):
        self.properties['temp'] = val
        self.update()

class StartVacuum(Step):
    """Start vacuum pump attached to given vessel.

    Keyword Arguments:
        vessel {str} -- Vessel name to start vacuum on.
    """
    def __init__(self, vessel=None):

        self.name = 'StartVacuum'
        self.properties = {
            'vessel': vessel,
        }

        self.steps = [
            CSwitchVacuum(vessel=vessel, destination='vacuum')
        ]

        self.human_readable = f'Start vacuum for {vessel}.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class StopVacuum(Step):
    """Stop vacuum pump attached to given vessel.

    Keyword Arguments:
        vessel {str} -- Vessel name to stop vacuum on.
    """
    def __init__(self, vessel=None):

        self.name = 'StopVacuum'
        self.properties = {
            'vessel': vessel,
        }

        self.steps = [
            CSwitchVacuum(vessel=vessel, destination='backbone')
        ]

        self.human_readable = f'Stop vacuum for {vessel}.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class CleanVessel(Step):
    """Clean given vessel.

    Keyword Arguments:
        vessel {str} -- Vessel to clean.
        solvent {str} -- Solvent to clean with. (optional)
        volume {str} -- Volume of solvent to clean with in mL. (optional)
        stir_rpm {str} -- RPM to stir vessel at during cleaning. (optional)
        stir_time {str} -- Time to stir once solvent has been added. (optional)
    """
    def __init__(self, vessel=None, solvent='default', volume='default', stir_rpm='default',
                    stir_time='default', waste_vessel=None):

        self.name = 'CleanVessel'
        self.properties = {
            'vessel': vessel,
            'solvent': solvent,
            'volume': volume,
            'stir_rpm': stir_rpm,
            'waste_vessel': waste_vessel,
        }
        self.get_defaults()

        self.steps = [
            CMove(from_vessel=f'flask_{solvent}', to_vessel=f"{vessel}", volume=self.volume),
            StartStir(vessel=vessel, stir_rpm=self.stir_rpm),
            CWait(time=60),
            CStopStir(vessel=vessel),
            CMove(from_vessel=vessel, to_vessel=waste_vessel, volume='all'),
        ]

        self.human_readable = f'Clean {vessel} with {solvent} ({volume}).\n'

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def solvent(self):
        return self.properties['solvent']

    @solvent.setter
    def solvent(self, val):
        self.properties['solvent'] = val
        self.update()

    @property
    def volume(self):
        return self.properties['volume']

    @volume.setter
    def volume(self, val):
        self.properties['volume'] = val
        self.update()

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

    @stir_rpm.setter
    def stir_rpm(self, val):
        self.properties['stir_rpm'] = val
        self.update()

    @property
    def waste_vessel(self):
        return self.properties['waste_vessel']

    @waste_vessel.setter
    def waste_vessel(self, val):
        self.properties['waste_vessel'] = val
        self.update()

class CleanTubing(Step):
    """Clean tubing with given reagent.

    Keyword Arguments:
        reagent {str} -- Reagent to clean tubing with.
        volume {float} -- Volume to clean tubing with in mL. (optional)
    """
    def __init__(self, reagent=None, volume='default', waste_vessel=None):

        self.name = 'CleanTubing'
        self.properties = {
            'reagent': reagent,
            'volume': volume,
            'waste_vessel': waste_vessel,
        }
        self.get_defaults()

        self.steps = [
            CMove(from_vessel=f'flask_{reagent}', to_vessel=waste_vessel,
                   volume=self.volume)
        ]
        self.steps.append(self.steps[0])

        self.human_readable = f'Clean tubing with {volume} mL of {reagent}.'

    @property
    def reagent(self):
        return self.properties['reagent']

    @reagent.setter
    def reagent(self, val):
        self.properties['reagent'] = val
        self.update()

    @property
    def volume(self):
        return self.properties['volume']

    @volume.setter
    def volume(self, val):
        self.properties['volume'] = val
        self.update()

    @property
    def waste_vessel(self):
        return self.properties['waste_vessel']

    @waste_vessel.setter
    def waste_vessel(self, val):
        self.properties['waste_vessel'] = val
        self.update()

class HeatAndReact(Step):
    """Under stirring, heat given vessel to given temp and wait for given time
     then stop heat and stirring.

    Keyword Arguments:
        vessel {str} -- Vessel to heat.
        time {float} -- Time to leave vessel under heating/stirring in seconds.
        temp {float} -- Temperature to heat to in °C.
        stir_rpm {int} -- RPM to stir at. (optional)
    """
    def __init__(self, vessel=None, time=None, temp=None, stir_rpm='default'):

        self.name = 'HeatAndReact'
        self.properties = {
            'vessel': vessel,
            'time': time,
            'temp': temp,
            'stir_rpm': stir_rpm,
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

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def time(self):
        return self.properties['time']

    @time.setter
    def time(self, val):
        self.properties['time'] = val
        self.update()

    @property
    def temp(self):
        return self.properties['temp']

    @temp.setter
    def temp(self, val):
        self.properties['temp'] = val
        self.update()

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

    @stir_rpm.setter
    def stir_rpm(self, val):
        self.properties['stir_rpm'] = val
        self.update()

class ContinueStirToRT(Step):
    """Set vessel temperature to room temperature, and continue stirring until
    this temperature is reached, then stop stirring. Assumes stirrer is already on.

    Keyword Arguments:
        vessel {str} -- Vessel to continue stirring until room temperature is reached.
    """
    def __init__(self, vessel=None):

        self.name = 'StirToRT'
        self.properties = {
            'vessel': vessel,
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

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class Chill(Step):
    """Chill vessel to given temperature.

    Keyword Arguments:
        vessel {str} -- Vessel name to chill.
        temp {float} -- Temperature in °C to chill to.
    """
    def __init__(self, vessel=None, temp=None):

        self.name = 'Chill'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
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

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def temp(self):
        return self.properties['temp']

    @temp.setter
    def temp(self, val):
        self.properties['temp'] = val
        self.update()

class ChillBackToRT(Step):
    """Chill given vessel back to room temperature.

    Keyword Arguments:
        vessel {str} -- Vessel name to chill.
    """
    def __init__(self, vessel=None):

        self.name = 'ChillBackToRT'
        self.properties = {
            'vessel': vessel,
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

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class PrimePumpForAdd(Step):
    """Prime pump attached to given reagent flask in anticipation of Add step.

    Keyword Arguments:
        reagent {str} -- Reagent to prime pump for addition.
        move_speed {str} -- Speed to move reagent at. (optional)
    """
    def __init__(self, reagent=None, move_speed='default', waste_vessel=None):

        self.name = 'PrimePumpForAdd'
        self.properties = {
            'reagent': reagent,
            'move_speed': move_speed,
            'waste_vessel': waste_vessel,
        }

        self.steps = [
            CMove(from_vessel=f"flask_{reagent}", to_vessel=waste_vessel,
                    volume=DEFAULT_PUMP_PRIME_VOLUME, move_speed=move_speed)
        ]

    @property
    def reagent(self):
        return self.properties['reagent']

    @reagent.setter
    def reagent(self, val):
        self.properties['reagent'] = val
        self.update()

    @property
    def move_speed(self):
        return self.properties['move_speed']

    @move_speed.setter
    def move_speed(self, val):
        self.properties['move_speed'] = val
        self.update()

    @property
    def waste_vessel(self):
        return self.properties['waste_vessel']

    @waste_vessel.setter
    def waste_vessel(self, val):
        self.properties['waste_vessel'] = val
        self.update()

class Add(Step):
    """Add given volume of given reagent to given vessel.

    Keyword Arguments:
        reagent {str} -- Reagent to add.
        volume {float} -- Volume of reagent to add.
        vessel {str} -- Vessel name to add reagent to.
        time {float} -- Time to spend doing addition in seconds. (optional)
        move_speed {float} -- Speed in mL / min to move liquid at. (optional)
        clean_tubing {bool} -- Clean tubing before and after addition. (optional)
    """
    def __init__(self, reagent=None, volume=None, vessel=None, time=None, move_speed='default', clean_tubing='default'):

        self.name = 'Add'
        self.properties = {
            'reagent': reagent,
            'volume': volume,
            'vessel': vessel,
            'time': time,
            'move_speed': move_speed,
            'clean_tubing': clean_tubing,
        }
        self.get_defaults()

        self.steps = []
        if clean_tubing:
            self.steps.append(PrimePumpForAdd(reagent=reagent))

        self.steps.append(CMove(from_vessel=f"flask_{reagent}", to_vessel=vessel,
                            volume=volume, move_speed=move_speed))
        if clean_tubing:
            self.steps.append(CleanTubing(reagent='default'))

        self.steps.append(CWait(time=DEFAULT_AFTER_ADD_WAIT_TIME))

        self.human_readable = f'Add {reagent} ({volume} mL) to {vessel}' # Maybe add in bit for clean tubing
        if time:
            self.human_readable += f' over {time}'
        self.human_readable += '.'

    @property
    def reagent(self):
        return self.properties['reagent']

    @reagent.setter
    def reagent(self, val):
        self.properties['reagent'] = val
        self.update()

    @property
    def volume(self):
        return self.properties['volume']

    @volume.setter
    def volume(self, val):
        self.properties['volume'] = val
        self.update()

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def time(self):
        return self.properties['time']

    @time.setter
    def time(self, val):
        self.properties['time'] = val
        self.update()

    @property
    def move_speed(self):
        return self.properties['move_speed']

    @move_speed.setter
    def move_speed(self, val):
        self.properties['move_speed'] = val
        self.update()

    @property
    def clean_tubing(self):
        return self.properties['clean_tubing']

    @clean_tubing.setter
    def clean_tubing(self, val):
        self.properties['clean_tubing'] = val
        self.update()

class StirAndTransfer(Step):
    """Stir vessel while transfering contents to another vessel.

    Keyword Arguments:
        from_vessel {str} -- Vessel name to transfer from.
        to_vessel {str} -- Vessel name to transfer to.
        volume {float} -- Volume to transfer in mL.
        stir_rpm {str} -- Speed to stir from_vessel at in RPM.
    """
    def __init__(self, from_vessel=None, to_vessel=None, volume=None, stir_rpm='default'):

        self.name = 'StirAndTransfer'
        self.properties = {
            'from_vessel': from_vessel,
            'to_vessel': to_vessel,
            'volume': volume,
            'stir_rpm': stir_rpm,
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

    @from_vessel.setter
    def from_vessel(self, val):
        self.properties['from_vessel'] = val
        self.update()

    @property
    def to_vessel(self):
        return self.properties['to_vessel']

    @to_vessel.setter
    def to_vessel(self, val):
        self.properties['to_vessel'] = val
        self.update()

    @property
    def volume(self):
        return self.properties['volume']

    @volume.setter
    def volume(self, val):
        self.properties['volume'] = val
        self.update()

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

    @stir_rpm.setter
    def stir_rpm(self, val):
        self.properties['stir_rpm'] = val
        self.update()

class WashFilterCake(Step):
    """Wash filter cake with given volume of given solvent.

    Keyword Arguments:
        filter_vessel {str} -- Filter vessel name to wash.
        solvent {str} -- Solvent to wash with.
        volume {float} -- Volume of solvent to wash with. (optional)
        move_speed {str} -- Speed to move solvent in mL / min. (optional)
        wait_time {str} -- Time to wait after moving solvent to filter flask. (optional)
    """
    def __init__(self, filter_vessel=None, solvent=None, volume='default', move_speed='default',
                wait_time='default', waste_vessel=None):

        self.name = 'WashFilterCake'
        self.properties = {
            'solvent': solvent,
            'filter_vessel': filter_vessel,
            'volume': volume,
            'move_speed': move_speed,
            'wait_time': wait_time,
            'waste_vessel': waste_vessel,
        }
        self.get_defaults()

        self.steps = [
            StartStir(vessel=self.filter_vessel),
            Add(reagent=self.solvent, volume=self.volume, vessel=self.filter_vessel + '_top'),
            CWait(time=self.wait_time),
            CMove(from_vessel=self.filter_vessel + '_bottom', to_vessel=self.waste_vessel,
                 volume=self.volume, move_speed=self.move_speed),
            CStopStir(vessel=self.filter_vessel)
        ]

        self.human_readable = f'Wash {filter_vessel} with {solvent} ({volume} mL).'


    @property
    def solvent(self):
        return self.properties['solvent']

    @solvent.setter
    def solvent(self, val):
        self.properties['solvent'] = val
        self.update()

    @property
    def filter_vessel(self):
        return self.properties['filter_vessel']

    @filter_vessel.setter
    def filter_vessel(self, val):
        self.properties['filter_vessel'] = val
        self.update()

    @property
    def volume(self):
        return self.properties['volume']

    @volume.setter
    def volume(self, val):
        self.properties['volume'] = val
        self.update()

    @property
    def move_speed(self):
        return self.properties['move_speed']

    @move_speed.setter
    def move_speed(self, val):
        self.properties['move_speed'] = val
        self.update()

    @property
    def wait_time(self):
        return self.properties['wait_time']

    @wait_time.setter
    def wait_time(self, val):
        self.properties['wait_time'] = val
        self.update()

    @property
    def waste_vessel(self):
        return self.properties['waste_vessel']

    @waste_vessel.setter
    def waste_vessel(self, val):
        self.properties['waste_vessel'] = val
        self.update()

class ChillReact(Step):
    """Add given volumes of given reagents to given vessel, chill to given temperature,
    and leave to react for given time.

    Keyword Arguments:
        reagents {list} -- List of reagents to add to vessel.
        volumes {list} -- List of volumes corresponding to list of reagents.
        vessel {str} -- Vessel name to add reagents to and chill.
        temp {float} -- Temperature to chill vessel to in °C.
        time {int} -- Time to leave reagents for in seconds.
    """
    def __init__(self, reagents=[], volumes=[], vessel=None, temp=None, time=None):

        self.name = 'ChillReact'
        self.properties = {
            'reagents': reagents,
            'volumes': volumes,
            'vessel': vessel,
            'temp': temp,
        }

        self.steps = [StartStir(vessel=vessel),]
        for reagent, volume in zip(reagents, volumes):
            self.steps.append(Add(reagent=reagent, volume=volume, vessel=vessel, clean_tubing=False,))
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

    @reagents.setter
    def reagents(self, val):
        self.properties['reagents'] = val
        self.update()

    @property
    def volumes(self):
        return self.properties['volumes']

    @volumes.setter
    def volumes(self, val):
        self.properties['volumes'] = val
        self.update()

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def temp(self):
        return self.properties['temp']

    @temp.setter
    def temp(self, val):
        self.properties['temp'] = val
        self.update()

class Dry(Step):
    """Dry given vessel by applying vacuum for given time.

    Keyword Arguments:
        vessel {str} -- Vessel name to dry.
        time {str} -- Time to dry vessel for in seconds. (optional)
    """
    def __init__(self, vessel=None, time='default'):

        self.name = 'Dry'
        self.properties = {
            'vessel': vessel,
            'time': time,
        }
        self.get_defaults()

        self.steps = [
            StartVacuum(vessel=vessel),
            CWait(time=time),
            StopVacuum(vessel=vessel)
        ]

        self.human_readable = f'Dry substance in {vessel} for {time} s.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def time(self):
        return self.properties['time']

    @time.setter
    def time(self, val):
        self.properties['time'] = val
        self.update()

class Filter(Step):
    """Filter contents of from_vessel in filter_vessel. Apply vacuum for given time.

    Keyword Arguments:
        from_vessel {str} -- Vessel to filter contents of.
        filter_vessel {str} -- Filter vessel.
        time {str} -- Time to leave vacuum on filter vessel after contents have been moved. (optional)
    """
    def __init__(self, from_vessel=None, filter_vessel=None, time='default'):

        self.name = 'Filter'
        self.properties = {
            'from_vessel': from_vessel,
            'filter_vessel': filter_vessel,
            'time': time,
        }
        self.get_defaults()
        self.steps = [
            StartVacuum(filter_vessel),
            StirAndTransfer(from_vessel=from_vessel, to_vessel=filter_vessel),
            CWait(time),
            StopVacuum(filter_vessel),
        ]

        self.human_readable = f'Filter contents of {from_vessel} in {filter_vessel} for {time} s.'

    @property
    def from_vessel(self):
        return self.properties['from_vessel']

    @from_vessel.setter
    def from_vessel(self, val):
        self.properties['from_vessel'] = val
        self.update()

    @property
    def filter_vessel(self):
        return self.properties['filter_vessel']

    @filter_vessel.setter
    def filter_vessel(self, val):
        self.properties['filter_vessel'] = val
        self.update()

    @property
    def time(self):
        return self.properties['time']

    @time.setter
    def time(self, val):
        self.properties['time'] = val
        self.update()

class Confirm(Step):

    def __init__(self, msg=None):

        self.name = 'Confirm'
        self.properties = {
            'msg': msg,
        }

    def execute(self, chempiler):
        keep_going = input(self.msg)
        if not keep_going or keep_going.lower() in ['y', 'yes']:
            return True
        return False

    @property
    def msg(self):
        return self.properties['msg']

    @msg.setter
    def msg(self, val):
        self.properties['msg'] = val
        self.update()

class MakeSolution(Step):
    """Make solution in given vessel of given solutes in given solvent.

    Keyword Arguments:
        solute {str or list} -- Solute(s).
        solvent {str} -- Solvent.
        solute_mass {str or list} -- Mass(es) corresponding to solute(s)
        solvent_volume {[type]} -- Volume of solvent to use in mL.
        vessel {[type]} -- Vessel name to make solution in.
    """
    def __init__(self, solutes=None, solvent=None, solute_masses=None, solvent_volume=None, vessel=None):

        self.name = 'MakeSolution'
        self.properties = {
            'solutes': solutes,
            'solvent': solvent,
            'solute_masses': solute_masses,
            'solvent_volume': solvent_volume,
            'vessel': vessel,
        }

        self.steps = []
        if not isinstance(solutes, list):
            solutes = [solutes]
        if not isinstance(solute_masses, list):
            solute_masses = [solute_masses]
        check_str = f'Are the following reagents in {vessel}? (y)/n\n\n'
        for solute, mass in zip(solutes, solute_masses):
            check_str += f'{solute} ({mass} g)\n'
        self.steps.append(Confirm(msg=check_str))
        self.steps.append(Add(reagent=solvent, volume=solvent_volume, vessel=vessel))

        self.human_readable = f'Make solution of '
        for s, m in zip(solutes, solute_masses):
            self.human_readable += f'{s} ({m} g), '
        self.human_readable = self.human_readable[:-2] + f' in {solvent} ({solvent_volume} mL) in {vessel}.'

    @property
    def solutes(self):
        return self.properties['solutes']

    @solutes.setter
    def solutes(self, val):
        self.properties['solutes'] = val
        self.update()

    @property
    def solvent(self):
        return self.properties['solvent']

    @solvent.setter
    def solvent(self, val):
        self.properties['solvent'] = val
        self.update()

    @property
    def solute_masses(self):
        return self.properties['solute_masses']

    @solute_masses.setter
    def solute_masses(self, val):
        self.properties['solute_masses'] = val
        self.update()

    @property
    def solvent_volume(self):
        return self.properties['solvent_volume']

    @solvent_volume.setter
    def solvent_volume(self, val):
        self.properties['solvent_volume'] = val
        self.update()

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class Reflux(Step):
    """Reflux given vessel at given temperature for given time.

    Keyword Arguments:
        vessel {str} -- Vessel to heat to reflux.
        temp {float} -- Temperature to heat vessel to in °C.
        time {int} -- Time to reflux vessel for in seconds.
    """
    def __init__(self, vessel=None, temp=None, time=None):

        self.name = 'Reflux'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'time': time,
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

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def temp(self):
        return self.properties['temp']

    @temp.setter
    def temp(self, val):
        self.properties['temp'] = val
        self.update()

    @property
    def time(self):
        return self.properties['time']

    @time.setter
    def time(self, val):
        self.properties['time'] = val
        self.update()

class Rotavap(Step):
    """Rotavap contents of given vessel at given temp and given pressure for given time.

    Keyword Arguments:
        vessel {str} -- Vessel with contents to be rotavapped.
        temp {float} -- Temperature to set rotary evaporator water bath to in °C.
        pressure {float} -- Pressure to set rotary evaporator vacuum to in mbar.
        time {int} -- Time to rotavap for in seconds.
    """
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
            CSwitchCartridge('rotavap', 0),
            CLiftArmDown('rotavap'),
            CSetRvRotationSpeed('rotavap', 'default'),
            CStartRotation('rotavap'),
            CSetVacSp('rotavap', 'default'),
            StartVacuum('rotavap'),
            CSetBathTemp('rotavap', temp),
            CStartHeaterBath('rotavap'),
            CWait(300),
            CSetVacSp('rotavap', 'default'),
            CWait(time),
            StopVacuum('rotavap'),
            CVentVac('rotavap'),
            CMove('flask_rv_bottom', 'waste', )
        ]

        self.human_readable = f'Rotavap contents of {vessel} at {temp} °C for {time}.'

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def temp(self):
        return self.properties['temp']

    @temp.setter
    def temp(self, val):
        self.properties['temp'] = val
        self.update()

    @property
    def pressure(self):
        return self.properties['pressure']

    @pressure.setter
    def pressure(self, val):
        self.properties['pressure'] = val
        self.update()

    @property
    def time(self):
        return self.properties['time']

    @time.setter
    def time(self, val):
        self.properties['time'] = val
        self.update()

class Extract(Step):
    """Extract contents of from_vessel using given amount of given solvent.

    Keyword Arguments:
        from_vessel {str} -- Vessel name with contents to be extracted.
        separation_vessel {str} -- Separation vessel name.
        solvent {str} -- Solvent to extract with.
        solvent_volume {float} -- Volume of solvent to extract with.
        n_separations {int} -- Number of separations to perform.
    """
    def __init__(self, from_vessel=None, separation_vessel=None, solvent=None, solvent_volume=None, n_extractions=1):

        self.name = 'Extract'
        self.properties = {
            'from_vessel': from_vessel,
            'separation_vessel': separation_vessel,
            'solvent': solvent,
            'solvent_volume': solvent_volume,
            'n_extractions': n_extractions,
        }

        self.steps = [
            CMove(from_vessel=from_vessel, to_vessel=separation_vessel, ),
        ]

        self.human_readable = f'Extract contents of {from_vessel} with {n_extractions}x{solvent_volume}'

    @property
    def from_vessel(self):
        return self.properties['from_vessel']

    @from_vessel.setter
    def from_vessel(self, val):
        self.properties['from_vessel'] = val
        self.update()

    @property
    def separation_vessel(self):
        return self.properties['separation_vessel']

    @separation_vessel.setter
    def separation_vessel(self, val):
        self.properties['separation_vessel'] = val
        self.update()

    @property
    def solvent(self):
        return self.properties['solvent']

    @solvent.setter
    def solvent(self, val):
        self.properties['solvent'] = val
        self.update()

    @property
    def solvent_volume(self):
        return self.properties['solvent_volume']

    @solvent_volume.setter
    def solvent_volume(self, val):
        self.properties['solvent_volume'] = val
        self.update()

    @property
    def n_extractions(self):
        return self.properties['n_extractions']

    @n_extractions.setter
    def n_extractions(self, val):
        self.properties['n_extractions'] = val
        self.update()

class Wash(Step):

    def __init__(self, from_vessel=None, separation_vessel=None,
                    solvent=None, solvent_volume=None, n_washes=1):

        self.name = 'Wash'
        self.properties = {
            'from_vessel': from_vessel,
            'separation_vessel': separation_vessel,
            'solvent': solvent,
            'solvent_volume': solvent_volume,
            'n_washes': n_washes,
        }

        self.steps = [

        ]

        self.human_readable = f'Wash contents of {from_vessel} with in {separation_vessel} with {solvent} ({n_washes}x{solvent_volume} mL)'

    @property
    def from_vessel(self):
        return self.properties['from_vessel']

    @property
    def separation_vessel(self):
        return self.properties['separation_vessel']

    @property
    def solvent(self):
        return self.properties['solvent']

    @property
    def solvent_volume(self):
        return self.properties['solvent_volume']

    @property
    def n_washes(self):
        return self.properties['n_washes']
