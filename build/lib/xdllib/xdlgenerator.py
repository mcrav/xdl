from lxml import etree
from .components import Reactor
from .reagents import Reagent
from .steps_xdl import Add
from .xdlwriter import get_xdl_string

class XDLGenerator(object):   

    def __init__(self, hardware=[], reagents=[], steps=[]):

        self.hardware, self.reagents, self.steps = hardware, reagents, steps
        self.generate_xdl()

    def generate_xdl(self):
        self.xdltree = etree.Element('Synthesis')
        self.append_hardware_tree()
        self.append_reagent_tree()
        self.append_operations_tree()

    def append_hardware_tree(self):
        hardware_tree = etree.Element('Hardware')
        for component in self.hardware:
            component_tree = etree.Element(component.name)
            for prop, val in component.properties.items():
                if val != None:
                    component_tree.attrib[prop] = str(val)
            hardware_tree.append(component_tree)
        self.xdltree.append(hardware_tree)

    def append_reagent_tree(self):
        reagents_tree = etree.Element('Reagents')
        for reagent in self.reagents:
            reagent_tree = etree.Element('Reagent')
            for prop, val in reagent.properties.items():
                if val != None:
                    reagent_tree.attrib[prop] = str(val)
            reagents_tree.append(reagent_tree)
        self.xdltree.append(reagents_tree)

    def append_operations_tree(self):
        procedure_tree = etree.Element('Procedure')
        for step in self.steps:
            step_tree = etree.Element(step.name)
            for prop, val in step.properties.items():
                if val != None:
                    step_tree.attrib[prop] = str(val)
            procedure_tree.append(step_tree)
        self.xdltree.append(procedure_tree)

    def save(self, save_file):
        with open(save_file, 'w') as fileobj:
            fileobj.write(get_xdl_string(self.xdltree))

    def as_string(self):
        return get_xdl_string(self.xdltree)

def main():
    hardware = [Reactor(id_word='reactor1', volume_ml='500ml')]
    reagents = [Reagent(id_word='acetonitrile', cas='420-420')]
    operations = [Add('acetonitrile', '50ml', 'reactor1')]
    xdlgenerator = XDLGenerator(hardware, reagents, operations)
    xdlgenerator.save('/home/group/XDLInterpreter/stuff/test.xdl')

if __name__ == '__main__':
    main()