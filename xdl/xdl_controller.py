from .execution.chemputer import XDLExecutor
import inspect
import re
from .steps.chemputer import steps_synthesis
from .steps.chemputer import steps_utility
from .steps.chemputer import steps_base
from .steps import Step, AbstractStep, AbstractBaseStep, AbstractAsyncStep, AbstractDynamicStep
from .utils.errors import XDLError

def make_xdl_controller(platform='chemputer'):
    """Generates XDLController class. This is a class that has methods corresponding
    to all the XDL steps,
    e.g. xdl_controller.add(reagent='water', vessel='reactor', volume='10 mL')
    """
    if platform != 'chemputer':
        raise XDLError('XDLController only supported for Chemputer.')

    class_name = 'XDLController'
    superclasses = ()
    attributes_dict = {
        '__init__': xdl_controller_init,
    }
    for step_module in [steps_synthesis, steps_utility, steps_base]:
        for step_name, step_class in inspect.getmembers(step_module, inspect.isclass):
            # Exclude unrelated classes and abstract base step classes.
            if not issubclass(step_class, Step) and not step_class in [
                Step, AbstractStep, AbstractBaseStep, AbstractAsyncStep, AbstractDynamicStep]:
                continue
            # Get snake case method name
            method_name = get_method_name(step_name)

            # If method name not already in attributes dict create method and
            # add to attributes dict.
            if not method_name in attributes_dict:
                # Define method. step_class must be defined as keyword argument
                # so that the current value of step_class is used. Not the value of
                # step_class when the method is called.
                def step_method(self, step_class=step_class, **kwargs):
                    block = [step_class(**kwargs)]
                    self.executor.prepare_block_for_execution(self.graph, block)
                    block[0].execute(self.chempiler)

                # Add Method to attributes
                attributes_dict[method_name] = step_method
    return type(class_name, superclasses, attributes_dict)

def get_method_name(class_name):
    """Pascal case -> snake case"""
    return re.sub(r'(?<!^)([A-Z])', r'_\1', class_name).lower()

def xdl_controller_init(self, chempiler):
    """Initialise XDL controller."""
    self.graph = chempiler.graph.graph
    self.executor = XDLExecutor()
    self.chempiler = chempiler

XDLController = make_xdl_controller()
