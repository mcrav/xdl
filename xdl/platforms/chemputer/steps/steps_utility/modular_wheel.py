from typing import Optional
from .liquid_handling import Transfer
from .....utils.misc import SanityCheck
from ...utils.execution import node_in_graph
from .....step_utils.base_steps import AbstractStep
from ..base_step import ChemputerStep
from ..steps_base.commanduino_labware import CTurnMotor

class MWAddAndTurn(ChemputerStep, AbstractStep):
    """Step for transfering liquid to the modular wheel and rotating it.

    Args:
        from_vessel (str): Vessel to move the liquid from
        to_vessel (str): Vessel to move the liquid to
        volume (float, optional): Volume to transfer
        motor_name (str, optional): Name of the motor on the modular wheel
        n_turns (int, optional): Number of turns to perform
    """

    DEFAULT_PROPS = {
        'volume': '25 mL',
        'motor_name': 'X',
        'n_turns': 1
    }

    PROP_TYPES = {
        'from_vessel': str,
        'to_vessel': str,
        'volume': float,
        'motor_name': str,
        'n_turns': int
    }

    def __init__(
        self,
        from_vessel: str,
        to_vessel: str,
        volume: Optional[float] = 'default',
        motor_name: Optional[str] = 'default',
        n_turns: Optional[int] = 'default'
    ):
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        pass

    def get_steps(self):
        return [
            Transfer(
                from_vessel=self.from_vessel,
                to_vessel=self.to_vessel,
                volume=self.volume),
            CTurnMotor(
                device_name=self.to_vessel,
                motor_name=self.motor_name,
                n_turns=self.n_turns
            )
        ]

    def sanity_checks(self, graph):
        return [
            SanityCheck(
                condition=self.from_vessel and node_in_graph(
                    graph, self.from_vessel),
                error_msg="from_vessel must be node in the graph"
            ),
            SanityCheck(
                condition=self.to_vessel and node_in_graph(
                    graph, self.to_vessel),
                error_msg="to_vessel must be node in the graph"
            ),
            SanityCheck(
                condition=(0 <= self.volume < 100),
                error_msg="Volume must be between 0 and 100 mL"
            )
        ]
