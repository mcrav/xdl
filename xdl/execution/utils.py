from typing import List

class VesselContents(object):
    """Convenience class to represents contents of one vessel.

    Attributes:
        reagents (List[str]): List of reagents flask contains.
        volume (float): Current volume of liquid in flask.
    """
    def __init__(self, reagents: List[str] = [], volume: float = 0) -> None:
        self.reagents = reagents
        self.volume = volume