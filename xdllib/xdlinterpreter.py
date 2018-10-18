from lxml import etree
import bs4
from io import StringIO
import re
import copy
import statistics
import os
from chempiler import Chempiler
from .utils import (convert_time_str_to_seconds, convert_volume_str_to_ml, convert_mass_str_to_g, 
    filter_bottom_name, filter_top_name, separator_top_name, separator_bottom_name, parse_bool)
from .constants import *
from .components import *
from .reagents import *
from .steps import *
from .safety import procedure_is_safe
from .syntax_validation import XDLSyntaxValidator
from .namespace import STEP_OBJ_DICT, COMPONENT_OBJ_DICT, BASE_STEP_OBJ_DICT
from .read_graphml import load_graph
import chembrain as cb

# Steps after which backbone should be cleaned
CLEAN_BACKBONE_AFTER_STEPS = [
    Add,
    Wash,
    Extract,
    MakeSolution,
    WashFilterCake,
    Filter,
    Dry,
]

class XDL(object):
    """
    Interpets XDL (file or str) and provides the following public methods:
    
    Public Methods:
        simulate -- Given a graphML file, simulates the XDL procedure.
        execute -- Given a graphML file, executes the XDL procedure on a Chemputer.
        as_human_readable -- Returns human readable description of the XDL procedure.
        print_human_readable -- Prints human readable description of the XDL procedure.
        print_full_xdl_tree -- Prints reasonably human readable visualisation of the nested XDL steps.
    """
    def __init__(self, xdl_file=None, xdl_str=None):
        """        
        Keyword Arguments:
            xdl_file {str} -- File path of XDL file.
            xdl_str {str} -- str of XDL
        """
        self.steps, self.hardware, self.reagent = [], [], []
        self._prepared_for_execution = False
        self.xdl_file = xdl_file
        if xdl_file:
            with open(xdl_file, 'r') as fileobj:
                self.xdl = fileobj.read()
        elif xdl_str:
            self.xdl = xdl_str
        if self.xdl:
            if self._xdl_valid() or 1 == 1:
                self._parse_xdl()
                self._add_hidden_steps()
        else:
            print('No XDL given.')

    def _get_full_xdl_tree(self):
        """
        Get list of all steps after unpacking nested steps.
        Root steps are included followed by all their children in order, recursively.
        """
        tree = []
        for step in self.steps:
            tree.extend(climb_down_tree(step))
        return tree
    
    def _parse_xdl(self):
        """Parse self.xdl and make self.steps, self.hardware and self.reagents lists."""
        self.steps = steps_from_xdl(self.xdl)
        self.hardware = hardware_from_xdl(self.xdl)
        self.reagents = reagents_from_xdl(self.xdl)

    def _xdl_valid(self):
        """Return True is XDL is syntactically valid, otherwise return False."""
        return XDLSyntaxValidator(self.xdl).valid

    def _hardware_is_compatible(self):
        """
        Determine if there is sufficient hardware in the graphML file
        to run the XDL file.
        """
        return _hardware_is_compatible(
            xdl_hardware=self.hardware, 
            graphml_hardware=self.graphml_hardware
        )

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
        for step in self.steps:
            for prop, val in step.properties.items():
                if isinstance(val, str) and val in self.hardware_map:
                    step.properties[prop] = self.hardware_map[val]
            step.update()
            if 'waste_vessel' in step.properties and not step.waste_vessel:
                step.waste_vessel = self._get_waste_vessel(step)

        for step in self.steps:
            if type(step) == CleanBackbone:
                step.waste_vessels = self.graphml_hardware.waste_cids

    def _get_waste_vessel(self, step):
        """
        Get nearest waste node to given step. 
        Assumes self._map_hardware_to_steps has already been executed.
        """
        nearest_node = None
        if type(step) == Add:
            vessel = step.vessel
            if 'filter' in step.vessel and is_generic_filter_name(step.vessel):
                vessel = filter_top_name(vessel)
            nearest_node = vessel
        elif type(step) in [PrepareFilter, Filter, Dry, WashFilterCake]:
            nearest_node = filter_bottom_name(step.filter_vessel)
        elif type(step) in [Wash, Extract]:
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


    def _add_filter_volumes(self):
        """
        Add volume of filter bottom (aka dead_volume) to PrepareFilter steps.
        Add volume of filter bottom (aka dead_volume) and volume of material
        added to filter top to Filter steps.
        """
        prev_vessel_contents = {}
        for i, step, vessel_contents in self.iter_vessel_contents():
            if type(step) == PrepareFilter:
                for vessel in self.graphml_hardware.filters:
                    if vessel.cid == step.filter_vessel:
                        step.volume = vessel.dead_volume
                        break
            elif type(step) == Filter:
                for vessel in self.graphml_hardware.filters:
                    if vessel.cid == step.filter_vessel:
                        step.filter_bottom_volume = vessel.dead_volume
                        step.filter_top_volume = sum([reagent[1] for reagent in prev_vessel_contents[step.filter_vessel]])
            prev_vessel_contents = vessel_contents

    def _check_safety(self):
        """
        Check if the procedure is safe.
        Any issues will be printed.

        Returns:
            bool -- True if no safety issues are found, False otherwise.
        """
        return procedure_is_safe(self.steps, self.reagents)

    def prepare_for_execution(self, graphml_file):
        """
        Prepare the XDL for execution on a Chemputer corresponding to the given
        graphML file.
        
        Arguments:
            graphml_file {str} -- Path to graphML file.
        """
        self.graphml_file = graphml_file
        if not self._prepared_for_execution:
            if self.steps: # if XDL is valid
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

    def _get_exp_id(self, default='xdl_exp'):
        """Get experiment ID name to give to the Chempiler."""
        if self.xdl_file:
            return os.path.splitext(os.path.split(self.xdl_file)[-1])[0]
        else:
            return default

    def _add_hidden_steps(self):
        """
        Add extra steps implied by explicit XDL steps.
        """
        self._add_hidden_prepare_filter_steps()
        self._add_hidden_clean_backbone_steps()

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
        for i, step in enumerate(self.steps):
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
                self.steps.insert(i, CleanBackbone(reagent=DEFAULT_ORGANIC_CLEANING_SOLVENT))
            elif clean_type == 'water':
                self.steps.insert(i, CleanBackbone(reagent='water'))

    def _add_hidden_prepare_filter_steps(self):
        """
        Add PrepareFilter steps if filter top is being used, to fill up the bottom of the filter with solvent,
        so material added to the top doesn't drip through.
        """
        prev_vessel_contents = {}
        filters = []
        for i, step, vessel_contents in self.iter_vessel_contents():
            if type(step) == Filter:
                filters.append((i, step.filter_vessel, prev_vessel_contents))
            prev_vessel_contents = vessel_contents

        aqueous_synonyms = []
        for synonym_list in [synonym_list for synonym_list in [cb.synonyms.CAS_MACHINE_SYNONYMS_DICT[cas] for cas in cb.waste.AQUEOUS_WASTE_REAGENTS]]:
            aqueous_synonyms.extend(synonym_list)
        aqueous_synonyms = tuple(aqueous_synonyms)

        for filter_i, filter_vessel, filter_contents in filters:
            j = filter_i
            while j > 0 and type(self.steps[j]) not in [Extract, Wash, Reflux, Transfer]:
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
            self.steps.insert(j, PrepareFilter(filter_vessel=filter_vessel, solvent=solvent)) 

    def iter_vessel_contents(self, additions=False):
        """
        Iterator. Allows you to track vessel contents as they change throughout the steps.

        Keyword Arguments:
            additions {bool} -- If True, list of what contents were added that step is yielded also.
        
        Yields:
            (i, step, contents, {additions})
            i -- index of step
            step -- Step object of step
            contents -- Dictionary of contents of all vessels after step.
            additions (optional) -- List of contents added during the step.
        """
        vessel_contents = {}
        for i, step in enumerate(self.steps):
            
            additions_l = []
            if type(step) == Add:
                additions_l.append((step.reagent, step.volume))
                vessel_contents.setdefault(step.vessel, []).append((step.reagent, step.volume))

            elif type(step) == MakeSolution:
                additions_l.append((step.solvent, step.solvent_volume))
                vessel_contents.setdefault(step.vessel, []).append((step.solvent, step.solvent_volume))
                for solute in step.solutes:
                    additions_l.append((solute, 0))
                    vessel_contents[step.vessel].append((solute, 0))

            elif type(step) == Extract:
                if step.from_vessel != step.separation_vessel:
                    vessel_contents[step.from_vessel].clear()
                    additions_l.extend(vessel_contents[step.from_vessel])
                vessel_contents.setdefault(step.to_vessel, []).append((step.solvent, step.solvent_volume))
                # vessel_contents.setdefault(step.waste_vessel, []).extend(vessel_contents[step.from_vessel])
                additions_l.append((step.solvent, step.solvent_volume))

            elif type(step) == Wash:
                additions_l.extend(vessel_contents[step.from_vessel])
                additions_l.append((step.solvent, step.solvent_volume))
                vessel_contents[step.to_vessel] = copy.copy(vessel_contents[step.from_vessel])
                if not step.from_vessel == step.to_vessel:
                    vessel_contents[step.from_vessel].clear()

            elif type(step) == WashFilterCake:
                additions_l.append((step.solvent, step.volume))

            elif type(step) == Filter:
                vessel_contents.setdefault(step.filter_vessel, []).clear()

            elif type(step) == CMove:
                additions_l.extend(vessel_contents[step.from_vessel])
                vessel_contents.setdefault(step.to_vessel, []).extend(vessel_contents[step.from_vessel])
                vessel_contents[step.from_vessel].clear()

            elif type(step) == Transfer:
                from_vessel = step.from_vessel
                if 'filter' in from_vessel and ('top' in from_vessel or 'bottom' in from_vessel):
                    from_vessel = from_vessel.split('_')[1]
                additions_l.extend(vessel_contents[from_vessel])
                vessel_contents.setdefault(step.to_vessel, []).extend(vessel_contents[from_vessel])
                vessel_contents[from_vessel].clear()

            if additions_l:
                for vessel in list(vessel_contents.keys()):
                    if 'filter' in vessel and 'top' in vessel:
                        bottom_vessel = vessel.split('_')[1]
                        if bottom_vessel in vessel_contents:
                            vessel_contents[bottom_vessel].extend(vessel_contents[vessel])
                        else:
                            vessel_contents[bottom_vessel] = vessel_contents[vessel]
                        vessel_contents[vessel] = []

            if additions:
                yield (i, step, copy.deepcopy(vessel_contents), additions_l)
            else:
                yield (i, step, copy.deepcopy(vessel_contents))

    def simulate(self, graphml_file):
        """Simulate XDL procedure using Chempiler and given graphML file."""
        self.prepare_for_execution(graphml_file)
        if self._prepared_for_execution:
            chempiler = Chempiler(self._get_exp_id(default='xdl_simulation'), graphml_file, True)
            # self.print_full_xdl_tree()
            # self.print_full_human_readable()
            print('Execution\n---------\n')
            for step in self.steps:
                print(f'\n{step.name}\n{len(step.name)*"-"}\n')
                print(f'{step.human_readable}\n')
                keep_going = step.execute(chempiler)
                if not keep_going:
                    return

    def execute(self, graphml_file):
        """Execute XDL procedure on a Chemputer corresponding to given graphML file."""
        self.prepare_for_execution(graphml_file)
        if self._prepared_for_execution:
            chempiler = Chempiler(self._get_exp_id(default='xdl_simulation'), graphml_file, False)
            self.print_full_xdl_tree()
            self.print_full_human_readable()
        print('Execution\n---------\n')
        for step in self.steps:
            print(f'\n{step.name}\n{len(step.name)*"-"}\n')
            print(f'{step.human_readable}\n')
            keep_going = step.execute(chempiler)
            if not keep_going:
                return

    def as_literal_chempiler_code(self, dry_run=False):
        """
        Returns string of literal chempiler code built from steps.
        """
        s = f'from chempiler import Chempiler\n\nchempiler = Chempiler(r"{self._get_exp_id(default="xdl_simulation")}", "{self.graphml_file}", False)\n\nchempiler.start_recording()\nchempiler.camera.change_recording_speed(14)\n'
        full_tree = self._get_full_xdl_tree()
        base_steps = list(BASE_STEP_OBJ_DICT.values())
        for step in full_tree:
            if step in self.steps:
                s += f'\n# {step.human_readable}\n'
            if type(step) in base_steps:
                if dry_run and type(step) == CWait:
                    new_step = copy.deepcopy(step)
                    new_step.time = 2
                    step = new_step
                s += re.sub(r'([a-zA-Z][a-z|A-Z|_|0-9]+)([\,|\)])', r"'\1'\2", step.literal_code) + '\n'
        return s

    def save_chempiler_script(self, save_path, dry_run=False):
        """Save a chempiler script from the given steps."""
        with open(save_path, 'w') as fileobj:
            fileobj.write(self.as_literal_chempiler_code(dry_run=dry_run))

    def as_human_readable(self):
        """Return human-readable English description of XDL procedure."""
        s = ''
        for step in self.steps:
            s += f'{step.human_readable}\n'
        return s

    def print_full_human_readable(self):
        """Print human-readable English description of XDL procedure."""
        print('Synthesis Description\n---------------------\n')
        print(self.as_human_readable())
        print('\n')

    def print_full_xdl_tree(self):
        """Print nested structure of all steps in XDL procedure."""
        print('\n')
        print('Operation Tree\n--------------\n')
        for step in self.steps:
            climb_down_tree(step, print_tree=True)
        print('\n')

    def _tidy_up_procedure(self):
        self._remove_pointless_pump_priming()
        self._keep_stirring_when_possible()
        
    def _remove_pointless_pump_priming(self):
        i = len(self.steps) - 1
        while i > 0:
            step = self.steps[i]
            if type(step) == CleanBackbone:
                reagents = []
                if i > 0 and i < len(self.steps) - 1:
                    before_step = self.steps[i - 1]
                    after_step = self.steps[i + 1]
                    # Don't clean between filter and subsequent dry.
                    if type(before_step) == Filter and type(after_step) == Dry:
                        self.steps.pop(i)
                    # If adding same thing twice in a row don't clean in between.
                    else:
                        for other_step in [before_step, after_step]:
                            if type(other_step) == Add:
                                reagents.append(other_step.reagent)
                            elif type(other_step) == PrepareFilter:
                                reagents.append(other_step.solvent)
                            
                        if len(reagents) == 2 and len(set(reagents)) == 1:
                            self.steps.pop(i)
            i -= 1

    def _keep_stirring_when_possible(self):
        stir_steps = [Add, Chill, StopChiller]
        steps = [step for step in self.steps if type(step) != CleanBackbone]
        for i in range(len(steps)):
            step = steps[i]
            if type(step) in stir_steps:
                before_step, after_step = None, None
                if i > 0:
                    before_step = steps[i - 1]
                if i < len(steps) - 1:
                    after_step = steps[i + 1]
                if before_step and type(before_step) in stir_steps:
                    step.start_stir = False
                if after_step and type(after_step) in stir_steps:
                    step.stop_stir = False
            

# XDL Parsing
def steps_from_xdl(xdl):
    """Given XDL str get list of steps."""
    steps = []
    xdl_tree = etree.parse(StringIO(xdl))
    for element in xdl_tree.findall('*'):
        if element.tag == 'Procedure':
            for step_xdl in element.findall('*'):
                steps.append(xdl_to_step(step_xdl))
    return steps

def hardware_from_xdl(xdl):
    """Get Hardware object given XDL str."""

    return Hardware(components_from_xdl(xdl))

def components_from_xdl(xdl):
    """Get list of components given XDL str."""
    components = []
    xdl_tree = etree.parse(StringIO(xdl))
    for element in xdl_tree.findall('*'):
        if element.tag == 'Hardware':
            for component_xdl in element.findall('*'):
                components.append(xdl_to_component(component_xdl))
    return components

def reagents_from_xdl(xdl):
    """Get list of reagents given XDL str."""
    reagents = []
    xdl_tree = etree.parse(StringIO(xdl))
    for element in xdl_tree.findall('*'):
        if element.tag == 'Reagents':
            for reagent_xdl in element.findall('*'):
                reagents.append(xdl_to_reagent(reagent_xdl))
    return reagents 

def xdl_to_step(step_xdl):
    """Convert XDL step str to Step object."""
    step = STEP_OBJ_DICT[step_xdl.tag]()
    step.load_properties(preprocess_attrib(step, step_xdl.attrib))
    return step

def xdl_to_component(component_xdl):
    """Convert XDL component str to Component object."""
    component = COMPONENT_OBJ_DICT[component_xdl.tag]()
    component.load_properties(component_xdl.attrib)        
    return component

def xdl_to_reagent(reagent_xdl):
    """Convert XDL reagent str to Reagent object."""
    reagent = Reagent()
    reagent.load_properties(reagent_xdl.attrib)
    return reagent

def preprocess_attrib(step, attrib):
    """
    1. Convert strs to bools i.e. 'false' -> False
    2. Convert all time strs to floats with second as unit.
    3. Convert all volume strs to floats with mL as unit.
    4. Convert all mass strs to floats with mL as unit.
    5. Convert MakeSolution solutes and solute_masses attributes to lists.

    Arguments:
        step {Step} -- Step object to preprocess attributes for.
        attrib {lxml.etree._Attrib} -- Raw attribute dictionary from XDL
    
    Returns:
        dict -- Dict of processed attributes.
    """
    attrib = dict(attrib)
    if 'clean_tubing' in attrib:
        if attrib['clean_tubing'].lower() == 'false':
            attrib['clean_tubing'] = False
        else:
            attrib['clean_tubing'] = True
    if 'time' in attrib:
        attrib['time'] = convert_time_str_to_seconds(attrib['time'])
    
    if 'volume' in attrib and attrib['volume'] != 'all':
        attrib['volume'] = convert_volume_str_to_ml(attrib['volume'])
    if 'solvent_volume' in attrib:
        attrib['solvent_volume'] = convert_volume_str_to_ml(attrib['solvent_volume'])
    if 'mass' in attrib:
        attrib['mass'] = convert_mass_str_to_g(attrib['mass'])
    if 'product_bottom' in attrib:
        attrib['product_bottom'] = parse_bool(attrib['product_bottom'])

    if isinstance(step, MakeSolution):
        attrib['solutes'] = attrib['solutes'].split(' ')
        attrib['solute_masses'] = attrib['solute_masses'].split(' ')
        attrib['solute_masses'] = [convert_mass_str_to_g(item) for item in attrib['solute_masses']]
        
    return attrib

def climb_down_tree(step, print_tree=False, lvl=0):
    """
    Go through given step's sub steps recursively until base steps are reached.
    Return list containing the step, all sub steps and all base steps.
    
    Arguments:
        step {Step} -- step to find all sub steps for.
    
    Keyword Arguments:
        lvl {int} -- Level of recursion. Used to determine indent level when print_tree=True.
    
    Returns:
        list -- List of all Steps involved with given step. Includes given step, and all sub steps all the way down to base steps.
    """
    indent = '  '
    base_steps = list(BASE_STEP_OBJ_DICT.values())
    tree = [step]
    if print_tree:
        print(f'{indent*lvl}{step.name}' + ' {')
    if type(step) in base_steps:
        return tree
    else:
        lvl += 1
        for step in step.steps:
            if type(step) in base_steps:
                if print_tree:
                    print(f'{indent*lvl}{step.name}')
                tree.append(step)
                continue
            else:
                tree.extend(climb_down_tree(step, print_tree=print_tree, lvl=lvl))
        if print_tree:
            print(f'{indent*(lvl-1)}' + '}')
    return tree

# Hardware compatibility

def graphml_hardware_from_file(graphml_file):
    """Return Hardware object given graphML_file path."""
    components = []
    with open(graphml_file, 'r') as fileobj:
        soup = bs4.BeautifulSoup(fileobj, 'xml')
    dead_volume_id = soup.find('key', {'attr.name': 'dead_volume'})['id']
    max_volume_id = soup.find('key', {'attr.name': 'max_volume'})['id']
    nodes = soup.findAll('node', {'yfiles.foldertype': ''})
    for node in nodes:
        component = None
        node_label = node.find("y:NodeLabel").text.strip()
        if node_label.startswith('reactor'):
            component = Reactor(cid=node_label)

        elif node_label.startswith(('filter')):
            if 'bottom' in node_label:
                dead_volume = node.find('data', {'key': dead_volume_id},) #, {'key': 'd13'})d
                component = FilterFlask(cid=node_label, dead_volume=float(dead_volume.string))

        elif node_label.startswith(('separator', 'flask_separator')):
            component = SeparatingFunnel(cid=node_label)

        elif node_label.startswith('flask'):
            component = Flask(cid=node_label)

        elif node_label.startswith('waste'):
            component = Waste(cid=node_label)
        if component:
            component.max_volume = float(node.find('data', {'key': max_volume_id}).string)
            components.append(component)
    return Hardware(components)

def _hardware_is_compatible(xdl_hardware=None, graphml_hardware=None):
    """Determine if XDL hardware object can be mapped to hardware available in graphML file."""
    enough_reactors = len(xdl_hardware.reactors) <= len(graphml_hardware.reactors)
    enough_filters = len(xdl_hardware.filters) <= len(graphml_hardware.filters)
    enough_separators = len(xdl_hardware.separators) <= len(graphml_hardware.separators)
    flasks_ok = True # NEEDS DONE
    waste_ok = True # NEEDS DONE

    return enough_reactors and enough_filters and flasks_ok and waste_ok