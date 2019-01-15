from ..constants import *
from ..utils import Step, filter_bottom_name, filter_top_name, is_generic_filter_name, separator_bottom_name, separator_top_name, is_generic_separator_name
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

        self.properties = {
            'vessel': vessel,
            'stir_rpm': stir_rpm,
        }
        self.get_defaults()

        self.steps = [
            CStartStir(vessel=self.vessel),
            CSetStirRpm(vessel=self.vessel, stir_rpm=self.stir_rpm),
        ]

        self.human_readable = f'Set stir rate to {stir_rpm} RPM and start stirring {vessel}.'

class StartHeat(Step):
    """Start heating given vessel at given temperature.

    Keyword Arguments:
        vessel {str} -- Vessel name to heat.
        temp {float} -- Temperature to heat to in °C.
    """
    def __init__(self, vessel=None, temp=None):

        self.properties = {
            'vessel': vessel,
            'temp': temp,
        }

        self.steps = [
            CSetTemp(vessel=vessel, temp=temp),
            CStartHeat(vessel=vessel),
        ]

        self.human_readable = f'Heat {vessel} to {temp} °C'

class StartVacuum(Step):
    """Start vacuum pump attached to given vessel.

    Keyword Arguments:
        vessel {str} -- Vessel name to start vacuum on.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.steps = [
            CSwitchVacuum(vessel=vessel, destination='vacuum')
        ]

        self.human_readable = f'Start vacuum for {vessel}.'

class StopVacuum(Step):
    """Stop vacuum pump attached to given vessel.

    Keyword Arguments:
        vessel {str} -- Vessel name to stop vacuum on.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.steps = [
            CSwitchVacuum(vessel=vessel, destination='backbone')
        ]

        self.human_readable = f'Stop vacuum for {vessel}.'

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
            Wait(time=60),
            CMove(from_vessel=vessel, to_vessel=self.waste_vessel, volume='all'),
        ]

        self.human_readable = f'Clean {vessel} with {solvent} ({volume}).\n'

class CleanBackbone(Step):

    def __init__(self, reagent=None, waste_vessels=[]):

        self.properties = {
            'reagent': reagent,
            'waste_vessels': waste_vessels,
        }

        self.steps = []
        for waste_vessel in self.waste_vessels:
            self.steps.append(CMove(from_vessel=f'flask_{self.reagent}', to_vessel=waste_vessel, volume=DEFAULT_CLEAN_BACKBONE_VOLUME, aspiration_speed=30))
        self.human_readable = f'Clean backbone with {self.reagent}.'

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

        self.properties = {
            'vessel': vessel,
            'time': time,
            'temp': temp,
            'stir_rpm': stir_rpm,
        }

        self.steps = [
            StartHeat(vessel=vessel, temp=temp),
            Wait(time=time),
            CStopHeat(vessel=vessel),
        ]

        self.human_readable = f'Heat {vessel} to {temp} °C under stirring and wait {float(time) / 3600} hrs.\nThen stop heating and continue stirring until {vessel} reaches room temperature.'

class ContinueStirToRT(Step):
    """Set vessel temperature to room temperature, and continue stirring until
    this temperature is reached, then stop stirring. Assumes stirrer is already on.

    Keyword Arguments:
        vessel {str} -- Vessel to continue stirring until room temperature is reached.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.steps = [
            CSetTemp(vessel=vessel, temp=ROOM_TEMPERATURE),
            CStirrerWaitForTemp(vessel=vessel),
            CStopStir(vessel=vessel),
        ]

        self.human_readable = f'Wait for {vessel} to reach room temperature and then stop stirring.'

class StopChiller(Step):
    """Stop the chiller.

    Keyword Arguments:
        vessel {str} -- Vessel to stop chiller for.
    """
    def __init__(self, vessel=None,):

        self.properties = {
            'vessel': vessel,
        }

        if is_generic_filter_name(vessel):
            vessel = filter_top_name(vessel)

        self.steps = [
            CSetChiller(vessel=vessel, temp=ROOM_TEMPERATURE),
            CChillerWaitForTemp(vessel=vessel),
            CStopChiller(vessel)
        ]

        self.human_readable = f'Stop chiller for {self.vessel}'

class Chill(Step):
    """Chill vessel to given temperature.

    Keyword Arguments:
        vessel {str} -- Vessel name to chill.
        temp {float} -- Temperature in °C to chill to.
    """
    def __init__(self, vessel=None, temp=None):

        self.properties = {
            'vessel': vessel,
            'temp': temp,
        }

        if is_generic_filter_name(vessel):
            vessel = filter_top_name(vessel)

        self.steps = []

        self.steps.extend([
            CSetChiller(vessel=vessel, temp=temp),
            CStartChiller(vessel=vessel),
            CChillerWaitForTemp(vessel=vessel),
        ])


        self.human_readable = f'Chill {vessel} to {temp} °C.'

class ChillBackToRT(Step):
    """Chill given vessel back to room temperature.

    Keyword Arguments:
        vessel {str} -- Vessel name to chill.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        if is_generic_filter_name(vessel):
            vessel = filter_top_name(vessel)

        # This is dodgy. Ideally will track which vessels have chillers.
        if vessel and 'filter' in vessel:
            self.steps = [
                CSetChiller(vessel=vessel, temp=ROOM_TEMPERATURE),
                CChillerWaitForTemp(vessel=vessel),
                CStopChiller(vessel=vessel),
            ]
        else:
            self.steps = [
                CSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
                CStirrerWaitForTemp(vessel=self.vessel),
            ]

        self.human_readable = f'Chill {vessel} to room temperature.'

class PrimePumpForAdd(Step):
    """Prime pump attached to given reagent flask in anticipation of Add step.

    Keyword Arguments:
        reagent {str} -- Reagent to prime pump for addition.
        move_speed {str} -- Speed to move reagent at. (optional)
    """
    def __init__(self, reagent=None,  waste_vessel=None, move_speed='default',):

        self.properties = {
            'reagent': reagent,
            'waste_vessel': waste_vessel,
            'move_speed': move_speed,
        }

        self.steps = [
            CMove(from_vessel=f"flask_{reagent}", to_vessel=self.waste_vessel,
                    volume=DEFAULT_PUMP_PRIME_VOLUME, move_speed=move_speed)
        ]

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
    def __init__(self, reagent=None, volume=None, vessel=None, time=None, move_speed='default', waste_vessel=None):

        self.properties = {
            'reagent': reagent,
            'volume': volume,
            'vessel': vessel,
            'time': time,
            'move_speed': move_speed,
            'waste_vessel': waste_vessel,
        }
        self.get_defaults()

        if is_generic_filter_name(self.vessel):
            vessel = filter_top_name(self.vessel)

        self.steps = []

        self.steps.append(PrimePumpForAdd(reagent=reagent, waste_vessel=waste_vessel))

        self.steps.append(CMove(from_vessel=f"flask_{reagent}", to_vessel=vessel,
                            volume=volume, move_speed=move_speed))

        self.steps.append(Wait(time=DEFAULT_AFTER_ADD_WAIT_TIME))

        self.human_readable = f'Add {reagent} ({volume} mL) to {vessel}' # Maybe add in bit for clean tubing
        if time:
            self.human_readable += f' over {time}'
        self.human_readable += '.'

class Transfer(Step):
    """Transfer contents of one vessel to another.

    Keyword Arguments:
        from_vessel {str} -- Vessel name to transfer from.
        to_vessel {str} -- Vessel name to transfer to.
        volume {float} -- Volume to transfer in mL.
    """
    def __init__(self, from_vessel=None, to_vessel=None, volume=None):

        self.properties = {
            'from_vessel': from_vessel,
            'to_vessel': to_vessel,
            'volume': volume,
        }
        self.get_defaults()
        remove_dead_volume = False

        if is_generic_filter_name(self.to_vessel):
            self.to_vessel = filter_top_name(self.to_vessel)

        if is_generic_filter_name(self.from_vessel):
            self.from_vessel = filter_bottom_name(self.from_vessel)

        self.steps = []

        self.steps.append(CMove(from_vessel=self.from_vessel, to_vessel=self.to_vessel, volume=self.volume))

        self.human_readable = f'Transfer {self.volume} mL to {self.to_vessel}.'

class WashFilterCake(Step):
    """Wash filter cake with given volume of given solvent.

    Keyword Arguments:
        filter_vessel {str} -- Filter vessel name to wash.
        solvent {str} -- Solvent to wash with.
        volume {float} -- Volume of solvent to wash with. (optional)
        wait_time {str} -- Time to wait after moving solvent to filter flask. (optional)
    """
    def __init__(self, filter_vessel=None, solvent=None, volume='default', waste_vessel=None,
                wait_time='default'):

        self.properties = {
            'solvent': solvent,
            'filter_vessel': filter_vessel,
            'volume': volume,
            'waste_vessel': waste_vessel, # should be set in prepare_for_execution
            'wait_time': wait_time,
        }
        self.get_defaults()

        filter_top = filter_top_name(self.filter_vessel)

        self.steps = [
            Add(reagent=self.solvent, volume=self.volume,
                vessel=filter_top, waste_vessel=self.waste_vessel),
            StirAtRT(vessel=filter_top, time=60),
            CMove(from_vessel=filter_bottom_name(self.filter_vessel), to_vessel=self.waste_vessel,
                 volume='all', aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),

            CMove(from_vessel=f'{filter_bottom_name(self.filter_vessel)}', to_vessel=self.waste_vessel,
                 volume=DEFAULT_WASHFILTERCAKE_WAIT_TIME, aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),
        ]

        self.human_readable = f'Wash {filter_vessel} with {solvent} ({volume} mL).'

class Dry(Step):
    """Dry given vessel by applying vacuum for given time.

    Keyword Arguments:
        vessel {str} -- Vessel name to dry.
        time {str} -- Time to dry vessel for in seconds. (optional)
    """
    def __init__(self, filter_vessel=None, waste_vessel=None, time='default'):

        self.properties = {
            'filter_vessel': filter_vessel,
            'waste_vessel': waste_vessel, # set in prepare_for_execution
            'time': time,
        }
        self.get_defaults()

        if is_generic_filter_name(self.filter_vessel):
            filter_vessel_bottom = filter_bottom_name(self.filter_vessel)
        else:
            filter_vessel_bottom = self.filter_vessel

        volume = (float(self.time) / 60) * DEFAULT_FILTER_ASPIRATION_SPEED
        self.steps = [
            CMove(from_vessel=filter_vessel_bottom, to_vessel=self.waste_vessel, volume=volume, aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),
        ]

        self.human_readable = f'Dry substance in {self.filter_vessel} for {self.time} s.'

class Filter(Step):
    """Filter contents of filter_vessel_top. Apply vacuum for given time.
    Assumes filter_filter_bottom already filled with solvent and stuff already in filter_vessel_top.

    Keyword Arguments:
        filter_vessel {str} -- Filter vessel.
        filter_top_volume {float} -- Volume (mL) of contents of filter top.
        filter_bottom_volume {float} -- Volume (mL) of the filter bottom.
        waste_vessel {float} -- Node to move waste material to.
        time {str} -- Time to leave vacuum on filter vessel after contents have been moved. (optional)
    """
    def __init__(self, filter_vessel=None, filter_top_volume=None, filter_bottom_volume=None, waste_vessel=None,
                        time='default'):

        self.properties = {
            'filter_vessel': filter_vessel,
            'filter_top_volume': filter_top_volume, # Filled in when XDL.prepare_for_execution is called
            'filter_bottom_volume': filter_bottom_volume, # Filled in when XDL.prepare_for_execution is called
            'waste_vessel': waste_vessel,
            'time': time,
        }
        self.get_defaults()

        filter_bottom = filter_bottom_name(self.filter_vessel)

        self.steps = [
            CMove(from_vessel=filter_bottom, to_vessel=self.waste_vessel, volume=self.filter_top_volume, aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),
            CMove(from_vessel=filter_bottom, to_vessel=self.waste_vessel, volume=self.filter_bottom_volume, aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),
            CMove(from_vessel=filter_bottom, to_vessel=self.waste_vessel, volume=DEFAULT_FILTER_MOVE_VOLUME, aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),
        ]

        self.human_readable = f'Filter contents of {filter_vessel} for {time} s.'

class Confirm(Step):
    """Get the user to confirm something before execution continues.

    Keyword Arguments:
        msg {str} -- Message to get user to confirm experiment should continue.
    """

    def __init__(self, msg=None):

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
        solvent_volume {float} -- Volume of solvent to use in mL.
        vessel {str} -- Vessel name to make solution in.
    """
    def __init__(self, solutes=None, solvent=None, solute_masses=None, solvent_volume=None, vessel=None):

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

class Reflux(Step):
    """Reflux given vessel at given temperature for given time.

    Keyword Arguments:
        vessel {str} -- Vessel to heat to reflux.
        temp {float} -- Temperature to heat vessel to in °C.
        time {int} -- Time to reflux vessel for in seconds.
    """
    def __init__(self, vessel=None, temp=None, time=None):

        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'time': time,
        }

        filter_vessel = vessel and 'filter' in vessel
        if is_generic_filter_name(vessel):
            vessel = filter_top_name(vessel)

        self.steps = []

        if filter_vessel:
            self.steps.append(Chill(vessel=vessel, temp=temp,))
        else:
            self.steps.append(StartHeat(vessel=vessel, temp=temp),)

        self.steps.append(Wait(time=time),)
        if filter_vessel:
            self.steps.append(StopChiller(vessel=vessel))
        else:
            self.steps.append(CStopHeat(vessel=vessel),)

        self.human_readable = f'Heat {vessel} to {temp} °C and reflux for {time} s.'

class Rotavap(Step):
    """Rotavap contents of given vessel at given temp and given pressure for given time.

    Keyword Arguments:
        vessel {str} -- Vessel with contents to be rotavapped.
        temp {float} -- Temperature to set rotary evaporator water bath to in °C.
        pressure {float} -- Pressure to set rotary evaporator vacuum to in mbar.
        time {int} -- Time to rotavap for in seconds.
    """
    def __init__(self, vessel=None, temp=None, pressure=None, time='default'):

        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'pressure': pressure,
            'time': time,
        }
        self.get_defaults()

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
            Wait(300),
            CSetVacSp('rotavap', 'default'),
            Wait(self.time),
            StopVacuum('rotavap'),
            CVentVac('rotavap'),
            CMove('flask_rv_bottom', 'waste', )
        ]

        self.human_readable = f'Rotavap contents of {vessel} at {temp} °C for {time}.'

class Wait(Step):
    """Wait for given time.

    Keyword Arguments:
        time {int} -- Time in seconds
        wait_recording_speed {int} -- Recording speed during wait (faster) ~2000
        after_recording_speed {int} -- Recording speed after wait (slower) ~14
    """
    def __init__(self, time=None, wait_recording_speed='default', after_recording_speed='default'):

        self.properties = {
            'time': time,
            'wait_recording_speed': wait_recording_speed,
            'after_recording_speed': after_recording_speed,
        }
        self.get_defaults()

        self.steps = [
            CSetRecordingSpeed(self.wait_recording_speed),
            CWait(self.time),
            CSetRecordingSpeed(self.after_recording_speed),
        ]

        self.human_readable = f'Wait for {self.time} s.'

class Extract(Step):
    """Extract contents of from_vessel using given amount of given solvent.

    Keyword Arguments:
        from_vessel {str} -- Vessel name with contents to be extracted.
        separation_vessel {str} -- Separation vessel name.
        solvent {str} -- Solvent to extract with.
        solvent_volume {float} -- Volume of solvent to extract with.
        n_separations {int} -- Number of separations to perform.
    """
    def __init__(self, from_vessel=None, separation_vessel=None, to_vessel=None, solvent=None,
                    solvent_volume=None, n_extractions=1, product_bottom=True, waste_vessel=None,
                    waste_phase_to_vessel=None, filter_dead_volume=None):

        self.properties = {
            'from_vessel': from_vessel,
            'separation_vessel': separation_vessel,
            'to_vessel': to_vessel,
            'solvent': solvent,
            'solvent_volume': solvent_volume,
            'n_extractions': n_extractions,
            'product_bottom': product_bottom,
            'waste_phase_to_vessel': waste_phase_to_vessel,
            'waste_vessel': waste_vessel, # set in prepare_for_execution
            'filter_dead_volume': filter_dead_volume,
        }
        if not to_vessel and from_vessel:
            self.to_vessel = from_vessel # is necessary to set self.to_vessel here not just to_vessel

        if not waste_phase_to_vessel and waste_vessel:
            self.waste_phase_to_vessel = waste_vessel

        if is_generic_filter_name(self.to_vessel):
            to_vessel = filter_top_name(to_vessel)

        if is_generic_filter_name(from_vessel):
            from_vessel = filter_bottom_name(from_vessel)

        if is_generic_separator_name(waste_phase_to_vessel):
            waste_phase_to_vessel = separator_top_name(waste_phase_to_vessel)
        elif is_generic_filter_name(waste_phase_to_vessel):
            waste_phase_to_vessel = filter_top_name(waste_phase_to_vessel)

        self.get_defaults()

        if not self.n_extractions:
            n_extractions = 1
        else:
            n_extractions = int(self.n_extractions)

        separator_top = separator_top_name(self.separation_vessel)
        separator_bottom = separator_bottom_name(self.separation_vessel)

        self.steps = []

        self.steps.extend([
                # Move from from_vessel to separation_vessel
                Transfer(from_vessel=from_vessel, to_vessel=separator_top, volume='all'),
                # Move solvent to separation_vessel.
                Add(reagent=self.solvent, volume=self.solvent_volume, vessel=separator_bottom, waste_vessel=self.waste_vessel),
                # Stir separation_vessel
                StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_FAST_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
                StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_SLOW_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
                # Wait for phases to separate
                Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
            ])

        if self.from_vessel in [self.separation_vessel, separator_top, separator_bottom]:
            self.steps.pop(0)

        remove_volume = 2

        # If product in bottom phase
        if self.product_bottom:
            if n_extractions > 1:
                for i in range(n_extractions - 1):
                    self.steps.extend([
                        Transfer(from_vessel=separator_bottom, to_vessel=self.waste_vessel, volume=remove_volume),
                        CSeparate(lower_phase_vessel=to_vessel, upper_phase_vessel=waste_phase_to_vessel,
                            separator_top=separator_top, separator_bottom=separator_bottom, dead_volume_target=self.waste_vessel),
                        # Move to_vessel to separation_vessel
                        CMove(from_vessel=to_vessel, to_vessel=separator_top, volume='all'),
                        # Move solvent to separation_vessel. Bottom as washes any reagent from previous separation back into funnel.
                        Add(reagent=self.solvent, volume=self.solvent_volume, vessel=separator_bottom, waste_vessel=self.waste_vessel),
                        # Stir separation_vessel
                        StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_FAST_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
                        StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_SLOW_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
                        # Wait for phases to separate
                        Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
                    ])


            self.steps.extend([
                Transfer(from_vessel=separator_bottom, to_vessel=self.waste_vessel, volume=remove_volume),
                CSeparate(lower_phase_vessel=to_vessel, upper_phase_vessel=waste_phase_to_vessel,
                            separator_top=separator_top, separator_bottom=separator_bottom, dead_volume_target=self.waste_vessel),
            ])
        else:
            if n_extractions > 1:
                for i in range(n_extractions - 1):
                    self.steps.extend([
                        Transfer(from_vessel=separator_bottom, to_vessel=self.waste_vessel, volume=remove_volume),
                        CSeparate(lower_phase_vessel=self.waste_vessel, upper_phase_vessel=separator_top,
                            separator_top=separator_top, separator_bottom=separator_bottom, dead_volume_target=self.waste_vessel),
                        # Move solvent to separation_vessel
                        Add(reagent=self.solvent, vessel=separator_bottom, volume=self.solvent_volume, waste_vessel=self.waste_vessel),
                        # Stir separation_vessel
                        StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_FAST_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
                        StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_SLOW_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
                        # Wait for phases to separate
                        Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
                    ])

            self.steps.extend([
                Transfer(from_vessel=separator_bottom, to_vessel=self.waste_vessel, volume=remove_volume),
                CSeparate(lower_phase_vessel=waste_phase_to_vessel, upper_phase_vessel=self.to_vessel,
                            separator_top=separator_top, separator_bottom=separator_bottom, dead_volume_target=self.waste_vessel),
            ])

        self.human_readable = f'Extract contents of {self.from_vessel} with {self.solvent} ({self.n_extractions}x{self.solvent_volume} mL).'

class WashSolution(Step):
    """Wash contents of from_vessel with given solvent.

    Keyword Arguments:
        from_vessel {str} -- Vessel with contents to be washed.
        separation_vessel {str} -- Separating funnel name.
        to_vessel {str} -- Vessel to put washed product after separation.
        solvent {str} -- Solvent to wash with.
        solvent_volume {float} -- Volume of solvent to wash with.
        n_washes {int} -- Number of washes to perform.
        product_bottom {bool} -- True if product is in bottom phase.
        waste_vessel {str} -- Vessel to put waste material.
        waste_phase_to_vessel {str} -- Vessel to put the phase that doesn't have the product.
    """
    def __init__(self, from_vessel=None, separation_vessel=None, to_vessel=None,
                    solvent=None, solvent_volume=None, n_washes=1, product_bottom=True,
                    waste_vessel=None, waste_phase_to_vessel=None, filter_dead_volume=None):

        self.properties = {
            'from_vessel': from_vessel,
            'to_vessel': to_vessel,
            'separation_vessel': separation_vessel,
            'solvent': solvent,
            'solvent_volume': solvent_volume,
            'n_washes': n_washes,
            'product_bottom': product_bottom,
            'waste_phase_to_vessel': waste_phase_to_vessel,
            'waste_vessel': waste_vessel,
            'filter_dead_volume': filter_dead_volume,
        }
        self.get_defaults()

        if not waste_phase_to_vessel and waste_vessel:
            self.waste_phase_to_vessel = waste_vessel

        if is_generic_filter_name(to_vessel):
            to_vessel = filter_top_name(to_vessel)

        if is_generic_filter_name(from_vessel):
            from_vessel = filter_bottom_name(from_vessel)

        if is_generic_separator_name(waste_phase_to_vessel):
            waste_phase_to_vessel = separator_top_name(waste_phase_to_vessel)
        elif is_generic_filter_name(waste_phase_to_vessel):
            waste_phase_to_vessel = filter_top_name(waste_phase_to_vessel)

        if not n_washes:
            n_washes = 1
        else:
            n_washes = int(n_washes)

        remove_volume = 2

        separator_top = separator_top_name(self.separation_vessel)
        separator_bottom = separator_bottom_name(self.separation_vessel)

        self.steps = []

        self.steps.extend([
            # Move from from_vessel to separation_vessel
            Transfer(from_vessel=from_vessel, to_vessel=separator_top, volume='all'),
            # Move solvent to separation_vessel
            Add(reagent=self.solvent, volume=self.solvent_volume, vessel=separator_bottom, waste_vessel=self.waste_vessel),
            # Stir separation_vessel
            StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_FAST_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
            StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_SLOW_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
            # Wait for phases to separate
            Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
        ])

        if self.from_vessel in [self.separation_vessel, separator_top, separator_bottom]:
            self.steps.pop(0)

        if self.product_bottom:
            if n_washes > 1:
                for i in range(n_washes - 1):
                    self.steps.extend([
                        # Move first 2 mL of product phase to waste just in case of contamination.
                        Transfer(from_vessel=separator_bottom, to_vessel=self.waste_vessel, volume=remove_volume),
                        CSeparate(lower_phase_vessel=to_vessel, upper_phase_vessel=self.waste_phase_to_vessel,
                            separator_top=separator_top, separator_bottom=separator_bottom, dead_volume_target=self.waste_vessel),
                        # Move to_vessel to separation_vessel
                        Transfer(from_vessel=to_vessel, to_vessel=separator_top, volume='all'),
                        # Move solvent to separation_vessel. Bottom as washes any reagent from previous separation back into funnel.
                        Add(reagent=self.solvent, volume=self.solvent_volume, vessel=separator_bottom, waste_vessel=self.waste_vessel),
                        # Stir separation_vessel
                        StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_FAST_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
                        StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_SLOW_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
                        # Wait for phases to separate
                        Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
                    ])
            remove_volume = 2
            self.steps.extend([
                Transfer(from_vessel=separator_bottom, to_vessel=self.waste_vessel, volume=remove_volume),
                # Do separation
                CSeparate(lower_phase_vessel=to_vessel, upper_phase_vessel=self.waste_phase_to_vessel,
                            separator_top=separator_top, separator_bottom=separator_bottom),
            ])
        else:
            if n_washes > 1:
                for i in range(n_washes - 1):
                    self.steps.extend([
                        Transfer(from_vessel=separator_bottom, to_vessel=self.waste_vessel, volume=remove_volume),
                        CSeparate(lower_phase_vessel=self.waste_phase_to_vessel, upper_phase_vessel=separator_top,
                            separator_top=separator_top, separator_bottom=separator_bottom, dead_volume_target=self.waste_vessel),
                        # Move solvent to separation_vessel
                        Add(reagent=self.solvent, volume=self.solvent_volume, vessel=separator_bottom, waste_vessel=self.waste_vessel),
                        # Stir separation_vessel
                        StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_FAST_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
                        StirAtRT(vessel=separator_top, time=DEFAULT_SEPARATION_SLOW_STIR_TIME, stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
                        # Wait for phases to separate
                        Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
                    ])
            self.steps.extend([
                Transfer(from_vessel=separator_bottom, to_vessel=self.waste_vessel, volume=remove_volume),
                # Do separation
                CSeparate(lower_phase_vessel=self.waste_phase_to_vessel, upper_phase_vessel=to_vessel,
                            separator_top=separator_top, separator_bottom=separator_bottom, dead_volume_target=self.waste_vessel),
            ])

        self.human_readable = f'Wash contents of {from_vessel} in {separation_vessel} with {solvent} ({n_washes}x{solvent_volume} mL)'

class StirAtRT(Step):
    """Stir given vessel for given time at room temperature.

    Keyword Arguments:
        vessel {str} -- Vessel to stir.
        time {float} -- Time to stir for.
    """
    def __init__(self, vessel=None, time=None, stir_rpm='default'):

        self.properties = {
            'vessel': vessel,
            'time': time,
            'stir_rpm': stir_rpm,
        }

        self.get_defaults()

        self.steps = [
            StartStir(vessel=self.vessel, stir_rpm=self.stir_rpm),
            Wait(time=self.time),
            CStopStir(vessel=self.vessel),
        ]

        self.human_readable = f'Stir {vessel} for {time} s.'

class PrepareFilter(Step):
    """Fill bottom of filter vessel with solvent in anticipation of the filter top being used.

    Keyword Arguments:
        filter_vessel {str} -- Filter vessel name to prepare (generic name 'filter' not 'filter_filter_bottom').
        solvent {str} -- Solvent to fill filter bottom with.
        volume {int} -- Volume of filter bottom.
        waste_vessel {str} -- Vessel to put waste material.
    """
    def __init__(self, filter_vessel=None, solvent=None, volume=10, waste_vessel=None):

        self.properties = {
            'filter_vessel': filter_vessel,
            'solvent': solvent,
            'volume': volume, # This value should be replaced when XDL calls prepare_for_execution.
            'waste_vessel': waste_vessel,
        }
        self.steps = [
            Add(reagent=self.solvent, volume=self.volume,
                vessel=filter_bottom_name(self.filter_vessel), waste_vessel=waste_vessel,)
        ]

        self.human_readable = f'Fill {filter_bottom_name(self.filter_vessel)} with {solvent} ({volume} mL).'