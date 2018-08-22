from chasmwriter import Chasm
from constants import *
from steps_generic import Step

class Move(Step):
    """
    Moves a specified volume from one node in the graph to another. Moving from and to
    the same node is supported.
    """
    def __init__(self, src=None, dest=None, volume=None, move_speed=20, aspiration_speed=20, dispense_speed=20, comment=''):
        """
        src -- Name of the source flask
        dest -- Name of the destination flask
        volume -- Can be a float or "all" in which case it moves the entire current volume
        move_speed -- Speed at which it moves material across the backbone. This argument is optional, if absent, it defaults to 50mL/min
        aspiration_speed -- Speed at which it aspirates from the source. This argument is optional, if absent, it defaults to {move_speed}. It will only be parsed as {aspiration_speed} if a move speed is given (argument is positional)
        dispense_speed -- Speed at which it aspirates from the source. This argument is optional, if absent, it defaults to {move_speed}. It will only be parsed as {aspiration_speed} if a move speed and aspiration speed is given (argument is positional)
        """
        self.name = 'Move'
        self.properties = {
            'src': src,
            'dest': dest,
            'volume': volume,
            'move_speed': move_speed,
            'aspiration_speed': aspiration_speed,
            'dispense_speed': dispense_speed,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S MOVE({self.properties['src']}, {self.properties['dest']}, {self.properties['volume']}, {self.properties['move_speed']}, {self.properties['aspiration_speed']}, {self.properties['dispense_speed']})")
        return chasm.code

class Home(Step):
    """
    Moves a given pump to home.
    """
    def __init__(self, pump_name=None, move_speed=20, comment=''):
        """
        pump_name -- Name of the pump to be homed.
        move_speed -- Requested speed in mL/min.
        """
        self.name = 'Home'
        self.properties = {
            'pump_name': pump_name,
            'move_speed': move_speed,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S HOME({self.properties['pump_name']}, {self.properties['move_speed']})")
        return chasm.code

class Separate(Step):
    """
    Launches a phase separation sequence. The name of the separator is currently
    hard-coded!
    """
    def __init__(self, lower_phase_target=None, upper_phase_target=None, comment=''):
        """
        lower_phase_target -- Name of the flask the lower phase should be transferred to.
        upper_phase_target -- Name of the flask the upper phase should be transferred to. If "separator_top" is specified, the upper phase is left in the separator.
        """
        self.name = 'Separate'
        self.properties = {
            'lower_phase_target': lower_phase_target,
            'upper_phase_target': upper_phase_target,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SEPARATE({self.properties['lower_phase_target']}, {self.properties['upper_phase_target']})")
        return chasm.code

class Prime(Step):
    """
    Moves the tube volume of every node with "flask" as class to waste.
    """
    def __init__(self, aspiration_speed=20, comment=''):
        """
        aspiration_speed -- Speed in mL/min at which material should be withdrawn.
        """
        self.name = 'Prime'
        self.properties = {
            'aspiration_speed': aspiration_speed,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S PRIME({self.properties['aspiration_speed']})")
        return chasm.code

class SwitchVacuum(Step):
    """
    Switches a vacuum valve between backbone and vacuum.
    """
    def __init__(self, flask=None, destination=None, comment=''):
        """
        flask -- Name of the node the vacuum valve is logically attacked to (e.g. "filter_bottom")
        destination -- Either "vacuum" or "backbone"
        """
        self.name = 'SwitchVacuum'
        self.properties = {
            'flask': flask,
            'destination': destination,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SWITCH_VACUUM({self.properties['flask']}, {self.properties['destination']})")
        return chasm.code

class SwitchCartridge(Step):
    """
    Switches a cartridge carousel to the specified position.
    """
    def __init__(self, flask=None, cartridge=None, comment=''):
        """
        flask -- Name of the node the vacuum valve is logically attacked to (e.g. "rotavap")
        cartridge -- Number of the position the carousel should be switched to (0-5)
        """
        self.name = 'SwitchCartridge'
        self.properties = {
            'flask': flask,
            'cartridge': cartridge,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SWITCH_CARTRIDGE({self.properties['flask']}, {self.properties['cartridge']})")
        return chasm.code

class SwitchColumn(Step):
    """
    Switches a fractionating valve attached to a chromatography column.
    """
    def __init__(self, column=None, destination=None, comment=''):
        """
        column -- Name of the column in the graph
        destination -- Either "collect" or "waste"
        """
        self.name = 'SwitchColumn'
        self.properties = {
            'column': column,
            'destination': destination,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SWITCH_COLUMN({self.properties['column']}, {self.properties['destination']})")
        return chasm.code

class StartStir(Step):
    """
    Starts the stirring operation of a hotplate or overhead stirrer.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the device is attached to.
        """
        self.name = 'StartStir'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_STIR({self.properties['name']})")
        return chasm.code

class StartHeat(Step):
    """
    Starts the stirring operation of a hotplate stirrer. This command is NOT available
    for overhead stirrers!
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the device is attached to.
        """
        self.name = 'StartHeat'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_HEAT({self.properties['name']})")
        return chasm.code

class StopStir(Step):
    """
    Stops the stirring operation of a hotplate or overhead stirrer.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the device is attached to.
        """
        self.name = 'StopStir'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_STIR({self.properties['name']})")
        return chasm.code

class StopHeat(Step):
    """
    Starts the stirring operation of a hotplate stirrer. This command is NOT available
    for overhead stirrers!
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the device is attached to.
        """
        self.name = 'StopHeat'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_HEAT({self.properties['name']})")
        return chasm.code

class SetTemp(Step):
    """
    Sets the temperature setpoint of a hotplate stirrer. This command is NOT available
    for overhead stirrers!
    """
    def __init__(self, name=None, temp=None, comment=''):
        """
        name -- Name of the node the device is attached to.
        temp -- Required temperature in °C
        """
        self.name = 'SetTemp'
        self.properties = {
            'name': name,
            'temp': temp,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_TEMP({self.properties['name']}, {self.properties['temp']})")
        return chasm.code

class SetStirRpm(Step):
    """
    Sets the stirring speed setpoint of a hotplate or overhead stirrer.
    """
    def __init__(self, name=None, rpm=None, comment=''):
        """
        name -- Name of the node the device is attached to.
        rpm -- Speed setpoint in rpm.
        """
        self.name = 'SetStirRpm'
        self.properties = {
            'name': name,
            'rpm': rpm,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_STIR_RPM({self.properties['name']}, {self.properties['rpm']})")
        return chasm.code

class StirrerWaitForTemp(Step):
    """
    Delays the script execution until the current temperature of the hotplate is within
    0.5°C of the setpoint. This command is NOT available for overhead stirrers!
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the device is attached to.
        """
        self.name = 'StirrerWaitForTemp'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STIRRER_WAIT_FOR_TEMP({self.properties['name']})")
        return chasm.code

class StartHeaterBath(Step):
    """
    Starts the heating bath of a rotary evaporator.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'StartHeaterBath'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_HEATER_BATH({self.properties['name']})")
        return chasm.code

class StopHeaterBath(Step):
    """
    Stops the heating bath of a rotary evaporator.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'StopHeaterBath'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_HEATER_BATH({self.properties['name']})")
        return chasm.code

class StartRotation(Step):
    """
    Starts the rotation of a rotary evaporator.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'StartRotation'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_ROTATION({self.properties['name']})")
        return chasm.code

class StopRotation(Step):
    """
    Stops the rotation of a rotary evaporator.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'StopRotation'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_ROTATION({self.properties['name']})")
        return chasm.code

class LiftArmUp(Step):
    """
    Lifts the rotary evaporator up.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'LiftArmUp'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S LIFT_ARM_UP({self.properties['name']})")
        return chasm.code

class LiftArmDown(Step):
    """
    Lifts the rotary evaporator down.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'LiftArmDown'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S LIFT_ARM_DOWN({self.properties['name']})")
        return chasm.code

class ResetRotavap(Step):
    """
    Resets the rotary evaporator.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'ResetRotavap'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S RESET_ROTAVAP({self.properties['name']})")
        return chasm.code

class SetBathTemp(Step):
    """
    Sets the temperature setpoint for the heating bath.
    """
    def __init__(self, name=None, temp=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        temp -- Temperature setpoint in °C.
        """
        self.name = 'SetBathTemp'
        self.properties = {
            'name': name,
            'temp': temp,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_BATH_TEMP({self.properties['name']}, {self.properties['temp']})")
        return chasm.code

class SetRotation(Step):
    """
    Sets the rotation speed setpoint for the rotary evaporator.
    """
    def __init__(self, name=None, rotation=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        rotation -- Speed setpoint in rpm.
        """
        self.name = 'SetRotation'
        self.properties = {
            'name': name,
            'rotation': rotation,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_ROTATION({self.properties['name']}, {self.properties['rotation']})")
        return chasm.code

class RvWaitForTemp(Step):
    """
    Delays the script execution until the current temperature of the heating bath is
    within 0.5°C of the setpoint.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'RvWaitForTemp'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S RV_WAIT_FOR_TEMP({self.properties['name']})")
        return chasm.code

class SetInterval(Step):
    """
    Sets the interval time for the rotary evaporator, causing it to periodically switch
    direction. Setting this to 0 deactivates interval operation.
    """
    def __init__(self, name=None, interval=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        interval -- Interval time in seconds.
        """
        self.name = 'SetInterval'
        self.properties = {
            'name': name,
            'interval': interval,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_INTERVAL({self.properties['name']}, {self.properties['interval']})")
        return chasm.code

class InitVacPump(Step):
    """
    Initialises the vacuum pump controller.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the vacuum pump is attached to.
        """
        self.name = 'InitVacPump'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S INIT_VAC_PUMP({self.properties['name']})")
        return chasm.code

class GetVacSp(Step):
    """
    Reads the current vacuum setpoint.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the vacuum pump is attached to.
        """
        self.name = 'GetVacSp'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S GET_VAC_SP({self.properties['name']})")
        return chasm.code

class SetVacSp(Step):
    """
    Sets a new vacuum setpoint.
    """
    def __init__(self, name=None, set_point=None, comment=''):
        """
        name -- Name of the node the vacuum pump is attached to.
        set_point -- Vacuum setpoint in mbar.
        """
        self.name = 'SetVacSp'
        self.properties = {
            'name': name,
            'set_point': set_point,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_VAC_SP({self.properties['name']}, {self.properties['set_point']})")
        return chasm.code

class StartVac(Step):
    """
    Starts the vacuum pump.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the vacuum pump is attached to.
        """
        self.name = 'StartVac'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_VAC({self.properties['name']})")
        return chasm.code

class StopVac(Step):
    """
    Stops the vacuum pump.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the vacuum pump is attached to.
        """
        self.name = 'StopVac'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_VAC({self.properties['name']})")
        return chasm.code

class VentVac(Step):
    """
    Vents the vacuum pump to ambient pressure.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the vacuum pump is attached to.
        """
        self.name = 'VentVac'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S VENT_VAC({self.properties['name']})")
        return chasm.code

class SetSpeedSp(Step):
    """
    Sets the speed of the vacuum pump (0-100%).
    """
    def __init__(self, name=None, set_point=None, comment=''):
        """
        name -- Name of the node the vacuum pump is attached to.
        set_point -- Vacuum pump speed in percent.
        """
        self.name = 'SetSpeedSp'
        self.properties = {
            'name': name,
            'set_point': set_point,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_SPEED_SP({self.properties['name']}, {self.properties['set_point']})")
        return chasm.code

class StartChiller(Step):
    """
    Starts the recirculation chiller.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the chiller is attached to.
        """
        self.name = 'StartChiller'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_CHILLER({self.properties['name']})")
        return chasm.code

class StopChiller(Step):
    """
    Stops the recirculation chiller.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the chiller is attached to.
        """
        self.name = 'StopChiller'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_CHILLER({self.properties['name']})")
        return chasm.code

class SetChiller(Step):
    """
    Sets the temperature setpoint.
    """
    def __init__(self, name=None, setpoint=None, comment=''):
        """
        name -- Name of the node the chiller is attached to.
        setpoint -- Temperature setpoint in °C.
        """
        self.name = 'SetChiller'
        self.properties = {
            'name': name,
            'setpoint': setpoint,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_CHILLER({self.properties['name']}, {self.properties['setpoint']})")
        return chasm.code

class ChillerWaitForTemp(Step):
    """
    Delays the script execution until the current temperature of the chiller is within
    0.5°C of the setpoint.
    """
    def __init__(self, name=None, comment=''):
        """
        name -- Name of the node the chiller is attached to.
        """
        self.name = 'ChillerWaitForTemp'
        self.properties = {
            'name': name,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S CHILLER_WAIT_FOR_TEMP({self.properties['name']})")
        return chasm.code

class RampChiller(Step):
    """
    Causes the chiller to ramp the temperature up or down. Only available for Petite
    Fleur.
    """
    def __init__(self, name=None, ramp_duration=None, end_temperature=None, comment=''):
        """
        name -- Name of the node the chiller is attached to.
        ramp_duration -- Desired duration of the ramp in seconds.
        end_temperature -- Final temperature of the ramp in °C.
        """
        self.name = 'RampChiller'
        self.properties = {
            'name': name,
            'ramp_duration': ramp_duration,
            'end_temperature': end_temperature,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S RAMP_CHILLER({self.properties['name']}, {self.properties['ramp_duration']}, {self.properties['end_temperature']})")
        return chasm.code

class SwitchChiller(Step):
    """
    Switches the solenoid valve.
    """
    def __init__(self, name=None, state=None, comment=''):
        """
        name -- Name of the node the solenoid valve is attached to.
        state -- Is either "on" or "off"
        """
        self.name = 'SwitchChiller'
        self.properties = {
            'name': name,
            'state': state,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SWITCH_CHILLER({self.properties['name']}, {self.properties['state']})")
        return chasm.code

class SetCoolingPower(Step):
    """
    Sets the cooling power (0-100%). Only available for CF41.
    """
    def __init__(self, name=None, cooling_power=None, comment=''):
        """
        name -- Name of the node the chiller is attached to.
        cooling_power -- Desired cooling power in percent.
        """
        self.name = 'SetCoolingPower'
        self.properties = {
            'name': name,
            'cooling_power': cooling_power,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_COOLING_POWER({self.properties['name']}, {self.properties['cooling_power']})")
        return chasm.code

class SetRecordingSpeed(Step):
    """
    Sets the timelapse speed of the camera module.
    """
    def __init__(self, speed=None, comment=''):
        """
        speed -- Factor by which the recording should be sped up, i.e. 2 would mean twice the normal speed. 1 means normal speed.
        """
        self.name = 'SetRecordingSpeed'
        self.properties = {
            'speed': speed,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_RECORDING_SPEED({self.properties['speed']})")
        return chasm.code

class Wait(Step):
    """
    Delays execution of the script for a set amount of time. This command will
    immediately reply with an estimate of when the waiting will be finished, and also
    give regular updates indicating that it is still alive.
    """
    def __init__(self, time=None, comment=''):
        """
        time -- Wait time in seconds.
        """
        self.name = 'Wait'
        self.properties = {
            'time': time,
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S WAIT({self.properties['time']})")
        return chasm.code

class Breakpoint(Step):
    """
    Introduces a breakpoint in the script. The execution is halted until the operator
    resumes it.
    """
    def __init__(self, comment=''):
        """
         -- Breakpoints take no arguments.
        """
        self.name = 'Breakpoint'
        self.properties = {
            'comment': comment
        }

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S BREAKPOINT()")
        return chasm.code

