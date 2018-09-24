from .chasmwriter import Chasm
from .constants import *
from .steps_generic import Step

"""
IMPORTANT:
This file is used along with add_getters in dev_utils.py to generate xdllib/steps_chasm.py.
add_getters takes everything in self.properties and creates a getter function for it so
properties can be accessed like step.property instead of step.properties['property'].

When writing code in this file you can assume all keys of self.properties are member variables of
the same name.
"""

### Pump ###

class CMove(Step):
    """
    Moves a specified volume from one node in the graph to another. Moving from and to
    the same node is supported.
    """
    def __init__(self, from_vessel=None, to_vessel=None, volume=None, move_speed='default',
                 aspiration_speed='default', dispense_speed='default', comment=''):
        """
        from_vessel -- Name of the source flask
        to_vessel -- Name of the destination flask
        volume -- Can be a float or "all" in which case it moves the entire current volume
        move_speed -- Speed at which it moves material across the backbone. This argument is optional, if absent, it defaults to 50mL/min
        aspiration_speed -- Speed at which it aspirates from the source. This argument is optional, if absent, it defaults to {move_speed}. It will only be parsed as {aspiration_speed} if a move speed is given (argument is positional)
        dispense_speed -- Speed at which it aspirates from the source. This argument is optional, if absent, it defaults to {move_speed}. It will only be parsed as {aspiration_speed} if a move speed and aspiration speed is given (argument is positional)
        """
        self.name = 'Move'

        self.properties = {
            'from_vessel': from_vessel,
            'to_vessel': to_vessel,
            'volume': volume,
            'move_speed': move_speed,
            'aspiration_speed': aspiration_speed,
            'dispense_speed': dispense_speed,
            'comment': comment
        }
        self.get_defaults()

        self.human_readable = f'Move {from_vessel} ({volume}) to {to_vessel}.'

    def execute(self, chempiler):
        chempiler.pump.move(
            self.from_vessel,
            self.to_vessel,
            self.volume,
            move_speed=self.move_speed,
            aspiration_speed=self.aspiration_speed,
            dispense_speed=self.dispense_speed,
        )

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S MOVE({self.from_vessel}, {self.to_vessel}, {self.volume}, {self.move_speed}, {self.aspiration_speed}, {self.dispense_speed})")
        return chasm.code

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
    def move_speed(self):
        return self.properties['move_speed']

    @property
    def aspiration_speed(self):
        return self.properties['aspiration_speed']

    @property
    def dispense_speed(self):
        return self.properties['dispense_speed']

    @property
    def comment(self):
        return self.properties['comment']

class CSeparate(Step):
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

    def execute(self, chempiler):
        chempiler.pump.separate_phases(
            self.lower_phase_target,
            self.upper_phase_target,
        )

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SEPARATE({self.lower_phase_target}, {self.upper_phase_target})")
        return chasm.code

    @property
    def lower_phase_target(self):
        return self.properties['lower_phase_target']

    @property
    def upper_phase_target(self):
        return self.properties['upper_phase_target']

    @property
    def comment(self):
        return self.properties['comment']

class CPrime(Step):
    """
    Moves the tube volume of every node with "flask" as class to waste.
    """
    def __init__(self, aspiration_speed='default', comment=''):
        """
        aspiration_speed -- Speed in mL/min at which material should be withdrawn.
        """
        self.name = 'Prime'
        self.properties = {
            'aspiration_speed': aspiration_speed,
            'comment': comment
        }
        self.get_defaults()

    def execute(self, chempiler):
        chempiler.pump.prime_tubes(self.aspiration_speed)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S PRIME({self.aspiration_speed})")
        return chasm.code

    @property
    def aspiration_speed(self):
        return self.properties['aspiration_speed']

    @property
    def comment(self):
        return self.properties['comment']

class CSwitchVacuum(Step):
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

    def execute(self, chempiler):
        chempiler.pump.switch_cartridge(self.flask, self.destination)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SWITCH_VACUUM({self.flask}, {self.destination})")
        return chasm.code

    @property
    def flask(self):
        return self.properties['flask']

    @property
    def destination(self):
        return self.properties['destination']

    @property
    def comment(self):
        return self.properties['comment']

class CSwitchCartridge(Step):
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

    def execute(self, chempiler):
        chempiler.pump.switch_cartridge(self.flask, self.cartridge)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SWITCH_CARTRIDGE({self.flask}, {self.cartridge})")
        return chasm.code

    @property
    def flask(self):
        return self.properties['flask']

    @property
    def cartridge(self):
        return self.properties['cartridge']

    @property
    def comment(self):
        return self.properties['comment']

class CSwitchColumn(Step):
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

    def execute(self, chempiler):
        chempiler.pump.switch_column_fraction(self.column, self.destination)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SWITCH_COLUMN({self.column}, {self.destination})")
        return chasm.code

### Stirrer ###

    @property
    def column(self):
        return self.properties['column']

    @property
    def destination(self):
        return self.properties['destination']

    @property
    def comment(self):
        return self.properties['comment']

class CStartStir(Step):
    """
    Starts the stirring operation of a hotplate or overhead stirrer.
    """
    def __init__(self, vessel=None, comment=''):
        """
        vessel -- Name of the node the device is attached to.
        """
        self.name = 'StartStir'
        self.properties = {
            'vessel': vessel,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.stirrer.stir(self.vessel)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_STIR({self.vessel})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class CStartHeat(Step):
    """
    Starts the stirring operation of a hotplate stirrer. This command is NOT available
    for overhead stirrers!
    """
    def __init__(self, vessel=None, comment=''):
        """
        vessel -- Name of the node the device is attached to.
        """
        self.name = 'StartHeat'
        self.properties = {
            'vessel': vessel,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.stirrer.heat(self.vessel)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_HEAT({self.vessel})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class CStopStir(Step):
    """
    Stops the stirring operation of a hotplate or overhead stirrer.
    """
    def __init__(self, vessel=None, comment=''):
        """
        vessel -- Name of the node the device is attached to.
        """
        self.name = 'StopStir'
        self.properties = {
            'vessel': vessel,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.stirrer.stop_stir(self.vessel)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_STIR({self.vessel})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class CStopHeat(Step):
    """
    Starts the stirring operation of a hotplate stirrer. This command is NOT available
    for overhead stirrers!
    """
    def __init__(self, vessel=None, comment=''):
        """
        vessel -- Name of the node the device is attached to.
        """
        self.name = 'StopHeat'
        self.properties = {
            'vessel': vessel,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.stop_heat(self.vessel)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_HEAT({self.vessel})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class CSetTemp(Step):
    """
    Sets the temperature setpoint of a hotplate stirrer. This command is NOT available
    for overhead stirrers!
    """
    def __init__(self, vessel=None, temp=None, comment=''):
        """
        vessel -- Name of the node the device is attached to.
        temp -- Required temperature in °C
        """
        self.name = 'SetTemp'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.stirrer.set_temp(self.vessel, self.temp)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_TEMP({self.vessel}, {self.temp})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def temp(self):
        return self.properties['temp']

    @property
    def comment(self):
        return self.properties['comment']

class CSetStirRpm(Step):
    """
    Sets the stirring speed setpoint of a hotplate or overhead stirrer.
    """
    def __init__(self, vessel=None, stir_rpm=None, comment=''):
        """
        vessel -- Name of the node the device is attached to.
        rpm -- Speed setpoint in rpm.
        """
        self.name = 'SetStirRpm'
        self.properties = {
            'vessel': vessel,
            'stir_rpm': stir_rpm,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.stirrer.set_stir_rate(self.vessel, self.stir_rpm)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_STIR_RPM({self.vessel}, {self.stir_rpm})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def stir_rpm(self):
        return self.properties['stir_rpm']

    @property
    def comment(self):
        return self.properties['comment']

class CStirrerWaitForTemp(Step):
    """
    Delays the script execution until the current temperature of the hotplate is within
    0.5°C of the setpoint. This command is NOT available for overhead stirrers!
    """
    def __init__(self, vessel=None, comment=''):
        """
        vessel -- Name of the node the device is attached to.
        """
        self.name = 'StirrerWaitForTemp'
        self.properties = {
            'vessel': vessel,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.stirrer.wait_for_temp(self.vessel)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STIRRER_WAIT_FOR_TEMP({self.vessel})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class CStartHeaterBath(Step):
    """
    Starts the heating bath of a rotary evaporator.
    """
    def __init__(self, rotavap_name=None, comment=''):
        """
        rotavap_name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'StartHeaterBath'
        self.properties = {
            'rotavap_name': rotavap_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.rotavap.start_heater(self.rotavap_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_HEATER_BATH({self.rotavap_name})")
        return chasm.code

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @property
    def comment(self):
        return self.properties['comment']

class CStopHeaterBath(Step):
    """
    Stops the heating bath of a rotary evaporator.
    """
    def __init__(self, rotavap_name=None, comment=''):
        """
        rotavap_name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'StopHeaterBath'
        self.properties = {
            'rotavap_name': rotavap_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.rotavap.stop_heater(self.rotavap_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_HEATER_BATH({self.rotavap_name})")
        return chasm.code

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @property
    def comment(self):
        return self.properties['comment']

class CStartRotation(Step):
    """
    Starts the rotation of a rotary evaporator.
    """
    def __init__(self, rotavap_name=None, comment=''):
        """
        rotavap_name -- Name of the node representing the rotary evaporator.
        """
        self.vessel = 'StartRotation'
        self.properties = {
            'rotavap_name': rotavap_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.rotavap.start_rotation(self.rotavap_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_ROTATION({self.rotavap_name})")
        return chasm.code

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @property
    def comment(self):
        return self.properties['comment']

class CStopRotation(Step):
    """
    Stops the rotation of a rotary evaporator.
    """
    def __init__(self, rotavap_name=None, comment=''):
        """
        rotavap_name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'StopRotation'
        self.properties = {
            'rotavap_name': rotavap_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.rotavap.stop_rotation(self.rotavap_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_ROTATION({self.rotavap_name})")
        return chasm.code

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @property
    def comment(self):
        return self.properties['comment']

class CLiftArmUp(Step):
    """
    Lifts the rotary evaporator up.
    """
    def __init__(self, rotavap_name=None, comment=''):
        """
        rotavap_name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'LiftArmUp'
        self.properties = {
            'rotavap_name': rotavap_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.rotavap.lift_up(self.rotavap_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S LIFT_ARM_UP({self.rotavap_name})")
        return chasm.code

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @property
    def comment(self):
        return self.properties['comment']

class CLiftArmDown(Step):
    """
    Lifts the rotary evaporator down.
    """
    def __init__(self, rotavap_name=None, comment=''):
        """
        name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'LiftArmDown'
        self.properties = {
            'rotavap_name': rotavap_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.rotavap.lift_down(self.rotavap_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S LIFT_ARM_DOWN({self.rotavap_name})")
        return chasm.code

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @property
    def comment(self):
        return self.properties['comment']

class CResetRotavap(Step):
    """
    Resets the rotary evaporator.
    """
    def __init__(self, rotavap_name=None, comment=''):
        """
        rotavap_name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'ResetRotavap'
        self.properties = {
            'rotavap_name': rotavap_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.rotavap.reset(self.rotavap_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S RESET_ROTAVAP({self.rotavap_name})")
        return chasm.code

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @property
    def comment(self):
        return self.properties['comment']

class CSetBathTemp(Step):
    """
    Sets the temperature setpoint for the heating bath.
    """
    def __init__(self, rotavap_name=None, temp=None, comment=''):
        """
        rotavap_name -- Name of the node representing the rotary evaporator.
        temp -- Temperature setpoint in °C.
        """
        self.name = 'SetBathTemp'
        self.properties = {
            'rotavap_name': rotavap_name,
            'temp': temp,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.rotavap.set_temp(self.rotavap_name, self.temp)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_BATH_TEMP({self.rotavap_name}, {self.temp})")
        return chasm.code

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @property
    def temp(self):
        return self.properties['temp']

    @property
    def comment(self):
        return self.properties['comment']

class CSetRvRotationSpeed(Step):
    """
    Sets the rotation speed setpoint for the rotary evaporator.
    """
    def __init__(self, rotavap_name=None, rotation_speed=None, comment=''):
        """
        rotavap_name -- Name of the node representing the rotary evaporator.
        rotation_speed -- Speed setpoint in rpm.
        """
        self.name = 'SetRvRotationSpeed'
        self.properties = {
            'rotavap_name': rotavap_name,
            'rotation_speed': rotation_speed,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.rotavap.set_rotation(self.rotavap_name, self.rotation_speed)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_ROTATION({self.rotavap_name}, {self.rotation_speed})")
        return chasm.code

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @property
    def rotation_speed(self):
        return self.properties['rotation_speed']

    @property
    def comment(self):
        return self.properties['comment']

class CRvWaitForTemp(Step):
    """
    Delays the script execution until the current temperature of the heating bath is
    within 0.5°C of the setpoint.
    """
    def __init__(self, rotavap_name=None, comment=''):
        """
        rotavap_name -- Name of the node representing the rotary evaporator.
        """
        self.name = 'RvWaitForTemp'
        self.properties = {
            'rotavap_name': rotavap_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.rotavap.wait_for_temp(self.rotavap_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S RV_WAIT_FOR_TEMP({self.rotavap_name})")
        return chasm.code

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @property
    def comment(self):
        return self.properties['comment']

class CSetInterval(Step):
    """
    Sets the interval time for the rotary evaporator, causing it to periodically switch
    direction. Setting this to 0 deactivates interval operation.
    """
    def __init__(self, rotavap_name=None, interval=None, comment=''):
        """
        rotavap_name -- Name of the node representing the rotary evaporator.
        interval -- Interval time in seconds.
        """
        self.name = 'SetInterval'
        self.properties = {
            'rotavap_name': rotavap_name,
            'interval': interval,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.rotavap.set_interval(self.rotavap_name, self.interval)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_INTERVAL({self.rotavap_name}, {self.interval})")
        return chasm.code

### Vacuum Pump ###

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @property
    def interval(self):
        return self.properties['interval']

    @property
    def comment(self):
        return self.properties['comment']

class CInitVacPump(Step):
    """
    Initialises the vacuum pump controller.
    """
    def __init__(self, vacuum_pump_name=None, comment=''):
        """
        vacuum_pump_name -- Name of the node the vacuum pump is attached to.
        """
        self.name = 'InitVacPump'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.vacuum.initialise(self.vacuum_pump_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S INIT_VAC_PUMP({self.vacuum_pump_name})")
        return chasm.code

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @property
    def comment(self):
        return self.properties['comment']

class CGetVacSp(Step):
    """
    Reads the current vacuum setpoint.
    """
    def __init__(self, vacuum_pump_name=None, comment=''):
        """
        vacuum_pump_name -- Name of the node the vacuum pump is attached to.
        """
        self.name = 'GetVacSp'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.vacuum.get_vacuum_set_point(self.vacuum_pump_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S GET_VAC_SP({self.vacuum_pump_name})")
        return chasm.code

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @property
    def comment(self):
        return self.properties['comment']

class CSetVacSp(Step):
    """
    Sets a new vacuum setpoint.
    """
    def __init__(self, vacuum_pump_name=None, set_point=None, comment=''):
        """
        vacuum_pump_name -- Name of the node the vacuum pump is attached to.
        set_point -- Vacuum setpoint in mbar.
        """
        self.name = 'SetVacSp'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
            'set_point': set_point,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.vacuum.set_vacuum_set_point(self.vacuum_pump_name, self.set_point)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_VAC_SP({self.vacuum_pump_name}, {self.set_point})")
        return chasm.code

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @property
    def set_point(self):
        return self.properties['set_point']

    @property
    def comment(self):
        return self.properties['comment']

class CStartVac(Step):
    """
    Starts the vacuum pump.
    """
    def __init__(self, vacuum_pump_name=None, comment=''):
        """
        vacuum_pump_name -- Name of the node the vacuum pump is attached to.
        """
        self.name = 'StartVac'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.vacuum.start_vacuum(self.vacuum_pump_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_VAC({self.vacuum_pump_name})")
        return chasm.code

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @property
    def comment(self):
        return self.properties['comment']

class CStopVac(Step):
    """
    Stops the vacuum pump.
    """
    def __init__(self, vacuum_pump_name=None, comment=''):
        """
        vacuum_pump_name -- Name of the node the vacuum pump is attached to.
        """
        self.name = 'StopVac'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.vacuum.stop_vacuum(self.vacuum_pump_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_VAC({self.vacuum_pump_name})")
        return chasm.code

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @property
    def comment(self):
        return self.properties['comment']

class CVentVac(Step):
    """
    Vents the vacuum pump to ambient pressure.
    """
    def __init__(self, vacuum_pump_name=None, comment=''):
        """
        vacuum_pump_name -- Name of the node the vacuum pump is attached to.
        """
        self.name = 'VentVac'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.vacuum.vent_vacuum(self.vacuum_pump_name)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S VENT_VAC({self.vacuum_pump_name})")
        return chasm.code

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @property
    def comment(self):
        return self.properties['comment']

class CSetSpeedSp(Step):
    """
    Sets the speed of the vacuum pump (0-100%).
    """
    def __init__(self, vacuum_pump_name=None, set_point=None, comment=''):
        """
        vacuum_pump_name -- Name of the node the vacuum pump is attached to.
        set_point -- Vacuum pump speed in percent.
        """
        self.name = 'SetSpeedSp'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
            'set_point': set_point,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.vacuum.set_speed_set_point(self.vacuum_pump_name, self.set_point)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_SPEED_SP({self.vacuum_pump_name}, {self.set_point})")
        return chasm.code

### Chiller ###

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @property
    def set_point(self):
        return self.properties['set_point']

    @property
    def comment(self):
        return self.properties['comment']

class CStartChiller(Step):
    """
    Starts the recirculation chiller.
    """
    def __init__(self, vessel=None, comment=''):
        """
        vessel -- Name of the node the chiller is attached to.
        """
        self.name = 'StartChiller'
        self.properties = {
            'vessel': vessel,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.chiller.start_chiller(self.vessel)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S START_CHILLER({self.vessel})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class CStopChiller(Step):
    """
    Stops the recirculation chiller.
    """
    def __init__(self, vessel=None, comment=''):
        """
        vessel -- Name of the node the chiller is attached to.
        """
        self.name = 'StopChiller'
        self.properties = {
            'vessel': vessel,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.chiller.stop_chiller(self.vessel)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S STOP_CHILLER({self.vessel})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class CSetChiller(Step):
    """
    Sets the temperature setpoint.
    """
    def __init__(self, vessel=None, temp=None, comment=''):
        """
        vessel -- Name of the node the chiller is attached to.
        temp -- Temperature in °C.
        """
        self.name = 'SetChiller'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.chiller.set_temp(self.vessel, self.temp)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_CHILLER({self.vessel}, {self.temp})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def temp(self):
        return self.properties['temp']

    @property
    def comment(self):
        return self.properties['comment']

class CChillerWaitForTemp(Step):
    """
    Delays the script execution until the current temperature of the chiller is within
    0.5°C of the setpoint.
    """
    def __init__(self, vessel=None, comment=''):
        """
        vessel -- Name of the node the chiller is attached to.
        """
        self.name = 'ChillerWaitForTemp'
        self.properties = {
            'vessel': vessel,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.chiller.wait_for_temp(self.vessel)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S CHILLER_WAIT_FOR_TEMP({self.vessel})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def comment(self):
        return self.properties['comment']

class CRampChiller(Step):
    """
    Causes the chiller to ramp the temperature up or down. Only available for Petite
    Fleur.
    """
    def __init__(self, vessel=None, ramp_duration=None, end_temperature=None, comment=''):
        """
        vessel -- Name of the node the chiller is attached to.
        ramp_duration -- Desired duration of the ramp in seconds.
        end_temperature -- Final temperature of the ramp in °C.
        """
        self.name = 'RampChiller'
        self.properties = {
            'vessel': vessel,
            'ramp_duration': ramp_duration,
            'end_temperature': end_temperature,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.chiller.ramp_chiller(self.vessel, self.ramp_duration, self.end_temperature)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S RAMP_CHILLER({self.vessel}, {self.ramp_duration}, {self.end_temperature})")
        return chasm.code

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def ramp_duration(self):
        return self.properties['ramp_duration']

    @property
    def end_temperature(self):
        return self.properties['end_temperature']

    @property
    def comment(self):
        return self.properties['comment']

class CSwitchChiller(Step):
    """
    Switches the solenoid valve.
    """
    def __init__(self, solenoid_valve_name=None, state=None, comment=''):
        """
        solenoid_valve_name -- Name of the node the solenoid valve is attached to.
        state -- Is either "on" or "off"
        """
        self.name = 'SwitchChiller'
        self.properties = {
            'solenoid_valve_name': solenoid_valve_name,
            'state': state,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.chiller.switch_vessel(self.solenoid_valve_name, self.state)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SWITCH_CHILLER({self.solenoid_valve_name}, {self.state})")
        return chasm.code

    @property
    def solenoid_valve_name(self):
        return self.properties['solenoid_valve_name']

    @property
    def state(self):
        return self.properties['state']

    @property
    def comment(self):
        return self.properties['comment']

class CSetCoolingPower(Step):
    """
    Sets the cooling power (0-100%). Only available for CF41.
    """
    def __init__(self, vessel=None, cooling_power=None, comment=''):
        """
        name -- Name of the node the chiller is attached to.
        cooling_power -- Desired cooling power in percent.
        """
        self.name = 'SetCoolingPower'
        self.properties = {
            'vessel': vessel,
            'cooling_power': cooling_power,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.chiller.cooling_power(self.vessel, self.cooling_power)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_COOLING_POWER({self.vessel}, {self.cooling_power})")
        return chasm.code

### Camera ###

    @property
    def vessel(self):
        return self.properties['vessel']

    @property
    def cooling_power(self):
        return self.properties['cooling_power']

    @property
    def comment(self):
        return self.properties['comment']

class CSetRecordingSpeed(Step):
    """
    Sets the timelapse speed of the camera module.
    """
    def __init__(self, recording_speed=None, comment=''):
        """
        speed -- Factor by which the recording should be sped up, i.e. 2 would mean twice the normal speed. 1 means normal speed.
        """
        self.name = 'SetRecordingSpeed'
        self.properties = {
            'recording_speed': recording_speed,
            'comment': comment
        }

    def execute(self, chempiler):
        chempiler.camera.change_recording_speed(self.recording_speed)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S SET_RECORDING_SPEED({self.recording_speed})")
        return chasm.code

    @property
    def recording_speed(self):
        return self.properties['recording_speed']

    @property
    def comment(self):
        return self.properties['comment']

class CWait(Step):
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

    def execute(self, chempiler):
        chempiler.wait(self.time)

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S WAIT({self.time})")
        return chasm.code

    @property
    def time(self):
        return self.properties['time']

    @property
    def comment(self):
        return self.properties['comment']

class CBreakpoint(Step):
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

    def execute(self, chempiler):
        chempiler.breakpoint()

    def as_chasm(self):
        """Return step as ChASM code (str)."""
        chasm = self.get_chasm_stub()
        chasm.add_line(f"S BREAKPOINT()")
        return chasm.code