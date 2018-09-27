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

    def __init__(self, xdl_file=None, xdl_str=None):
        self.steps, self.hardware, self.reagent = [], [], []
        self.prepared_for_execution = False
        self.xdl_file = xdl_file
        if xdl_file:
            with open(xdl_file, 'r') as fileobj:
                self.xdl = fileobj.read()
        elif xdl_str:
            self.xdl = xdl_str
        if self.xdl:
            if self.xdl_valid():
                self.parse_xdl()
        else:
            print('No XDL given.')

    def get_full_xdl_tree(self):
        tree = []
        i = 0
        for step in self.steps:
            tree.extend(climb_down_tree(step))
        return tree

    def print_full_xdl_tree(self):
        print('\n')
        print('Operation Tree\n--------------\n')
        for step in self.steps:
            climb_down_tree(step, verbose=True)
        print('\n')
        
    def insert_waste_vessels(self):
        waste_sound = True
        for step in self.get_full_xdl_tree():
            if isinstance(step, (WashFilterCake, CleanVessel)):
                step.waste_vessel = self.get_waste_vessel(step.solvent)
                print(step.waste_vessel)
            elif isinstance(step, (CleanTubing, PrimePumpForAdd)):
                step.waste_vessel = self.get_waste_vessel(step.reagent)
                print(step.waste_vessel)
            if 'waste_vessel' in step.properties and not step.waste_vessel:
                waste_sound = False
        return waste_sound

    def get_waste_vessel(self, reagent_id):
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

    def parse_xdl(self):
        self.steps = steps_from_xdl(self.xdl)
        self.hardware = hardware_from_xdl(self.xdl)
        self.reagents = reagents_from_xdl(self.xdl)

    def xdl_valid(self):
        return XDLSyntaxValidator(self.xdl).valid

    def hardware_is_compatible(self):
        return hardware_is_compatible(
            xdl_hardware=self.hardware, 
            graphml_hardware=self.graphml_hardware
            )

    def get_hardware_map(self):
        self.hardware_map = {}
        for i in range(len(self.hardware.reactors)):
            self.hardware_map[
                self.hardware.reactors[i].properties['id']
                ] = self.graphml_hardware.reactors[i].properties['id']

    def map_hardware_to_steps(self):
        self.get_hardware_map()
        for step in self.steps:
            for prop, val in step.properties.items():
                if isinstance(val, str) and val in self.hardware_map:
                    step.properties[prop] = self.hardware_map[val]
                    print(step.properties)
            step.update()

    def close_open_steps(self):
        self.steps = close_open_steps(self.steps)

    def check_safety(self):
        return procedure_is_safe(self.steps, self.reagents)

    def prepare_for_execution(self, graphml_file):#
        if not self.prepared_for_execution:
            if self.steps: # if XDL is valid
                print('XDL is valid')
                self.graphml_hardware = graphml_hardware_from_file(graphml_file)
                if self.hardware_is_compatible():
                    print('Hardware is compatible')
                    self.map_hardware_to_steps()
                    if self.insert_waste_vessels():
                        print('Waste vessels setup')
                        self.close_open_steps()         
                        if self.check_safety():
                            print('Procedure raises no safety flags')
                            self.prepared_for_execution = True

    def simulate(self, graphml_file):
        self.prepare_for_execution(graphml_file)
        if self.prepared_for_execution:
            chempiler = Chempiler(self.get_exp_id(default='xdl_simulation'), graphml_file, True)
            self.print_full_xdl_tree()
            self.print_full_human_readable()
            print('Execution\n---------\n')
            for step in self.steps:
                print(f'\n{step.name}\n{len(step.name)*"-"}')
                print(f'{step.human_readable}\n')
                keep_going = step.execute(chempiler)
                if not keep_going:
                    return

    def execute(self, graphml_file):
        self.prepare_for_execution(graphml_file)
        if self.prepared_for_execution:
            chempiler = Chempiler(self.get_exp_id(default='xdl_simulation'), graphml_file, False)
            self.print_full_xdl_tree()
            self.print_full_human_readable()
        print('Execution\n---------\n')
        for step in self.steps:
            step.execute(chempiler)

    def print_full_human_readable(self):
        print('Synthesis Description\n---------------------\n')
        print(self.as_human_readable())
        print('\n')

    def as_human_readable(self):
        """Return human-readable English str of synthesis described by steps."""
        s = ''
        for step in self.steps:
            s += f'{step.human_readable}\n'
        return s

    def get_exp_id(self, default='xdl_exp'):
        if self.xdl_file:
            return os.path.splitext(os.path.split(self.xdl_file)[-1])[0]
        else:
            return default
        
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

def hardware_is_compatible(xdl_hardware=None, graphml_hardware=None):
    enough_reactors = len(xdl_hardware.reactors) <= len(graphml_hardware.reactors)
    enough_filters = len(xdl_hardware.filters) <= len(graphml_hardware.filters)
    flasks_ok = True # NEEDS DONE
    waste_ok = True # NEEDS DONE
    return enough_reactors and enough_filters and flasks_ok and waste_ok