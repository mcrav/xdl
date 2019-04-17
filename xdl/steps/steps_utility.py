from typing import Optional, List

from .steps_base import *
from .base_step import Step
from ..constants import ROOM_TEMPERATURE, DEFAULT_CLEAN_BACKBONE_VOLUME
from ..utils.misc import get_port_str

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
            CStir(vessel=self.vessel),
            CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm),
        ]

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

        self.human_readable = 'Stir {vessel} for {time} s.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'stir': True,
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
            CStartVacuum(vessel=self.vessel)
        ]

        self.human_readable = f'Start vacuum for {self.vessel}.'

class StopVacuum(Step):
    """Stop vacuum pump attached to given vessel.

    Args:
        vessel (str): Vessel name to stop vacuum on.
    """
    def __init__(self, vessel: str, **kwargs) -> None:
        super().__init__(locals())

        self.steps = [
            CStopVacuum(vessel=self.vessel)
        ]

        self.human_readable = f'Stop vacuum for {self.vessel}.'


##################
### HEAT/CHILL ###
##################

class HeatChillToTemp(Step):
    """Heat/Chill vessel to given temp and leave heater/chiller on.
    
    Args:
        vessel (str): Vessel to heat/chill.
        temp (float): Temperature to heat/chill to in degrees C.
        stir (bool): If True, step will be stirred, otherwise False.
        stir_rpm (float): Speed to stir at, only used if stir == True.
        vessel_type (str): Given internally. Used to know whether to use
            heater or chiller base steps. 'ChemputerFilter' or
            'ChemputerReactor'.
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        stir: Optional[bool] = True,
        stir_rpm: Optional[float] = None,
        vessel_type: Optional[str] = None,
        wait_recording_speed: Optional[float] = 'default',
        after_recording_speed: Optional[float] = 'default',
        **kwargs
    ) -> None:

        super().__init__(locals())
        self.steps = []
        if self.vessel_type == 'ChemputerFilter':
            self.steps = [
                CChillerSetTemp(vessel=self.vessel, temp=self.temp),
                CStartChiller(vessel=self.vessel),
                CSetRecordingSpeed(self.wait_recording_speed),
                CChillerWaitForTemp(vessel=self.vessel),
                CSetRecordingSpeed(self.after_recording_speed),
            ]
        elif self.vessel_type == 'ChemputerReactor':
            self.steps = [
                CStirrerSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
                CStirrerHeat(vessel=self.vessel),
                CSetRecordingSpeed(self.wait_recording_speed),
                CStirrerWaitForTemp(vessel=self.vessel),
                CSetRecordingSpeed(self.after_recording_speed),
            ]

        if self.stir:
            self.steps.insert(0, CStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm='default'))
        else:
            self.steps.insert(0, CStopStir(vessel=self.vessel))

        self.human_readable = 'Heat/Chill {0} to {1} °C.'.format(
            self.vessel, self.temp)

        self.requirements = {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp]
            }
        }

class StopHeatChill(Step):
    """Stop heater/chiller on given vessel..
    
    Args:
        vessel (str): Name of vessel attached to heater/chiller..
        vessel_type (str): Given internally. Used to know whether to use
            heater or chiller base steps. 'ChemputerFilter' or
            'ChemputerReactor'.
    """
    def __init__(
        self, vessel: str, vessel_type: Optional[str] = None, **kwargs) -> None:
        super().__init__(locals())
        self.steps = []
        if self.vessel_type == 'ChemputerFilter':
            self.steps = [
                CStopChiller(self.vessel)
            ]
        elif self.vessel_type == 'ChemputerReactor':
            self.steps = [
                CStopHeat(self.vessel)
            ]
    
        self.human_readable = 'Stop heater/chiller for {0}.'.format(self.vessel)
    
        self.requirements = {
            'vessel': {
                'heatchill': True,
            }
        }

class HeatChillReturnToRT(Step):
    """Let heater/chiller return to room temperatre and then stop
    heating/chilling.
    
    Args:
        vessel (str): Vessel to attached to heater/chiller to return to room
            temperature.
        stir (bool): If True, step will be stirred, otherwise False.
        stir_rpm (float): Speed to stir at, only used if stir == True.
        vessel_type (str): Given internally. Used to know whether to use
            heater or chiller base steps. 'ChemputerFilter' or
            'ChemputerReactor'.
    """
    def __init__(
        self,
        vessel: str,
        stir: Optional[bool] = True,
        stir_rpm: Optional[float] = None,
        vessel_type: Optional[str] = None,
        **kwargs) -> None:

        super().__init__(locals())
        self.steps = []
        if self.vessel_type == 'ChemputerFilter':
            self.steps = [
                CChillerSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
                CStartChiller(vessel=self.vessel),
                CChillerWaitForTemp(vessel=self.vessel),
                CStopChiller(self.vessel)
            ]
        elif self.vessel_type == 'ChemputerReactor':
            self.steps = [
                CStirrerSetTemp(vessel=self.vessel, temp=ROOM_TEMPERATURE),
                CStirrerHeat(vessel=self.vessel),
                CStirrerWaitForTemp(vessel=self.vessel),
                CStopHeat(self.vessel),
            ]

        if self.stir:
            self.steps.insert(0, CStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm='default'))
        else:
            self.steps.insert(0, CStopStir(vessel=self.vessel))
            
        self.human_readable = 'Stop heater/chiller for {0} and wait for it to return to room temperature'.format(
            self.vessel)

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
        from_port (str): Port on from_vessel to transfer from.
        to_port (str): Port on to_vessel to transfer from.
        through (str): Node name to transfer to.
        aspiration_speed (float): Speed in mL / min to pull liquid out of
            from_vessel.
        move_speed (float): Speed in mL / min to move liquid at.
        dispense_speed (float): Speed in mL / min to push liquid out of pump
            into to_vessel.
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
        move_speed: Optional[float] = 'default',
        dispense_speed: Optional[float] = 'default',
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
                aspiration_speed=self.aspiration_speed,
                move_speed=self.move_speed,
                dispense_speed=self.dispense_speed))
                  
        self.human_readable = 'Transfer {0} mL from {1} {2} to {3} {4}.'.format(
            self.volume, self.from_vessel, get_port_str(self.from_port),
            self.to_vessel, get_port_str(self.to_port))


###################################
### FILTER DEAD VOLUME HANLDING ###
###################################

class AddFilterDeadVolume(Step):
    """Fill bottom of filter vessel with solvent in anticipation of the filter
    top being used.

    Args:
        filter_vessel (str): Filter vessel to fill dead volume with solvent.
        solvent (str): Solvent to fill filter bottom with.
        volume (int): Volume of filter bottom.
        waste_vessel (str): Given internally. Vessel to put waste material.
        solvent_vessel (str): Given internally. Vessel to take solvent from.
    """
    def __init__(
        self,
        filter_vessel: str,
        solvent: str,
        volume: float, 
        waste_vessel: Optional[str] = None,
        solvent_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            CMove(from_vessel=self.solvent_vessel, volume=self.volume,
                to_vessel=self.filter_vessel, to_port=BOTTOM_PORT)
        ]

        self.human_readable = 'Fill bottom of {filter_vessel} with {solvent} ({volume} mL).'.format(
            **self.properties)

        self.requirements = {
            'filter_vessel': {
                'filter': True
            }
        }

class RemoveFilterDeadVolume(Step):
    """Remove dead volume (volume below filter) from filter vessel.
    
    Args:
        filter_vessel (str): Filter vessel to remove dead volume from.
        dead_volume (float): Volume in mL to remove from bottom of filter vessel.
        waste_vessel (str): Given internally. Waste vessel to send solvent to.
    """
    def __init__(
        self,
        filter_vessel: str,
        dead_volume: Optional[float] = 0,
        waste_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            CMove(from_vessel=self.filter_vessel, from_port=BOTTOM_PORT,
                  to_vessel=self.waste_vessel, volume=self.dead_volume)
        ]

        self.human_readable = 'Remove dead volume ({dead_volume} mL) from bottom of {filter_vessel}'.format(
            **self.properties)

