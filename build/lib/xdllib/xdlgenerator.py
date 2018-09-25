from lxml import etree
from .components import Reactor
from .reagents import Reagent
from .steps_xdl import Add

class XDLGenerator(object):   
    """
    Class for generating XDL from lists of hardware, reagents and steps.
    """
    def __init__(self, hardware=[], reagents=[], steps=[]):
        """
        Generate XDL etree.
        
        Keyword Arguments:
            hardware {list} -- List of Component objects
            reagents {list} -- List of Reagent objects
            steps {list} -- List of Step objects
        """
        self.hardware, self.reagents, self.steps = hardware, reagents, steps
        self.generate_xdl()

    def generate_xdl(self):
        """Generate XDL tree."""
        self.xdltree = etree.Element('Synthesis')
        self.append_hardware_tree()
        self.append_reagents_tree()
        self.append_procedure_tree()

    def append_hardware_tree(self):
        """Create and add Hardware section to XDL tree."""
        hardware_tree = etree.Element('Hardware')
        for component in self.hardware:
            component_tree = etree.Element(component.name)
            for prop, val in component.properties.items():
                if val != None:
                    component_tree.attrib[prop] = str(val)
            hardware_tree.append(component_tree)
        self.xdltree.append(hardware_tree)

    def append_reagents_tree(self):
        """Create and add Reagents section to XDL tree."""
        reagents_tree = etree.Element('Reagents')
        for reagent in self.reagents:
            reagent_tree = etree.Element('Reagent')
            for prop, val in reagent.properties.items():
                if val != None:
                    reagent_tree.attrib[prop] = str(val)
            reagents_tree.append(reagent_tree)
        self.xdltree.append(reagents_tree)

    def append_procedure_tree(self):
        """Create and add Procedure section to XDL tree."""
        procedure_tree = etree.Element('Procedure')
        for step in self.steps:
            step_tree = etree.Element(step.name)
            for prop, val in step.properties.items():
                if val != None:
                    step_tree.attrib[prop] = str(val)
            procedure_tree.append(step_tree)
        self.xdltree.append(procedure_tree)

    def save(self, save_file):
        """Save XDL tree to given file path."""
        with open(save_file, 'w') as fileobj:
            fileobj.write(get_xdl_string(self.xdltree))

    def as_string(self):
        """Return XDL tree as XML string."""
        return get_xdl_string(self.xdltree)

def get_xdl_string(xdltree):
    """Convert XDL etree to pretty XML string.
    
    Arguments:
        xdltree {lxml.etree.ElementTree} -- etree of XDL

    Returns:
        str -- XML string
    """
    indent = '  '
    # Synthesis tag
    s = '<Synthesis>\n'
    indent_level = 1
    # Hardware, Reagents and Procedure tags
    for element in xdltree.findall('*'):
        s += f'{indent * indent_level}<{element.tag}>\n'
        indent_level += 1
        # Component, Reagent and Step tags
        for element2 in element.findall('*'):
            s += f'{indent * indent_level}<{element2.tag}\n'
            indent_level += 1
            # Element Properties
            for attr, val in element2.attrib.items():
                if val:
                    s += f'{indent * indent_level}{attr}="{val}"\n'
            s = s[:-1] + ' />\n'
            indent_level -= 1
        indent_level -= 1
        s += f'{indent * indent_level}</{element.tag}>\n\n'
    s += '</Synthesis>\n'
    return s
