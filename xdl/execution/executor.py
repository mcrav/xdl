import statistics
from ..constants import *
from ..steps import *

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
        self.xdl = xdl
        self._prepared_for_execution = False

    def prepare_for_execution(self, graphml_file):
        """
        Prepare the XDL for execution on a Chemputer corresponding to the given
        graphML file.
        
        Arguments:
            graphml_file {str} -- Path to graphML file.
        """
        self.graphml_file = graphml_file
        if not self._prepared_for_execution:
            if self.xdl.steps: # if XDL is valid
                print('XDL is valid')
                self.graphml_hardware = graphml_hardware_from_file(graphml_file)
                if self._hardware_is_compatible():
                    print('Hardware is compatible')
                    self._map_hardware_to_steps(graphml_file)
                    self._add_filter_volumes()
                    self._add_all_volumes()
                    self._tidy_up_procedure()
                    if self._check_safety():
                        print('Procedure raises no safety flags')
                        self._prepared_for_execution = True

    def _add_hidden_clean_backbone_steps(self):
        """
        Add steps to clean the backbone, after certain steps which will contaminate the backbone.
        Takes into account when organic and aqueous reagents have been used to determine what
        solvents to clean the backbone with.
        """
        cleans = []
        step_reagent_types = []
        step_reagent_type = 'organic'
        for i, step, vessel_contents, additions in self.iter_vessel_contents(additions=True):
            if additions:
                step_reagent_type = 'organic'
                for reagent in additions:
                    for word in ['water', 'aqueous', 'acid', '_m_']:
                        if word in reagent[0]:
                            step_reagent_type = 'aqueous'
                            break
            step_reagent_types.append(step_reagent_type)

        clean_backbone_steps = []
        for i, step in enumerate(self.xdl.steps):
            if type(step) in CLEAN_BACKBONE_AFTER_STEPS:
                clean_backbone_steps.append((i, step, step_reagent_types[i]))
        for j, step_tuple in enumerate(clean_backbone_steps):
            step_i, step, step_reagent_type = step_tuple
            if j + 1 < len(clean_backbone_steps):
                after_type = clean_backbone_steps[j+1][2]
            else:
                after_type = 'organic'
            before_type = clean_backbone_steps[j][2]

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

        for i, clean_type in reversed(cleans):
            if clean_type == 'organic':
                self.xdl.steps.insert(i, CleanBackbone(reagent=DEFAULT_ORGANIC_CLEANING_SOLVENT))
            elif clean_type == 'water':
                self.xdl.steps.insert(i, CleanBackbone(reagent='water'))

    def _add_hidden_prepare_filter_steps(self):
        """
        Add PrepareFilter steps if filter top is being used, to fill up the bottom of the filter with solvent,
        so material added to the top doesn't drip through.
        """
        filters = []
        full_vessel_contents = []
        prev_vessel_contents = {}
        for i, step, vessel_contents in self.xdl.iter_vessel_contents():
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
            self.xdl.steps.insert(j, PrepareFilter(filter_vessel=filter_vessel, solvent=solvent)) 

    def _tidy_up_procedure(self):
        self._remove_pointless_pump_priming()
        self._keep_stirring_when_possible()
        
    def _remove_pointless_pump_priming(self):
        i = len(self.xdl.steps) - 1
        while i > 0:
            step = self.xdl.steps[i]
            if type(step) == CleanBackbone:
                reagents = []
                if i > 0 and i < len(self.xdl.steps) - 1:
                    before_step = self.xdl.steps[i - 1]
                    after_step = self.xdl.steps[i + 1]
                    # Don't clean between filter and subsequent dry.
                    if type(before_step) == Filter and type(after_step) == Dry:
                        self.xdl.steps.pop(i)
                    # If adding same thing twice in a row don't clean in between.
                    else:
                        for other_step in [before_step, after_step]:
                            if type(other_step) == Add:
                                reagents.append(other_step.reagent)
                            elif type(other_step) == PrepareFilter:
                                reagents.append(other_step.solvent)
                            
                        if len(reagents) == 2 and len(set(reagents)) == 1:
                            self.xdl.steps.pop(i)
            i -= 1

    def _keep_stirring_when_possible(self):
        stirring = {}
        insertions = []
        stir_steps = [Add, Chill, StopChiller, Reflux, ChillBackToRT, HeatAndReact, ContinueStirToRT]

        for i, step in enumerate(self.xdl.steps):
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
            self.xdl.steps.insert(i, step)

        for i in reversed(range(len(self.xdl.steps))):
            step = self.xdl.steps[i]
            if type(step) != CleanBackbone:
                if type(step) == CStopStir:
                    return
                elif type(step) == StartStir:
                    self.xdl.steps.pop(i)
                    return

        # steps = [step for step in self.xdl.steps if type(step) != CleanBackbone]
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

    def _add_hidden_steps(self):
        """
        Add extra steps implied by explicit XDL steps.
        """
        self._add_hidden_prepare_filter_steps()
        self._add_hidden_clean_backbone_steps()

    def simulate(self, graphml_file, chempiler):
        """Simulate XDL procedure using Chempiler and given graphML file."""
        self.prepare_for_execution(graphml_file)
        if self._prepared_for_execution:
            # self.print_full_xdl_tree()
            # self.print_full_human_readable()
            print('Execution\n---------\n')
            for step in self.xdl.steps:
                print(f'\n{step.name}\n{len(step.name)*"-"}\n')
                print(f'{step.human_readable}\n')
                keep_going = step.execute(chempiler)
                if not keep_going:
                    return

    def execute(self, graphml_file=None, json_graph=None, json_graph_file=None, chempiler=None):
        """Execute XDL procedure on a Chemputer corresponding to given graphML file."""
        self.prepare_for_execution(
            graphml_file=graphml_file, json_graph=json_graph, json_graph_file=json_graph_file,)
        if self._prepared_for_execution:
            self.xdl.print_full_xdl_tree()
            self.xdl.print_full_human_readable()
        print('Execution\n---------\n')
        for step in self.xdl.steps:
            print(f'\n{step.name}\n{len(step.name)*"-"}\n')
            print(f'{step.human_readable}\n')
            keep_going = step.execute(chempiler)
            if not keep_going:
                return
                
    def _get_hardware_map(self):
        """
        Get map of hardware IDs in XDL to hardware IDs in graphML.
        """
        self.hardware_map = {}
        for xdl_hardware_list, graphml_hardware_list in zip(
            [self.hardware.reactors, self.hardware.filters, self.hardware.separators,],
            [self.graphml_hardware.reactors, self.graphml_hardware.filters, self.graphml_hardware.separators,]
        ):
            for i in range(len(xdl_hardware_list)):
                self.hardware_map[
                    xdl_hardware_list[i].cid
                ] = graphml_hardware_list[i].cid
        for k in list(self.hardware_map.keys()):
            v = self.hardware_map[k]
            if 'filter' in k:
                self.hardware_map[filter_top_name(k)] = filter_top_name(v)
                self.hardware_map[filter_bottom_name(k)] = filter_bottom_name(v)
            elif 'separator' in k and is_generic_separator_name(k):
                self.hardware_map[separator_top_name(k)] = separator_top_name(v)
                self.hardware_map[separator_bottom_name(k)] = separator_bottom_name(v)

    def _map_hardware_to_steps(self, graphml_file):
        """
        Go through steps in XDL and replace XDL hardware IDs with IDs
        from the graphML file.
        """
        self._graph = load_graph(graphml_file) 
        self._get_hardware_map()
        for step in self.xdl.steps:
            for prop, val in step.properties.items():
                if isinstance(val, str) and val in self.hardware_map:
                    step.properties[prop] = self.hardware_map[val]
            step.update()
            if 'waste_vessel' in step.properties and not step.waste_vessel:
                step.waste_vessel = self._get_waste_vessel(step)

        for step in self.xdl.steps:
            if type(step) == CleanBackbone:
                step.waste_vessels = self.graphml_hardware.waste_cids

    def _get_waste_vessel(self, step):
        """
        Get nearest waste node to given step. 
        Assumes self._map_hardware_to_steps has already been executed.
        """
        nearest_node = None
        if type(step) == Add:
            nearest_node = step.vessel
            if 'filter' in nearest_node and is_generic_filter_name(nearest_node):
                nearest_node = filter_top_name(nearest_node)
        elif type(step) in [PrepareFilter, Filter, Dry, WashFilterCake]:
            nearest_node = filter_bottom_name(step.filter_vessel)
        elif type(step) in [WashSolution, Extract]:
            nearest_node = separator_bottom_name(step.separation_vessel)
        if not nearest_node:
            return None
        for node_name in self._graph.nodes():
            if node_name == nearest_node:
                for pred in self._graph.pred[node_name]:
                    if pred.startswith('valve'):
                        for succ in self._graph.succ[pred]:
                            if succ.startswith('waste'):
                                return succ
        return None

    def _add_all_volumes(self):
        base_steps = BASE_STEP_OBJ_DICT.values()
        for step in self.steps:
            for sub_step in climb_down_tree(step):
                if type(sub_step) == CMove and sub_step.volume == 'all':
                    sub_step.volume = self.graphml_hardware[sub_step.from_vessel].max_volume

def _hardware_is_compatible(xdl_hardware=None, graphml_hardware=None):
    """Determine if XDL hardware object can be mapped to hardware available in graphML file."""
    enough_reactors = len(xdl_hardware.reactors) <= len(graphml_hardware.reactors)
    enough_filters = len(xdl_hardware.filters) <= len(graphml_hardware.filters)
    enough_separators = len(xdl_hardware.separators) <= len(graphml_hardware.separators)
    flasks_ok = True # NEEDS DONE
    waste_ok = True # NEEDS DONE

    return enough_reactors and enough_filters and flasks_ok and waste_ok