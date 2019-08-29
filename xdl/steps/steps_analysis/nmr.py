import logging
import queue
import time
from typing import Callable

from ..base_steps import AbstractBaseStep

CHECK_IF_COMPLETE_INTERVAL: int = 5 # seconds

class RunCarbon(AbstractBaseStep):
    """Run NMR experiment asynchronously and pass obtained spectrum to
    callback function.

    Args:
        nmr (str): Node name of NMR in graph.
        on_finish (Callable): Callback function. Must take spectrum as arg
            (spectrum is a list of numpy complex numbers).
    """
    def __init__(
        self,
        experiment_name:str,
        scans: int,
        repetition_time: float,
        nmr: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler: 'Chempiler', logger=None, level=0):
        nmr = chempiler[self.nmr]
        nmr.user_folder(data_path=self.experiment_name, data_folder_method="UserFolder")
        logger.info("Running carbon ...")
        nmr.carbon(options={
            "Number": str(self.scans),
            "RepetitionTime": str(self.repetition_time)})
        logger.info("Acquisition done.")
        time.sleep(5)
        return True


class RunProton(AbstractBaseStep):
    """Run NMR experiment asynchronously and pass obtained spectrum to
    callback function.

    Args:
        nmr (str): Node name of NMR in graph.
        on_finish (Callable): Callback function. Must take spectrum as arg
            (spectrum is a list of numpy complex numbers).
    """
    def __init__(
        self,
        experiment_name:str,
        nmr: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler: "Chempiler", logger=None, level=0):
        nmr = chempiler[self.nmr]
        nmr.user_folder(data_path=self.experiment_name, data_folder_method="UserFolder")
        logger.info("Running proton ...")
        nmr.proton(option="PowerScan")
        logger.info("Acquisition done.")
        time.sleep(5)
        return True


class Shim(AbstractBaseStep):
    """Run NMR experiment asynchronously and pass obtained spectrum to
    callback function.

    Args:
        nmr (str): Node name of NMR in graph.
        on_finish (Callable): Callback function. Must take spectrum as arg
            (spectrum is a list of numpy complex numbers).
    """
    def __init__(
        self,
        reference_peak: float,
        nmr: str) -> None:
        super().__init__(locals())

    def execute(self, chempiler: "Chempiler", logger=None, level=0):
        nmr = chempiler[self.nmr]
        logger.info("Shimming ...")
        nmr.shim_on_sample(reference_peak=self.reference_peak, option="QuickShim1")
        return True