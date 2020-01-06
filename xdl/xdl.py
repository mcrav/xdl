import os
import sys
import re
import logging
import inspect
import copy
from typing import List
from math import ceil

from .constants import *
from .localisation import HUMAN_READABLE_STEPS
from .graphgen import graph_from_template
from .graphgen_deprecated import get_graph

from .utils import parse_bool, get_logger
from .steps import Step, AbstractBaseStep
from .steps.chemputer import *
from .utils.errors import XDLError
from .readwrite.interpreter import xdl_file_to_objs, xdl_str_to_objs
from .readwrite import XDLGenerator
from .hardware import Hardware
from .reagents import Reagent

# For type annotations
if False:
    from chempiler import Chempiler

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

        self._xdl_file = None
        self.auto_clean = DEFAULT_AUTO_CLEAN
        self.organic_cleaning_solvent = None
        self.graph_sha256 = None
        self.aqueous_cleaning_solvent = DEFAULT_AQUEOUS_CLEANING_SOLVENT
        self.dry_run = False
        self.filter_dead_volume_method = 'inert_gas'
        self.filter_dead_volume_solvent = None
        self.prepared = False
        self.platform = platform
        executor_class = self._get_executor_class() # Also validates platform
        if xdl:
            parsed_xdl = {}
            if os.path.exists(xdl):
                self._xdl_file = xdl
                parsed_xdl = xdl_file_to_objs(xdl, self.logger, platform=platform)
            # Check XDL is XDL str and not just mistyped XDL file path.
            elif '<Synthesis' in xdl and '<Procedure>' in xdl:
                parsed_xdl = xdl_str_to_objs(xdl, self.logger, platform=platform)
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
                self.executor = executor_class(self)

            else:
                self.logger.info('Invalid XDL given.')

        elif (steps is not None
              and reagents is not None
              and hardware is not None):
            self.steps, self.hardware, self.reagents = steps, hardware, reagents
            self.executor = executor_class(self)
        else:
            raise ValueError(
                "Can't create XDL object. Insufficient args given to __init__ method.")

    def _get_executor_class(self):
        if self.platform == 'chemputer':
            from .execution.chemputer import XDLExecutor
        elif self.platform == 'chemobot':
            from .execution.chemobot import XDLExecutor
        else:
            raise XDLError(f'Platform given: {self.platform}. Valid platforms: {", ".join(VALID_PLATFORMS)}')
        return XDLExecutor

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
                        Includes given step, and all sub steps all the way down to
                        base steps.
        """
        indent = '  '
        tree = [step]
        if print_tree:
            self.logger.info('{0}{1}'.format(indent*lvl, step.name))
        if isinstance(step, AbstractBaseStep):
            return tree
        else:
            lvl += 1
            for step in step.steps:
                if isinstance(step, AbstractBaseStep):
                    if print_tree:
                        self.logger.info('{0}{1}'.format(indent*lvl, step.name))
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
            self.logger.error(f'Language {language} not supported. Available languages: {", ".join(available_languages)}')
        return s

    def get_available_languages(self) -> List[str]:
        """Get languages for which every step in human readable can output
        human_readable text in that language.

        Returns:
            List[str]: List of language codes, e.g. ['en', 'zh']
        """
        available_languages = []
        for _, human_readables in HUMAN_READABLE_STEPS.items():
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
        """Scale all volumes in procedure.

        Args:
            scale (float): Number to scale all volumes by.
        """
        for step in self.steps:
            if step.name not in UNSCALED_STEPS:
                for prop, val in step.properties.items():
                    if 'volume' in prop and type(val) == float:
                        if val:
                            step.properties[prop] = float(val) * scale

    @property
    def estimated_duration(self) -> float:
        """Estimated duration of procedure. It is approximate but should give a
        give a rough idea how long the procedure should take.

        Returns:
            float: Estimated runtime of procedure in seconds.
        """
        if self.platform != 'chemputer':
            self.logger.info('Estimated duration only supported for Chemputer.')
            return -1
        if not self.prepared:
            self.logger.warning(
                'prepare_for_execution must be called before estimated duration can be calculated.')
            return
        total_time = 0
        temps = {}
        heatchill_time_per_degree = 60 # seconds. Pretty random guess.
        fallback_wait_for_temp_time = 60 * 30 # seconds. Again random guess.
        for step in self.base_steps:
            (step.name,  step.properties, '\n')
            time = 0
            if type(step) == CMove:
                rate_seconds = (step.move_speed * 60
                                + step.aspiration_speed * 60
                                + step.dispense_speed * 60) / 3
                time += step.volume / rate_seconds
            elif type(step) == CWait:
                time += step.time
            elif type(step) == CSetRecordingSpeed:
                pass
            elif type(step) == CSeparatePhases:
                # VERY APPROXIMATE. Assumes 250 mL separation funnel and
                # 35 mL / min move speed (defined in Chempiler 481b10a1527280fa51a2134e536211614f8108e8).
                volume = 250
                move_speed = 35 * 60 # mL / s
                time += (volume / 2) / move_speed
                if step.upper_phase_vessel != step.separation_vessel:
                    time += (volume / 2) / move_speed
            elif type(step) == CRotavapAutoEvaporation:
                time += step.time_limit
            elif type(step) == CRampChiller:
                time += step.ramp_duration
            # EXTREMELY APPROXIMATE. Don't know what temp is in base steps or
            elif type(step) in [CChillerWaitForTemp, CStirrerWaitForTemp]:
                if step.vessel in temps:
                    abs_delta = abs(
                        temps[step.vessel][-1] - temps[step.vessel][-2])
                    time += abs_delta * heatchill_time_per_degree
                else:
                    time += fallback_wait_for_temp_time
            elif type(step) in [CChillerSetTemp, CStirrerSetTemp]:
                temps.setdefault(step.vessel, [25, step.temp])
                time += 1
            else:
                time += 1
            repeat = 1
            if 'repeat' in step.properties:
                repeat = step.repeat
            total_time += time * repeat
        return total_time

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
        if self.platform != 'chemputer':
            self.logger.info('Reagent volume prediction only supported for chemputer.')
            return {}

        if not self.prepared:
            self.logger.warning(
                'prepare_for_execution must be called before reagent volumes can be calculated.')
            return {}
        reagent_volumes = {}
        flasks = self.executor._graph_hardware.flasks
        flask_ids = [item.id for item in flasks]
        for step in self.base_steps:
            if type(step) == CMove and step.from_vessel in flask_ids:
                reagent = self.executor._graph_hardware[
                    step.from_vessel].chemical
                if reagent:
                    if not reagent in reagent_volumes:
                        reagent_volumes[reagent] = 0
                    reagent_volumes[reagent] += step.volume
        return reagent_volumes

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
            max_volume_length = max([len(volume) + 3 for _, volume in reagent_volumes])
            self.logger.info(f'    {"Reagent Volumes":^{max_reagent_name_length + max_volume_length + 3}}')
            self.logger.info(f'    {"-" * (max_reagent_name_length + max_volume_length + 3)}')
            for reagent, volume in reagent_volumes:
                self.logger.info(f'    {reagent:^{max_reagent_name_length}} | {volume} mL')
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
                            if req == 'temp' and req in vessel_requirements[step.properties[vessel]]:
                                vessel_requirements[step.properties[vessel]][req].extend(val)
                            else:
                                vessel_requirements[step.properties[vessel]][req] = val

                    else:
                        vessel_requirements[step.properties[vessel]] = requirements

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
        auto_fix_issues=False,
        ignore_errors=[]
    ):
        """Return graph to run procedure with, built on template.

        Returns:
            Dict: JSON node link graph as dictionary.
        """
        return graph_from_template(
            self,
            template=graph_template,
            save=save,
            auto_fix_issues=auto_fix_issues,
            ignore_errors=ignore_errors,
        )

    def graph_deprecated(
        self,
    ):
        """
        Here to maintain SynthReader compatibility. Eventually SynthReader should
        use new graph generator.
        """
        if self.platform == 'chemputer':
            liquid_reagents = [reagent.id for reagent in self.reagents]
            cartridge_reagents = []
            for step in self.steps:
                if type(step) == Add and step.mass:
                    if step.reagent in liquid_reagents:
                        liquid_reagents.remove(step.reagent)

                elif type(step) == FilterThrough and step.through:
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
    ) -> None:
        """Check hardware compatibility and prepare XDL for execution on given
        setup.

        Args:
            graph_file (str, optional): Path to graph file. May be GraphML file,
                                        JSON file with graph in node link format,
                                        or dict containing graph in same format
                                        as JSON file.
        """
        if not self.prepared:
            save_path = None
            if self._xdl_file:
                save_path = self._xdl_file.replace('.xdl', '.xdlexe')
            if self.platform == 'chemputer':
                self.executor.prepare_for_execution(
                    graph_file,
                    interactive=interactive,
                    save_path=save_path,
                    sanity_check=sanity_check,
                )

            elif self.platform == 'chemobot':
                self.executor.prepare_for_execution()

            else:
                raise XDLError('Invalid platform given. Valid platforms: chemputer, chemobot.')

            if self.executor._prepared_for_execution:
                self.prepared = True
                self.logger.info('    Experiment Details\n')
                self.print_reagent_volumes()
                self.print_estimated_duration()

        else:
            self.logger.warning('Cannot call prepare for execution twice on same XDL object.')

    def execute(self, chempiler: 'Chempiler') -> None:
        """Execute XDL using given Chempiler object. self.prepare_for_execution
        must have been called before calling thie method.

        Args:
            chempiler (chempiler.Chempiler): Chempiler object instantiated with
                modules and graph to run XDL on.
        """
        if self.prepared or (hasattr(self, 'graph_sha256') and self.graph_sha256):
            if hasattr(self, 'executor'):
                self.executor.execute(chempiler)
            else:
                raise RuntimeError(
                    'XDL executor not available. Call prepare_for_execution before trying to execute.')
        else:
            self.logger.warn('prepare_for_execution must be called before executing.')

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
        if self.filter_dead_volume_method != other.filter_dead_volume_method:
            raise ValueError(
                "Can't combine two XDL objects with different filter_dead_volume_methods")
        if self.filter_dead_volume_solvent != other.filter_dead_volume_solvent:
            raise ValueError(
                "Can't combine two XDL objects with different filter_dead_volume_solvents")
        if self.auto_clean != other.auto_clean:
            raise ValueError(
                "Can't combine two XDL objects with different auto_clean flags")
        new_xdl_obj.auto_clean = self.auto_clean
        new_xdl_obj.filter_dead_volume_method = self.filter_dead_volume_method
        new_xdl_obj.filter_dead_volume_solvent = self.filter_dead_volume_solvent
        return new_xdl_obj

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
        copy_props = copy.deepcopy(step.properties)
        copy_steps.append(type(step)(**copy_props))

    for reagent in xdl_obj.reagents:
        copy_props = copy.deepcopy(reagent.properties)
        copy_reagents.append(type(reagent)(**copy_props))

    for component in xdl_obj.hardware:
        copy_props = copy.deepcopy(component.properties)
        copy_hardware.append(type(component)(**copy_props))

    return XDL(steps=copy_steps,
               reagents=copy_reagents,
               hardware=Hardware(copy_hardware))
