from .....step_utils.base_steps import AbstractStep
from ..steps_base import CSwitchVacuum, CSwitchArgon
from .general import Wait
from ...utils.execution import get_pneumatic_controller

#: Time to wait after switching between argon/vacuum for pressure to change.
WAIT_AFTER_SWITCH_TIME = 30  # s

class SwitchVacuum(AbstractStep):
    """Supply given vessel with vacuum using PneumaticController.

    Args:
        vessel (str): Vessel to supply with vacuum.
        port (str): Port of vessel to supply with vacuum.
        pneumatic_controller (str): Internal property. Node name of pneumatic
            controller.
        pneumatic_controller_port (str): Internal property. Port of pneumatic
            controller attached to correct port of vessel.
    """

    DEFAULT_PROPS = {
        'after_switch_wait': '30 seconds',
    }

    INTERNAL_PROPS = [
        'pneumatic_controller',
        'pneumatic_controller_port',
    ]

    PROP_TYPES = {
        'vessel': str,
        'port': str,
        'after_switch_wait': float,
        'pneumatic_controller': str,
        'pneumatic_controller_port': str
    }

    def __init__(
        self,
        vessel: str,
        port: str = None,
        after_switch_wait: float = 'default',

        # Internal properties
        pneumatic_controller: str = None,
        pneumatic_controller_port: str = None,
        **kwargs,
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.pneumatic_controller:
            self.pneumatic_controller, self.pneumatic_controller_port =\
                get_pneumatic_controller(graph, self.vessel, self.port)

    def get_steps(self):
        steps = [
            CSwitchVacuum(
                pneumatic_controller=self.pneumatic_controller,
                port=self.pneumatic_controller_port
            ),
        ]
        if self.after_switch_wait:
            steps.append(
                Wait(time=self.after_switch_wait)
            )
        return steps

class SwitchArgon(AbstractStep):
    """Supply given vessel with argon using PneumaticController.

    Args:
        vessel (str): Vessel to supply with argon.
        port (str): Port of vessel to supply with argon.
        pressure (str): Argon pressure. 'high' or 'low'. Defaults to 'low'.
        pneumatic_controller (str): Internal property. Node name of pneumatic
            controller.
        pneumatic_controller_port (str): Internal property. Port of pneumatic
            controller attached to correct port of vessel.
    """

    DEFAULT_PROPS = {
        'after_switch_wait': '30 seconds',
    }

    INTERNAL_PROPS = [
        'pneumatic_controller',
        'pneumatic_controller_port',
    ]

    PROP_TYPES = {
        'vessel': str,
        'port': str,
        'pressure': str,
        'after_switch_wait': float,
        'pneumatic_controller': str,
        'pneumatic_controller_port': str
    }

    def __init__(
        self,
        vessel: str,
        port: str = None,
        pressure: str = 'low',
        after_switch_wait: float = None,

        # Internal properties
        pneumatic_controller: str = None,
        pneumatic_controller_port: str = None,
        **kwargs,
    ) -> None:
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.pneumatic_controller:
            self.pneumatic_controller, self.pneumatic_controller_port =\
                get_pneumatic_controller(graph, self.vessel, self.port)

    def get_steps(self):
        steps = [
            CSwitchArgon(
                pneumatic_controller=self.pneumatic_controller,
                port=self.pneumatic_controller_port,
                pressure=self.pressure
            )
        ]
        if self.after_switch_wait:
            steps.append(
                Wait(time=self.after_switch_wait)
            )
        return steps
