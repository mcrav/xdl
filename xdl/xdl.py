from typing import List, Dict, Any, Union, Optional
import os
import logging
import json
import re
from math import ceil

from .errors import (
    XDLError,
    XDLReagentNotDeclaredError,
    XDLVesselNotDeclaredError,
    XDLInvalidFileTypeError,
    XDLInvalidPlatformControllerError,
    XDLStepIndexError,
    XDLExecutionBeforeCompilationError,
    XDLInvalidPlatformError,
    XDLInvalidInputError,
    XDLFileNotFoundError,
    XDLInvalidArgsError,
    XDLDoubleCompilationError,
)
from .graphgen_deprecated import get_graph
from .hardware import Hardware
from .platforms.abstract_platform import AbstractPlatform
from .reagents import Reagent
from .readwrite.utils import read_file
from .readwrite.xml_interpreter import xdl_str_to_objs
from .readwrite.xml_generator import xdl_to_xml_string
from .readwrite.json import xdl_to_json, xdl_from_json_file
from .steps import Step, AbstractBaseStep, UnimplementedStep
from .utils import get_logger
from .utils.misc import steps_are_equal, xdl_elements_are_equal

class XDL(object):
    """
    Interpets XDL (file or str) and provides an object for further use.
    """
    # File name XDL was initialised from
    _xdl_file = None

    # Graph hash contained in <Synthesis> tag if XDL object is from xdlexe file
    graph_sha256 = None

    # True if XDL is loaded from xdlexe, or has been compiled, otherwise False
    # self.compiled == True implies that procedure is ready to execute
    compiled = False

    def __init__(
        self,
        xdl: str = None,
        steps: List[Step] = None,
        hardware: Hardware = None,
        reagents: List[Reagent] = None,
        logging_level: int = logging.INFO,
        platform: Union[str, AbstractPlatform] = 'chemputer',
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

        self._initialize_logging(logging_level)
        self._load_platform(platform)
        self._load_xdl(xdl, steps=steps, hardware=hardware, reagents=reagents)

        self.executor = self.platform.executor(self)
        self.compiled = self.graph_sha256 is not None

        self._validate_loaded_xdl()

    ##################
    # Initialization #
    ##################

    def _initialize_logging(self, logging_level: int) -> None:
        """Initialize logger with given logging level."""
        self.logger = get_logger()
        self.logger.setLevel(logging_level)
        self.logging_level = logging_level

    def _load_platform(self, platform: Union[str, AbstractPlatform]) -> None:
        """Initialise given platform. If 'chemputer' given initialise
        ChemputerPlatform otherwise platform should be a subclass of
        AbstractPlatform.

        Args:
            platform (Union[str, AbstractPlatform])

        Raises:
            XDLInvalidPlatformError: If platform is not 'chemputer' or a
                subclass of AbstractPlatform.
        """
        if platform == 'chemputer':
            from chemputerxdl import ChemputerPlatform
            self.platform = ChemputerPlatform()
        elif issubclass(platform, AbstractPlatform):
            self.platform = platform()
        else:
            raise XDLInvalidPlatformError(platform)

    def _load_xdl(
        self,
        xdl: str,
        steps: List[Step],
        reagents: List[Reagent],
        hardware: Hardware
    ) -> None:
        """Load XDL from given arguments. Valid argument combinations are
        just xdl, or all of steps, reagents and hardware. xdl can be a path to a
        .xdl, .xdlexe or .json file, or an XML string of the XDL.

        Args:
            xdl (str): Path to .xdl, .xdlexe or .json XDL file, or XML string.
            steps (List[Step]): List of Step objects to instantiate XDL with.
            reagents (List[Reagent]): List of Reagent objects to instantiate XDL
                with.
            hardware (Hardware): Hardware object to instantiate XDL with.

        Raises:
            XDLFileNotFoundError: xdl file given, but file not found.
            XDLInvalidInputError: xdl is not file or valid XML string.
            XDLInvalidArgsError: Invalid combination of arguments given.
                Valid argument combinations are just xdl, or all of steps,
                reagents and hardware.
        """
        # Load from XDL file or string
        if xdl:
            # Load from file
            if os.path.exists(xdl):
                self._load_xdl_from_file(xdl)

            # Incorrect file path, raise error.
            elif xdl.endswith(('.xdl', '.xdlexe', '.json')):
                raise XDLFileNotFoundError(xdl)

            # Load XDL from string, check string is not mismatched file path.
            elif '<Synthesis' in xdl and '<Procedure>' in xdl:
                self._load_xdl_from_xml_string(xdl)

            # Invalid input, raise error
            else:
                raise XDLInvalidInputError(xdl)

        # Initialise XDL from lists of Step, Reagent and Component objects
        elif (steps is not None
              and reagents is not None
              and hardware is not None):
            self.steps, self.hardware, self.reagents = steps, hardware, reagents
            self.executor = self.platform.executor(self)

        # Invalid combination of arguments given, raise error
        else:
            raise XDLInvalidArgsError()

    def _load_xdl_from_file(self, xdl_file):
        """Load XDL from .xdl, .xdlexe or .json file.

        Args:
            xdl_file (str): .xdl, .xdlexe or .json file to load XDL from.

        Raises:
            XDLInvalidFileTypeError: If given file is not .xdl, .xdlexe or .json
        """
        file_ext = os.path.splitext(xdl_file)[1]

        # Load from XML .xdl or .xdlexe file
        if file_ext == '.xdl' or file_ext == '.xdlexe':
            self._xdl_file = xdl_file
            xdl_str = read_file(xdl_file)
            self._load_xdl_from_xml_string(xdl_str)

        # Load from .json file
        elif file_ext == '.json':
            parsed_xdl = xdl_from_json_file(xdl_file, self.platform)
            self.steps = parsed_xdl['steps']
            self.hardware = parsed_xdl['hardware']
            self.reagents = parsed_xdl['reagents']

        # Invalid file type, raise error
        else:
            raise XDLInvalidFileTypeError(file_ext)

    def _load_xdl_from_xml_string(self, xdl_str):
        """Load XDL from XML string.

        Args:
            xdl_str (str): XML string of XDL.
        """
        parsed_xdl = xdl_str_to_objs(
            xdl_str=xdl_str, logger=self.logger, platform=self.platform)

        self._load_graph_hash(xdl_str)

        self.steps = parsed_xdl['steps']
        self.hardware = parsed_xdl['hardware']
        self.reagents = parsed_xdl['reagents']

    def _load_graph_hash(self, xdl_str: str) -> Optional[str]:
        """Obtain graph hash from given xdl str. If xdl str is not xdlexe, there
        will be no graph hash so return None.
        """
        graph_hash_search = re.search(r'graph_sha256="([a-z0-9]+)"', xdl_str)
        if graph_hash_search:
            self.graph_sha256 = graph_hash_search[1]

    def _validate_loaded_xdl(self):
        """Validate loaded XDL at end of __init__"""
        # Validate all vessels and reagents used in procedure are declared in
        # corresponding sections of XDL. Don't do this if XDL object is compiled
        # (xdlexe) as there will be lots of undeclared vessels from the graph.
        if not self.compiled:
            self._validate_vessel_and_reagent_props()

    def _validate_vessel_and_reagent_props(self):
        """Validate that all vessels and reagents used in procedure are declared
        in corresponding sections of XDL.

        Raises:
            XDLReagentNotDeclaredError: If reagent used in step but not declared
            XDLVesselNotDeclaredError: If vessel used in step but not declared
        """
        reagent_ids = [reagent.id for reagent in self.reagents]
        vessel_ids = [vessel.id for vessel in self.hardware]
        for step in self.steps:
            self._validate_vessel_and_reagent_props_step(
                step, reagent_ids, vessel_ids
            )

    def _validate_vessel_and_reagent_props_step(
            self, step, reagent_ids, vessel_ids):
        """Validate that all vessels and reagents used in given step are
        declared in corresponding sections of XDL.

        Args:
            step (Step): Step to validate all vessels and reagents declared.
            reagent_ids (List[str]): List of all declared reagent ids.
            vessel_ids (List[str]): List of all declared vessel ids.

        Raises:
            XDLReagentNotDeclaredError: If reagent used in step but not declared
            XDLVesselNotDeclaredError: If vessel used in step but not declared
        """
        for prop, prop_type in step.PROP_TYPES.items():
            # Check vessel has been declared
            if prop_type == 'vessel':
                vessel = step.properties[prop]
                if vessel and vessel not in vessel_ids:
                    raise XDLVesselNotDeclaredError(vessel)

            # Check reagent has been declared
            elif prop_type == 'reagent':
                reagent = step.properties[prop]
                if reagent and reagent not in reagent_ids:
                    raise XDLReagentNotDeclaredError(reagent)

        # Check child steps, don't need to check substeps as they aren't
        # obligated to have all vessels used explicitly declared.
        if hasattr(step, 'children'):
            for substep in step.children:
                self._validate_vessel_and_reagent_props_step(
                    substep, reagent_ids, vessel_ids
                )

    ###############
    # Information #
    ###############

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
        return xdl_to_xml_string(self)

    def as_json_string(self, pretty=True) -> Dict:
        """Return JSON str of procedure."""
        xdl_json = xdl_to_json(self)
        if pretty:
            return json.dumps(xdl_json, indent=2)
        return json.dumps(xdl_json)

    def save(
        self,
        save_file: str,
        full_properties: bool = False,
        file_format: str = 'xml'
    ) -> str:
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
        if file_format == 'xml':
            xml_string = xdl_to_xml_string(
                self, full_properties=full_properties)
            with open(save_file, 'w') as fd:
                fd.write(xml_string)

        elif file_format == 'json':
            with open(save_file, 'w') as fd:
                json.dump(
                    xdl_to_json(self, full_properties=full_properties),
                    fd, indent=2
                )

        else:
            raise XDLError(f'{file_format} is an invalid file format for saving\
 XDL. Valid file formats: "xml", "json".')

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
        if not self.compiled:
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

        if not self.compiled:
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
        if not self.compiled:
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
                self.compiled = True
                self.logger.info('    Experiment Details\n')
                self.print_reagent_volumes()
                self.print_estimated_duration()

        else:
            raise XDLDoubleCompilationError()

    def execute(self, platform_controller: Any, step: int = None) -> None:
        """Execute XDL using given platform controller object.
        XDL object must either be loaded from a xdlexe file, or it must have
        been prepared for execution.

        Args:
            platform_controller (Any): Platform controller object instantiated
            with modules and graph to run XDL on.
        """
        # Check step not accidentally passed as platform controller
        if type(platform_controller) in [int, str, list, dict]:
            raise XDLInvalidPlatformControllerError(platform_controller)

        # Check XDL object has been compiled
        if self.compiled:
            # Execute full procedure
            if step is None:
                self.executor.execute(platform_controller)

            # Execute individual step.
            else:
                # Check step index is valid.
                try:
                    self.steps[step]
                except IndexError:
                    raise XDLStepIndexError(step, len(self.steps))

                # Execute step
                self.executor.execute_step(
                    platform_controller, self.steps[step])

        # XDL object not compiled, raise error
        else:
            raise XDLExecutionBeforeCompilationError()

    @property
    def base_steps(self) -> List[AbstractBaseStep]:
        """Return full list of procedure base steps."""
        return [
            step
            for step in self._get_full_xdl_tree()
            if isinstance(step, AbstractBaseStep)
        ]

    #################
    # Magic Methods #
    #################

    def __add__(self, other: 'XDL') -> 'XDL':
        """Allow two XDL objects to be added together. Steps, reagents and
        components of this object are added to the new object lists first,
        followed by the same lists of the other object.
        """
        reagents, steps, components = [], [], []
        for xdl_obj in [self, other]:
            reagents.extend(xdl_obj.reagents)
            steps.extend(xdl_obj.steps)
            components.extend(list(xdl_obj.hardware))
        new_xdl_obj = XDL(steps=steps, reagents=reagents, hardware=components)
        return new_xdl_obj

    def __eq__(self, other: 'XDL') -> bool:
        """Compare equality of XDL objects based on steps, reagents and
        hardware. Steps are compared based step types and properties, including
        all substeps and child steps. Reagents and Components are compared
        based on properties.
        """
        if type(other) != XDL:
            # Don't raise NotImplementedError here as it causes unnecessary
            # crashes for example `if xdl_obj == None: ...`.
            return False

        # Compare lengths of lists first.
        if len(self.steps) != len(other.steps):
            return False
        if len(self.reagents) != len(other.reagents):
            return False
        if len(self.hardware.components) != len(other.hardware.components):
            return False

        # Detailed comparison of all step types and properties, including all
        # substeps and children.
        for i, step in enumerate(self.steps):
            if not steps_are_equal(step, other.steps[i]):
                return False

        # Compare properties of all reagents
        for i, reagent in enumerate(self.reagents):
            if not xdl_elements_are_equal(reagent, other.reagents[i]):
                return False

        # Compare properties of all components
        for i, component in enumerate(self.hardware.components):
            if not xdl_elements_are_equal(
                    component, other.hardware.components[i]):
                return False

        return True
