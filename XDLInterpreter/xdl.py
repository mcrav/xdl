from lxml import etree
from bs4 import BeautifulSoup
from io import StringIO
import re

from constants import *
from chasmwriter import Chasm, Reaction
from steps_xdl import *
from steps_generic import *
from components import *
from reagents import *
from steps_chasm import *

step_obj_dict = {
    'Step': Step,
    'Comment': Comment,
    'Repeat': Repeat,
    'Move': Move,
    'Home': Home,
    'Separate': Separate,
    'Prime': Prime,
    'SwitchVacuum': SwitchVacuum,
    'SwitchCartridge': SwitchCartridge,
    'SwitchColumn': SwitchColumn,
    'StartStir': StartStir,
    'StartHeat': StartHeat,
    'StopStir': StopStir,
    'StopHeat': StopHeat,
    'SetTemp': SetTemp,
    'SetStirRpm': SetStirRpm,
    'StirrerWaitForTemp': StirrerWaitForTemp,
    'StartHeaterBath': StartHeaterBath,
    'StopHeaterBath': StopHeaterBath,
    'StartRotation': StartRotation,
    'StopRotation': StopRotation,
    'LiftArmUp': LiftArmUp,
    'LiftArmDown': LiftArmDown,
    'ResetRotavap': ResetRotavap,
    'SetBathTemp': SetBathTemp,
    'SetRotation': SetRotation,
    'RvWaitForTemp': RvWaitForTemp,
    'SetInterval': SetInterval,
    'InitVacPump': InitVacPump,
    'GetVacSp': GetVacSp,
    'SetVacSp': SetVacSp,
    'StartVac': StartVac,
    'StopVac': StopVac,
    'VentVac': VentVac,
    'SetSpeedSp': SetSpeedSp,
    'StartChiller': StartChiller,
    'StopChiller': StopChiller,
    'SetChiller': SetChiller,
    'ChillerWaitForTemp': ChillerWaitForTemp,
    'RampChiller': RampChiller,
    'SwitchChiller': SwitchChiller,
    'SetCoolingPower': SetCoolingPower,
    'SetRecordingSpeed': SetRecordingSpeed,
    'Wait': Wait,
    'Breakpoint': Breakpoint,
    'SetRpmAndStartStir': SetRpmAndStartStir,
    'StartVacuum': StartVacuum,
    'StopVacuum': StopVacuum,
    'SetTempAndStartHeat': SetTempAndStartHeat,
    'CleanVessel': CleanVessel,
    'CleanTubing': CleanTubing,
    'HeatAndReact': HeatAndReact,
    'ContinueStirToRT': ContinueStirToRT,
    'Chill': Chill,
    'ChillBackToRT': ChillBackToRT,
    'Add': Add,
    'StirAndTransfer': StirAndTransfer,
    'Wash': Wash,
    'ChillReact': ChillReact,
    'Stir': StartStir,
    'Heat': StartHeat
}

component_obj_dict = {
    'Reactor': Reactor,
    'Filter': Filter,
    'Flask': Flask,
    'Waste': Waste,
}


class XDL(object):

    def __init__(self, xdl_file=None, xdl_str=None):
        if xdl_file:
            with open(xdl_file, 'r') as fileobj:
                self.xdl = fileobj.read()
        elif xdl_str:
            self.xdl = xdl_str
        if self.xdl:
            self.parse_xdl()
        else:
            print('No XDL given.')

    def parse_xdl(self):
        self.steps = steps_from_xdl(self.xdl)
        self.hardware = hardware_from_xdl(self.xdl)
        self.reagents = reagents_from_xdl(self.xdl)

    def xdl_valid(self):
        return validate_xdl(self.xdl)

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

    def get_reagent_map(self):
        self.reagent_map = {}
        for reagent in self.reagents:
            reagent_id = reagent.properties['id']
            for flask in self.graphml_hardware.flasks:
                flask_id = flask.properties['id']
                if reagent_id in flask_id:
                    self.reagent_map[reagent_id] = flask_id
                    break

    def map_hardware_to_steps(self):
        self.get_hardware_map()
        for step in self.steps:
            for prop, val in step.properties.items():
                if val in self.hardware_map:
                    step.properties[prop] = self.hardware_map[val]
            step.update_steps()

    def map_reagents_to_steps(self):
        self.get_reagent_map()
        for step in self.steps:
            for prop, val in step.properties.items():
                if val in self.reagent_map:
                    step.properties[prop] = self.reagent_map[val]
            step.update_steps()

    def check_safety(self):
        return procedure_is_safe(self.steps)

    def as_chasm(self, save_path=None, graphml_file=None):
        if self.xdl_valid():      
            self.graphml_hardware = graphml_hardware_from_file(graphml_file)
            if self.hardware_is_compatible():
            
                self.map_hardware_to_steps()
                
                # self.map_reagents_to_steps() # MAYBE NOT NECESSARY
                
                self.check_safety()
                
                chasm = Chasm(self.steps)
                if save_path:
                    chasm.save(save_path)
                return chasm.code

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
    if step_xdl.tag != 'Repeat':
        step = step_obj_dict[step_xdl.tag]()
        step.load_properties(preprocess_attrib(step, step_xdl.attrib))
    else:
        step = xdl_to_repeat_step(step_xdl)
    return step

def xdl_to_repeat_step(repeat_step_xdl):
    properties_dict = repeat_step_xdl.attrib
    properties_dict['steps'] = []
    for step_xdl in repeat_step_xdl.findall('*'):
        properties_dict['steps'].append(xdl_to_step(step_xdl))
    step = Repeat()
    step.load_properties(properties_dict)
    return step

def xdl_to_component(component_xdl):
    component = component_obj_dict[component_xdl.tag]()
    component.load_properties(component_xdl.attrib)        
    return component

def xdl_to_reagent(reagent_xdl):
    reagent = Reagent()
    reagent.load_properties(reagent_xdl.attrib)
    return reagent

def preprocess_attrib(step, attrib):
    print(step)
    print(attrib)
    print('~~~')
    if isinstance(step, (StartHeat, StartStir)):
        attrib['name'] = attrib['vessel']
        del attrib['vessel']
    if 'time' in attrib:
        attrib['time'] = convert_time_str_to_seconds(attrib['time'])
    if 'volume' in attrib:
        attrib['volume'] = convert_volume_str_to_ml(attrib['volume'])
    return attrib

def convert_time_str_to_seconds(time_str):
    time_str = time_str.lower()
    if time_str.endswith(('h', 'hr', 'hrs', 'hour', 'hours', )):
        multiplier = 3600
    elif time_str.endswith(('m', 'min', 'mins', 'minute', 'minutes')):
        multiplier = 60
    elif time_str.endswith(('s', 'sec', 'secs', 'second', 'seconds',)):
        multiplier = 1
    return str(int(float(re.match(r'([0-9]+(.[0-9]+)?)', time_str).group(1)) * multiplier))

def convert_volume_str_to_ml(volume_str):
    print(f'VOLUME STR: {volume_str}')
    volume_str = volume_str.lower()
    if volume_str.endswith(volume_ml_unit_words):
        multiplier = 1
    elif volume_str.endswith(volume_l_unit_words):
        multiplier = 1000
    elif volume_str.endswith(volume_dl_unit_words):
        multiplier = 100
    elif volume_str.endswith(volume_cl_unit_words):
        multiplier = 10
    return str(float(re.match(r'([0-9]+(.[0-9]+)?)', volume_str).group(1)) * multiplier)

# Syntax Validation

def validate_xdl(xdl):
    correct_tags = xdl_has_correct_base_tags(xdl)
    step_tags = xdl_has_valid_step_tags(xdl)
    return correct_tags and step_tags

def xdl_has_valid_step_tags(xdl):
    xdl_tree = etree.parse(StringIO(xdl))
    valid = True
    for element in xdl_tree.find('Procedure'):
        if element.tag not in step_obj_dict:
            print(f'Invalid step: {element.tag}')
            valid = False
    return valid

def xdl_has_correct_base_tags(xdl):
    xdl_tree = etree.parse(StringIO(xdl))
    hardware = 0
    reagents = 0
    procedure = 0
    for element in xdl_tree.findall('*'):
        if element.tag == 'Hardware':
            hardware += 1
        elif element.tag == 'Reagents':
            reagents += 1
        elif element.tag == 'Procedure':
            procedure += 1
    return hardware == 1 and reagents == 1 and procedure == 1

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
                components.append(Filter(id_word=node_label))
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

# Safety

def procedure_is_safe(steps):
    return True

def main():
    # from stuff import rufinamide_steps
    
    # xdl_f = '/home/group/ReaxysChemputerInterface/stuff/rufinamide.xdl'
    # reaction = Reaction('')
    # reaction.steps = rufinamide_steps
    # reaction.save_xdl(xdl_f)

    xdl_f = '/home/group/XDLInterpreter/stuff/xdl_v4.xdl'
    chasm_f = '/home/group/XDLInterpreter/stuff/xdl_v4.chasm'

    xdl = XDL(xdl_file=xdl_f)
    xdl.as_chasm(chasm_f, '/home/group/XDLInterpreter/stuff/rufinamide.graphml')
    
if __name__ == '__main__':
    main()
