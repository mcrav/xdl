from .....utils.errors import XDLError
from .....utils.graph import undirected_neighbors
from .....step_utils.base_steps import AbstractDynamicStep
from .liquid_handling import Transfer
from ..steps_base import ReadConductivitySensor
import statistics
from typing import Callable, Sequence

SEPARATION_DEAD_VOLUME = 2.5
SEPARATION_DEFAULT_PRIMING_VOLUME = 2.5
SEPARATION_DEFAULT_INITIAL_PUMP_SPEED = 10
SEPARATION_DEFAULT_MID_PUMP_SPEED = 40
SEPARATION_DEFAULT_END_PUMP_SPEED = 40

class SeparatePhases(AbstractDynamicStep):
    def __init__(
        self,
        separation_vessel: str,
        lower_phase_vessel: str,
        upper_phase_vessel: str,
        dead_volume_vessel: str = None,
        step_volume: float = 1,
        lower_phase_port: str = None,
        upper_phase_port: str = None,
        dead_volume_port: str = None,
        lower_phase_through: str = None,
        upper_phase_through: str = None,
        dead_volume_through: str = None,
        **kwargs,
    ) -> None:
        """
        Routine for separating layers in the automated sep funnel based on the
        conductivity sensor. Draws a known amount into the tube, measures
        response, then keeps removing portions and recording the conductivity
        reading until calling `discriminant` with all recorded conductivity
        values results in a return a `True`thy value. When not specified,
        `discriminant` is set to `default_discriminant` sensitive to both
        positive and negative changes in conductivity.

        Args:
            separation_vessel (str): name of the graph node corresponding to
                                   separator flask
            lower_phase_vessel (str): name of the flask the lower phase will be
                                      deposited to
            upper_phase_vessel (str): name of the flask the upper phase will be
                                      deposited to
            dead_volume_vessel (str or None): name of the flask the dead volume
                will be deposited to; if not set dead volume is not removed
            step_volume (float): volume of the individual withdrawals in mL
            discriminant (function): callback which gets passed all conductivity
                values up to current point and returns True or False indicating
                whether or not a phase change has been detected
            lower_phase_port (str): Optional. Port on lower_phase_target to use.
            upper_phase_port (str): Optional. Port on upper_phase_target to use.
            dead_volume_port (str): Optional. Port on dead_volume_target to use.
            lower_phase_through (str): Optional. Node to go through on way to
                lower_phase_target.
            upper_phase_through (str): Optional. Node to go through on way to
                upper_phase_target.
            dead_volume_through (str): Optional. Node to go through on way to
                dead_volume_target.
        """
        super().__init__(locals())
        self.reset()

    def default_discriminant(
        self,
        positive_edge=False,
        negative_edge=False,
        sensitivity=5,
        min_points=6
    ) -> Callable[[Sequence[float]], bool]:
        """
        Factory method to return a customized discriminant function with the
        given properties.

        Args:
            positive_edge (bool, optional): Detect phase change when
                conductivity measurement goes up.
            negative_edge (bool, optional): Detect phase change when
                conductivity measurment goes down.
            sensitivity (int, optional): How many standard deviations away from
                the window mean should a conductivity reading be to be
                interpreted as a phase change.
            min_points (int, optional): Minimum number of conductivity
                measurement before a phase change can occur. The same paramter
                dictates the window size for the moving average:
                `window_size = min_points - 1`.

        Returns:
            Callable: A (disciminant) function that takes a series of
                measurements and decides whether a phase change has occurred.
        """

        def discriminant(points: Sequence[float]) -> bool:
            """
            This closes over the parameters passed to `default_discriminant`
            and is never accessed directly.

            Args:
                points: All conductivity measurements performed so far, with
                    `points[0]` being the first measurement and `points[-1]`
                    the current one.

            Returns:
                bool: Whether phase change has occurred (True) or not (False).
            """
            # collect at least 6 points before making a judgement
            if len(points) < min_points:
                return False
            # maximum standard deviation in the absence of a phase change
            std = max(statistics.pstdev(points[-min_points:-1]), 5.0)
            delta = points[-1] - statistics.mean(points[-min_points:-1])
            if ((delta > sensitivity * std and positive_edge)
                    or (-delta > sensitivity * std and negative_edge)):
                return True
            return False
        return discriminant

    def on_prepare_for_execution(self, graph):
        """Get max volume of separation vessel and separation vessel pump."""
        self.separation_vessel_pump = None
        self.separation_vessel_max_volume = None
        self.pump_max_volume = None
        for neighbor in undirected_neighbors(graph, self.separation_vessel):
            if graph.nodes[neighbor]['class'] == 'ChemputerValve':
                for valve_neighbor in graph.neighbors(neighbor):
                    if graph.nodes[valve_neighbor]['class'] == 'ChemputerPump':
                        self.separation_vessel_pump = valve_neighbor
                        self.pump_max_volume = graph.nodes[
                            valve_neighbor]['max_volume']
                        break

            elif graph.nodes[neighbor]['class'] == 'ConductivitySensor':
                self.conductivity_sensor = neighbor
        self.separation_vessel_max_volume = graph.nodes[
            self.separation_vessel]['max_volume']

        if not self.separation_vessel_pump:
            raise XDLError(f"Can't find pump attached to\
 {self.separation_vessel}")

        if not self.conductivity_sensor:
            raise XDLError(f"Can't find conductivity sensor attached to\
 {self.separation_vessel}")

    def on_start(self):
        """Initial conductivity sensor reading."""
        self.read_conductivity = False
        return [
            self.prime_sensor_step(),
            ReadConductivitySensor(
                sensor=self.conductivity_sensor,
                on_reading=self.on_conductivity_sensor_reading
            ),
        ]

    def on_continue(self):
        """Either finish, take conductivity reading, or withdraw more liquid."""
        # Finish
        if self.done:
            return []

        else:
            # Read conductivity and switch read_conductivity flag.
            if self.read_conductivity:
                self.read_conductivity = False
                return [
                    ReadConductivitySensor(
                        sensor=self.conductivity_sensor,
                        on_reading=self.on_conductivity_sensor_reading
                    )
                ]
            # Withdraw and switch read_conductivity flag.
            else:
                self.read_conductivity = True
                return self.lower_phase_stepwise_withdraw_step()

    def on_finish(self):
        """Phase change detected. Send phases where they are supposed to go."""
        steps = []

        # Send remaining lower phase in pump to lower_phase_vessel.
        if self.pump_current_volume:
            steps.append(self.lower_phase_separation_pump_dispense_step())

        # Withdraw dead volume if dead_volume_target given.
        steps.extend(self.dead_volume_withdraw_step())

        # Send upper phase to upper_phase_vessel.
        steps.extend(self.upper_phase_withdraw_step())
        return steps

    def reset(self):
        self.pump_current_volume = 0  # Current volume in separation vessel pump
        self.pump_max_volume = None  # Max volume of separation vessel pump

        # Node name of separation vessel pump
        self.separation_vessel_pump = None
        self.conductivity_sensor = None  # Node name of conductivity sensor

        # Flag to switch between reading conductivity and withdrawing more
        # liquid
        self.read_conductivity = True
        self.readings = []
        self.done = False
        self.discriminant = self.default_discriminant(True, True)

    def prime_sensor_step(self):
        return Transfer(
            from_vessel=self.separation_vessel,
            to_vessel=self.lower_phase_vessel,
            volume=SEPARATION_DEFAULT_PRIMING_VOLUME,
            aspiration_speed=SEPARATION_DEFAULT_INITIAL_PUMP_SPEED,
            move_speed=SEPARATION_DEFAULT_MID_PUMP_SPEED,
            dispense_speed=SEPARATION_DEFAULT_END_PUMP_SPEED,
            to_port=self.lower_phase_port,
            through=self.lower_phase_through
        )

    def lower_phase_stepwise_withdraw_step(self):
        steps = [
            Transfer(
                from_vessel=self.separation_vessel,
                to_vessel=self.separation_vessel_pump,
                volume=self.step_volume,
                aspiration_speed=SEPARATION_DEFAULT_INITIAL_PUMP_SPEED,
                move_speed=SEPARATION_DEFAULT_MID_PUMP_SPEED,
                dispense_speed=SEPARATION_DEFAULT_END_PUMP_SPEED,
                to_port=self.lower_phase_port,
                through=self.lower_phase_through
            )
        ]

        if self.pump_current_volume + self.step_volume > self.pump_max_volume:
            steps.insert(0, self.lower_phase_separation_pump_dispense_step())
            self.pump_current_volume = 0
        self.pump_current_volume += self.step_volume
        return steps

    def lower_phase_separation_pump_dispense_step(self):
        return Transfer(
            from_vessel=self.separation_vessel_pump,
            to_vessel=self.lower_phase_vessel,
            to_port=self.lower_phase_port,
            volume=self.pump_current_volume,
            aspiration_speed=SEPARATION_DEFAULT_INITIAL_PUMP_SPEED,
            move_speed=SEPARATION_DEFAULT_MID_PUMP_SPEED,
            dispense_speed=SEPARATION_DEFAULT_END_PUMP_SPEED,
            through=self.lower_phase_through
        )

    def upper_phase_withdraw_step(self):
        if self.separation_vessel == self.upper_phase_vessel:
            return []
        else:
            return [Transfer(
                from_vessel=self.separation_vessel,
                to_vessel=self.upper_phase_vessel,
                volume=self.separation_vessel_max_volume,
                aspiration_speed=SEPARATION_DEFAULT_INITIAL_PUMP_SPEED,
                move_speed=SEPARATION_DEFAULT_MID_PUMP_SPEED,
                dispense_speed=SEPARATION_DEFAULT_END_PUMP_SPEED,
                to_port=self.upper_phase_port,
                through=self.upper_phase_through
            )]

    def dead_volume_withdraw_step(self):
        if self.dead_volume_vessel:
            return [Transfer(
                from_vessel=self.separation_vessel,
                to_vessel=self.dead_volume_vessel,
                volume=SEPARATION_DEAD_VOLUME,
                aspiration_speed=SEPARATION_DEFAULT_INITIAL_PUMP_SPEED,
                move_speed=SEPARATION_DEFAULT_MID_PUMP_SPEED,
                dispense_speed=SEPARATION_DEFAULT_END_PUMP_SPEED,
                to_port=self.dead_volume_port,
                through=self.dead_volume_through
            )]
        return []

    def on_conductivity_sensor_reading(self, reading):
        # Simulation, continue
        if reading == -1:
            self.logger.info('Phase separation complete.')
            self.done = True

        elif self.readings:
            self.readings.append(reading)
            self.logger.info("Sensor reading is {0}.".format(self.readings[-1]))
            if not self.discriminant(self.readings):
                self.logger.info("Nope still the same phase.")
            else:
                self.logger.info("Phase changed! Hurrah!")
                self.done = True

        else:
            self.readings = [reading]
