from typing import Optional
from ..base_step import Step
from ..steps_base import CMove, CConnect
from ..steps_utility import StopStir, Wait
from ...constants import BOTTOM_PORT, DEFAULT_FILTER_EXCESS_REMOVE_FACTOR

class Filter(Step):
    """Filter contents of filter vessel. Apply vacuum for given time.
    Assumes liquid is already in the top of the filter vessel.

    Args:
        filter_vessel (str): Filter vessel.
        filter_top_volume (float): Volume (mL) of contents of filter top.
        wait_time (float): Time to leave vacuum on filter vessel after contents
            have been moved. (optional)
        aspiration_speed (float): Speed in mL / min to draw liquid from
            filter_vessel.
        waste_vessel (float): Given internally. Vessel to move waste material to.
        filtrate_vessel (str): Optional. Vessel to send filtrate to. Defaults to
            waste_vessel.
        vacuum (str): Given internally. Name of vacuum flask.
        inert_gas (str): Given internally. Name of node supplying inert gas.
            Only used if inert gas filter dead volume method is being used.
    """
    def __init__(
        self,
        filter_vessel: str,
        filter_top_volume: Optional[float] = 0,
        wait_time: Optional[float] = 'default',
        aspiration_speed: Optional[float] = 'default',
        waste_vessel: Optional[str] = None,
        filtrate_vessel: Optional[str] = None,
        vacuum: Optional[str] = None,
        inert_gas: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        if not filtrate_vessel:
            filtrate_vessel = self.waste_vessel

        self.steps = [
            StopStir(vessel=self.filter_vessel),
            # Move the filter top volume from the bottom to the waste.
            CMove(
                from_vessel=self.filter_vessel,
                to_vessel=filtrate_vessel,
                from_port=BOTTOM_PORT,
                volume=self.filter_top_volume * DEFAULT_FILTER_EXCESS_REMOVE_FACTOR,
                aspiration_speed=self.aspiration_speed),
            # Connect the vacuum.
            CConnect(from_vessel=self.filter_vessel, to_vessel=self.vacuum,
                     from_port=BOTTOM_PORT),
            Wait(time=self.wait_time),
        ]

        if self.inert_gas:
            self.steps.append(
                CConnect(
                    from_vessel=self.inert_gas, to_vessel=self.filter_vessel))

        self.human_readable = 'Filter contents of {filter_vessel}.'.format(
            **self.properties)

        self.movements = [
            (self.filter_vessel, self.waste_vessel, 'all'),
        ]

        self.requirements = {
            'filter_vessel': {
                'filter': True
            }
        }