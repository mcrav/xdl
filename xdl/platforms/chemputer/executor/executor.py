from typing import List, Union, Tuple, Dict, Optional

from networkx import MultiDiGraph
from networkx.algorithms.shortest_paths.generic import shortest_path_length

from ....execution.abstract_executor import AbstractXDLExecutor
from ....constants import (
    DEFAULT_PORTS,
    BOTTOM_PORT,
    DEFAULT_STIR_SPEED,
    DEFAULT_STIR_REAGENT_FLASK_SPEED,
    CHEMPUTER_FILTER_CLASS_NAME,
    CHEMPUTER_VACUUM_CLASS_NAME,
    CHEMPUTER_VALVE_CLASS_NAME,
    HEATER_CLASSES,
    CHILLER_CLASSES,
    FILTER_DEAD_VOLUME_INERT_GAS_METHOD,
    FILTER_DEAD_VOLUME_LIQUID_METHOD,
    INERT_GAS_SYNONYMS,
)
from ....utils.graph import get_graph, undirected_neighbors
from ....utils.errors import XDLError
from ....step_utils import (
    AbstractBaseStep,
    AbstractAsyncStep,
    AbstractDynamicStep,
    AbstractStep,
    Step,
)
from ..steps import (
    RunColumn,
    FilterThrough,
    Separate,
    CleanVessel,
    CleanBackbone,
    Add,
    Transfer,
    Dry,
    Filter,
    Wait,
    AddFilterDeadVolume,
    RemoveFilterDeadVolume,
    StartHeatChill,
    StopHeatChill,
    StartStir,
    StopStir,
    CSetStirRate,
    CStir,
    CStopStir,
    CMove,
    CConnect,
    Shutdown
)
from .tracking import iter_vessel_contents
from .graph import (
    hardware_from_graph,
    make_vessel_map,
    make_inert_gas_map,
    get_unused_valve_port,
    vacuum_device_attached_to_flask,
)
from .utils import VesselContents, is_aqueous, validate_port
from .cleaning import (
    add_cleaning_steps,
    add_vessel_cleaning_steps,
    verify_cleaning_steps,
    get_cleaning_schedule
)
from .constants import (
    CLEAN_VESSEL_VOLUME_FRACTION,
    SOLVENT_BOILING_POINTS,
    CLEAN_VESSEL_BOILING_POINT_FACTOR,
    NON_RECURSIVE_ABSTRACT_STEPS
)
from ..utils.execution import get_pneumatic_controller

class ChemputerExecutor(AbstractXDLExecutor):

    """Class to execute XDL objects. To execute first call prepare_for_execution
    then execute.

    Args:
        xdl (XDL): XDL object to execute.
    """

    ################################
    # CHECK HARDWARE COMPATIBILITY #
    ################################

    def _hardware_is_compatible(self) -> bool:
        """Determine if XDL hardware object can be mapped to hardware available
        in graph.
        """
        enough_reactors = (len(self._xdl.hardware.reactors)
                           <= len(self._graph_hardware.reactors))
        enough_filters = (len(self._xdl.hardware.filters)
                          <= len(self._graph_hardware.filters))
        enough_separators = (len(self._xdl.hardware.separators)
                             <= len(self._graph_hardware.separators))
        if not enough_reactors:
            self.logger.warning(f'{len(self._xdl.hardware.reactors)} reactor\
 required, {len(self._graph_hardware.reactors)} present.')
        if not enough_filters:
            self.logger.warning(f'{len(self._xdl.hardware.filters)} filter\
 required, {len(self._graph_hardware.filters)} present.')
        if not enough_separators:
            self.logger.warning(f'{len(self._xdl.hardware.separators)}\
 separator required, {len(self._graph_hardware.separators)} present.')
        return enough_reactors and enough_filters and enough_separators

    def _check_enough_buffer_flasks(self) -> bool:
        buffer_flasks_required = []
        buffer_flasks_present = []
        vessels_for_search = []
        for step in self._xdl.steps:
            if type(step) == Separate:
                buffer_flasks_required.append(step.buffer_flasks_required)
                if step.buffer_flasks_required:
                    vessels_for_search.append(step.separation_vessel)

            elif type(step) in [RunColumn, FilterThrough]:
                buffer_flasks_required.append(step.buffer_flasks_required)
                if step.buffer_flasks_required:
                    vessels_for_search.append(step.from_vessel)

        if buffer_flasks_required:
            buffer_flasks_required = max(buffer_flasks_required)
            for vessel in list(set(vessels_for_search)):
                vessel_buffer_flasks = self._get_buffer_flask(
                    vessel, return_single=False)
                if vessel_buffer_flasks:
                    buffer_flasks_present.extend(vessel_buffer_flasks)
            buffer_flasks_present = len(buffer_flasks_present)
            if buffer_flasks_present:
                return (
                    buffer_flasks_present >= buffer_flasks_required,
                    buffer_flasks_required,
                    buffer_flasks_present
                )
            else:
                return (
                    buffer_flasks_required == 0,
                    buffer_flasks_required,
                    0
                )
        return (True, 0, None)

    def _check_all_flasks_present(self) -> bool:
        """Check that there is flask containing every reagent described in xdl.
        This just prints output to console and doesn't stop execution as there
        may be solid reagents present in XDL that won't be in the graph.

        Returns:
            bool: True if there is flask in graph for every reagent in XDL,
                  otherwise False.
        """
        flasks_ok = True
        for reagent in self._xdl.reagents:
            reagent_flask_present = False
            for flask in self._graph_hardware:
                if 'chemical' in flask.properties:
                    if flask.chemical == reagent.id:
                        reagent_flask_present = True
                        break
            if reagent_flask_present is False:
                self.logger.warning(
                    'WARNING: No flask present for {0}'.format(reagent.id))
                flasks_ok = False
        return flasks_ok

    def _check_all_cartridges_present(self) -> bool:
        """Check that there is a cartridge present for every FilterThrough step
        in the procedure.

        Returns:
            bool: True if all FilterThrough cartridges are present, otherwise
                False
        """
        cartridge_chemicals_in_graph = [
            cartridge.chemical for cartridge in self._graph_hardware.cartridges]
        for step in self._xdl.steps:
            if type(step) == FilterThrough:
                if step.through not in cartridge_chemicals_in_graph:
                    raise XDLError(
                        f'No cartridge present containing {step.through}')
        return True

    def _validate_ports(self, steps=None):
        if steps is None:
            steps = self._xdl.steps
        for step in steps:
            self._validate_ports_step(step)

    def _validate_ports_step(self, step):
        for vessel_keyword, port_keyword in [
            ('from_vessel', 'from_port'),
            ('to_vessel', 'to_port'),
            ('vessel', 'port'),
        ]:
            if vessel_keyword in step.properties:
                if port_keyword in step.properties:
                    if step.properties[port_keyword] is not None:
                        validate_port(
                            step.properties[vessel_keyword],
                            self._graph.nodes[
                                step.properties[vessel_keyword]]['class'],
                            step.properties[port_keyword]
                        )
        if not isinstance(step, NON_RECURSIVE_ABSTRACT_STEPS):
            for substep in step.steps:
                self._validate_ports_step(substep)

    ###############################
    # MAP GRAPH HARDWARE TO STEPS #
    ###############################

    def _get_hardware_map(self) -> None:
        """
        Get map of hardware IDs in XDL to hardware IDs in graphML.
        """
        self._xdl.hardware_map = {}
        for xdl_hardware_list, graphml_hardware_list in zip(
            [self._xdl.hardware.reactors, self._xdl.hardware.filters,
             self._xdl.hardware.separators, self._xdl.hardware.rotavaps],
            [self._graph_hardware.reactors, self._graph_hardware.filters,
             self._graph_hardware.separators, self._graph_hardware.rotavaps]
        ):
            for i in range(len(xdl_hardware_list)):
                self._xdl.hardware_map[
                    xdl_hardware_list[i].id
                ] = graphml_hardware_list[i].id

    def _map_hardware_to_step_list(self, step_list: List[Step]) -> None:
        for step in step_list:
            # Change all vessel IDs in steps to corresponding ones in graph.
            for prop, val in step.properties.items():
                if type(val) == str and val in self._xdl.hardware_map:
                    step.properties[prop] = self._xdl.hardware_map[val]
            step.update()

            if not isinstance(step, NON_RECURSIVE_ABSTRACT_STEPS):
                self._add_internal_properties_to_steps(step.steps)

    def _add_internal_properties_to_steps(self, step_list: List[Step]) -> None:
        """Recursively add internal properties to all steps and substeps in
        given list of steps.

        Args:
            step_list (List[Step]): List of steps to add internal properties to.
        """
        for step in step_list:

            if ('flush_tube_vessel' in step.properties
                    and not step.flush_tube_vessel):
                step.flush_tube_vessel = self._get_flush_tube_vessel()

            # FilterThrough step flushes cartridge with inert gas/air
            if ('flush_cartridge_vessel' in step.properties
                    and not step.flush_cartridge_vessel):
                step.flush_cartridge_vessel = self._get_flush_tube_vessel()

            # FilterThrough needs to know what dead volume of cartridge is. If
            # it is not provided in the graph it falls back to default.
            if 'cartridge_dead_volume' in step.properties:
                cartridge = self._graph_hardware[step.through_cartridge]
                if cartridge and 'dead_volume' in cartridge.properties:
                    step.cartridge_dead_volume = cartridge.dead_volume

            if 'vacuum' in step.properties and not step.vacuum:
                step.vacuum = self._get_vacuum(step)

            # Filter, WashSolid, Dry need this filled in if inert gas
            # filter dead volume method being used.
            if ('inert_gas' in step.properties):
                step.inert_gas = self._get_inert_gas(step)

            if ('vacuum_valve' in step.properties
                    and 'vacuum' in step.properties):
                if step.vacuum in self._valve_map:
                    step.vacuum_valve = self._valve_map[step.vacuum]
                    step.valve_unused_port = get_unused_valve_port(
                        graph=self._graph, valve_node=step.vacuum_valve)

            if ('vacuum_device' in step.properties
                    and 'vacuum' in step.properties):
                # Look for vacuum device attached to vacuum flask
                step.vacuum_device = vacuum_device_attached_to_flask(
                    graph=self._graph, flask_node=step.vacuum)

                # Look for vacuum device attached directly to vessel
                if not step.vacuum_device and 'vessel' in step.properties:
                    step.vacuum_device = vacuum_device_attached_to_flask(
                        graph=self._graph, flask_node=step.vessel)

            if 'vessel_has_stirrer' in step.properties:
                step.vessel_has_stirrer = step.vessel not in [
                    item.id
                    for item in self._graph_hardware.rotavaps
                    + self._graph_hardware.flasks]

            if 'vessel_type' in step.properties and not step.vessel_type:
                step.vessel_type = self._get_vessel_type(step.vessel)

            if 'volume' in step.properties and type(step) == CleanVessel:
                if step.volume is None:
                    step.volume = self._graph_hardware[
                        step.vessel].max_volume * CLEAN_VESSEL_VOLUME_FRACTION

            if ('collection_flask_volume' in step.properties
                    and not step.collection_flask_volume):
                rotavap = self._graph_hardware[step.rotavap_name]
                if 'collection_flask_volume' in rotavap.properties:
                    step.collection_flask_volume =\
                        rotavap.collection_flask_volume

            # When doing FilterThrough or RunColumn and from_vessel and to
            # vessel are the same, find an unused reactor to use as a buffer
            # flask.
            if 'buffer_flask' in step.properties:
                if type(step) in [FilterThrough, RunColumn]:
                    if (step.from_vessel == step.to_vessel
                            and not step.buffer_flask):
                        step.buffer_flask = self._get_buffer_flask(
                            step.from_vessel)
                elif type(step) == Separate:
                    step.buffer_flask = self._get_buffer_flask(
                        step.separation_vessel)

            if 'buffer_flasks' in step.properties:
                step.buffer_flasks = self._get_buffer_flask(
                    step.separation_vessel, return_single=False)

            # Add filter dead volume to WashSolid steps
            if ('filter_dead_volume' in step.properties
                    and not step.filter_dead_volume):
                vessel = self._graph_hardware[step.vessel]
                if 'dead_volume' in vessel.properties:
                    step.filter_dead_volume = vessel.dead_volume

            # Add pneumatic_controller to SwitchVacuum but not to CSwitchVacuum
            # as it is not an internal property in CSwitchVacuum
            if ('pneumatic_controller' in step.properties
                    and 'vessel' in step.properties
                    and not step.pneumatic_controller):
                port = None
                if hasattr(step, 'port'):
                    port = step.port
                if hasattr(step, 'pneumatic_controller_port'):
                    step.pneumatic_controller, step.pneumatic_controller_port =\
                        (get_pneumatic_controller(
                            self._graph, step.vessel, port))

            if ('through_cartridge' in step.properties
                    and not step.through_cartridge and step.through):
                for cartridge in self._graph_hardware.cartridges:
                    if cartridge.chemical == step.through:
                        step.through_cartridge = cartridge.id

            if 'heater' in step.properties and 'chiller' in step.properties:
                step.heater, step.chiller = self._find_heater_chiller(
                    self._graph, step.vessel)

            self._add_default_ports(step)

            step.on_prepare_for_execution(self._graph)

            if isinstance(step, AbstractDynamicStep):
                step.prepare_for_execution(self._graph, self)

            if 'children' in step.properties:
                self._add_internal_properties_to_steps(step.children)

            if not isinstance(step, NON_RECURSIVE_ABSTRACT_STEPS):
                self._add_internal_properties_to_steps(step.steps)

    def _add_default_ports(self, step):
        changed = False
        if type(step) != CConnect:
            for k in step.properties:
                if 'port' in k and step.properties[k] is None:
                    vessel_prop = k.replace('port', 'vessel')
                    if vessel_prop in step.properties:
                        vessel = step.properties[vessel_prop]
                        if vessel:
                            vessel_class = self._graph.nodes[vessel]['class']
                            if vessel_class in DEFAULT_PORTS:
                                changed = True
                                if 'from' in k:
                                    step.properties[k] = DEFAULT_PORTS[
                                        vessel_class]['from']
                                else:
                                    step.properties[k] = DEFAULT_PORTS[
                                        vessel_class]['to']
        if changed:
            step.update()
        return step

    def _find_heater_chiller(self, graph, node):
        heater, chiller = None, None
        neighbors = undirected_neighbors(graph, node)
        for neighbor in neighbors:
            if graph.nodes[neighbor]['class'] in HEATER_CLASSES:
                heater = neighbor
            elif graph.nodes[neighbor]['class'] in CHILLER_CLASSES:
                chiller = neighbor
        return heater, chiller

    def _map_hardware_to_steps(self) -> None:
        """
        Go through steps in XDL and replace XDL hardware IDs with IDs
        from the graph.
        """
        self._map_hardware_to_step_list(self._xdl.steps)

        # Give IDs of all waste vessels to clean backbone steps.
        for step in self._xdl.steps:
            if type(step) == CleanBackbone and not step.waste_vessels:
                step.waste_vessels = self._graph_hardware.waste_xids

    def _add_internal_properties(self, steps=None) -> None:
        """
        Go through steps in XDL and fill in internal properties for all steps
        and substeps.

        Args:
            steps (List[Step]): List of steps to add internal properties to. If
                not specified self._xdl.steps used.
        """
        if steps is None:
            steps = self._xdl.steps
        self._add_internal_properties_to_steps(steps)

        # Give IDs of all waste vessels to clean backbone steps.
        for step in steps:
            if type(step) == CleanBackbone and not step.waste_vessels:
                step.waste_vessels = self._graph_hardware.waste_xids

    def _get_vessel_type(self, vessel: str) -> str:
        """Given vessel return type of vessel from options 'filter', 'rotavap',
        'reactor', 'separator' or None if it isn't any of those options.

        Args:
            vessel (str): Vessel to get type of.

        Returns:
            str: Type of vessel, 'filter', 'reactor', 'rotavap', 'separator' or
                None
        """
        vessel_types = [
            ('filter', self._graph_hardware.filters),
            ('rotavap', self._graph_hardware.rotavaps),
            ('reactor', self._graph_hardware.reactors),
            ('separator', self._graph_hardware.separators),
            ('flask', self._graph_hardware.flasks)
        ]
        for vessel_type, hardware_list in vessel_types:
            if vessel in [item.id for item in hardware_list]:
                return vessel_type
        return None

    def _get_buffer_flask(self, vessel: str, return_single=True) -> str:
        """Get buffer flask closest to given vessel.

        Args:
            vessel (str): Node name in graph.

        Returns:
            str: Node name of buffer flask (unused reactor) nearest vessel.
        """
        # Get all reactor IDs
        flasks = [flask.id
                  for flask in self._graph_hardware.flasks
                  if not flask.chemical]

        # From remaining reactor IDs, return nearest to vessel.
        if flasks:
            if len(flasks) == 1:
                if return_single:
                    return flasks[0]
                else:
                    return [flasks[0]]
            else:
                shortest_paths = []
                for reactor in flasks:
                    shortest_paths.append((
                        reactor,
                        shortest_path_length(
                            self._graph, source=vessel, target=reactor)))
                if return_single:
                    return sorted(shortest_paths, key=lambda x: x[1])[0][0]
                else:
                    return [
                        item[0]
                        for item in sorted(shortest_paths, key=lambda x: x[1])
                    ]
        if return_single:
            return None
        else:
            return [None, None]

    def _get_vacuum(self, step: Step) -> str:
        if hasattr(step, 'filter_vessel'):
            if step.filter_vessel in self._vacuum_map:
                return self._vacuum_map[step.filter_vessel]
        elif hasattr(step, 'vessel'):
            if step.vessel in self._vacuum_map:
                return self._vacuum_map[step.vessel]
        return None

    def _get_inert_gas(self, step: Step) -> str:
        if hasattr(step, 'filter_vessel'):
            if step.filter_vessel in self._inert_gas_map:
                return self._inert_gas_map[step.filter_vessel]
        elif hasattr(step, 'vessel'):
            if step.vessel in self._inert_gas_map:
                return self._inert_gas_map[step.vessel]
        return None

    def _get_flush_tube_vessel(self) -> Optional[str]:
        """Look for gas vessel to flush tube with after Add steps.

        Returns:
            str: Flask to use for flushing tube.
                Preference is nitrogen > air > None.
        """
        inert_gas_flask = None
        air_flask = None
        for flask in self._graph_hardware.flasks:
            if flask.chemical.lower() in INERT_GAS_SYNONYMS:
                inert_gas_flask = flask.id
            elif flask.chemical.lower() == 'air':
                air_flask = flask.id
        if inert_gas_flask:
            return inert_gas_flask
        elif air_flask:
            return air_flask
        return None

    #####################
    # ADD IMPLIED STEPS #
    #####################

    def _add_implied_steps(self, interactive: bool = True) -> None:
        """Add extra steps implied by explicit XDL steps."""
        self._add_filter_dead_volume_handling_steps()
        if self._xdl.auto_clean:
            self._add_implied_clean_vessel_steps(interactive=interactive)
            self._add_implied_clean_backbone_steps(interactive=interactive)
        self._add_reagent_storage_steps()
        self._add_reagent_last_minute_addition_steps()

    def _add_implied_clean_backbone_steps(
        self, interactive: bool = True
    ) -> None:
        """Add CleanBackbone steps after certain steps which will contaminate
        the backbone.
        Takes into account when organic and aqueous reagents have been used to
        determine what solvents to clean the backbone with.
        """
        add_cleaning_steps(self._xdl)
        if interactive:
            verify = None
            while verify not in ['y', 'n', '']:
                verify = input(
                    'Verify solvents used in backbone cleaning? (y, [n])')
            if verify == 'y':
                verify_cleaning_steps(self._xdl)
        self._add_internal_properties()

    def _add_implied_clean_vessel_steps(self, interactive) -> None:
        """Add CleanVessel steps after steps which completely empty a vessel."""
        add_vessel_cleaning_steps(self._xdl, self._graph_hardware, interactive)
        self._add_internal_properties()

    def _add_reagent_storage_steps(self) -> None:
        """Add stirring and heating steps at start and end to flasks where
        reagent has stirring or temperature control specified in Reagents
        section of XDL.
        """
        for reagent in self._xdl.reagents:
            if reagent.stir or reagent.temp:
                reagent_flask = None
                for flask in self._graph_hardware.flasks:
                    if flask.chemical == reagent.id:
                        reagent_flask = flask.id
                if reagent_flask:
                    if reagent.stir:
                        self._xdl.steps.insert(
                            0,
                            StartStir(
                                vessel=reagent_flask,
                                stir_speed=DEFAULT_STIR_REAGENT_FLASK_SPEED
                            )
                        )

                        self._xdl.steps.append(StopStir(vessel=reagent_flask))

                    if reagent.temp is not None:
                        self._xdl.steps.insert(
                            0,
                            StartHeatChill(vessel=reagent_flask,
                                           temp=reagent.temp),
                        )
                        self._xdl.steps.append(
                            StopHeatChill(
                                vessel=reagent_flask,
                            ))

    def _add_reagent_last_minute_addition_steps(self) -> None:
        """Add addition steps where reagent specify that something must be added
        to them just before use with last_minute_addition property.
        """
        for reagent in self._xdl.reagents:
            addition, volume = (
                reagent.last_minute_addition,
                reagent.last_minute_addition_volume
            )

            if addition and volume:

                reagent_flask = None
                for flask in self._graph_hardware.flasks:
                    if flask.chemical == reagent.id:
                        reagent_flask = flask.id
                if reagent_flask:
                    first_use = -1

                    for i, step in enumerate(self._xdl.steps):
                        base_steps = step.base_steps

                        for base_step in base_steps:
                            if (type(base_step) == CMove
                                    and base_step.from_vessel == reagent_flask):
                                first_use = i
                                break

                        if first_use >= 0:
                            break

                    if first_use >= 0:
                        self._xdl.steps.insert(
                            first_use,
                            Add(vessel=reagent_flask,
                                reagent=addition,
                                volume=volume))

    ###############################
    # FILTER DEAD VOLUME HANDLING #
    ###############################

    def _add_filter_dead_volume_handling_steps(self) -> None:
        """Add steps to handle the filter dead volume. This can be handled in
        two ways determined by the XDL object's filter_dead_volume_method
        attribute (default is 'solvent', alternative is 'inert_gas').

        'solvent' means before liquid is added to the filter, the bottom is
        filled  up with a solvent specified in the <Synthesis> tag of the XDL.
        Before liquid is removed from the filter, the solvent in the bottom is
        removed first.

        'inert_gas' means that when not connected to the vacuumm, the bottom of
        the flask is connected to a stream of inert gas that keeps the liquid in
        the top part of the filter where it is.
        """
        if (self._xdl.filter_dead_volume_method
                == FILTER_DEAD_VOLUME_INERT_GAS_METHOD):
            self._add_filter_inert_gas_connect_steps()

        elif (self._xdl.filter_dead_volume_method
              == FILTER_DEAD_VOLUME_LIQUID_METHOD):
            self._add_filter_liquid_dead_volume_steps()

    def _add_filter_liquid_dead_volume_steps(self) -> None:
        """Using 'solvent' method for handling filter dead volume, add
        AddFilterDeadVolume steps and RemoveFilterDeadVolume steps at
        appropriate places to deal with the filter dead volume.
        """
        self._add_implied_add_dead_volume_steps()
        self._add_internal_properties()
        self._add_implied_remove_dead_volume_steps()
        self._add_internal_properties()

    def _get_filter_emptying_steps(
            self) -> List[Tuple[int, str, Dict[str, VesselContents]]]:

        """Get steps at which a filter vessel is emptied. Also return full
        list of vessel contents dict at every step.

        Returns:
            List[Tuple[int, str, Dict[str, VesselContents]]]: List of tuples,
                format: [(step_index,
                          filter_vessel_name,
                          {vessel: VesselContents, ...})...]
        """
        filter_emptying_steps = []
        full_vessel_contents = []
        prev_vessel_contents = {}
        for i, _, vessel_contents, _ in iter_vessel_contents(
                self._xdl.steps, self._graph_hardware):
            full_vessel_contents.append(vessel_contents)
            for vessel, contents in vessel_contents.items():
                if (self._graph_hardware[vessel].type
                        == CHEMPUTER_FILTER_CLASS_NAME
                        and vessel in prev_vessel_contents):
                    # If filter vessel has just been emptied, append to filters.
                    if (not contents.reagents
                            and prev_vessel_contents[vessel].reagents):
                        filter_emptying_steps.append(
                            (i, vessel, full_vessel_contents))

            prev_vessel_contents = vessel_contents
        return filter_emptying_steps

    def _get_filter_dead_volume(self, filter_vessel: str) -> float:
        """Return dead volume (volume below filter) of given filter vessel.

        Args:
            filter_vessel (str): ID of filter vessel.

        Returns:
            float: Dead volume of given filter vessel.
        """
        for vessel in self._graph_hardware.filters:
            if vessel.id == filter_vessel:
                return vessel.dead_volume
        return 0

    def _add_implied_add_dead_volume_steps(self) -> None:
        """
        Add PrepareFilter steps if filter top is being used, to fill up the
        bottom of the filter with solvent, so material added to the top doesn't
        drip through.

        Raises:
            AttributeError: If filter_dead_volume_method is liquid, but
                self._xdl has no filter_dead_volume_solvent attribute.
        """
        cleaning_solvents = get_cleaning_schedule(self._xdl)
        # Find steps at which a filter vessel is emptied. Can't just look for
        # Filter steps as liquid may be transferred to filter flask for other
        # reasons i.e. using the chiller.
        for filter_i, filter_vessel, full_vessel_contents in reversed(
                self._get_filter_emptying_steps()):
            j = filter_i - 1

            # Find point at which first reagent is added to filter vessel.
            # This is the point at which to insert the PrepareFilter step.
            while (j > 0
                   and filter_vessel in full_vessel_contents[j - 1]
                   and full_vessel_contents[j - 1][filter_vessel].reagents):
                j -= 1

            solvent = cleaning_solvents[j]

            # Insert AddFilterDeadVolume step into self._xdl.steps.
            self._xdl.steps.insert(j, AddFilterDeadVolume(
                filter_vessel=filter_vessel, solvent=solvent,
                volume=self._get_filter_dead_volume(filter_vessel)))

    def _add_implied_remove_dead_volume_steps(self) -> None:
        """When liquid is transferred from a filter vessel remove dead volume
        first.
        """
        # Look for filter emptying steps and add RemoveFilterDeadVolume step
        # just before them.
        for i, vessel, _ in reversed(self._get_filter_emptying_steps()):
            # Only move to waste after Filter step. For any other step should
            # become part of the reaction mixture.
            if self._xdl.steps[i].name == 'Filter':
                self._xdl.steps.insert(
                    i,
                    RemoveFilterDeadVolume(
                        filter_vessel=vessel,
                        dead_volume=self._get_filter_dead_volume(vessel))
                )

    def _add_filter_inert_gas_connect_steps(self) -> None:
        """Add steps to self._xdl.steps to implement the following:
        1) Connection of inert gas to bottom of filter flasks at start of
        procedure.
        """
        # Connect inert gas to bottom of filter flasks at start of procedure.
        for filter_vessel in self._graph_hardware.filters:
            if filter_vessel.id in self._inert_gas_map:
                self._xdl.steps.insert(
                    0, CConnect(
                        from_vessel=self._inert_gas_map[filter_vessel.id],
                        to_vessel=filter_vessel.id,
                        to_port=BOTTOM_PORT)
                )

    ###############################
    # SOLIDIFY IMPLIED PROPERTIES #
    ###############################

    def _add_all_volumes_to_step(self, step, vessel_contents, definite):
        if type(step) in [Transfer, CMove]:
            if step.volume == 'all':
                step.transfer_all = True
                if definite and step.from_vessel in vessel_contents:
                    step.volume = vessel_contents[step.from_vessel].volume
                else:
                    try:
                        step.volume = self._graph_hardware[
                            step.from_vessel].max_volume
                    except AttributeError:
                        raise XDLError(f'Missing flask ("from_vessel": \
"{step.from_vessel}") in {step.name} step.\n{step.properties}\n')

        if not isinstance(step, NON_RECURSIVE_ABSTRACT_STEPS):
            for substep in step.steps:
                self._add_all_volumes_to_step(
                    substep, vessel_contents, definite)

    def _add_all_volumes(self) -> None:
        """When volumes in CMove commands are specified by 'all', change
        these to max_volume of vessel.
        """
        prev_vessel_contents = None
        for _, step, vessel_contents, definite in iter_vessel_contents(
            self._xdl.steps, self._graph_hardware
        ):
            self._add_all_volumes_to_step(step, prev_vessel_contents, definite)
            prev_vessel_contents = vessel_contents

    def _add_filter_volumes(self) -> None:
        """
        Add volume of filter bottom (aka dead_volume) and volume of material
        added to filter top to Filter steps.
        """
        prev_vessel_contents = {}
        for _, step, vessel_contents, _ in iter_vessel_contents(
                self._xdl.steps, self._graph_hardware):
            if type(step) == Filter and not step.properties['inline_filter']:
                if step.filter_vessel in prev_vessel_contents:
                    step.filter_top_volume = max(prev_vessel_contents[
                        step.filter_vessel].volume, 0)
                    if step.filter_top_volume <= 0:
                        step.filter_top_volume = self._graph_hardware[
                            step.filter_vessel].max_volume
                else:
                    step.filter_top_volume = self._graph_hardware[
                        step.filter_vessel].max_volume

                # Need this as setting max_volume reinitialises step and
                # ApplyVacuum internal properties are lost.
                for substep in step.steps:
                    substep.on_prepare_for_execution(self._graph)

            prev_vessel_contents = vessel_contents

    def _add_clean_vessel_temps(self) -> None:
        """Add temperatures to CleanVessel steps. Priority is:
        1) Use explicitly given temperature.
        2) If solvent boiling point known use 80% of the boiling point.
        3) Use 30°C.

        Args:
            steps (List[List[Step]]): List of steps to add temperatures to
                CleanVessel steps

        Returns:
            List[List[Step]]: List of steps with temperatures added to
                CleanVessel steps.
        """
        for step in self._xdl.steps:
            if type(step) == CleanVessel:
                if step.temp is None:
                    solvent = step.solvent.lower()
                    if solvent in SOLVENT_BOILING_POINTS:
                        step.temp = (SOLVENT_BOILING_POINTS[solvent]
                                     * CLEAN_VESSEL_BOILING_POINT_FACTOR)
                    else:
                        step.temp = 30

    ######################
    # OPTIMISE PROCEDURE #
    ######################

    def _tidy_up_procedure(self, steps=None) -> None:
        """Remove steps that are pointless and optimise procedure.
        """
        self._set_all_stir_speeds()
        self._stop_stirring_when_vessels_lose_scope()
        self._remove_pointless_backbone_cleaning()
        self._no_waiting_if_dry_run()

    def _remove_pointless_dry_return_to_rt(self, steps=None) -> None:
        """If next step is heating to same temp as dry step, dry step shouldn't
        return to RT at end of stpe.
        """
        if steps is None:
            steps = self._xdl.steps
        for i, step in enumerate(steps):
            if type(step) == Dry and step.temp and not step.continue_heatchill:
                if (i + 1 < len(steps)
                        and 'temp' in steps[i + 1].properties
                        and step.temp == steps[i + 1].temp):
                    step.continue_heatchill = True

    def _optimise_separation_steps(self, steps=None) -> None:
        """Optimise separation steps to reduce risk of backbone contamination.
        The issue this addresses is that if a product is extracted into the
        aqueous phase, but the organic phase ends up in the backbone, the
        product can redissolve in the organic phase when transferred out of the
        separator.

        Rules implemented here:

        If:
        1) to_vessel of one Separate step is the separation_vessel
        2) Next Separate step uses same kind of solvent (organic or aqueous)

        Then:
        the separation step shouldn't remove the dead volume as you
        run the risk of contaminating the backbone, and there is no need to
        remove the dead volume to risk contaminating the product phase as
        more solvent is going to be added anyway in the next step.

        Args:
            steps (List[Step]): List of steps to optimise separation steps in.
                If not given self._xdl.steps used.
        """
        if steps is None:
            steps = self._xdl.steps
        for i in range(len(steps)):
            step = steps[i]
            if type(step) == Separate:
                if (step.waste_phase_to_vessel == step.separation_vessel
                        or step.to_vessel == step.separation_vessel):
                    j = i + 1
                    next_solvent = None
                    while j < len(steps):
                        if type(steps[j]) == Separate:
                            next_solvent = steps[j].solvent
                            break
                        j += 1
                    if (next_solvent
                        and is_aqueous(next_solvent)
                            == is_aqueous(step.solvent)):
                        step.remove_dead_volume = False

    def find_stirring_schedule(
        self, step: Step, stirring: List[str]
    ) -> List[str]:
        """Find vessels being stirred after given step.

        Args:
            step (Step): step to find stirring changes in.
            stirring (List[str]): List of vessels being stirred before step.

        Returns:
            List[str]: List of vessels being stirred after step.
        """
        if type(step) == CStir:
            stirring.append(step.vessel)
        elif type(step) == CStopStir:
            if step.vessel in stirring:
                stirring.remove(step.vessel)
        elif not isinstance(step, NON_RECURSIVE_ABSTRACT_STEPS):
            for sub_step in step.steps:
                if isinstance(sub_step, AbstractStep):
                    self.find_stirring_schedule(sub_step, stirring)
                else:
                    if type(sub_step) == CStir:
                        stirring.append(sub_step.vessel)
                    elif type(sub_step) == CStopStir:
                        if sub_step.vessel in stirring:
                            stirring.remove(sub_step.vessel)
        return stirring

    def _stop_stirring_when_vessels_lose_scope(self) -> None:
        """Add in CStopStir steps whenever a vessel that is stirring becomes
        empty.
        """
        stirring_schedule = []
        stirred_vessels = []
        insertions = []

        # Find stirring state after every step.
        for i, step in enumerate(self._xdl.steps):
            stirred_vessels = self.find_stirring_schedule(step, stirred_vessels)
            stirring_schedule.append(stirred_vessels)

        # Look for vessels out of scope that need stirring stopped
        for i, step, vessel_contents, _ in iter_vessel_contents(
                self._xdl.steps, self._graph_hardware):
            for prop, val in step.properties.items():
                if 'vessel' in prop and val in stirring_schedule[i]:
                    if (val in vessel_contents
                            and not vessel_contents[val].reagents):
                        insertions.append((i + 1, StopStir(vessel=val)))

    def _get_stir_vessels(self, step: Step):
        """Get vessels being stirred using CStir in substeps of given step.

        Args:
            step (Step): Step to find vessels being stirred.

        Returns:
            List[str]: List of vessels being stirred in given step.
        """
        stir_vessels = []
        if isinstance(step, NON_RECURSIVE_ABSTRACT_STEPS):
            if type(step) == CStir:
                stir_vessels.append(step.vessel)
        else:
            for substep in step.steps:
                if type(substep) == CStir:
                    stir_vessels.append(substep.vessel)
                elif not isinstance(
                        substep, (AbstractBaseStep, AbstractAsyncStep)):
                    stir_vessels.extend(self._get_stir_vessels(substep))
        return stir_vessels

    def _set_all_stir_speeds(self, steps: List[Step] = None) -> None:
        """Set stir RPM to default at start of procedure for all stirrers
        used in procedure.
        """
        if steps is None:
            steps = self._xdl.steps
        stir_vessels = []
        for step in steps:
            stir_vessels.extend(self._get_stir_vessels(step))
        for vessel in sorted(list(set(stir_vessels))):
            steps.insert(
                0, CSetStirRate(vessel=vessel, stir_speed=DEFAULT_STIR_SPEED))

    def _no_waiting_if_dry_run(self) -> None:
        """Set all Wait step times to 1 second if the dry run flag is True."""
        if self._xdl.dry_run:
            for step in self._xdl.steps:
                self._set_all_waits_to_one(step)

    def _set_all_waits_to_one(self, step: Step) -> None:
        """Recursive function setting all nested Wait step times to 1 second.

        Args:
            step (Step): step to set all nested Wait step times to 1 second.
        """
        for step in step.steps:
            if type(step) == Wait:
                step.time = 1
            elif step.steps:
                self._set_all_waits_to_one(step)

    def _remove_pointless_backbone_cleaning(self) -> None:
        """Remove pointless CleanBackbone steps.

        Rules are:

        1) No point cleaning between Filter and Dry steps.
        2) No point cleaning between consecutive additions of the same
               reagent.
        """
        i = len(self._xdl.steps) - 1
        while i > 0:
            step = self._xdl.steps[i]
            if type(step) == CleanBackbone:
                if i > 0 and i < len(self._xdl.steps) - 1:
                    before_step = self._xdl.steps[i - 1]
                    after_step = self._xdl.steps[i + 1]

                    if should_remove_clean_backbone_step(
                            before_step, after_step):
                        self._xdl.steps.pop(i)
            i -= 1

    ########
    # MISC #
    ########

    def _print_warnings(self) -> None:
        for warning in self._warnings:
            self.logger.info(warning)

    def _do_sanity_check(self, step, level=0):
        self.logger.debug(f'{"    "*level}{step.name}')
        step.final_sanity_check(self._graph)
        if not isinstance(step, NON_RECURSIVE_ABSTRACT_STEPS):
            for substep in step.steps:
                self._do_sanity_check(substep, level + 1)

    def _add_in_final_shutdown(self):
        self._xdl.steps.append(Shutdown())

    ##################
    # PUBLIC METHODS #
    ##################

    def prepare_block_for_execution(
        self, graph_file: Union[str, Dict], block: List[Step]
    ) -> None:
        """Prepare block of AbstractDynamicStep for execution

        Args:
            graph_file (Union[str, Dict]): Path to graph file. May be GraphML
                file, JSON file with graph in node link format, or dict
                containing graph in same format as JSON file.
        """
        if not type(graph_file) == MultiDiGraph:
            self._graph, self._raw_graph = get_graph(graph_file)
        else:
            self._graph = graph_file
        self._graph_hardware = hardware_from_graph(self._graph)
        self._vacuum_map = make_vessel_map(
            self._graph, CHEMPUTER_VACUUM_CLASS_NAME)
        self._inert_gas_map = make_inert_gas_map(self._graph)
        self._valve_map = make_vessel_map(
            self._graph, CHEMPUTER_VALVE_CLASS_NAME)

        self._add_internal_properties(steps=block)
        self._validate_ports(steps=block)
        # Convert implied properties to concrete values.
        self._remove_pointless_dry_return_to_rt(steps=block)
        self._optimise_separation_steps(steps=block)

        # Optimise procedure.
        self._set_all_stir_speeds(steps=block)

        self._print_warnings()

    def initialise_graph(self, graph_file):
        self._graph = get_graph(graph_file)

    def prepare_for_execution(
        self,
        graph_file: Union[str, Dict],
        interactive: bool = True,
        save_path: str = '',
        sanity_check: bool = True,
    ) -> None:
        """
        Prepare the XDL for execution on a Chemputer corresponding to the given
        graph. Any one of graphml_file, json_data, or json_file must be given.

        Args:
            graph_file (str, optional): Path to graph file. May be GraphML file,
                JSON file with graph in node link format, or dict containing
                graph in same format as JSON file.
        """
        if not self._prepared_for_execution:

            self._graph, self._raw_graph = get_graph(graph_file)
            # Load graph, make Hardware object from graph, and map nearest
            # waste vessels to every node.
            self._graph_hardware = hardware_from_graph(self._graph)
            self._vacuum_map = make_vessel_map(
                self._graph, CHEMPUTER_VACUUM_CLASS_NAME)
            self._inert_gas_map = make_inert_gas_map(self._graph)
            self._valve_map = make_vessel_map(
                self._graph, CHEMPUTER_VALVE_CLASS_NAME)

            # Check hardware compatibility
            if self._hardware_is_compatible():
                self.logger.info('Hardware is compatible')
                self._check_all_flasks_present()
                self._check_all_cartridges_present()

                # Map graph hardware to steps.
                # _map_hardware_to_steps is called twice so that
                # _xdl.iter_vessel_contents has all vessels to play with
                # during _add_implied_steps.
                self._get_hardware_map()
                self._map_hardware_to_steps()

                enough_buffer_flasks, n_buffer_required, n_buffer_present =\
                    self._check_enough_buffer_flasks()
                if not enough_buffer_flasks:
                    raise XDLError(f'The procedure requires {n_buffer_required}\
 empty buffer flasks but only {n_buffer_present} are present in the graph.')

                self._add_internal_properties()

                self._validate_ports()

                # Add in steps implied by explicit steps.
                self._add_implied_steps(interactive=interactive)
                # Convert implied properties to concrete values.
                self._add_clean_vessel_temps()
                self._optimise_separation_steps()
                self._remove_pointless_dry_return_to_rt()

                self._add_in_final_shutdown()

                self._add_internal_properties()
                self._add_all_volumes()
                self._add_filter_volumes()

                if sanity_check:
                    for step in self._xdl.steps:
                        self._do_sanity_check(step)

                # Optimise procedure.
                self._tidy_up_procedure()

                self._print_warnings()
                self._prepared_for_execution = True
                self.save_execution_script(save_path)

            else:
                self.logger.error(
                    "Hardware is not compatible. Can't execute.")

def should_remove_clean_backbone_step(
    before_step: Step, after_step: Step
) -> bool:
    """Return True if backbone cleaning is pointless between given two steps.

    Args:
        before_step (Step): Step object of first step of pair.
        after_step (Step): Step object of second step of pair.

    Returns:
        bool: True if backbone cleaning is pointless between given two steps,
            otherwise False.
    """
    # Don't clean between filter and subsequent dry.
    if type(before_step) == Filter and type(after_step) == Dry:
        return True

    else:
        # If adding same thing twice in a row don't clean in between.
        reagents = []
        for other_step in [before_step, after_step]:
            if type(other_step) == Add:
                reagents.append(other_step.reagent)
        if len(reagents) == 2 and len(set(reagents)) == 1:
            return True

    return False
