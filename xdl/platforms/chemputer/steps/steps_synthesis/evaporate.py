from typing import Optional, List, Dict, Any
from .....step_utils.base_steps import Step, AbstractStep
from ..steps_base import (
    CRotavapLiftDown,
    CRotavapAutoEvaporation,
)
from ..steps_utility import (
    Wait,
    Transfer,
    RotavapStopEverything,
    RotavapHeatToTemp,
    RotavapStartVacuum,
    RotavapStartRotation,
)

from ..steps_base.chiller import (
    CStartChiller,
    CStopChiller
)

from ...constants import (
    COLLECT_PORT, ROTAVAP_CLASSES, CHILLER_CLASSES, CHEMPUTER_WASTE)
from .....utils.graph import undirected_neighbors
from ...utils.execution import get_nearest_node

class Evaporate(AbstractStep):
    """Evaporate contents of given vessel at given temp and given pressure for
    given time.

    Args:
        rotavap_name (str): Name of rotavap vessel.
        temp (float): Temperature to set rotavap water bath to in °C.
        pressure (float): Pressure to set rotavap vacuum to in mbar. Has no
            effect if mode == 'auto', otherwise must be passed.
        time (float): Time to rotavap for in seconds.
        rotation_speed (float): Speed in RPM to rotate flask at.
        mode (str): 'manual' or 'auto'. If 'manual', given time/temp/pressure
            are used. If 'auto', automatic pressure/time evaluation built into
            the rotavap are used. In this case time and pressure should still be
            given, but correspond to maximum time and minimum pressure that if
            either is reached, the evaporation will stop.
    """

    DEFAULT_PROPS = {
        'time': '2 hrs',
        'rotation_speed': '150 RPM'
    }

    PROP_TYPES = {
        'rotavap_name': str,
        'temp': float,
        'pressure': float,
        'time': float,
        'rotation_speed': float,
        'mode': str,
        'waste_vessel': str,
        'collection_flask_volume': float,
        'has_chiller': bool
    }

    INTERNAL_PROPS = [
        'waste_vessel',
        'collection_flask_volume',
        'has_chiller',
    ]

    def __init__(
        self,
        rotavap_name: str,
        temp: float = 25,
        pressure: Optional[float] = None,
        time: Optional[float] = 'default',
        rotation_speed: Optional[float] = 'default',
        mode: Optional[str] = 'manual',

        # Internal properties
        waste_vessel: Optional[str] = None,
        collection_flask_volume: Optional[float] = None,
        has_chiller: bool = False,
        **kwargs
    ):
        super().__init__(locals())

    def on_prepare_for_execution(self, graph):
        if not self.collection_flask_volume:
            rotavap = graph.nodes[self.rotavap_name]
            if 'collection_flask_volume' in rotavap:
                self.collection_flask_volume = rotavap[
                    'collection_flask_volume']

        if not self.waste_vessel:
            self.waste_vessel = get_nearest_node(
                graph, self.rotavap_name, CHEMPUTER_WASTE)

        for node, data in graph.nodes(data=True):
            attached_vessels = [i for i in undirected_neighbors(graph, node)]

            if data["class"] in ROTAVAP_CLASSES:
                for vessel in attached_vessels:
                    if graph.nodes[vessel]["class"] in CHILLER_CLASSES:
                        self.has_chiller = True

    def get_chiller_steps_if_present(self, start: bool = True):
        if self.has_chiller:
            if start:
                return CStartChiller(self.rotavap_name)
            return CStopChiller(self.rotavap_name)

    def get_default_steps(self, col_vol):
        return [
            # Start rotation
            RotavapStartRotation(self.rotavap_name, self.rotation_speed),
            # Lower flask into bath.
            CRotavapLiftDown(self.rotavap_name),
            # Start chiller if present
            self.get_chiller_steps_if_present(),
            # Start vacuum
            RotavapStartVacuum(self.rotavap_name, self.pressure),
            # Start heating
            RotavapHeatToTemp(self.rotavap_name, self.temp),
            # Wait for evaporation to happen.
            Wait(time=self.time),
            # Stop evaporation.
            RotavapStopEverything(self.rotavap_name),
            # Stop chiller if present
            self.get_chiller_steps_if_present(start=False),
            # Empty collect flask
            Transfer(from_vessel=self.rotavap_name,
                     to_vessel=self.waste_vessel,
                     from_port=COLLECT_PORT,
                     volume=col_vol)
        ]

    def get_auto_steps(self, col_vol):
        pressure = 1  # 1 == auto pressure
        if self.pressure:
            # Approximation. Pressure given should be pressure solvent
            # evaporates at, but in auto evaporation, pressure is the limit
            # of the pressure ramp, so actual pressure given needs to be
            # lower.
            pressure = self.pressure / 2

        return [
            # Start rotation
            RotavapStartRotation(self.rotavap_name, self.rotation_speed),
            # Lower flask into bath.
            CRotavapLiftDown(self.rotavap_name),
            # Start chiller if present
            self.get_chiller_steps_if_present(),
            # Start heating
            RotavapHeatToTemp(self.rotavap_name, self.temp),
            # Auto Evaporation
            CRotavapAutoEvaporation(
                rotavap_name=self.rotavap_name,
                sensitivity=2,  # High sensitivity
                vacuum_limit=pressure,
                time_limit=self.time,
                vent_after=True
            ),
            # Stop evaporation.
            RotavapStopEverything(self.rotavap_name),
            # Stop chiller if present
            self.get_chiller_steps_if_present(start=False),
            # Empty collect flask
            Transfer(from_vessel=self.rotavap_name,
                     to_vessel=self.waste_vessel,
                     from_port=COLLECT_PORT,
                     volume=col_vol)
        ]

    def get_steps(self) -> List[Step]:
        collection_flask_volume = 'all'
        if self.collection_flask_volume:
            collection_flask_volume = self.collection_flask_volume

        if self.mode == "auto":
            steps = self.get_auto_steps(collection_flask_volume)
        else:
            steps = self.get_default_steps(collection_flask_volume)

        # Remove blanks
        steps = [step for step in steps if step is not None]
        return steps

    @property
    def requirements(self) -> Dict[str, Dict[str, Any]]:
        if self.temp and self.temp > 25:
            heatchill = True
        else:
            heatchill = False
        temps = []
        if self.temp:
            temps = [self.temp]
        return {
            'rotavap_name': {
                'rotavap': True,
                'heatchill': heatchill,
                'temp': temps,
            }
        }
