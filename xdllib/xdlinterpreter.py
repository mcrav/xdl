from lxml import etree
from bs4 import BeautifulSoup
from io import StringIO
import re
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
        """Insert correct waste vessel names into steps.
        If waste can't be determined for a reagent it will be printed,
        and this method will return False.

        Returns:
            waste_ok {bool} -- True if waste vessels all found, otherwise False
        """
        waste_ok = True
        for step in self._get_full_xdl_tree():
            if isinstance(step, (WashFilterCake, CleanVessel)):
                step.waste_vessel = self._get_waste_vessel(step.solvent)
                print(step.waste_vessel)
            elif isinstance(step, (CleanTubing, PrimePumpForAdd)):
                step.waste_vessel = self._get_waste_vessel(step.reagent)
                print(step.waste_vessel)
            if 'waste_vessel' in step.properties and not step.waste_vessel:
                waste_ok = False
        return waste_ok

    def _get_waste_vessel(self, reagent_id):
        """Get waste vessel for given reagent.
        
        Arguments:
            reagent_id {str} -- Name of reagent in XDL file.

        Returns:
            str -- Name of waste vessel, i.e. waste_aqueous. None if waste vessel not found.
        """
        for reagent in self.reagents:
            if reagent.id_word == reagent_id:
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
        for i in range(len(self.hardware.reactors)):
            self.hardware_map[
                self.hardware.reactors[i].properties['id']
                ] = self.graphml_hardware.reactors[i].properties['id']

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
                    print(step.properties)
            step.update()

    def _close_open_steps(self):
        """If there are steps like StartStir but no corresponding StopStir,
        put in the StopStir method automatically.
        NOTE: Debatable whether XDL interpreter should do this.
        """
        self.steps = close_open_steps(self.steps)

    def _check_safety(self):
        """Check if the procedure is safe.
        Any issues will be printed.

        Returns:
            bool -- True if no safety issues are found, False otherwise.
        """
        return procedure_is_safe(self.steps, self.reagents)

    def _prepare_for_execution(self, graphml_file):
        """Prepare the XDL for execution on a Chemputer corresponding to the given
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
                        self._close_open_steps()         
                        if self._check_safety():
                            print('Procedure raises no safety flags')
                            self._prepared_for_execution = True

    def _get_exp_id(self, default='xdl_exp'):
        """Get experiment ID name to give to the Chempiler."""
        if self.xdl_file:
            return os.path.splitext(os.path.split(self.xdl_file)[-1])[0]
        else:
            return default

    def simulate(self, graphml_file):
        """Simulate XDL procedure using Chempiler and given graphML file."""
        self._prepare_for_execution(graphml_file)
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
        self._prepare_for_execution(graphml_file)
        if self._prepared_for_execution:
            chempiler = Chempiler(self._get_exp_id(default='xdl_simulation'), graphml_file, False)
            self.print_full_xdl_tree()
            self.print_full_human_readable()
        print('Execution\n---------\n')
        for step in self.steps:
            step.execute(chempiler)

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
            climb_down_tree(step, verbose=True)
        print('\n')
        
def get_close_step(step):
    return ongoing_steps[type(step)](vessel=step.vessel)

def close_open_steps(steps):
    open_steps = get_open_steps(steps)
    for open_step in open_steps:
        steps.append(get_close_step(open_step))
    return steps

ongoing_steps = {
    StartStir: CStopStir,
    StartHeat: CStopHeat,
    StartHeat: CStopHeat,
    CStartChiller: CStopChiller,
    CStartRotation: CStopRotation,
    CStartVac: CStopVac,
    StartVacuum: StopVacuum,
    CStartHeaterBath: CStopHeaterBath,
}

def step_is_closed(open_step, steps):
    closed = False
    close_step = ongoing_steps[type(open_step)]
    after_step = False
    for step in steps:
        if after_step:
            if isinstance(step, close_step) and step.properties['vessel'] == open_step.properties['vessel']:
                closed = True
        if step is open_step:
            after_step = True
    return closed

def get_open_steps(steps):
    open_steps = []
    for step in steps:
        if isinstance(step, tuple(ongoing_steps.keys())) and not step_is_closed(step, steps):
            open_steps.append(step)
    return open_steps

# XDL Parsing
def steps_from_xdl(xdl):
    steps = []
    xdl_tree = etree.parse(StringIO(xdl))
    for element in xdl_tree.findall('*'):
        if element.tag == 'Procedure':
            for step_xdl in element.findall('*'):
                steps.append(xdl_to_step(step_xdl))
    return steps

def hardware_from_xdl(xdl):
    return Hardware(components_from_xdl(xdl))

def components_from_xdl(xdl):
    components = []
    xdl_tree = etree.parse(StringIO(xdl))
    for element in xdl_tree.findall('*'):
        if element.tag == 'Hardware':
            for component_xdl in element.findall('*'):
                components.append(xdl_to_component(component_xdl))
    return components

def reagents_from_xdl(xdl):
    reagents = []
    xdl_tree = etree.parse(StringIO(xdl))
    for element in xdl_tree.findall('*'):
        if element.tag == 'Reagents':
            for reagent_xdl in element.findall('*'):
                reagents.append(xdl_to_reagent(reagent_xdl))
    return reagents 

def xdl_to_step(step_xdl):
    step = STEP_OBJ_DICT[step_xdl.tag]()
    step.load_properties(preprocess_attrib(step, step_xdl.attrib))
    return step

def xdl_to_component(component_xdl):
    component = COMPONENT_OBJ_DICT[component_xdl.tag]()
    component.load_properties(component_xdl.attrib)        
    return component

def xdl_to_reagent(reagent_xdl):
    reagent = Reagent()
    reagent.load_properties(reagent_xdl.attrib)
    return reagent

def preprocess_attrib(step, attrib):
    attrib = dict(attrib)
    if 'clean_tubing' in attrib:
        if attrib['clean_tubing'].lower() == 'false':
            attrib['clean_tubing'] = False
        else:
            attrib['clean_tubing'] = True
    if 'time' in attrib:
        attrib['time'] = convert_time_str_to_seconds(attrib['time'])
    
    if 'volume' in attrib:
        attrib['volume'] = convert_volume_str_to_ml(attrib['volume'])
    if 'solvent_volume' in attrib:
        attrib['solvent_volume'] = convert_volume_str_to_ml(attrib['solvent_volume'])

    if isinstance(step, MakeSolution):
        attrib['solutes'] = attrib['solutes'].split(' ')
        attrib['solute_masses'] = attrib['solute_masses'].split(' ')

    if 'mass' in attrib:
        attrib['mass'] = convert_mass_str_to_g(attrib['mass'])
    if 'solute_masses' in attrib:
        attrib['solute_masses'] = [convert_mass_str_to_g(item) for item in attrib['solute_masses']]
    return attrib

def climb_down_tree(step, verbose=False, lvl=0):
    indent = '  '
    base_steps = list(BASE_STEP_OBJ_DICT.values())
    tree = [step]
    if verbose:
        print(f'{indent*lvl}{step.name}' + ' {')
    if type(step) in base_steps:
        return tree
    else:
        lvl += 1
        for step in step.steps:
            
                
            if type(step) in base_steps:
                if verbose:
                    print(f'{indent*lvl}{step.name}')
                tree.append(step)
                continue
            else:
                tree.extend(climb_down_tree(step, verbose=verbose, lvl=lvl))
        if verbose:
            print(f'{indent*(lvl-1)}' + '}')
    return tree

# Hardware compatibility

def graphml_hardware_from_file(graphml_file):
    components = []
    with open(graphml_file, 'r') as fileobj:
        soup = BeautifulSoup(fileobj, 'lxml')
        nodes = soup.findAll("node", {"yfiles.foldertype":""})
        for node in nodes:
            node_label = node.find("y:nodelabel").text.strip()
            if node_label.startswith('reactor'):
                components.append(Reactor(id_word=node_label))
            elif node_label.startswith('filter'):
                components.append(FilterFlask(id_word=node_label))
            elif node_label.startswith('flask'):
                components.append(Flask(id_word=node_label))
            elif node_label.startswith('waste'):
                components.append(Waste(id_word=node_label))
    return Hardware(components)

def _hardware_is_compatible(xdl_hardware=None, graphml_hardware=None):
    enough_reactors = len(xdl_hardware.reactors) <= len(graphml_hardware.reactors)
    enough_filters = len(xdl_hardware.filters) <= len(graphml_hardware.filters)
    flasks_ok = True # NEEDS DONE
    waste_ok = True # NEEDS DONE
    return enough_reactors and enough_filters and flasks_ok and waste_ok