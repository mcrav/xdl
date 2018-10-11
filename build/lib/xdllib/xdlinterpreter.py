from lxml import etree
from bs4 import BeautifulSoup
from io import StringIO
import re
import copy
import os
from chempiler import Chempiler
from .utils import convert_time_str_to_seconds, convert_volume_str_to_ml, convert_mass_str_to_g
from .constants import *
from .components import *
from .reagents import *
from .steps import *
from .safety import procedure_is_safe
from .syntax_validation import XDLSyntaxValidator
from .namespace import STEP_OBJ_DICT, COMPONENT_OBJ_DICT, BASE_STEP_OBJ_DICT
import chembrain as cb

CLEAN_BACKBONE_AFTER_STEPS = [
    Add,
    Wash,
    Extract,
    MakeSolution,
    WashFilterCake,
    Filter,
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
            if self._xdl_valid():
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
        
    def _insert_waste_vessels(self):
        """
        Insert correct waste vessel names into steps.
        If waste can't be determined for a reagent it will be printed,
        and this method will return False.

        Returns:
            waste_ok {bool} -- True if waste vessels all found, otherwise False
        """
        waste_ok = True
        for step in self._get_full_xdl_tree():
            if isinstance(step, (WashFilterCake, CleanVessel)):
                step.waste_vessel = self._get_waste_vessel(step.solvent)
            elif isinstance(step, (CleanTubing, PrimePumpForAdd)):
                step.waste_vessel = self._get_waste_vessel(step.reagent)
            if 'waste_vessel' in step.properties and not step.waste_vessel:
                waste_ok = False
        for step in self.steps:
            if type(step) == CleanBackbone:
                step.waste_vessels = self.graphml_hardware.waste_cids
        return waste_ok

    def _get_waste_vessel(self, reagent_id):
        """
        Get waste vessel for given reagent.
        
        Arguments:
            reagent_id {str} -- Name of reagent in XDL file.

        Returns:
            str -- Name of waste vessel, i.e. waste_aqueous. None if waste vessel not found.
        """
        for reagent in self.reagents:
            if reagent.rid == reagent_id:
                if reagent.waste:
                    return f'waste_{reagent.waste}'
                else:
                    waste_type = cb.waste.get_waste_type(reagent_id)
                    if not waste_type:
                        print(f'Waste unknown for {reagent_id}, please add waste to Reagents section.')
                    else:
                        return f'waste_{waste_type}'
        return None

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
                

    def _map_hardware_to_steps(self):
        """
        Go through steps in XDL and replace XDL hardware IDs with IDs
        from the graphML file.
        """
        self._get_hardware_map()
        for step in self.steps:
            for prop, val in step.properties.items():
                if isinstance(val, str) and val in self.hardware_map:
                    step.properties[prop] = self.hardware_map[val]
            step.update()

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
        if not self._prepared_for_execution:
            if self.steps: # if XDL is valid
                print('XDL is valid')
                self.graphml_hardware = graphml_hardware_from_file(graphml_file)
                if self._hardware_is_compatible():
                    print('Hardware is compatible')
                    self._map_hardware_to_steps()
                    if self._insert_waste_vessels():
                        print('Waste vessels setup')
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
        self._add_hidden_prepare_filter_steps()
        self._add_hidden_clean_backbone_steps()

    def _add_hidden_clean_backbone_steps(self):
        cleans = []
        for i, step, vessel_contents in self.iter_vessel_contents():
            if type(step) in CLEAN_BACKBONE_AFTER_STEPS:
                cleans.append((i+1, step, vessel_contents))
        for i, step, vessel_contents in reversed(sorted(cleans, key=lambda x: x[0])):
            solvent = None
            for vessel, contents in vessel_contents.items():
                for reagent in contents:
                    if cb.solvents.density_from_machine_name(reagent):
                        solvent = DEFAULT_ORGANIC_CLEANING_SOLVENT
                        break
                if solvent:
                    break
            if not solvent:
                solvent = 'water'
            self.steps.insert(i, CleanBackbone(reagent=solvent))

    def _add_hidden_prepare_filter_steps(self):
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
            while j > 0 and type(self.steps[j]) not in [Extract, Wash, Reflux, StirAndTransfer]:
                j -= 1
            solvent = None
            for reagent in filter_contents[filter_vessel]:
                if reagent.endswith(aqueous_synonyms):
                    solvent = 'water'
                    break
                else:
                    if cb.solvents.density_from_machine_name(reagent):
                        solvent = reagent
                        break
            self.steps.insert(j, PrepareFilter(filter_vessel=filter_vessel, solvent=solvent)) 

    def iter_vessel_contents(self):
        vessel_contents = {}
        for i, step in enumerate(self.steps):
            if type(step) == Add:
                vessel_contents.setdefault(step.vessel, []).append(step.reagent)
            elif type(step) == MakeSolution:
                vessel_contents.setdefault(step.vessel, []).append(step.solvent)
                for solute in step.solutes:
                    vessel_contents[step.vessel].append(solute)
            elif type(step) == Extract:
                vessel_contents[step.from_vessel].clear()
                vessel_contents.setdefault(step.to_vessel, []).append(step.solvent)
            elif type(step) == Wash:
                vessel_contents[step.to_vessel] = copy.copy(vessel_contents[step.from_vessel])
                if not step.from_vessel == step.to_vessel:
                    vessel_contents[step.from_vessel].clear()
            elif type(step) == Filter:
                vessel_contents.setdefault(step.filter_vessel, []).clear()
            elif type(step) == CMove:
                vessel_contents.setdefault(step.to_vessel, []).extend(vessel_contents[step.from_vessel])
                vessel_contents[step.from_vessel].clear()
            elif type(step) == StirAndTransfer:
                vessel_contents.setdefault(step.to_vessel, []).extend(vessel_contents[step.from_vessel])
                vessel_contents[step.from_vessel].clear()
            yield (i, step, copy.deepcopy(vessel_contents))

    def simulate(self, graphml_file):
        """Simulate XDL procedure using Chempiler and given graphML file."""
        self.prepare_for_execution(graphml_file)
        if self._prepared_for_execution:
            chempiler = Chempiler(self._get_exp_id(default='xdl_simulation'), graphml_file, True)
            self.print_full_xdl_tree()
            self.print_full_human_readable()
            print('Execution\n---------\n')
            for step in self.steps:
                print(f'\n{step.name}\n{len(step.name)*"-"}exit')
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
            step.execute(chempiler)

    def as_literal_chempiler_code(self):
        s = 'from chempiler import Chempiler\n\nchempiler = Chempiler()\n\n'
        full_tree = self._get_full_xdl_tree()
        base_steps = list(BASE_STEP_OBJ_DICT.values())
        for step in full_tree:
            if step in self.steps:
                s += f'\n# {step.human_readable}\n'
            if type(step) in base_steps:
                s += re.sub(r'([a-zA-Z][a-z|A-Z|_|0-9]+)([\,|\)])', r"'\1'\2", step.literal_code) + '\n'
        return s

    def save_chempiler_script(self, save_path):
        with open(save_path, 'w') as fileobj:
            fileobj.write(self.as_literal_chempiler_code())

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
        soup = BeautifulSoup(fileobj, 'lxml')
        nodes = soup.findAll("node", {"yfiles.foldertype":""})
        for node in nodes:
            node_label = node.find("y:nodelabel").text.strip()
            if node_label.startswith('reactor'):
                components.append(Reactor(cid=node_label))
            elif node_label.startswith('filter'):
                components.append(FilterFlask(cid=node_label))
            elif node_label.startswith(('separator', 'flask_separator')):
                components.append(SeparatingFunnel(cid=node_label))
            elif node_label.startswith('flask'):
                components.append(Flask(cid=node_label))
            elif node_label.startswith('waste'):
                components.append(Waste(cid=node_label))
            
    return Hardware(components)

def _hardware_is_compatible(xdl_hardware=None, graphml_hardware=None):
    """Determine if XDL hardware object can be mapped to hardware available in graphML file."""
    enough_reactors = len(xdl_hardware.reactors) <= len(graphml_hardware.reactors)
    enough_filters = len(xdl_hardware.filters) <= len(graphml_hardware.filters)
    enough_separators = len(xdl_hardware.separators) <= len(graphml_hardware.separators)
    flasks_ok = True # NEEDS DONE
    waste_ok = True # NEEDS DONE
    return enough_reactors and enough_filters and flasks_ok and waste_ok