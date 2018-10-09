from ..constants import *
from ..utils import Step

"""
IMPORTANT:
All getters and setters are generated when setup.py is run. Don't bother writing them here.
"""

class CMove(Step):
    """Moves a specified volume from one node in the graph to another. Moving from and to
    the same node is supported.

    Keyword Arguments:
        from_vessel {str} -- Vessel name to move from.
        to_vessel {str} -- Vessel name to move to.
        volume {float} -- Volume to move in mL. 'all' moves everything.
        move_speed -- Speed at which liquid is moved in mL / min. (optional)
        aspiration_speed -- Speed at which liquid aspirates from from_vessel. (optional)
        dispense_speed -- Speed at which liquid dispenses from from_vessel. (optional)
    """
    def __init__(self, from_vessel=None, to_vessel=None, volume=None, move_speed='default',
                 aspiration_speed='default', dispense_speed='default'):

        self.name = 'Move'
        self.properties = {
            'from_vessel': from_vessel,
            'to_vessel': to_vessel,
            'volume': volume,
            'move_speed': move_speed,
            'aspiration_speed': aspiration_speed,
            'dispense_speed': dispense_speed,
        }
        self.get_defaults()

        self.human_readable = f'Move {from_vessel} ({volume}) to {to_vessel}.'

        self.literal_code = f'chempiler.pump.move( {self.from_vessel}, {self.to_vessel}, {self.volume}, move_speed={self.move_speed}, aspiration_speed={self.aspiration_speed}, dispense_speed={self.dispense_speed}, )'

    def execute(self, chempiler):
        chempiler.pump.move(
            self.from_vessel,
            self.to_vessel,
            self.volume,
            move_speed=self.move_speed,
            aspiration_speed=self.aspiration_speed,
            dispense_speed=self.dispense_speed,
        )
        return True

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
    def move_speed(self):
        return self.properties['move_speed']

    @move_speed.setter
    def move_speed(self, val):
        self.properties['move_speed'] = val
        self.update()

    @property
    def aspiration_speed(self):
        return self.properties['aspiration_speed']

    @aspiration_speed.setter
    def aspiration_speed(self, val):
        self.properties['aspiration_speed'] = val
        self.update()

    @property
    def dispense_speed(self):
        return self.properties['dispense_speed']

    @dispense_speed.setter
    def dispense_speed(self, val):
        self.properties['dispense_speed'] = val
        self.update()

class CSeparate(Step):
    """Launches a phase separation sequence. The name of the separator is currently
    hard-coded in the Chempiler!

    Keywords Arguments:
        lower_phase_vessel {str} -- Vessel name the lower phase should be transferred to.
        upper_phase_vessel {str} -- Vessel name the upper phase should be transferred to.
                            If "separator_top" is specified, the upper phase is left in the separator.
    """
    def __init__(self, lower_phase_vessel=None, upper_phase_vessel=None):

        self.name = 'Separate'
        self.properties = {
            'lower_phase_vessel': lower_phase_vessel,
            'upper_phase_vessel': upper_phase_vessel,
        }

        self.literal_code = f'chempiler.pump.separate_phases( {self.lower_phase_vessel}, {self.upper_phase_vessel}, )'

    def execute(self, chempiler):
        chempiler.pump.separate_phases(
            self.lower_phase_vessel,
            self.upper_phase_vessel,
        )
        return True

    @property
    def lower_phase_vessel(self):
        return self.properties['lower_phase_vessel']

    @lower_phase_vessel.setter
    def lower_phase_vessel(self, val):
        self.properties['lower_phase_vessel'] = val
        self.update()

    @property
    def upper_phase_vessel(self):
        return self.properties['upper_phase_vessel']

    @upper_phase_vessel.setter
    def upper_phase_vessel(self, val):
        self.properties['upper_phase_vessel'] = val
        self.update()

class CPrime(Step):
    """Moves the tube volume of every node with "flask" as class to waste.

    Keyword Arguments:
        aspiration_speed {float} -- Speed in mL / min at which material should be withdrawn.
    """
    def __init__(self, aspiration_speed='default'):

        self.name = 'Prime'
        self.properties = {
            'aspiration_speed': aspiration_speed,
        }
        self.get_defaults()

        self.literal_code = f'chempiler.pump.prime_tubes({self.aspiration_speed})'

    def execute(self, chempiler):
        chempiler.pump.prime_tubes(self.aspiration_speed)
        return True

    @property
    def aspiration_speed(self):
        return self.properties['aspiration_speed']

    @aspiration_speed.setter
    def aspiration_speed(self, val):
        self.properties['aspiration_speed'] = val
        self.update()

class CSwitchVacuum(Step):
    """Switches a vacuum valve between backbone and vacuum.

    Keyword Arguments:
        vessel {str} -- Name of the node the vacuum valve is logically attacked to (e.g. "filter_bottom")
        destination {str} -- Either "vacuum" or "backbone"
    """
    def __init__(self, vessel=None, destination=None):

        self.name = 'SwitchVacuum'
        self.properties = {
            'vessel': vessel,
            'destination': destination,
        }

        self.literal_code = f'chempiler.pump.switch_cartridge({self.vessel}, {self.destination})'

    def execute(self, chempiler):
        chempiler.pump.switch_cartridge(self.vessel, self.destination)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def destination(self):
        return self.properties['destination']

    @destination.setter
    def destination(self, val):
        self.properties['destination'] = val
        self.update()

class CSwitchCartridge(Step):
    """Switches a cartridge carousel to the specified position.

    Keyword Arguments:
        vessel {str} -- Name of the node the vacuum valve is logically attacked to (e.g. "rotavap")
        cartridge {int} -- Number of the position the carousel should be switched to (0-5)
    """
    def __init__(self, vessel=None, cartridge=None):
        self.name = 'SwitchCartridge'
        self.properties = {
            'vessel': vessel,
            'cartridge': cartridge,
        }

        self.literal_code = f'chempiler.pump.switch_cartridge({self.flask}, {self.cartridge})'

    def execute(self, chempiler):
        chempiler.pump.switch_cartridge(self.flask, self.cartridge)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def cartridge(self):
        return self.properties['cartridge']

    @cartridge.setter
    def cartridge(self, val):
        self.properties['cartridge'] = val
        self.update()

class CSwitchColumn(Step):
    """Switches a fractionating valve attached to a chromatography column.

    Keyword Arguments:
        column {str} -- Name of the column in the graph
        destination {str} -- Either "collect" or "waste"
    """
    def __init__(self, column=None, destination=None):

        self.name = 'SwitchColumn'
        self.properties = {
            'column': column,
            'destination': destination,
        }

        self.literal_code = f'chempiler.pump.switch_column_fraction({self.column}, {self.destination})'

    def execute(self, chempiler):
        chempiler.pump.switch_column_fraction(self.column, self.destination)
        return True

    @property
    def column(self):
        return self.properties['column']

    @column.setter
    def column(self, val):
        self.properties['column'] = val
        self.update()

    @property
    def destination(self):
        return self.properties['destination']

    @destination.setter
    def destination(self, val):
        self.properties['destination'] = val
        self.update()

class CStartStir(Step):
    """Starts the stirring operation of a hotplate or overhead stirrer.

    Keyword Arguments:
        vessel {str} -- Vessel name to stir.
    """
    def __init__(self, vessel=None):

        self.name = 'StartStir'
        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.stirrer.stir({self.vessel})'

    def execute(self, chempiler):
        chempiler.stirrer.stir(self.vessel)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class CStartHeat(Step):
    """Starts the heating operation of a hotplate stirrer.

    Keyword Arguments:
        vessel {str} -- Vessel name to heat.
    """
    def __init__(self, vessel=None):

        self.name = 'StartHeat'
        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.stirrer.heat({self.vessel})'

    def execute(self, chempiler):
        chempiler.stirrer.heat(self.vessel)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class CStopStir(Step):
    """Stops the stirring operation of a hotplate or overhead stirrer.

    Keyword Arguments:
        vessel {str} -- Vessel name to stop stirring.
    """
    def __init__(self, vessel=None):

        self.name = 'StopStir'
        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.stirrer.stop_stir({self.vessel})'

    def execute(self, chempiler):
        chempiler.stirrer.stop_stir(self.vessel)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class CStopHeat(Step):
    """Starts the stirring operation of a hotplate stirrer. This command is NOT available
    for overhead stirrers!

    Keyword Arguments:
        vessel {str} -- Vessel name to stop heating.
    """
    def __init__(self, vessel=None):

        self.name = 'StopHeat'
        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.stirrer.stop_heat({self.vessel})'

    def execute(self, chempiler):
        chempiler.stirrer.stop_heat(self.vessel)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class CSetTemp(Step):
    """Sets the temperature setpoint of a hotplate stirrer. This command is NOT available
    for overhead stirrers!

    Keyword Arguments:
        vessel {str} -- Vessel name to set temperature of hotplate stirrer.
        temp {float} -- Temperature in °C
    """
    def __init__(self, vessel=None, temp=None):

        self.name = 'SetTemp'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
        }

        self.literal_code = f'chempiler.stirrer.set_temp({self.vessel}, {self.temp})'

    def execute(self, chempiler):
        chempiler.stirrer.set_temp(self.vessel, self.temp)
        return True

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

class CSetStirRpm(Step):
    """Sets the stirring speed setpoint of a hotplate or overhead stirrer.

    Keyword Arguments:
        vessel {str} -- Vessel name to set stir speed.
        stir_rpm {float} -- Stir speed in RPM.
    """
    def __init__(self, vessel=None, stir_rpm=None):

        self.name = 'SetStirRpm'
        self.properties = {
            'vessel': vessel,
            'stir_rpm': stir_rpm,
        }

        self.literal_code = f'chempiler.stirrer.set_stir_rate({self.vessel}, {self.stir_rpm})'

    def execute(self, chempiler):
        chempiler.stirrer.set_stir_rate(self.vessel, self.stir_rpm)
        return True

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

class CStirrerWaitForTemp(Step):
    """Delays the script execution until the current temperature of the hotplate is within
    0.5 °C of the setpoint. This command is NOT available for overhead stirrers!

    Keyword Arguments:
        vessel {str} -- Vessel name to wait for temperature.
    """
    def __init__(self, vessel=None):

        self.name = 'StirrerWaitForTemp'
        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.stirrer.wait_for_temp({self.vessel})'

    def execute(self, chempiler):
        chempiler.stirrer.wait_for_temp(self.vessel)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class CStartHeaterBath(Step):
    """Starts the heating bath of a rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.name = 'StartHeaterBath'
        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.start_heater({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.start_heater(self.rotavap_name)
        return True

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @rotavap_name.setter
    def rotavap_name(self, val):
        self.properties['rotavap_name'] = val
        self.update()

class CStopHeaterBath(Step):
    """Stops the heating bath of a rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.name = 'StopHeaterBath'
        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.stop_heater({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.stop_heater(self.rotavap_name)
        return True

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @rotavap_name.setter
    def rotavap_name(self, val):
        self.properties['rotavap_name'] = val
        self.update()

class CStartRotation(Step):
    """Starts the rotation of a rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.name = 'StartRotation'
        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.start_rotation({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.start_rotation(self.rotavap_name)
        return True

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @rotavap_name.setter
    def rotavap_name(self, val):
        self.properties['rotavap_name'] = val
        self.update()

class CStopRotation(Step):
    """Stops the rotation of a rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.name = 'StopRotation'
        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.stop_rotation({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.stop_rotation(self.rotavap_name)
        return True

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @rotavap_name.setter
    def rotavap_name(self, val):
        self.properties['rotavap_name'] = val
        self.update()

class CLiftArmUp(Step):
    """Lifts the rotary evaporator arm up.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.name = 'LiftArmUp'
        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.lift_up({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.lift_up(self.rotavap_name)
        return True

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @rotavap_name.setter
    def rotavap_name(self, val):
        self.properties['rotavap_name'] = val
        self.update()

class CLiftArmDown(Step):
    """Lifts the rotary evaporator down.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.name = 'LiftArmDown'
        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.lift_down({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.lift_down(self.rotavap_name)
        return True

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @rotavap_name.setter
    def rotavap_name(self, val):
        self.properties['rotavap_name'] = val
        self.update()

class CResetRotavap(Step):
    """
    Resets the rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.name = 'ResetRotavap'
        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.reset({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.reset(self.rotavap_name)
        return True

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @rotavap_name.setter
    def rotavap_name(self, val):
        self.properties['rotavap_name'] = val
        self.update()

class CSetBathTemp(Step):
    """Sets the temperature setpoint for the heating bath.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
        temp {float} -- Temperature in °C.
    """
    def __init__(self, rotavap_name=None, temp=None):

        self.name = 'SetBathTemp'
        self.properties = {
            'rotavap_name': rotavap_name,
            'temp': temp,
        }

        self.literal_code = f'chempiler.rotavap.set_temp({self.rotavap_name}, {self.temp})'

    def execute(self, chempiler):
        chempiler.rotavap.set_temp(self.rotavap_name, self.temp)
        return True

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @rotavap_name.setter
    def rotavap_name(self, val):
        self.properties['rotavap_name'] = val
        self.update()

    @property
    def temp(self):
        return self.properties['temp']

    @temp.setter
    def temp(self, val):
        self.properties['temp'] = val
        self.update()

class CSetRvRotationSpeed(Step):
    """Sets the rotation speed setpoint for the rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
        rotation_speed {str} -- Rotation speed setpoint in RPM.
    """
    def __init__(self, rotavap_name=None, rotation_speed=None):

        self.name = 'SetRvRotationSpeed'
        self.properties = {
            'rotavap_name': rotavap_name,
            'rotation_speed': rotation_speed,
        }

        self.literal_code = f'chempiler.rotavap.set_rotation({self.rotavap_name}, {self.rotation_speed})'

    def execute(self, chempiler):
        chempiler.rotavap.set_rotation(self.rotavap_name, self.rotation_speed)
        return True

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @rotavap_name.setter
    def rotavap_name(self, val):
        self.properties['rotavap_name'] = val
        self.update()

    @property
    def rotation_speed(self):
        return self.properties['rotation_speed']

    @rotation_speed.setter
    def rotation_speed(self, val):
        self.properties['rotation_speed'] = val
        self.update()

class CRvWaitForTemp(Step):
    """Delays the script execution until the current temperature of the heating bath is
    within 0.5°C of the setpoint.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.name = 'RvWaitForTemp'
        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.wait_for_temp({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.wait_for_temp(self.rotavap_name)
        return True

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @rotavap_name.setter
    def rotavap_name(self, val):
        self.properties['rotavap_name'] = val
        self.update()

class CSetInterval(Step):
    """Sets the interval time for the rotary evaporator, causing it to periodically switch
    direction. Setting this to 0 deactivates interval operation.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
        interval {int} -- Interval time in seconds.
    """
    def __init__(self, rotavap_name=None, interval=None):

        self.name = 'SetInterval'
        self.properties = {
            'rotavap_name': rotavap_name,
            'interval': interval,
        }

        self.literal_code = f'chempiler.rotavap.set_interval({self.rotavap_name}, {self.interval})'

    def execute(self, chempiler):
        chempiler.rotavap.set_interval(self.rotavap_name, self.interval)
        return True

    @property
    def rotavap_name(self):
        return self.properties['rotavap_name']

    @rotavap_name.setter
    def rotavap_name(self, val):
        self.properties['rotavap_name'] = val
        self.update()

    @property
    def interval(self):
        return self.properties['interval']

    @interval.setter
    def interval(self, val):
        self.properties['interval'] = val
        self.update()

class CInitVacPump(Step):
    """Initialises the vacuum pump controller.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vacuum_pump_name=None):
        self.name = 'InitVacPump'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
        }

        self.literal_code = f'chempiler.vacuum.initialise({self.vacuum_pump_name})'

    def execute(self, chempiler):
        chempiler.vacuum.initialise(self.vacuum_pump_name)
        return True

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @vacuum_pump_name.setter
    def vacuum_pump_name(self, val):
        self.properties['vacuum_pump_name'] = val
        self.update()

class CGetVacSp(Step):
    """Reads the current vacuum setpoint.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vacuum_pump_name=None):

        self.name = 'GetVacSp'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
        }

        self.literal_code = f'chempiler.vacuum.get_vacuum_set_point({self.vacuum_pump_name})'

    def execute(self, chempiler):
        chempiler.vacuum.get_vacuum_set_point(self.vacuum_pump_name)
        return True

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @vacuum_pump_name.setter
    def vacuum_pump_name(self, val):
        self.properties['vacuum_pump_name'] = val
        self.update()

class CSetVacSp(Step):
    """Sets a new vacuum setpoint.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
        vacuum_pressure {float} -- Vacuum pressure setpoint in mbar.
    """
    def __init__(self, vacuum_pump_name=None, vacuum_pressure=None):

        self.name = 'SetVacSp'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
            'vacuum_pressure': vacuum_pressure,
        }

        self.literal_code = f'chempiler.vacuum.set_vacuum_set_point({self.vacuum_pump_name}, {self.set_point})'

    def execute(self, chempiler):
        chempiler.vacuum.set_vacuum_set_point(self.vacuum_pump_name, self.set_point)
        return True

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @vacuum_pump_name.setter
    def vacuum_pump_name(self, val):
        self.properties['vacuum_pump_name'] = val
        self.update()

    @property
    def vacuum_pressure(self):
        return self.properties['vacuum_pressure']

    @vacuum_pressure.setter
    def vacuum_pressure(self, val):
        self.properties['vacuum_pressure'] = val
        self.update()

class CStartVac(Step):
    """Starts the vacuum pump.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vacuum_pump_name=None):

        self.name = 'StartVac'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
        }

        self.literal_code = f'chempiler.vacuum.start_vacuum({self.vacuum_pump_name})'

    def execute(self, chempiler):
        chempiler.vacuum.start_vacuum(self.vacuum_pump_name)
        return True

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @vacuum_pump_name.setter
    def vacuum_pump_name(self, val):
        self.properties['vacuum_pump_name'] = val
        self.update()

class CStopVac(Step):
    """Stops the vacuum pump.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vacuum_pump_name=None):

        self.name = 'StopVac'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
        }

        self.literal_code = f'chempiler.vacuum.stop_vacuum({self.vacuum_pump_name})'

    def execute(self, chempiler):
        chempiler.vacuum.stop_vacuum(self.vacuum_pump_name)
        return True

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @vacuum_pump_name.setter
    def vacuum_pump_name(self, val):
        self.properties['vacuum_pump_name'] = val
        self.update()

class CVentVac(Step):
    """Vents the vacuum pump to ambient pressure.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vacuum_pump_name=None):

        self.name = 'VentVac'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
        }

        self.literal_code = f'chempiler.vacuum.vent_vacuum({self.vacuum_pump_name})'

    def execute(self, chempiler):
        chempiler.vacuum.vent_vacuum(self.vacuum_pump_name)
        return True

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @vacuum_pump_name.setter
    def vacuum_pump_name(self, val):
        self.properties['vacuum_pump_name'] = val
        self.update()

class CSetSpeedSp(Step):
    """Sets the speed of the vacuum pump (0-100%).

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
        vacuum_pump_speed {float} -- Vacuum pump speed in percent.
    """
    def __init__(self, vacuum_pump_name=None, vacuum_pump_speed=None):

        self.name = 'SetSpeedSp'
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
            'vacuum_pump_speed': vacuum_pump_speed,
        }

        self.literal_code = f'chempiler.vacuum.set_speed_set_point({self.vacuum_pump_name}, {self.set_point})'

    def execute(self, chempiler):
        chempiler.vacuum.set_speed_set_point(self.vacuum_pump_name, self.set_point)
        return True

    @property
    def vacuum_pump_name(self):
        return self.properties['vacuum_pump_name']

    @vacuum_pump_name.setter
    def vacuum_pump_name(self, val):
        self.properties['vacuum_pump_name'] = val
        self.update()

    @property
    def vacuum_pump_speed(self):
        return self.properties['vacuum_pump_speed']

    @vacuum_pump_speed.setter
    def vacuum_pump_speed(self, val):
        self.properties['vacuum_pump_speed'] = val
        self.update()

class CStartChiller(Step):
    """Starts the recirculation chiller.

    Keyword Arguments:
        vessel {str} -- Vessel to chill. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel=None):

        self.name = 'StartChiller'
        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.chiller.start_chiller({self.vessel})'

    def execute(self, chempiler):
        chempiler.chiller.start_chiller(self.vessel)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class CStopChiller(Step):
    """Stops the recirculation chiller.

    Keyword Arguments:
        vessel {str} -- Vessel to stop chilling. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel=None):

        self.name = 'StopChiller'
        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.chiller.stop_chiller({self.vessel})'

    def execute(self, chempiler):
        chempiler.chiller.stop_chiller(self.vessel)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class CSetChiller(Step):
    """Sets the temperature setpoint.

    Keyword Arguments:
        vessel {str} -- Vessel to set chiller temperature. Name of the node the chiller is attached to.
        temp {float} -- Temperature in °C.
    """
    def __init__(self, vessel=None, temp=None):

        self.name = 'SetChiller'
        self.properties = {
            'vessel': vessel,
            'temp': temp,
        }

        self.literal_code = f'chempiler.chiller.set_temp({self.vessel}, {self.temp})'

    def execute(self, chempiler):
        chempiler.chiller.set_temp(self.vessel, self.temp)
        return True

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

class CChillerWaitForTemp(Step):
    """Delays the script execution until the current temperature of the chiller is within
    0.5°C of the setpoint.

    Keyword Arguments:
        vessel {str} -- Vessel to wait for temperature. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel=None):

        self.name = 'ChillerWaitForTemp'
        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.chiller.wait_for_temp({self.vessel})'

    def execute(self, chempiler):
        chempiler.chiller.wait_for_temp(self.vessel)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

class CRampChiller(Step):
    """Causes the chiller to ramp the temperature up or down. Only available for Petite
    Fleur.

    Keyword Arguments:
        vessel {str} -- Vessel to ramp chiller on. Name of the node the chiller is attached to.
        ramp_duration {int} -- Desired duration of the ramp in seconds.
        end_temperature {float} -- Final temperature of the ramp in °C.
    """
    def __init__(self, vessel=None, ramp_duration=None, end_temperature=None):

        self.name = 'RampChiller'
        self.properties = {
            'vessel': vessel,
            'ramp_duration': ramp_duration,
            'end_temperature': end_temperature,
        }

        self.literal_code = f'chempiler.chiller.ramp_chiller({self.vessel}, {self.ramp_duration}, {self.end_temperature})'

    def execute(self, chempiler):
        chempiler.chiller.ramp_chiller(self.vessel, self.ramp_duration, self.end_temperature)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def ramp_duration(self):
        return self.properties['ramp_duration']

    @ramp_duration.setter
    def ramp_duration(self, val):
        self.properties['ramp_duration'] = val
        self.update()

    @property
    def end_temperature(self):
        return self.properties['end_temperature']

    @end_temperature.setter
    def end_temperature(self, val):
        self.properties['end_temperature'] = val
        self.update()

class CSwitchChiller(Step):
    """Switches the solenoid valve.

    Keyword Arguments:
        solenoid_valve_name -- {str} Name of the node the solenoid valve is attached to.
        state {str} -- Is either "on" or "off"
    """
    def __init__(self, solenoid_valve_name=None, state=None):

        self.name = 'SwitchChiller'
        self.properties = {
            'solenoid_valve_name': solenoid_valve_name,
            'state': state,
        }

        self.literal_code = f'chempiler.chiller.switch_vessel({self.solenoid_valve_name}, {self.state})'

    def execute(self, chempiler):
        chempiler.chiller.switch_vessel(self.solenoid_valve_name, self.state)
        return True

    @property
    def solenoid_valve_name(self):
        return self.properties['solenoid_valve_name']

    @solenoid_valve_name.setter
    def solenoid_valve_name(self, val):
        self.properties['solenoid_valve_name'] = val
        self.update()

    @property
    def state(self):
        return self.properties['state']

    @state.setter
    def state(self, val):
        self.properties['state'] = val
        self.update()

class CSetCoolingPower(Step):
    """Sets the cooling power (0-100%). Only available for CF41.

    Keyword Arguments:
        vessel -- Vessel to set cooling power of chiller. Name of the node the chiller is attached to.
        cooling_power -- Desired cooling power in percent.
    """
    def __init__(self, vessel=None, cooling_power=None):

        self.name = 'SetCoolingPower'
        self.properties = {
            'vessel': vessel,
            'cooling_power': cooling_power,
        }

        self.literal_code = f'chempiler.chiller.cooling_power({self.vessel}, {self.cooling_power})'

    def execute(self, chempiler):
        chempiler.chiller.cooling_power(self.vessel, self.cooling_power)
        return True

    @property
    def vessel(self):
        return self.properties['vessel']

    @vessel.setter
    def vessel(self, val):
        self.properties['vessel'] = val
        self.update()

    @property
    def cooling_power(self):
        return self.properties['cooling_power']

    @cooling_power.setter
    def cooling_power(self, val):
        self.properties['cooling_power'] = val
        self.update()

class CSetRecordingSpeed(Step):
    """Sets the timelapse speed of the camera module.

    Keyword Arguments:
        recording_speed {float} -- Factor by which the recording should be sped up, i.e. 2 would mean twice the normal speed. 1 means normal speed.
    """
    def __init__(self, recording_speed=None):

        self.name = 'SetRecordingSpeed'
        self.properties = {
            'recording_speed': recording_speed,
        }

        self.literal_code = f'chempiler.camera.change_recording_speed({self.recording_speed})'

    def execute(self, chempiler):
        chempiler.camera.change_recording_speed(self.recording_speed)
        return True

    @property
    def recording_speed(self):
        return self.properties['recording_speed']

    @recording_speed.setter
    def recording_speed(self, val):
        self.properties['recording_speed'] = val
        self.update()

class CWait(Step):
    """Delays execution of the script for a set amount of time. This command will
    immediately reply with an estimate of when the waiting will be finished, and also
    give regular updates indicating that it is still alive.

    Keyword Arguments:
        time -- Time to wait in seconds.
    """
    def __init__(self, time=None):

        self.name = 'CWait'
        self.properties = {
            'time': time,
        }

        self.literal_code = f'chempiler.wait({self.time})'

    def execute(self, chempiler):
        chempiler.wait(self.time)
        return True

    @property
    def time(self):
        return self.properties['time']

    @time.setter
    def time(self, val):
        self.properties['time'] = val
        self.update()

class CBreakpoint(Step):
    """Introduces a breakpoint in the script. The execution is halted until the operator
    resumes it.
    """
    def __init__(self):

        self.name = 'Breakpoint'
        self.properties = {
        }

        self.literal_code = f'chempiler.breakpoint()'

    def execute(self, chempiler):
        chempiler.breakpoint()
        return True