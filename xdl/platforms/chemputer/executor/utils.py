from typing import List
from .constants import AQUEOUS_KEYWORDS
from ....constants import VALID_PORTS
from ....utils.errors import IllegalPortError

class VesselContents(object):
    """Convenience class to represents contents of one vessel.

    Attributes:
        reagents (List[str]): List of reagents flask contains.
        volume (float): Current volume of liquid in flask.
    """
    def __init__(self, reagents: List[str] = [], volume: float = 0) -> None:
        self.reagents = reagents
        self.volume = volume

    def __str__(self):
        return f'Reagents: {", ".join(self.reagents)}\nVolume {self.volume} mL'

    def __iter__(self):
        for item in self.reagents:
            yield item

def is_aqueous(reagent_name):
    if not reagent_name:
        return False
    else:
        reagent_name = reagent_name.lower()
        for keyword in AQUEOUS_KEYWORDS:
            if keyword in reagent_name:
                return True
        return False

def validate_port(vessel, vessel_class, port):
    try:
        assert str(port) in VALID_PORTS[vessel_class]
    except AssertionError as e:
        raise IllegalPortError(f'{port} is an illegal port for {vessel}. Valid ports: {", ".join(VALID_PORTS[vessel_class])}')
