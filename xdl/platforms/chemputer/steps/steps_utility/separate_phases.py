from ...constants import BOTTOM_PORT, VALID_PORTS
from .....utils.errors import XDLError
from .....utils.misc import SanityCheck
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

SEPARATION_DEFAULT_INITIAL_PUMP_SPEED_CART = 10
SEPARATION_DEFAULT_MID_PUMP_SPEED_CART = 5
SEPARATION_DEFAULT_END_PUMP_SPEED_CART = 5

class SeparatePhases(AbstractDynamicStep):

    PROP_TYPES = {
        'separation_vessel': str,
        'lower_phase_vessel': str,
        'upper_phase_vessel': str,
        'dead_volume_vessel': str,
        'step_volume': float,
        'lower_phase_port': str,
        'upper_phase_port': str,
        'dead_volume_port': str,
        'lower_phase_through': str,
        'upper_phase_through': str,
        'dead_volume_through': str,
        'failure_vessel': str,
        'max_retries': int
    }

    FINISH = 0  # Finish successfully
    READ_CONDUCTIVITY = 1  # Take conductivity measurement
    WITHDRAW = 2  # Withdraw more liquid
    RETRY = 3  # Try separation again if phase change undetected
    TERMINATE = 4  # If phase change undetected 3 times graceful exit.
    RAISE_ERROR = 5  # Raise the error once done

    pump_max_volume = None
    conductivity_sensor = None
    separation_vessel_pump = None
    can_retry = True

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
        failure_vessel: str = None,
        max_retries: int = 2,
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
        self.continue_options = {
            self.FINISH: lambda: [],
            self.READ_CONDUCTIVITY: self.continue_read_conductivity,
            self.WITHDRAW: self.continue_withdraw,
            self.RETRY: self.continue_retry,
            self.TERMINATE: self.continue_terminate,
            self.RAISE_ERROR: self.continue_raise_error
        }
        self.discriminant = self.default_discriminant(True, True)
        self.reset()

    def reset(self, retries=True):
        self.pump_current_volume = 0  # Current volume in separation vessel pump
        self.readings = []
        if retries:
            self.retries = 0
        self.total_withdrawn = 0
        self.continue_option = self.READ_CONDUCTIVITY
        self.done = False

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
        self.graph = graph
        self.check_if_can_retry(graph)
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

    def get_pump_speeds(self, through):
        if through:
            self.init_pump_speed = SEPARATION_DEFAULT_INITIAL_PUMP_SPEED_CART
            self.mid_pump_speed = SEPARATION_DEFAULT_MID_PUMP_SPEED_CART
            self.end_pump_speed = SEPARATION_DEFAULT_END_PUMP_SPEED_CART
        else:
            self.init_pump_speed = SEPARATION_DEFAULT_INITIAL_PUMP_SPEED
            self.mid_pump_speed = SEPARATION_DEFAULT_MID_PUMP_SPEED
            self.end_pump_speed = SEPARATION_DEFAULT_END_PUMP_SPEED

    def check_if_can_retry(self, graph):
        if self.lower_phase_vessel:
            if graph.nodes[
                    self.lower_phase_vessel]['class'] == 'ChemputerWaste':
                self.can_retry = False

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=self.lower_phase_vessel,
            ),
            SanityCheck(
                condition=self.upper_phase_vessel,
            ),
            SanityCheck(
                condition=self.separation_vessel,
            ),
            SanityCheck(
                condition=self.separation_vessel_pump,
            ),
        ]

    def final_sanity_check(self, graph):
        super().final_sanity_check(graph)
        self.sanity_check_transfer_ports(graph)

    def sanity_check_transfer_ports(self, graph):
        # Check that no incorrect ports are being used. Added as a bug with an
        # invalid port assigned threw no errors in simulation, and messed up a
        # physical run.
        for fn in [
            self.lower_phase_stepwise_withdraw_step,
            self.lower_phase_separation_pump_dispense_step,
            self.prime_sensor_step,
            self.upper_phase_withdraw_step,
            self.dead_volume_withdraw_step,
            self.continue_retry,
        ]:
            steps = fn()
            if type(steps) != list:
                steps = [steps]
            for step in steps:
                if type(step) == Transfer:
                    self.test_valid_transfer_ports(graph, step)

    def test_valid_transfer_ports(self, graph, step):
        if step.from_port is not None:
            from_class = graph.nodes[step.from_vessel]['class']
            try:
                assert str(step.from_port) in VALID_PORTS[from_class]
            except AssertionError:
                raise XDLError(
                    f'"{step.from_port}" is not a valid port for {from_class}')
        if step.to_port is not None:
            to_class = graph.nodes[step.to_vessel]['class']
            try:
                assert str(step.to_port) in VALID_PORTS[to_class]
            except AssertionError:
                raise XDLError(
                    f'"{step.to_port}" is not a valid port for {to_class}')

    def on_start(self):
        """Initial conductivity sensor reading."""
        self.continue_option = self.WITHDRAW
        return [
            self.prime_sensor_step(),
            ReadConductivitySensor(
                sensor=self.conductivity_sensor,
                on_reading=self.on_conductivity_sensor_reading
            ),
        ]

    def on_continue(self):
        """Either finish, take conductivity reading, or withdraw more liquid."""
        if self.done:
            return []
        else:
            return self.continue_options[self.continue_option]()

    def continue_read_conductivity(self):
        """Read conductivity."""
        self.continue_option = self.WITHDRAW
        return [
            ReadConductivitySensor(
                sensor=self.conductivity_sensor,
                on_reading=self.on_conductivity_sensor_reading
            )
        ]

    def continue_withdraw(self):
        """Withdraw."""
        self.continue_option = self.READ_CONDUCTIVITY
        steps = self.lower_phase_stepwise_withdraw_step()

        # If phase separation unsuccessful
        if self.total_withdrawn >= self.separation_vessel_max_volume:
            # Either retry or raise XDLError.
            if self.retries < self.max_retries and self.can_retry:
                self.logger.info('Separation failed. Retrying...')
                self.continue_option = self.RETRY
            else:
                self.continue_option = self.TERMINATE
        return steps

    def continue_retry(self):
        self.retries += 1
        steps = []
        if self.pump_max_volume:
            steps.append(self.lower_phase_separation_pump_dispense_step())
        steps.append(
            Transfer(
                from_vessel=self.lower_phase_vessel,
                from_port=self.lower_phase_port,
                to_vessel=self.separation_vessel,
                to_port=BOTTOM_PORT,
                volume=self.total_withdrawn,
            )
        )
        self.reset(retries=False)
        steps.extend(self.on_start())
        return steps

    def continue_terminate(self):
        self.continue_option = self.RAISE_ERROR

        steps = []
        steps.append(
            Transfer(
                from_vessel=self.separation_vessel_pump,
                to_vessel=self.failure_vessel,
                volume=self.pump_current_volume,
                aspiration_speed=SEPARATION_DEFAULT_INITIAL_PUMP_SPEED,
                move_speed=SEPARATION_DEFAULT_MID_PUMP_SPEED,
                dispense_speed=SEPARATION_DEFAULT_END_PUMP_SPEED,
            )
        )

        steps.append(
            Transfer(
                from_vessel=self.lower_phase_vessel,
                to_vessel=self.failure_vessel,
                volume=self.total_withdrawn - self.pump_current_volume
            )
        )

        return steps

    def continue_raise_error(self):
        raise XDLError(
            f'Attempted and failed separation {self.retries + 1} times.\
Lower phase sent to \"{self.failure_vessel}\".\n\
Please check the appropriate log files for conductivity sensor readings.\
\n{self.properties}')

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

    def prime_sensor_step(self):
        self.get_pump_speeds(self.lower_phase_through)
        return Transfer(
            from_vessel=self.separation_vessel,
            to_vessel=self.lower_phase_vessel,
            volume=SEPARATION_DEFAULT_PRIMING_VOLUME,
            aspiration_speed=self.init_pump_speed,
            move_speed=self.mid_pump_speed,
            dispense_speed=self.end_pump_speed,
            to_port=self.lower_phase_port,
            through=self.lower_phase_through
        )

    def lower_phase_stepwise_withdraw_step(self):
        self.get_pump_speeds(self.lower_phase_through)
        steps = [
            Transfer(
                from_vessel=self.separation_vessel,
                to_vessel=self.separation_vessel_pump,
                volume=self.step_volume,
                aspiration_speed=self.init_pump_speed,
                move_speed=self.mid_pump_speed,
                dispense_speed=self.end_pump_speed,
            )
        ]

        if self.pump_current_volume + self.step_volume > self.pump_max_volume:
            steps.insert(0, self.lower_phase_separation_pump_dispense_step())
            self.pump_current_volume = 0
        self.pump_current_volume += self.step_volume
        self.total_withdrawn += self.step_volume
        return steps

    def lower_phase_separation_pump_dispense_step(self):
        self.get_pump_speeds(self.lower_phase_through)
        return Transfer(
            from_vessel=self.separation_vessel_pump,
            to_vessel=self.lower_phase_vessel,
            to_port=self.lower_phase_port,
            volume=self.pump_current_volume,
            aspiration_speed=self.init_pump_speed,
            move_speed=self.mid_pump_speed,
            dispense_speed=self.end_pump_speed,
            through=self.lower_phase_through
        )

    def upper_phase_withdraw_step(self):
        self.get_pump_speeds(self.upper_phase_through)
        if self.separation_vessel == self.upper_phase_vessel:
            return []
        else:
            return [Transfer(
                from_vessel=self.separation_vessel,
                to_vessel=self.upper_phase_vessel,
                volume=self.separation_vessel_max_volume,
                aspiration_speed=self.init_pump_speed,
                move_speed=self.mid_pump_speed,
                dispense_speed=self.end_pump_speed,
                to_port=self.upper_phase_port,
                through=self.upper_phase_through
            )]

    def dead_volume_withdraw_step(self):
        if self.dead_volume_vessel:
            self.get_pump_speeds(self.dead_volume_through)
            return [Transfer(
                from_vessel=self.separation_vessel,
                to_vessel=self.dead_volume_vessel,
                volume=SEPARATION_DEAD_VOLUME,
                aspiration_speed=self.init_pump_speed,
                move_speed=self.mid_pump_speed,
                dispense_speed=self.end_pump_speed,
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
