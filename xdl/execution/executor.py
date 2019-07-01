import statistics
import copy
import logging
from typing import List, Union, Tuple

from networkx.algorithms.shortest_paths.generic import shortest_path_length
if False:
    from ..xdl import XDL
    from chempiler import Chempiler

from ..constants import *
from ..utils.namespace import BASE_STEP_OBJ_DICT
from ..utils.errors import raise_error
from ..steps import *
from ..reagents import Reagent
from .tracking import iter_vessel_contents
from .graph import (
    hardware_from_graph,
    get_graph,
    make_vessel_map,
    make_inert_gas_map,
    get_unused_valve_port,
    vacuum_device_attached_to_flask,
)
from .utils import VesselContents, is_aqueous
from .cleaning import (
    add_cleaning_steps,
    add_vessel_cleaning_steps,
    verify_cleaning_steps,
    get_cleaning_schedule
)
from .constants import (
    INERT_GAS_SYNONYMS,
    CLEAN_VESSEL_VOLUME_FRACTION,
    SOLVENT_BOILING_POINTS,
    CLEAN_VESSEL_BOILING_POINT_FACTOR
)

class XDLExecutor(object):

    """Class to execute XDL objects. To execute first call prepare_for_execution
    then execute.

    Args:
        xdl (XDL): XDL object to execute.
    """

    def __init__(self, xdl: 'XDL') -> None:

        self.logger = xdl.logger
        self._xdl = xdl
        self._warnings = []
        self._prepared_for_execution = False

    ####################################
    ### CHECK HARDWARE COMPATIBILITY ###
    ####################################

    def _hardware_is_compatible(self) -> bool:
        """Determine if XDL hardware object can be mapped to hardware available
        in graph.
        """
        enough_reactors = (len(self._xdl.hardware.reactors) <=
                           len(self._graph_hardware.reactors))
        enough_filters = (len(self._xdl.hardware.filters) <=
                          len(self._graph_hardware.filters))
        enough_separators = (len(self._xdl.hardware.separators) <=
                             len(self._graph_hardware.separators))
        return enough_reactors and enough_filters and enough_separators

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
            if reagent_flask_present == False:
                self.logger.warning(
                    'WARNING: No flask present for {0}'.format(reagent.id))
                flasks_ok = False
        return flasks_ok


    ###################################
    ### MAP GRAPH HARDWARE TO STEPS ###
    ###################################

    def _get_hardware_map(self) -> None:
        """
        Get map of hardware IDs in XDL to hardware IDs in graphML.
        """
        self._xdl.hardware_map = {}
        for xdl_hardware_list, graphml_hardware_list in zip(
            [self._xdl.hardware.reactors, self._xdl.hardware.filters,
             self._xdl.hardware.separators],
            [self._graph_hardware.reactors, self._graph_hardware.filters,
             self._graph_hardware.separators]
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

            if not isinstance(step, AbstractBaseStep):
                self._add_internal_properties_to_steps(step.steps)


    def _add_internal_properties_to_steps(self, step_list: List[Step]) -> None:
        """Recursively add internal properties to all steps and substeps in
        given list of steps.

        Args:
            step_list (List[Step]): List of steps to add internal properties to.
        """
        for step in step_list:

            # Set step.waste_vessel to nearest waste_vessel to vessel involved
            # in step.
            if 'waste_vessel' in step.properties and not step.waste_vessel:
                step.waste_vessel = self._get_waste_vessel(step)

            if 'solvent_vessel' in step.properties and not step.solvent_vessel:
                step.solvent_vessel = self._get_reagent_vessel(step.solvent)

            if ('eluting_solvent_vessel' in step.properties
                and step.eluting_solvent):
                step.eluting_solvent_vessel = self._get_reagent_vessel(
                    step.eluting_solvent)

            if 'reagent_vessel' in step.properties and not step.reagent_vessel:
                step.reagent_vessel = self._get_reagent_vessel(step.reagent)

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

            if ('vacuum_valve' in step.properties):
                if step.vacuum in self._valve_map:
                    step.vacuum_valve = self._valve_map[step.vacuum]
                    step.valve_unused_port = get_unused_valve_port(
                        graph=self._graph, valve_node=step.vacuum_valve)

            if 'vacuum_device' in step.properties:
                step.vacuum_device = vacuum_device_attached_to_flask(
                    graph=self._graph, flask_node=step.vacuum)

            if 'vessel_has_stirrer' in step.properties:
                step.vessel_has_stirrer = not step.vessel in [
                    item.id
                    for item in self._graph_hardware.rotavaps
                                + self._graph_hardware.flasks]

            if 'vessel_type' in step.properties and not step.vessel_type:
                step.vessel_type = self._get_vessel_type(step.vessel)

            if 'volume' in step.properties and type(step) == CleanVessel:
                if step.volume == None:
                    step.volume = self._graph_hardware[
                        step.vessel].max_volume * CLEAN_VESSEL_VOLUME_FRACTION

            if ('collection_flask_volume' in step.properties
                 and not step.collection_flask_volume):
                rotavap = self._graph_hardware[step.rotavap_name]
                if 'collection_flask_volume' in rotavap.properties:
                    step.collection_flask_volume = rotavap.collection_flask_volume

            # When doing FilterThrough or RunColumn and from_vessel and to_vessel
            # are the same, find an unused reactor to use as a buffer flask.
            if ('buffer_flask' in step.properties
                 and step.from_vessel == step.to_vessel
                 and not step.buffer_flask):
                step.buffer_flask = self._get_buffer_flask(step.from_vessel)

            # Add filter dead volume to WashSolid steps
            if ('filter_dead_volume' in step.properties
                and not step.filter_dead_volume):
                vessel = self._graph_hardware[step.vessel]
                if 'dead_volume' in vessel.properties:
                    step.filter_dead_volume = vessel.dead_volume

            if not isinstance(step, AbstractBaseStep):
                self._add_internal_properties_to_steps(step.steps)

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

    def _add_internal_properties(self) -> None:
        """
        Go through steps in XDL and fill in internal properties for all steps
        and substeps.
        """
        self._add_internal_properties_to_steps(self._xdl.steps)

        # Give IDs of all waste vessels to clean backbone steps.
        for step in self._xdl.steps:
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

    def _get_buffer_flask(self, vessel: str) -> str:
        """Get buffer flask closest to given vessel.

        Args:
            vessel (str): Node name in graph.

        Returns:
            str: Node name of buffer flask (unused reactor) nearest vessel.
        """
        # Get all reactor IDs
        reactors = [reactor.id
                    for reactor in self._graph_hardware.reactors]

        # Remove reactor IDs that are actually used as reactors not just
        # buffer flasks.
        for i in reversed(range(len(reactors))):
            reactor = reactors[i]
            reactor_neighbours = self._graph.neighbors(reactor)
            for neighbour in reactor_neighbours:
                if self._graph.nodes[neighbour]['type'] != 'ChemputerValve':
                    reactors.pop(i)
                    break

        # From remaining reactor IDs, return nearest to vessel.
        if reactors:
            if len(reactors) == 1:
                return reactors[0]
            else:
                shortest_paths = []
                for reactor in reactors:
                    shortest_paths.append((
                        reactor,
                        shortest_path_length(
                            self._graph, source=vessel, target=reactor)))
                return sorted(shortest_paths, key=lambda x: x[1])[0][0]
        return None

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

    def _get_reagent_vessel(self, reagent: str) -> Union[str, None]:
        """Get vessel containing given reagent.

        Args:
            reagent (str): Name of reagent to find vessel for.

        Returns:
            str: ID of vessel containing given reagent.
        """
        for flask in self._graph_hardware.flasks:
            if flask.chemical == reagent:
                return flask.id
        return None

    def _get_waste_vessel(self, step: Step) -> Union[None, str]:
        """
        Get nearest waste node to given step.
        """
        nearest_node = None
        if type(step) in [Add, WashSolid, CleanVessel, Dry]:
            nearest_node = step.vessel

        elif type(step) in [
            Filter,
            AddFilterDeadVolume,
            RemoveFilterDeadVolume
        ]:
            nearest_node = step.filter_vessel

        elif type(step) == Separate:
            nearest_node = step.separation_vessel

        elif type(step) == Evaporate:
            nearest_node = step.rotavap_name

        if not nearest_node:
            return None
        else:
            return self._waste_map[nearest_node]


    #########################
    ### ADD IMPLIED STEPS ###
    #########################

    def _add_implied_steps(self, interactive: bool = True) -> None:
        """Add extra steps implied by explicit XDL steps."""
        self._add_filter_dead_volume_handling_steps()
        if self._xdl.auto_clean:
            self._add_implied_clean_vessel_steps()
            self._add_implied_clean_backbone_steps(interactive=interactive)

    def _add_implied_clean_backbone_steps(
        self, interactive: bool = True) -> None:
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

    def _add_implied_clean_vessel_steps(self) -> None:
        """Add CleanVessel steps after steps which completely empty a vessel."""
        add_vessel_cleaning_steps(self._xdl, self._graph_hardware)
        self._add_internal_properties()

###################################
### FILTER DEAD VOLUME HANDLING ###
###################################

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
                format: [(step_index, filter_vessel_name, {vessel: VesselContents, ...},...]
        """
        filter_emptying_steps = []
        full_vessel_contents = []
        prev_vessel_contents = {}
        for i, _, vessel_contents in iter_vessel_contents(
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
                   and filter_vessel in full_vessel_contents[j-1]
                   and full_vessel_contents[j-1][filter_vessel].reagents):
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
                self._xdl.steps.insert(i,
                    RemoveFilterDeadVolume(
                        filter_vessel=vessel,
                        dead_volume=self._get_filter_dead_volume(vessel)))

    def _add_filter_inert_gas_connect_steps(self) -> None:
        """Add steps to self._xdl.steps to implement the following:
        1) Connection of inert gas to bottom of filter flasks at start of
        procedure.
        """
        # Connect inert gas to bottom of filter flasks at start of procedure.
        for filter_vessel in self._graph_hardware.filters:
            self._xdl.steps.insert(
                0, CConnect(
                    from_vessel=self._inert_gas_map[filter_vessel.id],
                    to_vessel=filter_vessel.id,
                    to_port=BOTTOM_PORT))


    ###################################
    ### SOLIDIFY IMPLIED PROPERTIES ###
    ###################################

    def _add_all_volumes(self) -> None:
        """When volumes in CMove commands are specified by 'all', change
        these to max_volume of vessel.
        """
        for step in self._xdl.steps:
            for base_step in self._xdl.climb_down_tree(step):
                if type(base_step) == CMove and base_step.volume == 'all':
                    base_step.volume = self._graph_hardware[
                        base_step.from_vessel].max_volume

    def _add_filter_volumes(self) -> None:
        """
        Add volume of filter bottom (aka dead_volume) and volume of material
        added to filter top to Filter steps.
        """
        prev_vessel_contents = {}
        for _, step, vessel_contents in iter_vessel_contents(
            self._xdl.steps, self._graph_hardware):
            if type(step) == Filter:
                if step.filter_vessel in prev_vessel_contents:
                    step.filter_top_volume = max(prev_vessel_contents[
                        step.filter_vessel].volume, 0)
                    if step.filter_top_volume <= 0:
                        step.filter_top_volume = self._graph_hardware[
                            step.filter_vessel].max_volume
                else:
                    step.filter_top_volume = self._graph_hardware[
                        step.filter_vessel].max_volume

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
            List[List[Step]]: List of steps with temperatures added to CleanVessel
                steps.
        """
        for step in self._xdl.steps:
            if type(step) == CleanVessel:
                if step.temp == None:
                    solvent = step.solvent.lower()
                    if solvent in SOLVENT_BOILING_POINTS:
                        step.temp = (SOLVENT_BOILING_POINTS[solvent]
                                    * CLEAN_VESSEL_BOILING_POINT_FACTOR)
                    else:
                        step.temp = 30

    ##########################
    ### OPTIMISE PROCEDURE ###
    ##########################

    def _tidy_up_procedure(self) -> None:
        """Remove steps that are pointless and optimise procedure."""
        self._set_all_stir_speeds()
        self._stop_stirring_when_vessels_lose_scope()
        self._remove_pointless_backbone_cleaning()
        self._no_waiting_if_dry_run()

    def _optimise_separation_steps(self) -> None:
        """Optimise separation steps to reduce risk of backbone contamination.
        The issue this addresses is that if a product is extracted into the
        aqueous phase, but the organic phase ends up in the backbone, the product
        can redissolve in the organic phase when transferred out of the separator.

        Rules implemented here:

        If:
        1) to_vessel of one Separate step is the separation_vessel
        2) Next Separate step uses same kind of solvent (organic or aqueous)

        Then:
        the separation step shouldn't remove the dead volume as you
        run the risk of contaminating the backbone, and there is no need to
        remove the dead volume to risk contaminating the product phase as
        more solvent is going to be added anyway in the next step.
        """
        steps = self._xdl.steps
        for i in range(len(steps)):
            step = steps[i]
            if type(step) == Separate:
                if (step.to_vessel == step.separation_vessel
                    or step.waste_phase_to_vessel == step.separation_vessel):
                    j = i + 1
                    next_solvent = None
                    while j < len(steps):
                        if type(steps[j]) == Separate:
                            next_solvent = steps[j].solvent
                            break
                        j += 1
                    if (next_solvent
                        and is_aqueous(next_solvent) == is_aqueous(step.solvent)):
                        step.remove_dead_volume = False

    def find_stirring_schedule(
        self, step: Step, stirring: List[str]) -> List[str]:
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
        elif not isinstance(step, AbstractBaseStep):
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
        for i, step, vessel_contents in iter_vessel_contents(
            self._xdl.steps, self._graph_hardware):
            for prop, val in step.properties.items():
                if 'vessel' in prop and val in stirring_schedule[i]:
                    if (val in vessel_contents
                        and not vessel_contents[val].reagents):

                        insertions.append((i + 1, StopStir(vessel=val)))

    def _set_all_stir_speeds(self) -> None:
        """Set stir RPM to default at start of procedure for all stirrers
        used in procedure.
        """
        stir_vessels = []
        for step in self._xdl.base_steps:
            if type(step) == CStir:
                if not step.vessel in stir_vessels:
                    stir_vessels.append(step.vessel)
        for vessel in stir_vessels:
            self._xdl.steps.insert(
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


    ############
    ### MISC ###
    ############

    def _print_warnings(self) -> None:
        for warning in self._warnings:
            self.logger.info(warning)

    ######################
    ### PUBLIC METHODS ###
    ######################

    def prepare_for_execution(
        self, graph_file: Union[str, Dict], interactive=True) -> None:
        """
        Prepare the XDL for execution on a Chemputer corresponding to the given
        graph. Any one of graphml_file, json_data, or json_file must be given.

        Args:
            graph_file (str, optional): Path to graph file. May be GraphML file,
                                        JSON file with graph in node link format,
                                        or dict containing graph in same format
                                        as JSON file.
        """
        if not self._prepared_for_execution:
            # Check XDL is not empty.
            if self._xdl.steps:
                self.logger.info('XDL is valid')

                self._graph = get_graph(graph_file)
                # Load graph, make Hardware object from graph, and map nearest
                # waste vessels to every node.
                self._graph_hardware = hardware_from_graph(self._graph)
                self._waste_map = make_vessel_map(
                    self._graph, CHEMPUTER_WASTE_CLASS_NAME)
                self._vacuum_map = make_vessel_map(
                    self._graph, CHEMPUTER_VACUUM_CLASS_NAME)
                self._inert_gas_map = make_inert_gas_map(self._graph)
                self._valve_map = make_vessel_map(
                    self._graph, CHEMPUTER_VALVE_CLASS_NAME)

                # Check hardware compatibility
                if self._hardware_is_compatible():
                    self.logger.info('Hardware is compatible')
                    self._check_all_flasks_present()

                    # Map graph hardware to steps.
                    # _map_hardware_to_steps is called twice so that
                    # _xdl.iter_vessel_contents has all vessels to play with
                    # during _add_implied_steps.
                    self._get_hardware_map()
                    self._map_hardware_to_steps()
                    self._add_internal_properties()
                    # Add in steps implied by explicit steps.
                    self._add_implied_steps(interactive=interactive)
                    # Convert implied properties to concrete values.
                    self._add_clean_vessel_temps()
                    self._optimise_separation_steps()
                    self._add_internal_properties()
                    self._add_all_volumes()
                    self._add_filter_volumes()

                    # Optimise procedure.
                    self._tidy_up_procedure()

                    self._print_warnings()
                    self._prepared_for_execution = True

                else:
                    self.logger.error(
                        "Hardware is not compatible. Can't execute.")

    def execute(self, chempiler: 'Chempiler') -> None:
        """Execute XDL procedure with given chempiler. The same graph must be
        passed to the chempiler and to prepare_for_execution.

        Args:
            chempiler (chempiler.Chempiler): Chempiler object to execute XDL
                                             with.
        """
        if self._prepared_for_execution:
            self._xdl.print_full_xdl_tree()
            self._xdl.log_human_readable()
            self.logger.info('Execution\n---------\n')
            for step in self._xdl.steps:
                self.logger.info(step.name)
                try:
                    keep_going = step.execute(chempiler, self.logger)
                except Exception as e:
                    self.logger.info(
                        'Step failed {0} {1}'.format(
                            type(step), step.properties))
                    raise e
                if not keep_going:
                    return
        else:
            self.logger.error(
                'Not prepared for execution. Prepare by calling xdlexecutor.prepare_for_execution with your graph.')


def should_remove_clean_backbone_step(
    before_step: Step, after_step: Step) -> bool:
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
