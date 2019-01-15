from ..constants import *
from .base_step import Step

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

        self.properties = {
            'from_vessel': from_vessel,
            'to_vessel': to_vessel,
            'volume': volume,
            'move_speed': move_speed,
            'aspiration_speed': aspiration_speed,
            'dispense_speed': dispense_speed,
        }
        self.get_defaults()

        self.human_readable = f'Move {self.from_vessel} ({self.volume}) to {self.to_vessel}.'

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

class CSeparate(Step):

    def __init__(self, lower_phase_vessel, upper_phase_vessel, separator_top, 
                       separator_bottom, dead_volume_target):
        """        
        Args:
            lower_phase_vessel (str): Name of vessel to transfer lower phase to.
            upper_phase_vessel (str): Name of vessel to transfer upper phase to.
            separator_top (str): Name of separator top node in graph.
            separator_bottom (str): Name of separator bottom node in graph.
            dead_volume_target (str): Name of waste vessel to transfer dead 
                                      volume between phases to.
        """
        self.properties = {
            'lower_phase_vessel': lower_phase_vessel,
            'upper_phase_vessel': upper_phase_vessel,
            'separator_top': separator_top,
            'separator_bottom': separator_bottom,
            'dead_volume_target': dead_volume_target,
        }

        self.literal_code = f'chempiler.pump.separate_phases( lower_phase_target={self.lower_phase_vessel}, upper_phase_target={self.upper_phase_vessel}, separator_top={self.separator_top}, separator_bottom={self.separator_bottom}, dead_volume_target={self.dead_volume_target}, )'

    def execute(self, chempiler):
        chempiler.pump.separate_phases(
            lower_phase_target=self.lower_phase_vessel,
            upper_phase_target=self.upper_phase_vessel,
            separator_top=self.separator_top,
            separator_bottom=self.separator_bottom,
            dead_volume_target=self.dead_volume_target,
        )
        return True

class CPrime(Step):
    """Moves the tube volume of every node with "flask" as class to waste.

    Keyword Arguments:
        aspiration_speed {float} -- Speed in mL / min at which material should 
                                    be withdrawn.
    """
    def __init__(self, aspiration_speed='default'):

        self.properties = {
            'aspiration_speed': aspiration_speed,
        }
        self.get_defaults()

        self.literal_code = f'chempiler.pump.prime_tubes({self.aspiration_speed})'

    def execute(self, chempiler):
        chempiler.pump.prime_tubes(self.aspiration_speed)
        return True

class CSwitchVacuum(Step):
    """Switches a vacuum valve between backbone and vacuum.

    Keyword Arguments:
        vessel {str} -- Name of the node the vacuum valve is logically attacked to (e.g. "filter_bottom")
        destination {str} -- Either "vacuum" or "backbone"
    """
    def __init__(self, vessel=None, destination=None):

        self.properties = {
            'vessel': vessel,
            'destination': destination,
        }

        self.literal_code = f'chempiler.pump.switch_cartridge({self.vessel}, {self.destination})'

    def execute(self, chempiler):
        chempiler.pump.switch_cartridge(self.vessel, self.destination)
        return True

class CSwitchCartridge(Step):
    """Switches a cartridge carousel to the specified position.

    Keyword Arguments:
        vessel {str} -- Name of the node the vacuum valve is logically attacked to (e.g. "rotavap")
        cartridge {int} -- Number of the position the carousel should be switched to (0-5)
    """
    def __init__(self, vessel=None, cartridge=None):
        self.properties = {
            'vessel': vessel,
            'cartridge': cartridge,
        }

        self.literal_code = f'chempiler.pump.switch_cartridge({self.vessel}, {self.cartridge})'

    def execute(self, chempiler):
        chempiler.pump.switch_cartridge(self.vessel, self.cartridge)
        return True

class CSwitchColumn(Step):
    """Switches a fractionating valve attached to a chromatography column.

    Keyword Arguments:
        column {str} -- Name of the column in the graph
        destination {str} -- Either "collect" or "waste"
    """
    def __init__(self, column=None, destination=None):

        self.properties = {
            'column': column,
            'destination': destination,
        }

        self.literal_code = f'chempiler.pump.switch_column_fraction({self.column}, {self.destination})'

    def execute(self, chempiler):
        chempiler.pump.switch_column_fraction(self.column, self.destination)
        return True

class CStartStir(Step):
    """Starts the stirring operation of a hotplate or overhead stirrer.

    Keyword Arguments:
        vessel {str} -- Vessel name to stir.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.stirrer.stir({self.vessel})'

    def execute(self, chempiler):
        chempiler.stirrer.stir(self.vessel)
        return True

class CStartHeat(Step):
    """Starts the heating operation of a hotplate stirrer.

    Keyword Arguments:
        vessel {str} -- Vessel name to heat.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.stirrer.heat({self.vessel})'

    def execute(self, chempiler):
        chempiler.stirrer.heat(self.vessel)
        return True

class CStopStir(Step):
    """Stops the stirring operation of a hotplate or overhead stirrer.

    Keyword Arguments:
        vessel {str} -- Vessel name to stop stirring.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.human_readable = f'Stop stirring {self.vessel}.'

        self.literal_code = f'chempiler.stirrer.stop_stir({self.vessel})'

    def execute(self, chempiler):
        chempiler.stirrer.stop_stir(self.vessel)
        return True

class CStopHeat(Step):
    """Starts the stirring operation of a hotplate stirrer. This command is NOT available
    for overhead stirrers!

    Keyword Arguments:
        vessel {str} -- Vessel name to stop heating.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.stirrer.stop_heat({self.vessel})'

    def execute(self, chempiler):
        chempiler.stirrer.stop_heat(self.vessel)
        return True

class CSetTemp(Step):
    """Sets the temperature setpoint of a hotplate stirrer. This command is NOT available
    for overhead stirrers!

    Keyword Arguments:
        vessel {str} -- Vessel name to set temperature of hotplate stirrer.
        temp {float} -- Temperature in °C
    """
    def __init__(self, vessel=None, temp=None):

        self.properties = {
            'vessel': vessel,
            'temp': temp,
        }

        self.literal_code = f'chempiler.stirrer.set_temp({self.vessel}, {self.temp})'

    def execute(self, chempiler):
        chempiler.stirrer.set_temp(self.vessel, self.temp)
        return True

class CSetStirRpm(Step):
    """Sets the stirring speed setpoint of a hotplate or overhead stirrer.

    Keyword Arguments:
        vessel {str} -- Vessel name to set stir speed.
        stir_rpm {float} -- Stir speed in RPM.
    """
    def __init__(self, vessel=None, stir_rpm=None):

        self.properties = {
            'vessel': vessel,
            'stir_rpm': stir_rpm,
        }

        self.literal_code = f'chempiler.stirrer.set_stir_rate({self.vessel}, {self.stir_rpm})'

    def execute(self, chempiler):
        chempiler.stirrer.set_stir_rate(self.vessel, self.stir_rpm)
        return True

class CStirrerWaitForTemp(Step):
    """Delays the script execution until the current temperature of the hotplate is within
    0.5 °C of the setpoint. This command is NOT available for overhead stirrers!

    Keyword Arguments:
        vessel {str} -- Vessel name to wait for temperature.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.stirrer.wait_for_temp({self.vessel})'

    def execute(self, chempiler):
        chempiler.stirrer.wait_for_temp(self.vessel)
        return True

class CStartHeaterBath(Step):
    """Starts the heating bath of a rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.start_heater({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.start_heater(self.rotavap_name)
        return True

class CStopHeaterBath(Step):
    """Stops the heating bath of a rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.stop_heater({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.stop_heater(self.rotavap_name)
        return True

class CStartRotation(Step):
    """Starts the rotation of a rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.start_rotation({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.start_rotation(self.rotavap_name)
        return True

class CStopRotation(Step):
    """Stops the rotation of a rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.stop_rotation({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.stop_rotation(self.rotavap_name)
        return True

class CLiftArmUp(Step):
    """Lifts the rotary evaporator arm up.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.lift_up({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.lift_up(self.rotavap_name)
        return True

class CLiftArmDown(Step):
    """Lifts the rotary evaporator down.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.lift_down({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.lift_down(self.rotavap_name)
        return True

class CResetRotavap(Step):
    """
    Resets the rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.reset({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.reset(self.rotavap_name)
        return True

class CSetBathTemp(Step):
    """Sets the temperature setpoint for the heating bath.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
        temp {float} -- Temperature in °C.
    """
    def __init__(self, rotavap_name=None, temp=None):

        self.properties = {
            'rotavap_name': rotavap_name,
            'temp': temp,
        }

        self.literal_code = f'chempiler.rotavap.set_temp({self.rotavap_name}, {self.temp})'

    def execute(self, chempiler):
        chempiler.rotavap.set_temp(self.rotavap_name, self.temp)
        return True

class CSetRvRotationSpeed(Step):
    """Sets the rotation speed setpoint for the rotary evaporator.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
        rotation_speed {str} -- Rotation speed setpoint in RPM.
    """
    def __init__(self, rotavap_name=None, rotation_speed=None):

        self.properties = {
            'rotavap_name': rotavap_name,
            'rotation_speed': rotation_speed,
        }

        self.literal_code = f'chempiler.rotavap.set_rotation({self.rotavap_name}, {self.rotation_speed})'

    def execute(self, chempiler):
        chempiler.rotavap.set_rotation(self.rotavap_name, self.rotation_speed)
        return True

class CRvWaitForTemp(Step):
    """Delays the script execution until the current temperature of the heating bath is
    within 0.5°C of the setpoint.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
    """
    def __init__(self, rotavap_name=None):

        self.properties = {
            'rotavap_name': rotavap_name,
        }

        self.literal_code = f'chempiler.rotavap.wait_for_temp({self.rotavap_name})'

    def execute(self, chempiler):
        chempiler.rotavap.wait_for_temp(self.rotavap_name)
        return True

class CSetInterval(Step):
    """Sets the interval time for the rotary evaporator, causing it to periodically switch
    direction. Setting this to 0 deactivates interval operation.

    Keyword Arguments:
        rotavap_name {str} -- Name of the node representing the rotary evaporator.
        interval {int} -- Interval time in seconds.
    """
    def __init__(self, rotavap_name=None, interval=None):

        self.properties = {
            'rotavap_name': rotavap_name,
            'interval': interval,
        }

        self.literal_code = f'chempiler.rotavap.set_interval({self.rotavap_name}, {self.interval})'

    def execute(self, chempiler):
        chempiler.rotavap.set_interval(self.rotavap_name, self.interval)
        return True

class CInitVacPump(Step):
    """Initialises the vacuum pump controller.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vacuum_pump_name=None):
        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
        }

        self.literal_code = f'chempiler.vacuum.initialise({self.vacuum_pump_name})'

    def execute(self, chempiler):
        chempiler.vacuum.initialise(self.vacuum_pump_name)
        return True

class CGetVacSp(Step):
    """Reads the current vacuum setpoint.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vacuum_pump_name=None):

        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
        }

        self.literal_code = f'chempiler.vacuum.get_vacuum_set_point({self.vacuum_pump_name})'

    def execute(self, chempiler):
        chempiler.vacuum.get_vacuum_set_point(self.vacuum_pump_name)
        return True

class CSetVacSp(Step):
    """Sets a new vacuum setpoint.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
        vacuum_pressure {float} -- Vacuum pressure setpoint in mbar.
    """
    def __init__(self, vacuum_pump_name=None, vacuum_pressure=None):

        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
            'vacuum_pressure': vacuum_pressure,
        }

        self.literal_code = f'chempiler.vacuum.set_vacuum_set_point({self.vacuum_pump_name}, {self.vacuum_pressure})'

    def execute(self, chempiler):
        chempiler.vacuum.set_vacuum_set_point(self.vacuum_pump_name, self.vacuum_pressure)
        return True

class CStartVac(Step):
    """Starts the vacuum pump.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vacuum_pump_name=None):

        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
        }

        self.literal_code = f'chempiler.vacuum.start_vacuum({self.vacuum_pump_name})'

    def execute(self, chempiler):
        chempiler.vacuum.start_vacuum(self.vacuum_pump_name)
        return True

class CStopVac(Step):
    """Stops the vacuum pump.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vacuum_pump_name=None):

        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
        }

        self.literal_code = f'chempiler.vacuum.stop_vacuum({self.vacuum_pump_name})'

    def execute(self, chempiler):
        chempiler.vacuum.stop_vacuum(self.vacuum_pump_name)
        return True

class CVentVac(Step):
    """Vents the vacuum pump to ambient pressure.

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
    """
    def __init__(self, vacuum_pump_name=None):

        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
        }

        self.literal_code = f'chempiler.vacuum.vent_vacuum({self.vacuum_pump_name})'

    def execute(self, chempiler):
        chempiler.vacuum.vent_vacuum(self.vacuum_pump_name)
        return True

class CSetSpeedSp(Step):
    """Sets the speed of the vacuum pump (0-100%).

    Keyword Arguments:
        vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.
        vacuum_pump_speed {float} -- Vacuum pump speed in percent.
    """
    def __init__(self, vacuum_pump_name=None, vacuum_pump_speed=None):

        self.properties = {
            'vacuum_pump_name': vacuum_pump_name,
            'vacuum_pump_speed': vacuum_pump_speed,
        }

        self.literal_code = f'chempiler.vacuum.set_speed_set_point({self.vacuum_pump_name}, {self.set_point})'

    def execute(self, chempiler):
        chempiler.vacuum.set_speed_set_point(self.vacuum_pump_name, self.set_point)
        return True

class CStartChiller(Step):
    """Starts the recirculation chiller.

    Keyword Arguments:
        vessel {str} -- Vessel to chill. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.chiller.start_chiller({self.vessel})'

    def execute(self, chempiler):
        chempiler.chiller.start_chiller(self.vessel)
        return True

class CStopChiller(Step):
    """Stops the recirculation chiller.

    Keyword Arguments:
        vessel {str} -- Vessel to stop chilling. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }
        self.human_readable = f'Stop chiller for {vessel}.'

        self.literal_code = f'chempiler.chiller.stop_chiller({self.vessel})'

    def execute(self, chempiler):
        chempiler.chiller.stop_chiller(self.vessel)
        return True

class CSetChiller(Step):
    """Sets the temperature setpoint.

    Keyword Arguments:
        vessel {str} -- Vessel to set chiller temperature. Name of the node the chiller is attached to.
        temp {float} -- Temperature in °C.
    """
    def __init__(self, vessel=None, temp=None):

        self.properties = {
            'vessel': vessel,
            'temp': temp,
        }

        self.literal_code = f'chempiler.chiller.set_temp({self.vessel}, {self.temp})'

    def execute(self, chempiler):
        chempiler.chiller.set_temp(self.vessel, self.temp)
        return True

class CChillerWaitForTemp(Step):
    """Delays the script execution until the current temperature of the chiller is within
    0.5°C of the setpoint.

    Keyword Arguments:
        vessel {str} -- Vessel to wait for temperature. Name of the node the chiller is attached to.
    """
    def __init__(self, vessel=None):

        self.properties = {
            'vessel': vessel,
        }

        self.literal_code = f'chempiler.chiller.wait_for_temp({self.vessel})'

    def execute(self, chempiler):
        chempiler.chiller.wait_for_temp(self.vessel)
        return True

class CRampChiller(Step):
    """Causes the chiller to ramp the temperature up or down. Only available for Petite
    Fleur.

    Keyword Arguments:
        vessel {str} -- Vessel to ramp chiller on. Name of the node the chiller is attached to.
        ramp_duration {int} -- Desired duration of the ramp in seconds.
        end_temperature {float} -- Final temperature of the ramp in °C.
    """
    def __init__(self, vessel=None, ramp_duration=None, end_temperature=None):

        self.properties = {
            'vessel': vessel,
            'ramp_duration': ramp_duration,
            'end_temperature': end_temperature,
        }

        self.literal_code = f'chempiler.chiller.ramp_chiller({self.vessel}, {self.ramp_duration}, {self.end_temperature})'

    def execute(self, chempiler):
        chempiler.chiller.ramp_chiller(self.vessel, self.ramp_duration, self.end_temperature)
        return True

class CSwitchChiller(Step):
    """Switches the solenoid valve.

    Keyword Arguments:
        solenoid_valve_name -- {str} Name of the node the solenoid valve is attached to.
        state {str} -- Is either "on" or "off"
    """
    def __init__(self, solenoid_valve_name=None, state=None):

        self.properties = {
            'solenoid_valve_name': solenoid_valve_name,
            'state': state,
        }

        self.literal_code = f'chempiler.chiller.switch_vessel({self.solenoid_valve_name}, {self.state})'

    def execute(self, chempiler):
        chempiler.chiller.switch_vessel(self.solenoid_valve_name, self.state)
        return True

class CSetCoolingPower(Step):
    """Sets the cooling power (0-100%). Only available for CF41.

    Keyword Arguments:
        vessel -- Vessel to set cooling power of chiller. Name of the node the chiller is attached to.
        cooling_power -- Desired cooling power in percent.
    """
    def __init__(self, vessel=None, cooling_power=None):

        self.properties = {
            'vessel': vessel,
            'cooling_power': cooling_power,
        }

        self.literal_code = f'chempiler.chiller.cooling_power({self.vessel}, {self.cooling_power})'

    def execute(self, chempiler):
        chempiler.chiller.cooling_power(self.vessel, self.cooling_power)
        return True

class CSetRecordingSpeed(Step):
    """Sets the timelapse speed of the camera module.

    Keyword Arguments:
        recording_speed {float} -- Factor by which the recording should be sped up, i.e. 2 would mean twice the normal speed. 1 means normal speed.
    """
    def __init__(self, recording_speed=None):

        self.properties = {
            'recording_speed': recording_speed,
        }

        self.literal_code = f'chempiler.camera.change_recording_speed({self.recording_speed})'

    def execute(self, chempiler):
        chempiler.camera.change_recording_speed(self.recording_speed)
        return True

class CWait(Step):
    """Delays execution of the script for a set amount of time. This command will
    immediately reply with an estimate of when the waiting will be finished, and also
    give regular updates indicating that it is still alive.

    Keyword Arguments:
        time -- Time to wait in seconds.
    """
    def __init__(self, time=None):

        self.properties = {
            'time': time,
        }

        self.literal_code = f'chempiler.wait({self.time})'

    def execute(self, chempiler):
        chempiler.wait(self.time)
        return True

class CBreakpoint(Step):
    """Introduces a breakpoint in the script. The execution is halted until the operator
    resumes it.
    """
    def __init__(self):

        self.properties = {
        }

        self.literal_code = f'chempiler.breakpoint()'

    def execute(self, chempiler):
        chempiler.breakpoint()
        return True

# class StartRecordingVideo(Step):

#     def __init__(self):

#         self.properties = {
#         }

#         self.literal_code = f'# spawn queues message_queue = multiprocessing.Queue() recording_speed_queue = multiprocessing.Queue()'

#     def execute(self, chempiler):
#         # spawn queues
#         message_queue = multiprocessing.Queue()
#         recording_speed_queue = multiprocessing.Queue()

#         # create logging message handlers
#         video_handler = VlogHandler(message_queue)
#         recording_speed_handler = VlogHandler(recording_speed_queue)

#         # set logging levels
#         video_handler.setLevel(logging.INFO)
#         recording_speed_handler.setLevel(5)  # set a logging level below DEBUG

#         # only allow dedicated messages for the recording speed handler
#         speed_filter = RecordingSpeedFilter()
#         recording_speed_handler.addFilter(speed_filter)

#         # attach the handlers
#         logger.addHandler(video_handler)
#         logger.addHandler(recording_speed_handler)

#         # work out video name and path
#         i = 0
#         video_path = os.path.join(HERE, "log_videos", "{0}_{1}.avi".format(EXPERIMENT_CODE, i))

#         while True:
#             # keep incrementing the file counter until you hit one that doesn't yet exist
#             if os.path.isfile(video_path):
#                 i += 1
#                 video_path = os.path.join(HERE, "log_videos", "{0}_{1}.avi".format(EXPERIMENT_CODE, i))
#             else:
#                 break
#         # launch recording process
#         recording_process = multiprocessing.Process(target=recording_worker, args=(message_queue, recording_speed_queue, video_path))
#         recording_process.start()
#         time.sleep(5)  # wait for the video feed to stabilise