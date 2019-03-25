from typing import Optional

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
    def __init__(
        self,
        time: float,
        wait_recording_speed: float = 'default',
        after_recording_speed: float = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            CSetRecordingSpeed(self.wait_recording_speed),
            CWait(self.time),
            CSetRecordingSpeed(self.after_recording_speed),
        ]

        self.human_readable = 'Wait for {0} s.'.format(self.time)

class PrimePumpForAdd(Step):
    """Prime pump attached to given reagent flask in anticipation of Add step.

    Args:
        reagent (str): Reagent to prime pump for addition.
        move_speed (str): Speed to move reagent at. (optional)
    """
    def __init__(
        self,
        reagent: str,
        volume: Optional[float] = 'default',
        reagent_vessel: Optional[str] = None,
        waste_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            CMove(from_vessel=self.reagent_vessel, to_vessel=self.waste_vessel,
                  volume=self.volume)
        ]


################
### STIRRING ###
################

class StartStir(Step):
    """Start stirring given vessel.

    Args:
        vessel (str): Vessel name to stir.
        stir_rpm (int, optional): Speed in RPM to stir at.
    """
    def __init__(
        self,
        vessel: str,
        stir_rpm: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            CStartStir(vessel=self.vessel),
            CSetStirRpm(vessel=self.vessel, stir_rpm=self.stir_rpm),
        ]

        self.vessel_chain = [self.vessel]

        self.human_readable = 'Set stir rate to {stir_rpm} RPM and start stirring {vessel}.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'stir': True,
            }
        }

class StopStir(Step):
    """Stop stirring given vessel.
    
    Args:
        vessel (str): Vessel name to stop stirring.
    """
    def __init__(self, vessel: str, **kwargs) -> None:
        super().__init__(locals())

        self.steps = [CStopStir(vessel=self.vessel)]

        self.vessel_chain = [self.vessel]

        self.human_readable = 'Stop stirring {0}.'.format(self.vessel)

        self.requirements = {
            'vessel': {
                'stir': True,
            }
        }

class Stir(Step):
    """Stir given vessel for given time at room temperature.

    Args:
        vessel (str): Vessel to stir.
        time (float): Time to stir for.
    """
    def __init__(
        self,
        vessel: str,
        time: float,
        stir_rpm: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            StartStir(vessel=self.vessel, stir_rpm=self.stir_rpm),
            Wait(time=self.time),
            StopStir(vessel=self.vessel),
        ]

        self.vessel_chain = [self.vessel]

        self.human_readable = 'Stir {vessel} for {time} s.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'stir': True,
            }
        }

###############
### HEATING ###
###############

class HeatToTemp(Step):
    """Start heating given vessel at given temperature.

    Args:
        vessel (str): Vessel name to heat.
        temp (float): Temperature to heat to in °C.
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        stir: Optional[bool] = True,
        stir_rpm: Optional[float] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            CSetTemp(vessel=self.vessel, temp=self.temp),
            CStartHeat(vessel=self.vessel),
            CStirrerWaitForTemp(vessel=self.vessel),
        ]
        if self.stir:
            self.steps.insert(0, CStartStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRpm(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRpm(vessel=self.vessel, stir_rpm='default'))

        self.vessel_chain = ['vessel']

        self.human_readable = 'Heat {vessel} to {temp} °C'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp]
            }
        }

class StopHeat(Step):
    """Stop heating given vessel.
    
    Args:
        vessel (str): Vessel name to stop heating.
    """
    def __init__(self, vessel: str, **kwargs) -> None:
        super().__init__(locals())

        self.steps = [CStopHeat(vessel=self.vessel)]

        self.vessel_chain = ['vessel']

        self.human_readable = 'Stop heating {0}.'.format(self.vessel)

        self.human_readable = {
            'vessel': {
                'heatchill': True,
            }
        }

class HeaterReturnToRT(Step):
    """Wait for heater to return to room temperature then stop it.

    Args:
        vessel (str): Vessel to return to room temperature.
    """
    def __init__(
        self,
        vessel: str,
        stir: Optional[bool] = True,
        stir_rpm: Optional[float] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            CSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
            CStirrerWaitForTemp(vessel=self.vessel),
            CStopHeat(vessel=self.vessel),
        ]
        if self.stir:
            self.steps.insert(0, CStartStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRpm(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRpm(vessel=self.vessel, stir_rpm='default'))

        self.vessel_chain = ['vessel']

        self.human_readable = 'Wait for heater attached to {0} to return to room temperature then stop it.'.format(
            self.vessel)

        self.human_readable = {
            'vessel': {
                'heatchill': True,
            }
        }

##############
### VACUUM ###
##############

class StartVacuum(Step):
    """Start vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to start vacuum on.
    """
    def __init__(self, vessel: str, **kwargs) -> None:
        super().__init__(locals())

        self.steps = [
            CSwitchVacuum(vessel=self.vessel, destination='vacuum')
        ]

        self.vessel_chain = ['vessel']

        self.human_readable = f'Start vacuum for {self.vessel}.'

class StopVacuum(Step):
    """Stop vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to stop vacuum on.
    """
    def __init__(self, vessel: str, **kwargs) -> None:
        super().__init__(locals())

        self.steps = [
            CSwitchVacuum(vessel=self.vessel, destination='backbone')
        ]

        self.vessel_chain = ['vessel']

        self.human_readable = f'Stop vacuum for {self.vessel}.'

################
### CHILLING ###
################

class ChillToTemp(Step):

    def __init__(
        self,
        vessel: str,
        temp: float,
        stir: Optional[bool] = True,
        stir_rpm: Optional[float] = None,
        **kwargs) -> None:
        super().__init__(locals())

        self.steps = [
            CSetChiller(vessel=self.vessel, temp=self.temp),
            CStartChiller(vessel=self.vessel),
            CChillerWaitForTemp(vessel=self.vessel),
        ]
        if self.stir:
            self.steps.insert(0, CStartStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRpm(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRpm(vessel=self.vessel, stir_rpm='default'))
            
        self.vessel_chain = ['vessel']

        self.human_readable = 'Chill {0} to {1} °C.'.format(
            self.vessel, self.temp)

        self.requirements = {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp]
            }
        }

class StopChiller(Step):

    def __init__(self, vessel: str, **kwargs) -> None:
        super().__init__(locals())

        self.steps = [
            CStopChiller(self.vessel)
        ]
    
        self.vessel_chain = ['vessel']

        self.human_readable = 'Stop chiller for {0}.'.format(self.vessel)
    
        self.requirements = {
            'vessel': {
                'heatchill': True,
            }
        }

class ChillerReturnToRT(Step):
    """Stop the chiller.

    Args:
        vessel (str): Vessel to stop chiller for.
    """
    def __init__(
        self,
        vessel: str,
        stir: Optional[bool] = True,
        stir_rpm: Optional[float] = None,
        **kwargs) -> None:
        super().__init__(locals())

        self.steps = [
            CSetChiller(vessel=self.vessel, temp=ROOM_TEMPERATURE),
            CChillerWaitForTemp(vessel=self.vessel),
            CStopChiller(vessel)
        ]
        if self.stir:
            self.steps.insert(0, CStartStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRpm(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRpm(vessel=self.vessel, stir_rpm='default'))
            
        self.vessel_chain = ['vessel']

        self.human_readable = 'Stop chiller for {0}'.format(self.vessel)

        self.requirements = {
            'vessel': {
                'heatchill': True,
            }
        }

################
### CLEANING ###
################

class CleanBackbone(Step):

    def __init__(
        self,
        solvent: str,
        waste_vessels: Optional[List[str]] = [],
        solvent_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

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
    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
        volume: float,
        from_port: Optional[str] = None, 
        to_port: Optional[str] = None, 
        through: Optional[str] = None,
        aspiration_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = []
        self.steps.append(
            CMove(
                from_vessel=self.from_vessel,
                from_port=self.from_port,
                to_vessel=self.to_vessel,
                to_port=self.to_port, 
                volume=self.volume,
                through=self.through,
                aspiration_speed=self.aspiration_speed))
                  
        self.vessel_chain = ['from_vessel', 'to_vessel']

        self.human_readable = 'Transfer {0} mL from {1} {2} to {3} {4}.'.format(
            self.volume, self.from_vessel, get_port_str(self.from_port),
            self.to_vessel, get_port_str(self.to_port))