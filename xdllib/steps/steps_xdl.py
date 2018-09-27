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

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

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

    @property
    def temp(self):
        return self.properties['temp']

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

class CleanVessel(Step):
    """Clean given vessel.

    Keyword Arguments:
        vessel {str} -- Vessel to clean.
        solvent {str} -- Solvent to clean with. (optional)
        volume {str} -- Volume of solvent to clean with in mL. (optional)
        stir_rpm {str} -- RPM to stir vessel at during cleaning. (optional)
        stir_time {str} -- Time to stir once solvent has been added. (optional)
    """
    def __init__(self, vessel=None, solvent='default', volume='default', stir_rpm='default', stir_time='default'):

        self.name = 'CleanVessel'
        self.properties = {
            'vessel': vessel,
            'solvent': solvent,
            'volume': volume,
            'stir_rpm': stir_rpm,
        }
        self.get_defaults()

        self.steps = [
            CMove(from_vessel=f'flask_{solvent}', to_vessel=f"{vessel}", volume=volume),
            StartStir(vessel=vessel, stir_rpm=stir_rpm),
            CWait(time=60),
            CStopStir(vessel=vessel),
            CMove(from_vessel=vessel, to_vessel='waste', volume='all'),
        ]

        self.human_readable = f'Clean {vessel} with {solvent} ({volume}).\n'

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def solvent(self):
        return self.properties['solvent']

    @property
    def volume(self):
        return self.properties['volume']

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

class CleanTubing(Step):
    """Clean tubing with given reagent.

    Keyword Arguments:
        reagent {str} -- Reagent to clean tubing with.
        volume {float} -- Volume to clean tubing with in mL. (optional)
    """
    def __init__(self, reagent=None, volume='default'):

        self.name = 'CleanTubing'
        self.properties = {
            'reagent': reagent,
            'volume': volume,
        }
        self.get_defaults()

        self.steps = [
            CMove(from_vessel=f'flask_{reagent}', to_vessel='waste',
                   volume=self.volume)
        ]
        self.steps.append(self.steps[0])

        self.human_readable = f'Clean tubing with {volume} mL of {reagent}.'

    @property
    def reagent(self):
        return self.properties['reagent']

    @property
    def volume(self):
        return self.properties['volume']

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

    @property
    def time(self):
        return self.properties['time']

    @property
    def temp(self):
        return self.properties['temp']

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

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

    @property
    def temp(self):
        return self.properties['temp']

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

class PrimePumpForAdd(Step):
    """Prime pump attached to given reagent flask in anticipation of Add step.

    Keyword Arguments:
        reagent {str} -- Reagent to prime pump for addition.
        move_speed {str} -- Speed to move reagent at. (optional)
    """
    def __init__(self, reagent=None, move_speed='default'):

        self.name = 'PrimePumpForAdd'
        self.properties = {
            'reagent': reagent,
            'move_speed': move_speed,
        }

        self.steps = [
            CMove(from_vessel=f"flask_{reagent}", to_vessel="waste",
                    volume=DEFAULT_PUMP_PRIME_VOLUME, move_speed=move_speed)
        ]

    @property
    def reagent(self):
        return self.properties['reagent']

    @property
    def move_speed(self):
        return self.properties['move_speed']

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

        self.steps = []
        if clean_tubing:
            self.steps.append(PrimePumpForAdd(reagent=reagent))

        self.steps.append(CMove(from_vessel=f"flask_{reagent}", to_vessel=vessel,
                            volume=volume, move_speed=move_speed))
        if clean_tubing:
            self.steps.append(CleanTubing(solvent='default', vessel="waste"))

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

    @property
    def to_vessel(self):
        return self.properties['to_vessel']

    @property
    def volume(self):
        return self.properties['volume']

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

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
                wait_time='default'):

        self.name = 'Wash'
        self.properties = {
            'solvent': solvent,
            'filter_vessel': filter_vessel,
            'volume': volume,
            'move_speed': move_speed,
            'wait_time': wait_time,
        }
        self.get_defaults()

        self.steps = [
            StartStir(vessel=filter_vessel),
            Add(reagent=solvent, volume=volume, vessel=filter_vessel + '_top'),
            CWait(time=wait_time),
            CMove(src=filter_vessel + '_bottom', dest='waste',
                 volume=volume, move_speed=move_speed),
            CStopStir(vessel=filter_vessel)
        ]

        self.human_readable = f'Wash {filter_vessel} with {solvent} ({volume} mL).'

    @property
    def solvent(self):
        return self.properties['solvent']

    @property
    def filter_vessel(self):
        return self.properties['filter_vessel']

    @property
    def volume(self):
        return self.properties['volume']

    @property
    def move_speed(self):
        return self.properties['move_speed']

    @property
    def wait_time(self):
        return self.properties['wait_time']

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

    @property
    def volumes(self):
        return self.properties['volumes']

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def temp(self):
        return self.properties['temp']

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

    @property
    def filter_vessel(self):
        return self.properties['filter_vessel']

    @property
    def time(self):
        return self.properties['time']

class MakeSolution(Step):
    """Make solution in given vessel of given solutes in given solvent.

    Keyword Arguments:
        solute {str or list} -- Solute(s).
        solvent {str} -- Solvent.
        solute_mass {str or list} -- Mass(es) corresponding to solute(s)
        solvent_volume {[type]} -- Volume of solvent to use in mL.
        vessel {[type]} -- Vessel name to make solution in.
    """
    def __init__(self, solute=None, solvent=None, solute_mass=None, solvent_volume=None, vessel=None):

        self.name = 'MakeSolution'
        self.properties = {
            'solute': solute,
            'solvent': solvent,
            'solute_mass': solute_mass,
            'solvent_volume': solvent_volume,
            'vessel': vessel,
        }

        self.steps = []
        if not isinstance(solute, list):
            solute = [solute]
        if not isinstance(solute_mass, list):
            solute_mass = [solute_mass]
        # for s, m in zip(solute, solute_mass):
        #     self.steps.append(AddSolid(reagent=s, mass=m, vessel=vessel)),
        # self.steps.append(Add(reagent=solvent, volume=solvent_volume, vessel=vessel))

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

    @property
    def temp(self):
        return self.properties['temp']

    @property
    def time(self):
        return self.properties['time']

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
            Move('flask_rv_bottom', 'waste', )
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
    """Extract contents of from_vessel using given amount of given solvent.

    Keyword Arguments:
        from_vessel {str} -- Vessel name with contents to be extracted.
        separation_vessel {str} -- Separation vessel name.
        solvent {str} -- Solvent to extract with.
        solvent_volume {float} -- Volume of solvent to extract with.
        n_separations {int} -- Number of separations to perform.
    """
    def __init__(self, from_vessel=None, separation_vessel=None, solvent=None, solvent_volume=None, n_separations=1):

        self.name = 'Extract'
        self.properties = {
            'from_vessel': from_vessel,
            'solvent': solvent,
            'solvent_volume': solvent_volume,
            'n_separations': n_separations,
        }

        self.steps = [
            CMove(from_vessel=from_vessel, to_vessel=separation_vessel, ),
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
