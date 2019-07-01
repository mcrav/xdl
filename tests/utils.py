import os
from xdl import XDL
from xdl.steps import Confirm, Step, AbstractBaseStep
from chempiler import Chempiler
import ChemputerAPI

HERE = os.path.abspath(os.path.dirname(__file__))

def generic_chempiler_test(xdl_file: str, graph_file: str) -> None:
    """Given XDL file and graph file, try and execute Chempiler simulation
    of XDL.

    Args:
        xdl_file (str): Path to XDL file.
        graph_file (str): Path to graph file.
    """
    x = XDL(xdl_file)
    x.prepare_for_execution(graph_file, interactive=False)
    x.steps = [
        remove_confirm_steps(step) for step in x.steps]
    chempiler = Chempiler(
        experiment_code='test',
        output_dir=os.path.join(HERE, 'chempiler_output'),
        simulation=True,
        graph_file=graph_file,
        device_modules=[ChemputerAPI])
    x.execute(chempiler)

def remove_confirm_steps(step: Step) -> None:
    """Recursively remove Confirm steps from given step, going all the way down
    step tree. This needs to be done as you can't ask for input during an
    automated test.

    Args:
        step (Step): Step to remove Confirm steps from.
    """
    if isinstance(step, AbstractBaseStep): # If step is base step just return step.
        return step
    else:
        for i in reversed(range(len(step.steps))):
            if type(step.steps[i]) == Confirm:
                step.steps.pop(i)
            else:
                step.steps[i] = remove_confirm_steps(step.steps[i])
        return step
