from ..constants import *
from ..utils.misc import get_port_str
from .base_step import Step
from .steps_chasm import (
    CMove,
    CSeparatePhases,
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

######################
### INTERNAL STEPS ###
######################

class StirAtRT(Step):
    """Stir given vessel for given time at room temperature.

    Keyword Arguments:
        vessel {str} -- Vessel to stir.
        time {float} -- Time to stir for.
    """
    def __init__(self, vessel, time, stir_rpm='default'):

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

        self.human_readable = 'Stir {vessel} for {time} s.'.format(
            **self.properties)

class PrimePumpForAdd(Step):
    """Prime pump attached to given reagent flask in anticipation of Add step.

    Keyword Arguments:
        reagent {str} -- Reagent to prime pump for addition.
        move_speed {str} -- Speed to move reagent at. (optional)
    """
    def __init__(self, reagent, reagent_vessel=None, waste_vessel=None, move_speed='default',):

        self.properties = {
            'reagent': reagent,
            'reagent_vessel': reagent_vessel,
            'waste_vessel': waste_vessel,
            'move_speed': move_speed,
        }

        self.steps = [
            CMove(from_vessel=self.reagent_vessel, to_vessel=self.waste_vessel,
                    volume=DEFAULT_PUMP_PRIME_VOLUME, move_speed=move_speed)
        ]

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
            'solvent': solvent,            'volume': volume, # This value should be replaced when XDL calls prepare_for_execution.
            'waste_vessel': waste_vessel,
        }
        self.steps = [
            Add(reagent=self.solvent, volume=self.volume,
                vessel=self.filter_vessel, port=BOTTOM_PORT, 
                waste_vessel=waste_vessel)
        ]

        self.human_readable = 'Fill bottom of {filter_vessel} with {solvent} ({volume} mL).'.format(
            **self.properties)

class RemoveFilterDeadVolume(Step):
    """Remove dead volume (volume below filter) from filter vessel.
    
    Args:
        filter_vessel (str): Filter vessel ID to remove dead volume from.
        dead_volume (float): Volume in mL to remove from bottom of filter vessel.
    """
    def __init__(self, filter_vessel=None, dead_volume=0, waste_vessel=None):

        self.properties = {
            'filter_vessel': filter_vessel,
            'dead_volume': dead_volume,
            'waste_vessel': waste_vessel,
        }

        self.steps = [
            Transfer(from_vessel=self.filter_vessel, to_vessel=self.waste_vessel, 
                     volume=self.dead_volume)
        ]

        self.human_readable = 'Remove dead volume ({volume} mL) from bottom of {filter_vessel}'.format(
            **self.properties)


########################
### START/STOP STEPS ###
########################

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

class StopStir(Step):
    pass

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
            CSetTemp(vessel=self.vessel, temp=self.temp),
            CStartHeat(vessel=self.vessel),
        ]

        self.human_readable = f'Heat {self.vessel} to {self.temp} °C'

class StopHeat(Step):
    pass

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
            CSwitchVacuum(vessel=self.vessel, destination='vacuum')
        ]

        self.human_readable = f'Start vacuum for {self.vessel}.'

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
            CSwitchVacuum(vessel=self.vessel, destination='backbone')
        ]

        self.human_readable = f'Stop vacuum for {self.vessel}.'

class StartChiller(Step):
    pass

class StopChiller(Step):
    """Stop the chiller.

    Keyword Arguments:
        vessel {str} -- Vessel to stop chiller for.
    """
    def __init__(self, vessel=None,):

        self.properties = {
            'vessel': vessel,
        }

        self.steps = [
            CSetChiller(vessel=self.vessel, temp=ROOM_TEMPERATURE),
            CChillerWaitForTemp(vessel=self.vessel),
            CStopChiller(vessel)
        ]

        self.human_readable = 'Stop chiller for {0}'.format(self.vessel)


######################
### CLEANING STEPS ###
######################

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
            'solvent_vessel': solvent_vessel,
            'volume': volume,
            'stir_rpm': stir_rpm,
            'waste_vessel': waste_vessel,
        }
        self.get_defaults()

        self.steps = [
            CMove(from_vessel=self.solvent_flask, 
                  to_vessel=self.vessel, volume=self.volume),
            Wait(time=60),
            CMove(from_vessel=self.vessel, to_vessel=self.waste_vessel,
                  volume='all'),
        ]

        self.human_readable = 'Clean {0} with {1} ({2}).'.format(
            self.vessel, self.solvent, self.volume)

class CleanBackbone(Step):

    def __init__(self, solvent, waste_vessels=[], solvent_vessel=None):

        self.properties = {
            'solvent': solvent,
            'solvent_vessel': solvent_vessel,
            'waste_vessels': waste_vessels,
        }

        self.steps = []
        for waste_vessel in self.waste_vessels:
            self.steps.append(CMove(
                from_vessel=self.solvent_vessel, to_vessel=waste_vessel,
                volume=DEFAULT_CLEAN_BACKBONE_VOLUME,
                aspiration_speed=DEFAULT_CLEAN_BACKBONE_ASPIRATION_SPEED))

        self.human_readable = 'Clean backbone with {0}.'.format(self.solvent)


##################
### MOVE STEPS ###
##################

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
    def __init__(self, reagent, volume, vessel, port=None, time=None,
                       move_speed='default', reagent_vessel=None, 
                       waste_vessel=None):

        self.properties = {
            'reagent': reagent,
            'reagent_vessel': reagent_vessel,
            'volume': volume,
            'vessel': vessel,
            'port': port,
            'time': time,
            'move_speed': move_speed,
            'waste_vessel': waste_vessel,
        }
        self.get_defaults()

        self.steps = []
        self.steps.append(PrimePumpForAdd(reagent=reagent, waste_vessel=waste_vessel))
        self.steps.append(
            CMove(from_vessel=self.reagent_vessel, to_vessel=self.vessel, 
                  to_port=self.port, volume=self.volume, move_speed=self.move_speed))
        self.steps.append(Wait(time=DEFAULT_AFTER_ADD_WAIT_TIME))

        self.human_readable = 'Add {0} ({1} mL) to {2} {3}'.format(
            self.reagent, self.volume, self.vessel, get_port_str(self.port))
        if time:
            self.human_readable += ' over {0}'.format(self.time)
        self.human_readable += '.'

class Transfer(Step):
    """Transfer contents of one vessel to another.

    Keyword Arguments:
        from_vessel {str} -- Vessel name to transfer from.
        to_vessel {str} -- Vessel name to transfer to.
        volume {float} -- Volume to transfer in mL.
    """
    def __init__(self, from_vessel=None, to_vessel=None, from_port=None, 
                       to_port=None, volume=None):

        self.properties = {
            'from_vessel': from_vessel,
            'from_port': from_port,
            'to_vessel': to_vessel,
            'to_port': to_port,
            'volume': volume,
        }
        self.get_defaults()

        self.steps = []
        self.steps.append(
            CMove(from_vessel=self.from_vessel, from_port=self.from_port,
                  to_vessel=self.to_vessel, to_port=self.to_port, 
                  volume=self.volume))
        
        self.human_readable = 'Transfer {0} mL from {1} {2} to {3} {4}.'.format(
            self.volume, self.from_vessel, get_port_str(self.from_port),
            self.to_vessel, get_port_str(self.to_port))

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
        self.steps.append(Add(reagent=solvent, volume=solvent_volume, vessel=vessel))

        self.human_readable = f'Make solution of '
        for s, m in zip(solutes, solute_masses):
            self.human_readable += '{0} ({1} g), '.format(s, m)
        self.human_readable = self.human_readable[:-2] + ' in {solvent} ({solvent_volume} mL) in {vessel}.'.format(
            **self.properties)


####################
### FILTER STEPS ###
####################

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

        self.steps = [
            Add(reagent=self.solvent, volume=self.volume,
                vessel=self.filter_vessel, port=TOP_PORT, 
                waste_vessel=self.waste_vessel),
            StirAtRT(vessel=self.filter_vessel, time=60),
            CMove(from_vessel=self.filter_vessel, from_port=BOTTOM_PORT,
                  to_vessel=self.waste_vessel, volume='all',
                  aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),

            CMove(from_vessel=self.filter_vessel, from_port=BOTTOM_PORT, 
                  to_vessel=self.waste_vessel, 
                  volume=DEFAULT_WASHFILTERCAKE_WAIT_TIME, 
                  aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),
        ]

        self.human_readable = 'Wash {0} with {1} ({2} mL).'.format(
            **self.properties)

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

        volume = ((self.time) / 60) * DEFAULT_FILTER_ASPIRATION_SPEED
        self.steps = [
            CMove(from_vessel=self.filter_vessel, from_port=BOTTOM_PORT,
                  to_vessel=self.waste_vessel, volume=self.volume,
                  aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),
        ]

        self.human_readable = 'Dry substance in {filter_vessel} for {time} s.'.format(
            **self.properties)

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

        self.steps = [
            CMove(from_vessel=filter_bottom, to_vessel=self.waste_vessel, volume=self.filter_top_volume, aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),
            CMove(from_vessel=filter_bottom, to_vessel=self.waste_vessel, volume=self.filter_bottom_volume, aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),
            CMove(from_vessel=filter_bottom, to_vessel=self.waste_vessel, volume=DEFAULT_FILTER_MOVE_VOLUME, aspiration_speed=DEFAULT_FILTER_ASPIRATION_SPEED),
        ]

        self.human_readable = f'Filter contents of {filter_vessel} for {time} s.'


########################
### SEPARATION STEPS ###
########################

class Separate(Step):
    """Extract contents of from_vessel using given amount of given solvent.

    NOTE: If n_separations > 1, to_vessel/to_port must be capable of giving
          and receiving material.
    Keyword Arguments:
        from_vessel {str} -- Vessel name with contents to be extracted.
        separation_vessel {str} -- Separation vessel name.
        solvent {str} -- Solvent to extract with.
        solvent_volume {float} -- Volume of solvent to extract with.
        n_separations {int} -- Number of separations to perform.
    """
    def __init__(self, from_vessel=None, from_port=None, separation_vessel=None, 
                       to_vessel=None, to_port=None, solvent=None, 
                       solvent_volume=None, n_separations=1, product_bottom=True,
                       waste_vessel=None, waste_phase_to_vessel=None,
                       waste_phase_to_port=None):

        self.properties = {
            'from_vessel': from_vessel,
            'from_port': from_port,
            'separation_vessel': separation_vessel,
            'to_vessel': to_vessel,
            'to_port': to_port,
            'solvent': solvent,
            'solvent_volume': solvent_volume,
            'n_separations': n_separations,
            'product_bottom': product_bottom,
            'waste_phase_to_vessel': waste_phase_to_vessel,
            'waste_phase_to_port': waste_phase_to_port,
            'waste_vessel': waste_vessel, # set in prepare_for_execution
        }
        self.get_defaults()

        if not waste_phase_to_vessel and waste_vessel:
            self.waste_phase_to_vessel = waste_vessel

        if not self.n_separations:
            n_separations = 1
        else:
            n_separations = int(self.n_separations)

        self.steps = []
        self.steps.extend([
            # Move from from_vessel to separation_vessel
            Transfer(
                from_vessel=self.from_vessel, from_port=self.from_port, 
                to_vessel=self.separation_vessel, to_port=TOP_PORT, 
                volume='all'),
            # Move solvent to separation_vessel.
            Add(reagent=self.solvent, volume=self.solvent_volume, 
                vessel=self.separation_vessel, port=BOTTOM_PORT, 
                waste_vessel=self.waste_vessel),
            # Stir separation_vessel
            StirAtRT(vessel=self.separation_vessel, 
                     time=DEFAULT_SEPARATION_FAST_STIR_TIME, 
                     stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
            StirAtRT(vessel=self.separation_vessel, 
                     time=DEFAULT_SEPARATION_SLOW_STIR_TIME, 
                     stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
            # Wait for phases to separate
            Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
        ])

        if self.from_vessel == self.separation_vessel:
            self.steps.pop(0)

        remove_volume = 2

        # If product in bottom phase
        if self.product_bottom:
            if n_separations > 1:
                for _ in range(n_separations - 1):
                    self.steps.extend([
                        Transfer(from_vessel=self.separation_vessel, 
                                 from_port=BOTTOM_PORT, 
                                 to_vessel=self.waste_vessel, 
                                 volume=remove_volume),
                        CSeparatePhases(lower_phase_vessel=self.to_vessel, 
                                  lower_phase_port=self.to_port,
                                  upper_phase_vessel=self.waste_phase_to_vessel,
                                  upper_phase_port=self.waste_phase_to_port,
                                  separation_vessel=self.separation_vessel, 
                                  dead_volume_target=self.waste_vessel),
                        # Move to_vessel to separation_vessel
                        CMove(from_vessel=to_vessel, 
                              to_vessel=self.separation_vessel, volume='all'),
                        # Move solvent to separation_vessel. 
                        # Bottom port as washes any reagent from previous 
                        # separation back into funnel.
                        Add(reagent=self.solvent, volume=self.solvent_volume, 
                            vessel=self.separation_vessel, port=BOTTOM_PORT, 
                            waste_vessel=self.waste_vessel),
                        # Stir separation_vessel
                        StirAtRT(vessel=self.separation_vessel, 
                                 time=DEFAULT_SEPARATION_FAST_STIR_TIME, 
                                 stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
                        StirAtRT(vessel=self.separation_vessel, 
                                 time=DEFAULT_SEPARATION_SLOW_STIR_TIME, 
                                 stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
                        # Wait for phases to separate
                        Wait(time=DEFAULT_SEPARATION_SETTLE_TIME)
                    ])


            self.steps.extend([
                Transfer(from_vessel=self.separation_vessel, 
                         from_port=BOTTOM_PORT, to_vessel=self.waste_vessel, 
                         volume=remove_volume),
                CSeparatePhases(lower_phase_vessel=self.to_vessel,
                          lower_phase_port=self.to_port,
                          upper_phase_vessel=self.waste_phase_to_vessel,
                          upper_phase_port=self.waste_phase_to_port,
                          separation_vessel=self.separation_vessel,
                          dead_volume_target=self.waste_vessel),
            ])
        else:
            if n_separations > 1:
                for _ in range(n_separations - 1):
                    self.steps.extend([
                        Transfer(from_vessel=self.separation_vessel, 
                                 from_port=BOTTOM_PORT, 
                                 to_vessel=self.waste_vessel,
                                 volume=remove_volume),
                        CSeparatePhases(
                            lower_phase_vessel=self.waste_phase_to_vessel,
                            lower_phase_port=self.waste_phase_to_port,
                            upper_phase_vessel=self.separation_vessel,
                            separation_vessel=self.separation_vessel,
                            dead_volume_target=self.waste_vessel),
                        # Move solvent to separation_vessel
                        Add(reagent=self.solvent, vessel=self.separation_vessel, 
                            port=BOTTOM_PORT, volume=self.solvent_volume, 
                            waste_vessel=self.waste_vessel),
                        # Stir separation_vessel
                        StirAtRT(vessel=self.separation_vessel, 
                                 time=DEFAULT_SEPARATION_FAST_STIR_TIME, 
                                 stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
                        StirAtRT(vessel=self.separation_vessel, 
                                 time=DEFAULT_SEPARATION_SLOW_STIR_TIME, 
                                 stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
                        # Wait for phases to separate
                        Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
                    ])

            self.steps.extend([
                Transfer(from_vessel=self.separation_vessel, 
                         from_port=BOTTOM_PORT, to_vessel=self.waste_vessel, 
                         volume=remove_volume),
                CSeparatePhases(lower_phase_vessel=self.waste_phase_to_vessel, 
                          lower_phase_port=self.waste_phase_to_port, 
                          upper_phase_vessel=self.to_vessel,
                          upper_phase_port=self.to_port,
                          separation_vessel=self.separation_vessel,
                          dead_volume_target=self.waste_vessel),
            ])

        self.human_readable = 'Separate contents of {0} {1} with {2} ({3}x{4} mL). Transfer waste phase to {5} {6} and product phase to {7} {8}.'.format(
            self.from_vessel, get_port_str(self.from_port), self.solvent,
            self.n_separations, self.solvent_volume, self.waste_phase_to_vessel,
            get_port_str(self.waste_phase_to_port), self.to_vessel, self.to_port)


########################
### HEAT/CHILL STEPS ###
########################

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

        self.steps = [
            StartHeat(vessel=self.vessel, temp=self.temp),
            Wait(time=self.time),
            StopHeat(vessel=self.vessel),
        ]
        self.human_readable = 'Heat {vessel} to {temp} °C and reflux for {time} s.'.format(
            **self.properties)

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

        self.steps = []
        self.steps.extend([
            CSetChiller(vessel=self.vessel, temp=self.temp),
            CStartChiller(vessel=self.vessel),
            CChillerWaitForTemp(vessel=self.vessel),
        ])


        self.human_readable = 'Chill {vessel} to {temp} °C.'.format(
            **self.properties)

#####################
### ROTAVAP STEPS ###
#####################

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

        self.human_readable = 'Rotavap contents of {vessel} at {temp} °C for {time}.'.format(
            **self.properties)

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

        self.human_readable = 'Wait for {0} s.'.format(self.time)

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