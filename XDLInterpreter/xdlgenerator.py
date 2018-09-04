from lxml import etree
from components import Reactor
from reagents import Reagent
from steps_xdl import Add

class XDLGenerator(object):   

    def __init__(self, hardware=[], reagents=[], operations=[]):

        self.hardware, self.reagents, self.operations = hardware, reagents, operations
        self.generate_xdl()

    def generate_xdl(self):
        self.xdlroot = etree.Element('Synthesis')
        self.append_hardware_tree()
        self.append_reagent_tree()
        self.append_operations_tree()

    def append_hardware_tree(self):
        hardware_tree = etree.Element('Hardware')
        for component in self.hardware:
            pass
        self.xdlroot.append(hardware_tree)

    def append_reagent_tree(self):
        reagent_tree = etree.Element('Reagents')
        self.xdlroot.append(reagent_tree)

    def append_operations_tree(self):
        procedure_tree = etree.Element('Procedure')
        self.xdlroot.append(procedure_tree)

    def save(self, save_file):
        etree.ElementTree(self.xdlroot).write(save_file, pretty_print=True)

def main():
    hardware = [Reactor(id_word='reactor1', volume_ml='500ml')]
    reagents = [Reagent(id_word='acetonitrile', cas='420-420')]
    operations = [Add('acetonitrile', '50ml', 'reactor1')]
    xdlgenerator = XDLGenerator(hardware, reagents, operations)
    xdlgenerator.save('/home/group/XDLInterpreter/stuff/test.xdl')

if __name__ == '__main__':
    main()