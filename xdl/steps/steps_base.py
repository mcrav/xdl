from typing import Optional

from ..constants import *
from ..utils.misc import get_port_str
from .base_step import Step

# For type annotations
if False:
    from chempiler import Chempiler

class Confirm(Step):
    """Get the user to confirm something before execution continues.

    Args:
        msg (str): Message to get user to confirm experiment should continue.
    """

    def __init__(self, msg: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler: 'Chempiler') -> bool:
        keep_going = input(self.msg)
        if not keep_going or keep_going.lower() in ['y', 'yes']:
            return True
        return False

#################
### chempiler ###
#################

class CMove(Step):
    """Moves a specified volume from one node in the graph to another. Moving from and to
    the same node is supported.

    Args:
        from_vessel (str): Vessel name to move from.
        to_vessel (str): Vessel name to move to.
        volume (float): Volume to move in mL. 'all' moves everything.
        move_speed (float): Speed at which liquid is moved in mL / min. (optional)
        aspiration_speed (float): Speed at which liquid aspirates from from_vessel. (optional)
        dispense_speed (float): Speed at which liquid dispenses from from_vessel. (optional)
    """
    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
        volume: float,
        move_speed: Optional[float] = 'default',
        aspiration_speed: Optional[float] = 'default',
        dispense_speed: Optional[float] = 'default',
        from_port: Optional[str] = None,
        to_port: Optional[str] = None,
        unique: Optional[bool] = False,
        through: Optional[str] = None
    ) -> None:
        super().__init__(locals())


    def execute(self, chempiler, logger=None, level=0):
        chempiler.move(
            src_node=self.from_vessel,
            dst_node=self.to_vessel,
            volume=self.volume,
            speed=(self.aspiration_speed, self.move_speed, self.dispense_speed),
            src_port=self.from_port,
            dst_port=self.to_port,
            unique=self.unique,
            through_node=self.through,
        )
        return True

class CConnect(Step):
    """Connect two nodes together.
    
    Args:
        from_vessel (str): Node name to connect from.
        to_vessel (str): Node name to connect to.
        from_port (str): Port name to connect from.
        to_port (str): Port name to connect to.
        unique (bool): Must use unique route.
    """
    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
        from_port: Optional[str] = None,
        to_port: Optional[str] = None,
        unique: Optional[bool] = True
    ) -> None:
        super().__init__(locals())
        
    def execute(self, chempiler, logger=None, level=0):
        chempiler.connect(
            src_node=self.from_vessel,
            dst_node=self.to_vessel,
            src_port=self.from_port,
            dst_port=self.to_port,
            unique=self.unique,
        )
        return True

######################
### chempiler.pump ###
######################

class CSeparatePhases(Step):
    """
    Args:
        lower_phase_vessel (str): Name of vessel to transfer lower phase to.
        lower_phase_port (str): Name of port to transfer lower phase to
        upper_phase_vessel (str): Name of vessel to transfer upper phase to.
        separator_top (str): Name of separator top node in graph.
        separator_bottom (str): Name of separator bottom node in graph.
        dead_volume_target (str): Name of waste vessel to transfer dead
                                    volume between phases to.
    """

    def __init__(
        self,
        lower_phase_vessel: str,
        upper_phase_vessel: str,
        separation_vessel: str,
        dead_volume_target: str,
        lower_phase_port: Optional[str] = None,
        upper_phase_port: Optional[str] = None
    ) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.pump.separate_phases(
            separator_flask=self.separation_vessel,
            lower_phase_target=self.lower_phase_vessel,
            lower_phase_port=self.lower_phase_port,
            upper_phase_target=self.upper_phase_vessel,
            upper_phase_port=self.upper_phase_port,
            dead_volume_target=self.dead_volume_target,
        )
        return True

#########################
### chempiler.stirrer ###
#########################

class CStir(Step):
    """Starts the stirring operation of a hotplate or overhead stirrer.

    Args:
        vessel (str): Vessel name to stir.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.stir(self.vessel)
        return True

class CStirrerHeat(Step):
    """Starts the heating operation of a hotplate stirrer.

    Args:
        vessel (str): Vessel name to heat.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.heat(self.vessel)
        return True

class CStopStir(Step):
    """Stops the stirring operation of a hotplate or overhead stirrer.

    Args:
        vessel (str): Vessel name to stop stirring.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.stop_stir(self.vessel)
        return True

class CStopHeat(Step):
    """Stop heating hotplace stirrer.

    Args:
        vessel (str): Vessel name to stop heating.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.stop_heat(self.vessel)
        return True

class CStirrerSetTemp(Step):
    """Sets the temperature setpoint of a hotplate stirrer. This command is NOT available
    for overhead stirrers!

    Args:
        vessel (str): Vessel name to set temperature of hotplate stirrer.
        temp (float): Temperature in °C
    """
    def __init__(self, vessel: str, temp: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.set_temp(self.vessel, self.temp)
        return True

class CSetStirRate(Step):
    """Sets the stirring speed setpoint of a hotplate or overhead stirrer.

    Args:
        vessel (str): Vessel name to set stir speed.
        stir_rpm (float): Stir speed in RPM.
    """
    def __init__(self, vessel: str, stir_rpm: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.set_stir_rate(self.vessel, self.stir_rpm)
        return True

class CStirrerWaitForTemp(Step):
    """Delays the script execution until the current temperature of the hotplate is within
    0.5 °C of the setpoint. This command is NOT available for overhead stirrers!

    Args:
        vessel (str): Vessel name to wait for temperature.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.stirrer.wait_for_temp(self.vessel)
        return True

#########################
### chempiler.rotavap ###
#########################

# class CStartHeaterBath(Step):
#     """Starts the heating bath of a rotary evaporator.

#     Args:
#         rotavap_name (str): Name of the node representing the rotary evaporator.
#     """
#     def __init__(self, rotavap_name: str) -> None:
#         super().__init__(locals())

#     def execute(self, chempiler, logger=None, level=0):
#         chempiler.rotavap.start_heater(self.rotavap_name)
#         return True

# class CStopHeaterBath(Step):
#     """Stops the heating bath of a rotary evaporator.

#     Args:
#         rotavap_name (str): Name of the node representing the rotary evaporator.
#     """
#     def __init__(self, rotavap_name: str) -> None:
#         super().__init__(locals())

#     def execute(self, chempiler, logger=None, level=0):
#         chempiler.rotavap.stop_heater(self.rotavap_name)
#         return True

# class CStartRotation(Step):
#     """Starts the rotation of a rotary evaporator.

#     Args:
#         rotavap_name (str): Name of the node representing the rotary evaporator.
#     """
#     def __init__(self, rotavap_name: str) -> None:
#         super().__init__(locals())

#     def execute(self, chempiler, logger=None, level=0):
#         chempiler.rotavap.start_rotation(self.rotavap_name)
#         return True

# class CStopRotation(Step):
#     """Stops the rotation of a rotary evaporator.

#     Args:
#         rotavap_name (str): Name of the node representing the rotary evaporator.
#     """
#     def __init__(self, rotavap_name: str) -> None:
#         super().__init__(locals())

#     def execute(self, chempiler, logger=None, level=0):
#         chempiler.rotavap.stop_rotation(self.rotavap_name)
#         return True

# class CLiftArmUp(Step):
#     """Lifts the rotary evaporator arm up.

#     Args:
#         rotavap_name (str): Name of the node representing the rotary evaporator.
#     """
#     def __init__(self, rotavap_name: str) -> None:
#         super().__init__(locals())

#     def execute(self, chempiler, logger=None, level=0):
#         chempiler.rotavap.lift_up(self.rotavap_name)
#         return True

# class CLiftArmDown(Step):
#     """Lifts the rotary evaporator down.

#     Args:
#         rotavap_name (str): Name of the node representing the rotary evaporator.
#     """
#     def __init__(self, rotavap_name: str) -> None:
#         super().__init__(locals())

#     def execute(self, chempiler, logger=None, level=0):
#         chempiler.rotavap.lift_down(self.rotavap_name)
#         return True

# class CResetRotavap(Step):
#     """
#     Resets the rotary evaporator.

#     Args:
#         rotavap_name (str): Name of the node representing the rotary evaporator.
#     """
#     def __init__(self, rotavap_name: str) -> None:
#         super().__init__(locals())

#     def execute(self, chempiler, logger=None, level=0):
#         chempiler.rotavap.reset(self.rotavap_name)
#         return True

# class CSetBathTemp(Step):
#     """Sets the temperature setpoint for the heating bath.

#     Args:
#         rotavap_name (str): Name of the node representing the rotary evaporator.
#         temp (float): Temperature in °C.
#     """
#     def __init__(self, rotavap_name: str, temp: float) -> None:
#         super().__init__(locals())

#     def execute(self, chempiler, logger=None, level=0):
#         chempiler.rotavap.set_temp(self.rotavap_name, self.temp)
#         return True

# class CSetRvRotationSpeed(Step):
#     """Sets the rotation speed setpoint for the rotary evaporator.

#     Args:
#         rotavap_name (str): Name of the node representing the rotary evaporator.
#         rotation_speed (str): Rotation speed setpoint in RPM.
#     """
#     def __init__(self, rotavap_name: str, rotation_speed: float) -> None:
#         super().__init__(locals())

#     def execute(self, chempiler, logger=None, level=0):
#         chempiler.rotavap.set_rotation(self.rotavap_name, self.rotation_speed)
#         return True

# class CRvWaitForTemp(Step):
#     """Delays the script execution until the current temperature of the heating bath is
#     within 0.5°C of the setpoint.

#     Args:
#         rotavap_name (str): Name of the node representing the rotary evaporator.
#     """
#     def __init__(self, rotavap_name: str) -> None:
#         super().__init__(locals())

#     def execute(self, chempiler, logger=None, level=0):
#         chempiler.rotavap.wait_for_temp(self.rotavap_name)
#         return True

# class CSetInterval(Step):
#     """Sets the interval time for the rotary evaporator, causing it to periodically switch
#     direction. Setting this to 0 deactivates interval operation.

#     Args:
#         rotavap_name (str): Name of the node representing the rotary evaporator.
#         interval (int): Interval time in seconds.
#     """
#     def __init__(self, rotavap_name: str, interval: int) -> None:
#         super().__init__(locals())

#     def execute(self, chempiler, logger=None, level=0):
#         chempiler.rotavap.set_interval(self.rotavap_name, self.interval)
#         return True

########################
### chempiler.vacuum ###
########################

class CGetVacuumSetPoint(Step):
    """Reads the current vacuum setpoint.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_vacuum_set_point(self.vessel)
        return True

class CSetVacuumSetPoint(Step):
    """Sets a new vacuum setpoint.

    Args:
        vessel:$ (str): Name of the node the vacuum pump is attached to.
        vacuum_pressure (float): Vacuum pressure setpoint in mbar.
    """
    def __init__(self, vessel: str, vacuum_pressure: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_vacuum_set_point(
            self.vessel, self.vacuum_pressure)
        return True

class CStartVacuum(Step):
    """Starts the vacuum pump.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.start_vacuum(self.vessel)
        return True

class CStopVacuum(Step):
    """Stops the vacuum pump.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.stop_vacuum(self.vessel)
        return True

class CVentVacuum(Step):
    """Vents the vacuum pump to ambient pressure.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.vent_vacuum(self.vessel)
        return True

class CSetSpeedSetPoint(Step):
    """Sets the speed of the vacuum pump (0-100%).

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        vacuum_pump_speed (float): Vacuum pump speed in percent.
    """
    def __init__(self, vessel: str, vacuum_pump_speed: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_speed_set_point(self.vessel, self.set_point)
        return True

class CSetEndVacuumSetPoint(Step):
    """
    Sets the switch off vacuum set point.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        vacuum_set_point (int): Set point value to set vacuum to.
    """
    def __init__(self, vessel: str, vacuum_set_point: int) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_end_vacuum_set_point(
            self.vessel, self.vacuum_set_point)
        return True

class CGetEndVacuumSetPoint(Step):
    """
    Gets the set point (target) for the switch off vacuum in mode Auto.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_end_vacuum_set_point(self.vessel)
        return True

class CSetRuntimeSetPoint(Step):
    """
    Sets the switch off vacuum set point.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
        time (float): Desired runtime.
    """
    def __init__(self, vessel: str, time: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.set_runtime_set_point(self.vessel, self.time)
        return True

class CGetRuntimeSetPoint(Step):
    """
    Gets the set point (target) for the run time in mode Auto.

    Args:
        vessel (str): Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.vacuum.get_runtime_set_point(self.vessel)
        return True


#########################
### chempiler.chiller ###
#########################

class CStartChiller(Step):
    """Starts the recirculation chiller.

    Args:
        vessel (str): Vessel to chill. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.start_chiller(self.vessel)
        return True

class CStopChiller(Step):
    """Stops the recirculation chiller.

    Args:
        vessel (str): Vessel to stop chilling. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.stop_chiller(self.vessel)
        return True

class CChillerSetTemp(Step):
    """Sets the temperature setpoint.

    Args:
        vessel (str): Vessel to set chiller temperature. Name of the node the chiller is attached to.
        temp (float): Temperature in °C.
    """
    def __init__(self, vessel: str, temp: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.set_temp(self.vessel, self.temp)
        return True

class CChillerWaitForTemp(Step):
    """Delays the script execution until the current temperature of the chiller is within
    0.5°C of the setpoint.

    Args:
        vessel (str): Vessel to wait for temperature. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.wait_for_temp(self.vessel)
        return True

class CRampChiller(Step):
    """Causes the chiller to ramp the temperature up or down. Only available for Petite
    Fleur.

    Args:
        vessel (str): Vessel to ramp chiller on. Name of the node the chiller is attached to.
        ramp_duration (int): Desired duration of the ramp in seconds.
        end_temperature (float): Final temperature of the ramp in °C.
    """
    def __init__(
        self,
        vessel: str,
        ramp_duration: int,
        end_temperature: float
    ) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.ramp_chiller(self.vessel, self.ramp_duration, self.end_temperature)
        return True

class CSetCoolingPower(Step):
    """Sets the cooling power (0-100%). Only available for CF41.

    Args:
        vessel (str): Vessel to set cooling power of chiller. Name of the node the chiller is attached to.
        cooling_power (float): Desired cooling power in percent.
    """
    def __init__(self, vessel: str, cooling_power: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.chiller.cooling_power(self.vessel, self.cooling_power)
        return True

class CSetRecordingSpeed(Step):
    """Sets the timelapse speed of the camera module.

    Args:
        recording_speed (float): Factor by which the recording should be sped up, i.e. 2 would mean twice the normal speed. 1 means normal speed.
    """
    def __init__(self, recording_speed: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.camera.change_recording_speed(self.recording_speed)
        return True

class CWait(Step):
    """Delays execution of the script for a set amount of time. This command will
    immediately reply with an estimate of when the waiting will be finished, and also
    give regular updates indicating that it is still alive.

    Args:
        time (int): Time to wait in seconds.
    """
    def __init__(self, time: float) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.wait(self.time)
        return True

class CBreakpoint(Step):
    """Introduces a breakpoint in the script. The execution is halted until the operator
    resumes it.
    """
    def __init__(self) -> None:
        super().__init__(locals())

    def execute(self, chempiler, logger=None, level=0):
        chempiler.breakpoint()
        return True
        