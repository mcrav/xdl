from typing import Callable
import time
import queue
from ..base_steps import AsyncStep

CHECK_IF_COMPLETE_INTERVAL: int = 5 # seconds

class RunNMR(AsyncStep):
    """Run NMR experiment asynchronously and pass obtained spectrum to
    callback function.

    Args:
        nmr (str): Node name of NMR in graph.
        on_finish (Callable): Callback function. Must take spectrum as arg
            (spectrum is a list of numpy complex numbers).
    """
    def __init__(self, nmr: str, on_finish: Callable) -> None:
        super().__init__(locals())

    def async_execute(self, chempiler, logger=None):
        nmr = chempiler[self.nmr]
        nmr.shim()
        nmr.proton() # Run NMR experiment

        while True:
            # Wait
            time.sleep(CHECK_IF_COMPLETE_INTERVAL)

            # Check if spectrum has been obtained
            spectrum = nmr.get_spectrum()

            if spectrum != None:
                # Pass spectrum to on_finish callback.
                self.on_finish(spectrum)
                return

            else:
                # Check if should return
                if self._kill:
                    return
