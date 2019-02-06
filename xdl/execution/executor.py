import statistics
import copy
import logging

from ..constants import *
from ..utils.namespace import BASE_STEP_OBJ_DICT
from ..steps import *
from ..safety import procedure_is_safe
from .tracking import iter_vessel_contents
from .graph import hardware_from_graph, get_graph, make_vessel_map

# Steps after which backbone should be cleaned
CLEAN_BACKBONE_AFTER_STEPS = [
    Add,
    Separate,
    MakeSolution,
    WashFilterCake,
    Filter,
    Dry,
]

# Steps that should be stirred.
STIR_STEPS = [Add, Chill, ChillerReturnToRT, Reflux]

class XDLExecutor(object):
 
    """Class to execute XDL objects. To execute first call prepare_for_execution
    then execute.

    Public methods:
        prepare_for_execution(graphml_file=None, json_data=None, json_file=None)
        execute(chempiler)
    """

    def __init__(self, xdl):
        """XDLExecutor init method.
        
        Args:
            xdl (XDL): XDL object to execute.
        """
        self._xdl = xdl
        self._warnings = []
        self._prepared_for_execution = False

    ####################################
    ### CHECK HARDWARE COMPATIBILITY ###
    ####################################

    def _hardware_is_compatible(self):
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

    def _check_all_flasks_present(self):
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
                if 'chemical' in self._graph.node[flask.xid]:
                    flask_chemical = self._graph.node[
                        flask.xid]['chemical']
                    if flask_chemical == reagent.xid:
                        reagent_flask_present = True
                        break
            if reagent_flask_present == False:
                self._warnings.append(
                    'No flask present for {0}'.format(reagent.xid))
                flasks_ok = False
        return flasks_ok


    ###################################
    ### MAP GRAPH HARDWARE TO STEPS ###
    ###################################

    def _get_hardware_map(self):
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
                    xdl_hardware_list[i].xid
                ] = graphml_hardware_list[i].xid

    def _map_hardware_to_step_list(self, step_list):
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

    def _map_hardware_to_steps(self):
        """
        Go through steps in XDL and replace XDL hardware IDs with IDs
        from the graph.
        """
        self._map_hardware_to_step_list(self._xdl.steps)

        # Give IDs of all waste vessels to clean backbone steps.
        for step in self._xdl.steps:
            if type(step) == CleanBackbone and not step.waste_vessels:
                step.waste_vessels = self._graph_hardware.waste_xids

    def _get_vacuum(self, filter_vessel):
        return self._vacuum_map[filter_vessel]

    def _get_reagent_vessel(self, reagent):
        """Get vessel containing given reagent.
        
        Args:
            reagent (str): Name of reagent to find vessel for.
        
        Returns:
            str: ID of vessel containing given reagent.
        """
        for flask in self._graph_hardware.flasks:
            if flask.chemical == reagent:
                return flask.xid
        return None

    def _get_waste_vessel(self, step):
        """
        Get nearest waste node to given step. 
        """
        nearest_node = None
        if type(step) == Add:
            nearest_node = step.vessel
                
        elif type(step) in [PrepareFilter, Filter, Dry, WashFilterCake]:
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

    def _add_implied_steps(self):
        """Add extra steps implied by explicit XDL steps."""
        self._add_implied_prepare_filter_steps()
        self._add_implied_remove_dead_volume_steps()
        if self._xdl.autoClean:
            self._add_implied_clean_backbone_steps()
        self._add_implied_stirring_steps()

    def _get_step_reagent_types(self):
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
                    if is_aqueous(reagent[0]):
                        step_reagent_type = 'aqueous'
                        break
            step_reagent_types.append(step_reagent_type)
        return step_reagent_types

    def _get_clean_backbone_steps(self):
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

    def _get_clean_backbone_sequence(self):
        """Get sequence of backbone cleans required. clean_type can be 'organic'
        or 'aqueous'.
        
        Returns:
            List[int, str]: List of Tuples like this
                [(step_to_insert_backbone_clean, clean_type), ]
        """
        step_reagent_types = self._get_step_reagent_types()
        clean_backbone_steps = self._get_clean_backbone_steps()
        cleans = []
        for j, step_i in enumerate(clean_backbone_steps):

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

    def _add_implied_clean_backbone_steps(self):
        """Add CleanBackbone steps after certain steps which will contaminate 
        the backbone. 
        Takes into account when organic and aqueous reagents have been used to 
        determine what solvents to clean the backbone with.
        """
        for i, clean_type in reversed(self._get_clean_backbone_sequence()):
            solvent = self._xdl.organicCleaningReagent 
            if clean_type == 'water':
                solvent = self._xdl.aqueousCleaningReagent
            self._xdl.steps.insert(i, CleanBackbone(solvent=solvent))

    def _get_filter_emptying_steps(self):
        """Get steps at which a filter vessel is emptied. Also return full
        list of vessel contents dict at every step.
        
        Returns:
            Tuple[List, List]: filters and full_vessel_contents in tuple.
                filters -- List of tuples [(step_i, vessel, contents_when_emptied),]
                full_vessel_contents -- List of vessel_contents dicts from every 
                                        step
        """
        filters = []
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
                    if (not contents['reagents']
                        and prev_vessel_contents[vessel]['reagents']):
                        filters.append((i, vessel, prev_vessel_contents))
                        break
            prev_vessel_contents = vessel_contents
        return (filters, full_vessel_contents)

    def _get_filter_dead_volume(self, filter_vessel):
        """Return dead volume (volume below filter) of given filter vessel.
        
        Args:
            filter_vessel (str): xid of filter vessel.
        
        Returns:
            float: Dead volume of given filter vessel.
        """
        for vessel in self._graph_hardware.filters:
            if vessel.xid == filter_vessel:
                return vessel.dead_volume
        return 0

    def _add_implied_prepare_filter_steps(self):
        """
        Add PrepareFilter steps if filter top is being used, to fill up the 
        bottom of the filter with solvent, so material added to the top doesn't 
        drip through.
        """
        # Find steps at which a filter vessel is emptied. Can't just look for
        # Filter steps as liquid may be transferred to filter flask for other
        # reasons i.e. using the chiller.
        filters, full_vessel_contents = self._get_filter_emptying_steps()

        # Find appropriate reagents to add to filter bottom and add
        # PrepareFilter steps
        for filter_i, filter_vessel, filter_contents in reversed(filters):
            j = filter_i - 1

            # Find point at which first reagent is added to filter vessel.
            # This is the point at which to insert the PrepareFilter step.
            while (j > 0 and full_vessel_contents[j-1].get(
                filter_vessel, {}).get('reagents', [])):
                j -= 1

            # Find first thing that could be considered a solvent.
            solvent = max(filter_contents[filter_vessel], key=lambda x: x[1])[0] 
            if is_aqueous(solvent):
                solvent = 'water'
            
            # Insert PrepareFilter step into self._xdl.steps.
            self._xdl.steps.insert(j, PrepareFilter(
                filter_vessel=filter_vessel, solvent=solvent, 
                volume=self._get_filter_dead_volume(filter_vessel)))

    def _add_implied_remove_dead_volume_steps(self):
        """When liquid is transferred from a filter vessel remove dead volume
        first.
        """
        insertions = []
        for i, step in enumerate(self._xdl.steps):
            if 'from_vessel' in step.properties:
                if (self._xdl.hardware[step.from_vessel]
                    == CHEMPUTER_FILTER_CLASS_NAME):
                    insertions.append(i, step.from_vessel)

        for i, filter_vessel in insertions:
            self._xdl._steps.insert(
                RemoveFilterDeadVolume(
                    filter_vessel=filter_vessel, 
                    dead_volume=self._get_filter_dead_volume(filter_vessel)))

    def _add_implied_stirring_steps(self):
        """Add in stirring to appropriate steps."""
        stirring = {}
        insertions = []
        for i, step in enumerate(self._xdl.steps):
            if type(step) != CleanBackbone:
                if type(step) in STIR_STEPS:
                    vessel = step.vessel
                    # If vessel not stirring, add StartStir(vessel)
                    if not vessel in stirring or not stirring[vessel]:
                        stirring[vessel] = True
                        insertions.append((i, StartStir(vessel)))
                else:
                    # If vessel is stirring add StopStir(vessel)
                    for vessel in stirring:
                        if stirring[vessel]:
                            insertions.append((i, StopStir(vessel)))
                            stirring[vessel] = False

        for i, step in reversed(insertions):
            self._xdl.steps.insert(i, step)


    ###################################
    ### SOLIDIFY IMPLIED PROPERTIES ###
    ###################################

    def _add_all_volumes(self):
        """When volumes in CMove commands are specified by 'all', change
        these to max_volume of vessel.
        """
        for step in self._xdl.steps:
            for base_step in self._xdl.climb_down_tree(step):
                if type(base_step) == CMove and base_step.volume == 'all':
                    base_step.volume = self._graph_hardware[
                        base_step.from_vessel].max_volume


    def _add_filter_volumes(self):
        """
        Add volume of filter bottom (aka dead_volume) and volume of material
        added to filter top to Filter steps.
        """
        prev_vessel_contents = {}
        for _, step, vessel_contents in iter_vessel_contents(
            self._xdl.steps, self._graph_hardware):

            if type(step) == Filter:
                step.filter_bottom_volume = self._get_filter_dead_volume(
                    step.filter_vessel)
                step.filter_top_volume = prev_vessel_contents[
                    step.filter_vessel]['volume']

            prev_vessel_contents = vessel_contents


    ##########################
    ### OPTIMISE PROCEDURE ###
    ##########################

    def _tidy_up_procedure(self):
        """Remove steps that are pointless.
        """
        self._remove_pointless_backbone_cleaning()
        
    def _remove_pointless_backbone_cleaning(self):
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

    def _print_warnings(self):
        for warning in self._warnings:
            print(warning)


    ####################
    ### CHECK SAFETY ###
    ####################

    def _check_safety(self):
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

    def prepare_for_execution(
        self, graph_file):
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
                print('XDL is valid')

                self._graph = get_graph(graph_file)
                # Load graph, make Hardware object from graph, and map nearest
                # waste vessels to every node.
                self._graph_hardware = hardware_from_graph(self._graph)
                self._waste_map = make_vessel_map(
                    self._graph, CHEMPUTER_WASTE_CLASS_NAME)
                self._vacuum_map = make_vessel_map(
                    self._graph, CHEMPUTER_VACUUM_CLASS_NAME)

                # Check hardware compatibility
                if self._hardware_is_compatible():
                    print('Hardware is compatible')
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
                    print("Hardware is not compatible. Can't execute.")

    def execute(self, chempiler, logger=None):
        """Execute XDL procedure with given chempiler. The same graph must be
        passed to the chempiler and to prepare_for_execution.
        """
        if not logger:
            logger = logging.getLogger()
        if self._prepared_for_execution:
            self._xdl.print_full_xdl_tree()
            self._xdl.print_full_human_readable()
            for step in self._xdl.steps:
                if logger:
                    logger.info(step.name)
                keep_going = step.execute(chempiler, logger)
                if not keep_going:
                    return
        else:
            print('Not prepared for execution. Prepare by calling xdlexecutor.prepare_for_execution with your graph.')
                

def is_aqueous(reagent_name):
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

def should_remove_clean_backbone_step(before_step, after_step):
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
            elif type(other_step) == PrepareFilter:
                reagents.append(other_step.solvent)
        if len(reagents) == 2 and len(set(reagents)) == 1:
            return True

    return False