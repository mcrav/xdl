import statistics
from ..constants import *
from ..steps import *
from .graph import hardware_from_graph, get_graph, make_waste_map

# Steps after which backbone should be cleaned
CLEAN_BACKBONE_AFTER_STEPS = [
    Add,
    WashSolution,
    Extract,
    MakeSolution,
    WashFilterCake,
    Filter,
    Dry,
]

class XDLExecutor(object):

    def __init__(self, xdl):
        self._xdl = xdl
        self._warnings = []
        self._prepared_for_execution = False

    def prepare_for_execution(
        self, graphml_file=None, json_data=None, json_file=None):
        """
        Prepare the XDL for execution on a Chemputer corresponding to the given
        graph. Any one of graphml_file, json_data, or json_file must be given.
        
        Args:
            graphml_file (str, optional): Path to graphML file.
            json_data (str, optional): Graph in node link JSON format.
            json_file (str, optional): Path to file containing node link JSON 
                                       graph.
        """
        if not self._prepared_for_execution:
            # Check XDL is not empty.
            if self._xdl.steps:
                print('XDL is valid')

                # Load graph, make Hardware object from graph, and map nearest
                # waste vessels to every node.
                self._graph = get_graph(
                    graphml_file=graphml_file, json_data=json_data,
                    json_file=json_file)                )
                self._graph_hardware = hardware_from_graph(self._graph)
                self._waste_map = make_waste_map(self._graph)

                # Check hardware compatibility
                if self._hardware_is_compatible():
                    print('Hardware is compatible')
                    self._check_all_flasks_present()

                    # Map graph hardware to steps.
                    self._map_hardware_to_steps()

                    # Add in steps implied by explicit steps.
                    self._add_implied_steps()

                    # Convert implied properties to concrete values.
                    self._add_all_volumes()
                    self._add_filter_volumes()
                    self._tidy_up_procedure()

                    # Check safety of procedure
                    if self._check_safety():
                        print('Procedure raises no safety flags')
                        self._prepared_for_execution = True


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
                if self._graph.node[flask]['properties']['chemical'] == reagent:
                    reagent_flask_present = True
            if reagent_flask_present == False:
                self._warnings.append(
                    'No flask present for {0}'.format(reagent))
                flasks_ok = False
        return flasks_ok


    ###################################
    ### MAP GRAPH HARDWARE TO STEPS ###
    ###################################

    def _map_hardware_to_steps(self):
        """
        Go through steps in XDL and replace XDL hardware IDs with IDs
        from the graph.
        """
        self._get_hardware_map()
        for step in self._xdl.steps:
            # Change all vessel IDs in steps to corresponding ones in graph.
            for prop, val in step.properties.items():
                if isinstance(val, str) and val in self._xdl.hardware_map:
                    step.properties[prop] = self._xdl.hardware_map[val]
            step.update()

            # Set step.waste_vessel to nearest waste_vessel to vessel involved 
            # in step.
            if 'waste_vessel' in step.properties and not step.waste_vessel:
                step.waste_vessel = self._get_waste_vessel(step)

        # Give IDs of all waste vessels to clean backbone steps.
        for step in self._xdl.steps:
            if type(step) == CleanBackbone:
                step.waste_vessels = self._graph_hardware.waste_xids

    def _get_waste_vessel(self, step):
        """
        Get nearest waste node to given step. 
        """
        nearest_node = None
        if type(step) == Add:
            nearest_node = step.vessel
                
        elif type(step) in [PrepareFilter, Filter, Dry, WashFilterCake]:
            nearest_node = step.filter_vessel

        elif type(step) in [WashSolution, Extract]:
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
        self._add_implied_clean_backbone_steps()

    def _get_step_reagent_types(self):
        """Get the reagent type, 'organic' or 'aqueous' involved in every step.
        
        Returns:
            List[str]: List of reagent types, 'organic' or 'aqueous',
                corresponding to every step in self._xdl.steps.
        """

        step_reagent_types = []
        step_reagent_type = 'organic'
        for i, step, vessel_contents, additions in self._xdl.iter_vessel_contents(
            additions=True):
            if additions:
                step_reagent_type = 'organic'
                for reagent in additions:
                    for word in AQUEOUS_KEYWORDS:
                        if word in reagent[0]:
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
            reagent = DEFAULT_ORGANIC_CLEANING_SOLVENT
            if clean_type == 'water':
                reagent = 'water'
            self._xdl.steps.insert(i, CleanBackbone(reagent=reagent))

    def _add_implied_prepare_filter_steps(self):
        """
        Add PrepareFilter steps if filter top is being used, to fill up the 
        bottom of the filter with solvent, so material added to the top doesn't 
        drip through.
        """
        filters = []
        full_vessel_contents = []
        prev_vessel_contents = {}
        for i, step, vessel_contents in self._xdl.iter_vessel_contents():
            full_vessel_contents.append(vessel_contents)
            for vessel, contents in vessel_contents.items():
                if 'filter' in vessel and vessel in prev_vessel_contents:
                    if not contents and prev_vessel_contents[vessel]:
                        filters.append((i, vessel, prev_vessel_contents))
                        break
            prev_vessel_contents = vessel_contents
    
        for filter_i, filter_vessel, filter_contents in reversed(filters):
            j = filter_i - 1
            while j > 0 and full_vessel_contents[j-1][filter_vessel]:
                j -= 1
            solvent = None
            filter_bottom_contents = filter_contents[filter_vessel]
            volume_threshold = 0.7 * statistics.mean([item[1] for item in filter_bottom_contents]) # Find first thing that could be considered a solvent. 0.7 is arbitrary.
            for reagent in filter_bottom_contents:
                if reagent[1] > volume_threshold:
                    solvent = reagent[0]
                    break
            if '_m_' in solvent:
                solvent = 'water'
            self._xdl.steps.insert(j, PrepareFilter(filter_vessel=filter_vessel, solvent=solvent)) 


    ###################################
    ### SOLIDIFY IMPLIED PROPERTIES ###
    ###################################

    def _add_all_volumes(self):
        """When volumes in CMove commands are specified by 'all', change
        these to max_volume of vessel.
        """
        base_steps = BASE_STEP_OBJ_DICT.values()
        for step in self.steps:
            for base_step in climb_down_tree(step):
                if type(base_step) == CMove and base_step.volume == 'all':
                    base_step.volume = self._graph_hardware[
                        base_step.from_vessel].max_volume

    def _add_filter_volumes(self):
        """
        Add volume of filter bottom (aka dead_volume) to PrepareFilter steps.
        Add volume of filter bottom (aka dead_volume) and volume of material
        added to filter top to Filter steps.
        """
        prev_vessel_contents = {}
        for i, step, vessel_contents in self._xdl.iter_vessel_contents():
            if type(step) == PrepareFilter:
                step.volume = self._get_filter_dead_volume(step.filter_vessel)
            elif type(step) == Filter:
                step.filter_bottom_volume = self._get_filter_dead_volume(
                    step.filter_vessel)
                step.filter_top_volume = sum(
                    [reagent[1] 
                     for reagent in prev_vessel_contents[step.filter_vessel]])
            elif type(step) in [WashSolution, Extract]:
                if 'filter' in step.from_vessel:
                    step.filter_dead_volume = self._get_filter_dead_volume(
                        step.from_vessel)
            prev_vessel_contents = vessel_contents


    def _tidy_up_procedure(self):
        self._remove_pointless_pump_priming()
        self._keep_stirring_when_possible()
        
    def _remove_pointless_pump_priming(self):
        i = len(self._xdl.steps) - 1
        while i > 0:
            step = self._xdl.steps[i]
            if type(step) == CleanBackbone:
                reagents = []
                if i > 0 and i < len(self._xdl.steps) - 1:
                    before_step = self._xdl.steps[i - 1]
                    after_step = self._xdl.steps[i + 1]
                    # Don't clean between filter and subsequent dry.
                    if type(before_step) == Filter and type(after_step) == Dry:
                        self._xdl.steps.pop(i)
                    # If adding same thing twice in a row don't clean in between.
                    else:
                        for other_step in [before_step, after_step]:
                            if type(other_step) == Add:
                                reagents.append(other_step.reagent)
                            elif type(other_step) == PrepareFilter:
                                reagents.append(other_step.solvent)
                            
                        if len(reagents) == 2 and len(set(reagents)) == 1:
                            self._xdl.steps.pop(i)
            i -= 1

    def _keep_stirring_when_possible(self):
        stirring = {}
        insertions = []
        stir_steps = [Add, Chill, StopChiller, Reflux, ChillBackToRT, HeatAndReact, ContinueStirToRT]

        for i, step in enumerate(self._xdl.steps):
            if type(step) != CleanBackbone:
                if type(step) in stir_steps:
                    vessel = step.vessel
                    if is_generic_filter_name(vessel):
                        vessel = filter_top_name(vessel)
                    if is_generic_separator_name(vessel):
                        vessel = separator_top_name(vessel)
                    if not vessel in stirring or not stirring[vessel]:
                        stirring[vessel] = True
                        insertions.append((i, StartStir(vessel)))
                else:
                    for vessel in list(stirring.keys()):
                        if stirring[vessel]:
                            insertions.append((i, CStopStir(vessel)))
                            stirring[vessel] = False

        for i, step in reversed(insertions):
            self._xdl.steps.insert(i, step)

        for i in reversed(range(len(self._xdl.steps))):
            step = self._xdl.steps[i]
            if type(step) != CleanBackbone:
                if type(step) == CStopStir:
                    return
                elif type(step) == StartStir:
                    self._xdl.steps.pop(i)
                    return

        # steps = [step for step in self._xdl.steps if type(step) != CleanBackbone]
        # for i in range(len(steps)):
        #     step = steps[i]
        #     if type(step) in stir_steps:
        #         before_step, after_step = None, None
        #         if i > 0:
        #             before_step = steps[i - 1]
        #         if i < len(steps) - 1:
        #             after_step = steps[i + 1]
        #         if before_step and type(before_step) in stir_steps:
        #             step.start_stir = False
        #         else:
        #             step.start_stir = True
        #         if after_step and type(after_step) in stir_steps:
        #             step.stop_stir = False
        #         else:
        #             step.stop_stir = True


    def execute(self, graphml_file=None, json_graph=None, json_graph_file=None, chempiler=None):
        """Execute XDL procedure on a Chemputer corresponding to given graphML file."""
        self.prepare_for_execution(
            graphml_file=graphml_file, json_data=json_graph, json_file=json_graph_file,)

        if self._prepared_for_execution:
            self._xdl.print_full_xdl_tree()
            self._xdl.print_full_human_readable()
            print('Execution\n---------\n')
            for step in self._xdl.steps:
                print(f'\n{step.name}\n{len(step.name)*"-"}\n')
                print(f'{step.human_readable}\n')
                keep_going = step.execute(chempiler)
                if not keep_going:
                    return
                
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
                    xdl_hardware_list[i].cid
                ] = graphml_hardware_list[i].cid

