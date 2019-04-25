from typing import List
from .base_step import Step
from .steps_base import CConnect, CValveMoveToPosition

def get_vacuum_valve_reconnect_steps(
    vessel: str,
    inert_gas: str,
    vacuum_valve: str,
    valve_unused_port: str
) -> List[Step]:
    if inert_gas:
        return [CConnect(
            from_vessel=inert_gas, to_vessel=vessel)]
    elif vacuum_valve:
        return [CValveMoveToPosition(
            valve_name=vacuum_valve, position=valve_unused_port)]
    return []