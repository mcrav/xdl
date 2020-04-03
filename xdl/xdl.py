import os
import logging
import copy
from typing import List, Dict, Any
from math import ceil

from .graphgen_deprecated import get_graph

from .utils import get_logger
from .steps import Step, AbstractBaseStep, UnimplementedStep
from .utils.errors import XDLError
from .readwrite.interpreter import xdl_file_to_objs, xdl_str_to_objs
from .readwrite import XDLGenerator
from .hardware import Hardware
from .reagents import Reagent
from .platforms.abstract_platform import AbstractPlatform
from .platforms.modular_wheel import ModularWheelPlatform

class XDL(object):
    """
    Interpets XDL (file or str) and provides an object for further use.
    """
    def __init__(
        self,
        xdl: str = None,
        steps: List[Step] = None,
        hardware: Hardware = None,
        reagents: List[Reagent] = None,
        logging_level: int = logging.INFO,
        platform: str = 'chemputer',
    ) -> None:
        """Init method for XDL object.
        One of xdl or (steps, hardware and reagents) must be given.

        Args:
            xdl(str, optional): Path to XDL file or XDL str.
            steps (List[Step], optional): List of Step objects.
            hardware (Hardware, optional): Hardware object containing all
                components in XDL.
            reagents (List[Reagent], optional): List of Reagent objects.
            logger (logging.Logger): Logger object to use. If not given will
                be made.
            platform (str): Platform to run XDL on. 'chemputer' or 'chemobot'.

        Raises:
            ValueError: If insufficient args provided to instantiate object.
        """
        self.logger = get_logger()
        self.logger.setLevel(logging_level)
        self.logging_level = logging_level

        self._xdl_file = None
        self.graph_sha256 = None
        self.prepared = False
        self._validate_platform(platform)
        if xdl:
            parsed_xdl = {}
            if os.path.exists(xdl):
                self._xdl_file = xdl
                parsed_xdl = xdl_file_to_objs(
                    xdl_file=xdl, logger=self.logger, platform=self.platform)

            # Check XDL is XDL str and not just mistyped XDL file path.
            elif '<Synthesis' in xdl and '<Procedure>' in xdl:
                parsed_xdl = xdl_str_to_objs(
                    xdl_str=xdl, logger=self.logger, platform=self.platform)
            else:
                raise ValueError(
                    f"Can't instantiate XDL from this: \n{xdl}"
                )
            if parsed_xdl:
                self.steps = parsed_xdl['steps']
                self.hardware = parsed_xdl['hardware']
                self.reagents = parsed_xdl['reagents']
                # Get attrs from <Synthesis> tag.
                for k, v in parsed_xdl['procedure_attrs'].items():
                    setattr(self, k, v)
                self.executor = self.platform.executor(self)

            else:
                self.logger.info('Invalid XDL given.')

        elif (steps is not None
              and reagents is not None
              and hardware is not None):
            self.steps, self.hardware, self.reagents = steps, hardware, reagents
            self.executor = self.platform.executor(self)
        else:
            raise ValueError(
                "Can't create XDL object. Insufficient args given to __init__\
 method.")

    def _validate_platform(self, platform):
        if platform == 'chemputer':
            from chemputerxdl import ChemputerPlatform
            self.platform = ChemputerPlatform()
        elif platform == 'modular_wheel':
            self.platform = ModularWheelPlatform()
        elif issubclass(platform, AbstractPlatform):
            self.platform = platform()
        else:
            raise XDLError(f'{platform} is an invalid platform. Platform must\
 be "chemputer", "modular_wheel" or a subclass of AbstractPlatform.')

    def _get_exp_id(self, default: str = 'xdl_exp') -> str:
        """Get experiment ID name to give to the Chempiler."""
        if self._xdl_file:
            return os.path.splitext(os.path.split(self._xdl_file)[-1])[0]
        return default

    def climb_down_tree(
        self, step: Step, print_tree: bool = False, lvl: int = 0
    ) -> List[Step]:
        """Go through given step's sub steps recursively until base steps are
        reached. Return list containing the step, all sub steps and all base
        steps.

        Args:
            step (Step): step to find all sub steps for.
            print_tree (bool, optional): Defaults to False.
                Print tree as well as returning it.
            lvl (int, optional): Level of recursion. Defaults to 0.
                Used to determine indent level when print_tree=True.

        Returns:
            List[Step]: List of all Steps involved with given step.
                        Includes given step, and all sub steps all the way down
                        to base steps.
        """
        indent = '  '
        tree = [step]
        if print_tree:
            self.logger.info('{0}{1}'.format(indent * lvl, step.name))
        if isinstance(step, AbstractBaseStep):
            return tree
        else:
            lvl += 1
            for step in step.steps:
                if isinstance(step, AbstractBaseStep):
                    if print_tree:
                        self.logger.info(
                            '{0}{1}'.format(indent * lvl, step.name))
                    tree.append(step)
                    continue
                else:
                    tree.extend(
                        self.climb_down_tree(
                            step, print_tree=print_tree, lvl=lvl))
        return tree

    def _get_full_xdl_tree(self) -> List[Step]:
        """
        Return list of all steps after unpacking nested steps.
        Root steps are included followed by all their children in order,
        recursively.

        Returns:
            List[Step]
        """
        tree = []
        for step in self.steps:
            tree.extend(self.climb_down_tree(step))
        return tree

    def print_full_xdl_tree(self) -> None:
        """Print nested structure of all steps in XDL procedure."""
        self.logger.info('\nOperation Tree\n--------------\n')
        for step in self.steps:
            self.climb_down_tree(step, print_tree=True)
        self.logger.info('\n')

    def human_readable(self, language='en') -> str:
        """Return human-readable English description of XDL procedure.

        Arguments:
            language (str): Language code corresponding to language that should
                be used. If language code not supported error message will be
                logged and no human_readable text will be logged.

        Returns:
            str: Human readable description of procedure.
        """
        if self.platform == 'chemobot':
            return '\n'.join([step.name for step in self.steps])
        s = ''
        available_languages = self.get_available_languages()
        if language in available_languages:
            for i, step in enumerate(self.steps):
                s += f'{i+1}) {step.human_readable(language=language)}\n'
        else:
            self.logger.error(f'Language {language} not supported. Available\
 languages: {", ".join(available_languages)}')
        return s

    def get_available_languages(self) -> List[str]:
        """Get languages for which every step in human readable can output
        human_readable text in that language.

        Returns:
            List[str]: List of language codes, e.g. ['en', 'zh']
        """
        available_languages = []
        for _, human_readables in self.platform.localisation.items():
            for language in human_readables:
                if language not in available_languages:
                    available_languages.append(language)
        return available_languages

    def log_human_readable(self) -> None:
        """Log human-readable English description of XDL procedure."""
        self.logger.info('Synthesis Description\n---------------------\n')
        self.logger.info('{0}\n'.format(self.human_readable()))

    def save_human_readable(self, save_file: str) -> None:
        """Save human readable description of procedure to given path."""
        with open(save_file, 'w') as fileobj:
            fileobj.write(self.human_readable())

    def as_string(self) -> str:
        """Return XDL str of procedure."""
        self._xdlgenerator = XDLGenerator(steps=self.steps,
                                          hardware=self.hardware,
                                          reagents=self.reagents)
        return self._xdlgenerator.as_string()

    def save(self, save_file: str, full_properties: bool = False) -> str:
        """Save as XDL file.

        Args:
            save_file (str): File path to save XDL to.
            full_properties (bool): If True, all properties will be included.
                If False, only properties that differ from their default values
                will be included.
                Including full properties is recommended for making XDL files
                that will stand the test of time, as defaults may change in new
                versions of XDL.
        """
        self._xdlgenerator = XDLGenerator(steps=self.steps,
                                          hardware=self.hardware,
                                          reagents=self.reagents,
                                          full_properties=full_properties)
        self._xdlgenerator.save(save_file)

    def scale_procedure(self, scale: float) -> None:
        """Scale all volumes and masses in procedure.

        Args:
            scale (float): Number to scale all volumes and masses by.
        """
        for step in self.steps:
            self.apply_scaling(step, scale)

    def apply_scaling(self, step: Step, scale: float) -> None:
        """Apply scale to steps, recursively applying to any child steps if the
        step has the attribute 'children', e.g. Repeat steps.

        Args:
            step (Step): Step to apply scaling to.
            scale (float): Amount to scale volumes and masses.
        """
        step.scale(scale)
        if hasattr(step, 'children') and step.children:
            for substep in step.children:
                self.apply_scaling(substep, scale)

    @property
    def estimated_duration(self) -> float:
        """Estimated duration of procedure. It is approximate but should give a
        give a rough idea how long the procedure should take.

        Returns:
            float: Estimated runtime of procedure in seconds.
        """
        if not self.prepared:
            self.logger.warning(
                'prepare_for_execution must be called before estimated duration\
 can be calculated.')
            return

        duration = 0
        for step in self.steps:
            duration += step.duration(self.executor._graph)
        return duration

    def print_estimated_duration(self) -> None:
        """Format estimated duration into hours, minutes and seconds and log it
        like "Estimated duration: 19 hrs 30 mins".
        """
        s = ''
        seconds = self.estimated_duration
        if seconds < 60:
            s = f'{ceil(seconds):.0f} seconds'
        else:
            seconds_remainder = seconds % 60
            minutes = (seconds - seconds_remainder) / 60
            if minutes < 60:
                s = f'{minutes+1:.0f} mins'
            else:
                minutes_remainder = minutes % 60
                hours = (minutes - minutes_remainder) / 60
                minutes = minutes - (hours * 60)
                s = f'{hours:.0f} hrs {minutes+1:.0f} mins'
        self.logger.info(f'    Estimated duration: {s}')

    @property
    def reagent_volumes(self) -> Dict:
        """Compute volumes used of all liquid reagents in procedure and return
        as dict.

        Returns:
            Dict[str, float]: Dict of { reagent_name: volume_used... }
        """

        if not self.prepared:
            raise XDLError(
                'prepare_for_execution must be called before reagent volumes\
 can be calculated.')

        reagents_consumed = {}
        for step in self.steps:
            step_reagents_consumed = step.reagents_consumed(
                self.executor._graph)
            for reagent, volume in step_reagents_consumed.items():
                if reagent in reagents_consumed:
                    reagents_consumed[reagent] += volume
                else:
                    reagents_consumed[reagent] = volume
        return reagents_consumed

    def print_reagent_volumes(self) -> None:
        """Pretty print table of reagent volumes used in procedure.
        """
        reagent_volumes = self.reagent_volumes
        reagent_volumes = [
            (reagent, volume)
            for reagent, volume in reagent_volumes.items()]
        reagent_volumes = sorted(reagent_volumes, key=lambda x: 1 / x[1])
        reagent_volumes = [
            (reagent, f'{volume:.2f}'.rstrip('0').rstrip('0').rstrip('.'))
            for reagent, volume in reagent_volumes]
        if reagent_volumes:
            max_reagent_name_length = max(
                [len(reagent) for reagent, _ in reagent_volumes])
            max_volume_length = max(
                [len(volume) + 3 for _, volume in reagent_volumes])
            max_name_vol_length = max_reagent_name_length + max_volume_length
            self.logger.info(
                f'    {"Reagent Volumes":^{max_name_vol_length + 3}}')
            self.logger.info(f'    {"-" * (max_name_vol_length + 3)}')
            for reagent, volume in reagent_volumes:
                self.logger.info(
                    f'    {reagent:^{max_reagent_name_length}} | {volume} mL')
            self.logger.info('\n')

    def print_hardware_requirements(self) -> None:
        """Print new modules needed, and requirements of hardware in procedure.
        """
        vessel_requirements = {}
        new_modules_needed = []
        for step in self.steps:
            if isinstance(step, UnimplementedStep):
                new_modules_needed.extend(list(step.requirements))
            else:
                for vessel, requirements in step.requirements.items():
                    if step.properties[vessel] in vessel_requirements:
                        for req, val in requirements.items():
                            if req == 'temp' and req in vessel_requirements[
                                    step.properties[vessel]]:
                                vessel_requirements[
                                    step.properties[vessel]][req].extend(val)
                            else:
                                vessel_requirements[
                                    step.properties[vessel]][req] = val

                    else:
                        vessel_requirements[
                            step.properties[vessel]] = requirements

        self.logger.info('')
        if new_modules_needed:
            self.logger.info(f'  New Modules Needed\n{22*"-"}')
            for new_module in list(set(new_modules_needed)):
                self.logger.info(f'  -- {new_module.capitalize()}')
            self.logger.info('')

        if vessel_requirements:
            self.logger.info(f'  Hardware Requirements\n{25*"-"}')
            for vessel, reqs in vessel_requirements.items():
                self.logger.info(f'  -- {vessel}')
                self.logger.info('')
                for req, val in reqs.items():
                    if req == 'temp':
                        self.logger.info(f'    * Max temp: {max(val)} °C')
                        self.logger.info(f'    * Min temp: {min(val)} °C')
                    else:
                        self.logger.info(f'    * {req.capitalize()}')
                self.logger.info('')
            self.logger.info('')

    def graph(
        self,
        graph_template=None,
        save=None,
        **kwargs
    ):
        """Return graph to run procedure with, built on template.

        Returns:
            Dict: JSON node link graph as dictionary.
        """
        return self.platform.graph(
            self,
            template=graph_template,
            save=save,
            **kwargs
        )

    def graph_deprecated(
        self,
    ):
        """
        Here to maintain SynthReader compatibility. Eventually SynthReader
        should use new graph generator.
        """
        from chemputerxdl import ChemputerPlatform
        if type(self.platform) == ChemputerPlatform:
            liquid_reagents = [reagent.id for reagent in self.reagents]
            cartridge_reagents = []
            for step in self.steps:
                if step.name == 'Add' and step.mass:
                    if step.reagent in liquid_reagents:
                        liquid_reagents.remove(step.reagent)

                elif step.name == 'FilterThrough' and step.through:
                    cartridge_reagents.append(step.through)
            return get_graph(liquid_reagents, list(set(cartridge_reagents)))

        else:
            self.logger.info(
                'Graph generation only supported for Chemputer platform.')
            return None

    def prepare_for_execution(
        self,
        graph_file: str = None,
        interactive: bool = True,
        save_path: str = '',
        sanity_check: bool = True,
        **kwargs
    ) -> None:
        """Check hardware compatibility and prepare XDL for execution on given
        setup.

        Args:
            graph_file (str, optional): Path to graph file. May be GraphML file,
                JSON file with graph in node link format, or dict containing
                graph in same format as JSON file.
        """
        if not self.prepared:
            if not save_path:
                save_path = None
            if self._xdl_file:
                save_path = self._xdl_file.replace('.xdl', '.xdlexe')

            self.executor.prepare_for_execution(
                graph_file,
                interactive=interactive,
                save_path=save_path,
                sanity_check=sanity_check,
                **kwargs
            )

            if self.executor._prepared_for_execution:
                self.prepared = True
                self.logger.info('    Experiment Details\n')
                self.print_reagent_volumes()
                self.print_estimated_duration()

        else:
            self.logger.warning(
                'Cannot call prepare for execution twice on same XDL object.')

    def execute(self, platform_controller: Any, step: int = None) -> None:
        """Execute XDL using given platform controller object.
        self.prepare_for_execution must have been called before calling this
        method.

        Args:
            platform_controller (Any): Platform controller object instantiated
            with modules and graph to run XDL on.
        """
        # Check step not accidentally passed as platform controller
        try:
            assert type(platform_controller) not in [int, str, list, dict]
        except AssertionError:
            raise XDLError(
                f'Invalid platform controller supplied. Type:\
 {type(platform_controller)} Value: {platform_controller}')

        if (self.prepared
                or (hasattr(self, 'graph_sha256') and self.graph_sha256)):
            if hasattr(self, 'executor'):
                if step is None:
                    self.executor.execute(platform_controller)
                else:
                    try:
                        self.steps[step]
                    except IndexError:
                        raise XDLError(
                            f'Trying to execute step {step} but step list has\
 length {len(self.steps)}.')
                    self.executor.execute_step(
                        platform_controller, self.steps[step])
            else:
                raise RuntimeError(
                    'XDL executor not available. Call prepare_for_execution\
 before trying to execute.')
        else:
            self.logger.warn('prepare_for_execution must be called before\
 executing.')

    @property
    def base_steps(self):
        return [step
                for step in self._get_full_xdl_tree()
                if isinstance(step, AbstractBaseStep)]

    def __add__(self, other):
        reagents, steps, components = [], [], []
        for xdl_obj in [self, other]:
            reagents.extend(xdl_obj.reagents)
            steps.extend(xdl_obj.steps)
            components.extend(list(xdl_obj.hardware))
        new_xdl_obj = XDL(steps=steps, reagents=reagents, hardware=components)
        return new_xdl_obj

def deep_copy_step(step):
    """Return a deep copy of a step. Written this way with children handled
    specially for compatibility with Python 3.6.
    """
    children = []
    if 'children' in step.properties and step.children:
        for child in step.children:
            children.append(deep_copy_step(child))
    try:
        copy_props = {}
        for k, v in step.properties.items():
            if k != 'children':
                copy_props[k] = v
        copy_props['children'] = children
        copied_step = type(step)(**copy_props)
    except TypeError:
        raise TypeError(f'{step.name}\n\n{step.properties}')
    return copied_step

def xdl_copy(xdl_obj: XDL) -> XDL:
    """Returns a deepcopy of a XDL object. copy.deepcopy can be used with
    Python 3.7, but for Python 3.6 you have to use this.

    Args:
        xdl_obj (XDL): XDL object to copy.

    Returns:
        XDL: Deep copy of xdl_obj.
    """
    copy_steps = []
    copy_reagents = []
    copy_hardware = []

    for step in xdl_obj.steps:
        copy_steps.append(deep_copy_step(step))

    for reagent in xdl_obj.reagents:
        copy_props = copy.deepcopy(reagent.properties)
        copy_reagents.append(type(reagent)(**copy_props))

    for component in xdl_obj.hardware:
        copy_props = copy.deepcopy(component.properties)
        copy_hardware.append(type(component)(**copy_props))

    return XDL(steps=copy_steps,
               reagents=copy_reagents,
               hardware=Hardware(copy_hardware),
               logging_level=xdl_obj.logging_level)
