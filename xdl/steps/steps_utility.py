from .steps_base import *
from .base_step import Step
from ..constants import ROOM_TEMPERATURE

############
### MISC ###
############

class Wait(Step):
    """Wait for given time.

    Args:
        time (int): Time in seconds
        wait_recording_speed (int): Recording speed during wait (faster) ~2000
        after_recording_speed (int): Recording speed after wait (slower) ~14
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

    Args:
        msg (str): Message to get user to confirm experiment should continue.
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

class PrimePumpForAdd(Step):
    """Prime pump attached to given reagent flask in anticipation of Add step.

    Args:
        reagent (str): Reagent to prime pump for addition.
        move_speed (str): Speed to move reagent at. (optional)
    """
    def __init__(self, reagent=None, volume=None, reagent_vessel=None,
                       waste_vessel=None):

        self.properties = {
            'reagent': reagent,
            'volume': volume,
            'reagent_vessel': reagent_vessel,
            'waste_vessel': waste_vessel,
        }
        self.get_defaults()

        self.steps = [
            CMove(from_vessel=self.reagent_vessel, to_vessel=self.waste_vessel,
                  volume=self.volume)
        ]

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


################
### STIRRING ###
################

class StartStir(Step):
    """Start stirring given vessel.

    Args:
        vessel (str): Vessel name to stir.
        stir_rpm (int, optional): Speed in RPM to stir at.
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

        self.human_readable = 'Set stir rate to {stir_rpm} RPM and start stirring {vessel}.'.format(
            **self.properties)

class StopStir(Step):
    """Stop stirring given vessel.
    
    Args:
        vessel (str): Vessel name to stop stirring.
    """
    def __init__(self, vessel=None, temp=None):

        self.properties = {
            'vessel': vessel,
        }

        self.steps = [CStopStir(vessel=self.vessel)]

        self.human_readable = 'Stop stirring {0}.'.format(self.vessel)

class Stir(Step):
    """Stir given vessel for given time at room temperature.

    Args:
        vessel (str): Vessel to stir.
        time (float): Time to stir for.
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
            StopStir(vessel=self.vessel),
        ]

        self.human_readable = 'Stir {vessel} for {time} s.'.format(
            **self.properties)

###############
### HEATING ###
###############

class StartHeat(Step):
    """Start heating given vessel at given temperature.

    Args:
        vessel (str): Vessel name to heat.
        temp (float): Temperature to heat to in °C.
    """
    def __init__(self, vessel=None, temp=None):

        self.properties = {
            'vessel': vessel,
            'temp': temp,
        }

        self.steps = [
            CSetTemp(vessel=self.vessel, temp=self.temp),
            CStartHeat(vessel=self.vessel),
            CStirrerWaitForTemp(vessel=self.vessel),
        ]

        self.human_readable = 'Heat {vessel} to {temp} °C'.format(
            **self.properties)

class StopHeat(Step):
    """Stop heating given vessel.
    
    Args:
        vessel (str): Vessel name to stop heating.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.steps = [CStopHeat(vessel=self.vessel)]

        self.human_readable = 'Stop heating {0}.'.format(self.vessel)

class HeaterReturnToRT(Step):
    """Wait for heater to return to room temperature then stop it.

    Args:
        vessel (str): Vessel to return to room temperature.
    """
    def __init__(self, vessel: str = None) -> None:

        self.properties = {
            'vessel': vessel,
        }

        self.steps = [
            CSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
            CStirrerWaitForTemp(vessel=self.vessel),
            CStopHeat(vessel=self.vessel),
        ]

        self.human_readable = 'Wait for heater attached to {0} to return to room temperature then stop it.'.format(
            self.vessel)

##############
### VACUUM ###
##############

class StartVacuum(Step):
    """Start vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to start vacuum on.
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

    Args:
        vessel (str): Vessel name to stop vacuum on.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.steps = [
            CSwitchVacuum(vessel=self.vessel, destination='backbone')
        ]

        self.human_readable = f'Stop vacuum for {self.vessel}.'

################
### CHILLING ###
################

class StartChiller(Step):

    def __init__(self, vessel=None, temp=None):

        self.properties = {
            'vessel': vessel,
            'temp': temp,
        }

        self.steps = [
            CSetChiller(vessel=self.vessel, temp=self.temp),
            CStartChiller(vessel=self.vessel),
            CChillerWaitForTemp(vessel=self.vessel),
        ]

        self.human_readable = 'Chill {0} to {1} °C.'.format(
            self.vessel, self.temp)

class StopChiller(Step):

    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.steps = [
            CStopChiller(self.vessel)
        ]
    
        self.human_readable = 'Stop chiller for {0}.'.format(self.vessel)

class ChillerReturnToRT(Step):
    """Stop the chiller.

    Args:
        vessel (str): Vessel to stop chiller for.
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

################
### CLEANING ###
################

class CleanVessel(Step):
    """Clean given vessel.

    Args:
        vessel (str): Vessel to clean.
        solvent (str, optional): Solvent to clean with.
        volume (str, optional): Volume of solvent to clean with in mL.
        stir_rpm (str, optional): RPM to stir vessel at during cleaning.
        stir_time (str, optional): Time to stir once solvent has been added.
        waste_vessel (str, optional): Vessel to send waste to. 
            Passed automatically by executor.
        solvent_vessel (str, optional): Vessel containing solvent.
            Passed automatically by executor.
    """
    def __init__(self, vessel=None, solvent='default', volume='default', stir_rpm='default',
                    stir_time='default', waste_vessel=None, solvent_vessel=None):

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
            CMove(
                from_vessel=self.solvent_vessel,
                to_vessel=self.vessel,
                volume=self.volume
            ),
            StartStir(vessel=self.vessel, stir_rpm=1000),
            StartChiller(vessel=self.vessel, 60), # SPECIFIC TO FILTER IN CHILLER
            CMove(
                from_vessel=self.vessel, to_vessel=self.waste_vessel, volume=400,
            ),
            StopStir(vessel=self.vessel),
            Dry(vessel=self.vessel, time=300),
            CSetChiller(vessel=self.vessel, temp=ROOM_TEMPERATURE),
            Dry(vessel=self.vessel, time=600),
            CChillerWaitForTemp(vessel=self.vessel),
            StopChiller(vessel=self.vessel),
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
                volume=DEFAULT_CLEAN_BACKBONE_VOLUME))

        self.human_readable = 'Clean backbone with {0}.'.format(self.solvent)

#######################
### LIQUID MOVEMENT ###
#######################

class Transfer(Step):
    """Transfer contents of one vessel to another.

    Args:
        from_vessel (str): Vessel name to transfer from.
        to_vessel (str): Vessel name to transfer to.
        volume (float): Volume to transfer in mL.
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