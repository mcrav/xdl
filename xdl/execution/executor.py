import statistics
import copy
import logging
from typing import List, Union, Tuple
if False:
    from ..xdl import XDL
    from chempiler import Chempiler

from ..constants import *
from ..utils.namespace import BASE_STEP_OBJ_DICT
from ..steps import *
from ..safety import procedure_is_safe
from .tracking import iter_vessel_contents
from .graph import (
    hardware_from_graph, get_graph, make_vessel_map, make_filter_inert_gas_map)

# Steps after which backbone should be cleaned
CLEAN_BACKBONE_AFTER_STEPS: List[type] = [
    Add,
    Separate,
    MakeSolution,
    WashFilterCake,
    Filter,
    Dry,
]

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

            # Set step.waste_vessel to nearest waste_vessel to vessel involved 
            # in step.
            if 'waste_vessel' in step.properties and not step.waste_vessel:
                step.waste_vessel = self._get_waste_vessel(step)

            if 'solvent_vessel' in step.properties and not step.solvent_vessel:
                step.solvent_vessel = self._get_reagent_vessel(step.solvent)

            if 'reagent_vessel' in step.properties and not step.reagent_vessel:
                step.reagent_vessel = self._get_reagent_vessel(step.reagent)

            if 'vacuum' in step.properties and not step.vacuum:
                step.vacuum = self._get_vacuum(step.filter_vessel)

            if step.name not in BASE_STEP_OBJ_DICT:
                self._map_hardware_to_step_list(step.steps)

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

    def _get_vacuum(self, filter_vessel: str) -> str:
        return self._vacuum_map[filter_vessel]

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
        if type(step) == Add:
            nearest_node = step.vessel
                
        elif type(step) in [Filter, Dry, WashFilterCake]:
            nearest_node = step.filter_vessel

        elif type(step) == Separate:
            nearest_node = step.separation_vessel

        if not nearest_node:
            return None
        else:
            return self._waste_map[nearest_node]


    #########################
    ### ADD IMPLIED STEPS ###
    #########################

    def _add_implied_steps(self) -> None:
        """Add extra steps implied by explicit XDL steps."""
        if self._xdl.auto_clean:
            self._add_implied_clean_backbone_steps()
        self._add_filter_inert_gas_connect_steps()

    def _get_step_reagent_types(self) -> List[str]:
        """Get the reagent type, 'organic' or 'aqueous' involved in every step.
        
        Returns:
            List[str]: List of reagent types, 'organic' or 'aqueous',
                corresponding to every step in self._xdl.steps.
        """
        step_reagent_types = []
        step_reagent_type = 'organic'
        for _, _, _, additions in iter_vessel_contents(
            self._xdl.steps, self._graph_hardware, additions=True):
            if additions:
                step_reagent_type = 'organic'
                for reagent in additions:
                    if is_aqueous(reagent):
                        step_reagent_type = 'aqueous'
                        break
            step_reagent_types.append(step_reagent_type)
        return step_reagent_types

    def _get_clean_backbone_steps(self) -> List[int]:
        """Get list of steps after which backbone should be cleaned.
        
        Returns:
            List[int]: List of indexes for steps after which the backbone should
                be cleaned.
        """
        clean_backbone_steps = []
        for i, step in enumerate(self._xdl.steps):
            if type(step) in CLEAN_BACKBONE_AFTER_STEPS:
                clean_backbone_steps.append(i)
        return clean_backbone_steps

    def _get_clean_backbone_sequence(self) -> List[Tuple[int, str]]:
        """Get sequence of backbone cleans required. clean_type can be 'organic'
        or 'aqueous'.
        
        Returns:
            List[int, str]: List of Tuples like this
                [(step_to_insert_backbone_clean, clean_type), ]
        """
        step_reagent_types = self._get_step_reagent_types()
        clean_backbone_steps = self._get_clean_backbone_steps()
        cleans = []
        for _, step_i in enumerate(clean_backbone_steps):

            # Get after_type and before_type
            if step_i+1 < len(step_reagent_types):
                after_type = step_reagent_types[step_i+1]
            else:
                after_type = 'organic'
            before_type = step_reagent_types[step_i] 

            # Workout sequence of cleans needed.
            # organic then organic -> organic clean
            # aqueous then organic -> aqueous clean then organic clean
            # organic then aqueous -> organic clean then aqueous clean
            # aqueous then aqueous -> aqueous clean
            if before_type == 'organic' and after_type == 'organic':
                cleans.append((step_i+1, 'organic'))
            elif before_type == 'aqueous' and after_type == 'organic':
                cleans.append((step_i+1, 'water'))
                cleans.append((step_i+1, 'organic'))
            elif before_type == 'organic' and after_type == 'aqueous':
                cleans.append((step_i+1, 'organic'))
                cleans.append((step_i+1, 'water'))
            elif before_type == 'aqueous' and after_type == 'aqueous':
                cleans.append((step_i+1, 'water'))
        return cleans

    def _add_implied_clean_backbone_steps(self) -> None:
        """Add CleanBackbone steps after certain steps which will contaminate 
        the backbone. 
        Takes into account when organic and aqueous reagents have been used to 
        determine what solvents to clean the backbone with.
        """
        for i, clean_type in reversed(self._get_clean_backbone_sequence()):
            print(clean_type)
            solvent = self._xdl.organic_cleaning_reagent 
            if clean_type == 'water':
                solvent = self._xdl.aqueous_cleaning_reagent
            self._xdl.steps.insert(i, CleanBackbone(solvent=solvent))

    def _add_filter_inert_gas_connect_steps(self) -> None:
        """Add steps to self._xdl.steps to implement the following:
        1) Connection of inert gas to bottom of filter flasks at start of
        procedure.
        2) Reconnect inert gas to bottom of filter flasks after filtration
        sequences.
        """
        # Connect inert gas to bottom of filter flasks at start of procedure.
        for filter_vessel in self._graph_hardware.filters:
            self._xdl.steps.insert(
                0, CConnect(
                    from_vessel=self._filter_inert_gas_map[filter_vessel.id],
                    to_vessel=filter_vessel.id,
                    to_port=BOTTOM_PORT))

        # Reconnect inert gas to bottom of filter flasks after filtration
        # sequences.
        filter_step_types = [Filter, WashFilterCake, Dry]
        for i in reversed(range(len(self._xdl.steps))):
            step = self._xdl.steps[i]
            if type(step) in filter_step_types:
                self._xdl.steps.insert(
                    i+1,
                    CConnect(
                        from_vessel=self._filter_inert_gas_map[
                            step.filter_vessel],
                        to_vessel=step.filter_vessel,
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
            print(step)
            print(vessel_contents)
            print('\n')
            if type(step) == Filter:
                step.filter_top_volume = prev_vessel_contents[
                    step.filter_vessel]['volume']

            prev_vessel_contents = vessel_contents


    ##########################
    ### OPTIMISE PROCEDURE ###
    ##########################

    def _tidy_up_procedure(self) -> None:
        """Remove steps that are pointless."""
        self._remove_pointless_backbone_cleaning()
        self._no_waiting_if_dry_run()

    def _no_waiting_if_dry_run(self) -> None:
        if self._xdl.dry_run:
            for step in self._xdl.steps:
                self._set_all_waits_to_one(step)

    def _set_all_waits_to_one(self, step: Step) -> None:
        for step in step.steps:
            if type(step) == Wait:
                step.time = 1
            elif hasattr(step, 'steps'):
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


    ####################
    ### CHECK SAFETY ###
    ####################

    def _check_safety(self) -> bool:
        """
        Check if the procedure is safe.
        Any issues will be printed.

        Returns:
            bool: True if no safety issues are found, False otherwise.
        """
        return procedure_is_safe(self._xdl.steps, self._xdl.reagents)


    ######################
    ### PUBLIC METHODS ###
    ######################

    def prepare_for_execution(self, graph_file: Union[str, Dict]) -> None:
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
                self._filter_inert_gas_map = make_filter_inert_gas_map(
                    self._graph)

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

                    # Add in steps implied by explicit steps.
                    self._add_implied_steps()
                    self._map_hardware_to_steps()

                    # Convert implied properties to concrete values.
                    self._add_all_volumes()
                    self._add_filter_volumes()

                    # Optimise procedure.
                    self._tidy_up_procedure()

                    # Check safety of procedure
                    self._check_safety()

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
            self._xdl.print_full_human_readable()
            self.logger.info('Execution\n---------\n')
            for step in self._xdl.steps:
                self.logger.info(step.name)
                repeats = 1
                if 'repeat' in step.properties: repeats = int(step.repeat)
                for _ in range(repeats):
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
                

def is_aqueous(reagent_name: str) -> bool:
    """Return True if reagent_name is an aqueous reagent, otherwise False.
    
    Args:
        reagent_name (str): Name of reagent.
    
    Returns:
        bool: True if reagent_name is aqueous, otherwise False.
    """
    for word in AQUEOUS_KEYWORDS:
        if word in reagent_name:
            return True
    return False

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