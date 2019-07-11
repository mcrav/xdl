from ..base_steps import AbstractStep
from ..steps_base import CSwitchVacuum, CSwitchArgon
from  .general import Wait

#: Time to wait after switching between argon/vacuum for pressure to change.
WAIT_AFTER_SWITCH_TIME = 30 # s

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
    def __init__(
        self,
        vessel: str,
        port: str = None,
        pneumatic_controller: str = None,
        pneumatic_controller_port: str = None,
        **kwargs,
    ) -> None:
        super().__init__(locals())

    def get_steps(self):
        return [
            CSwitchVacuum(
                pneumatic_controller=self.pneumatic_controller,
                port=self.pneumatic_controller_port
            ),
            Wait(time=WAIT_AFTER_SWITCH_TIME)
        ]

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
    def __init__(
        self,
        vessel: str,
        port: str = None,
        pressure: str = 'low',
        pneumatic_controller: str = None,
        pneumatic_controller_port: str = None,
        **kwargs,
    ) -> None:
        super().__init__(locals())

    def get_steps(self):
        return [
            CSwitchArgon(
                pneumatic_controller=self.pneumatic_controller,
                port=self.pneumatic_controller_port,
                pressure=self.pressure
            ),
            Wait(time=WAIT_AFTER_SWITCH_TIME)
        ]
