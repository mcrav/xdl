from lxml import etree
from ..reagents import Reagent
from ..steps import Add

class XDLGenerator(object):   
    """
    Class for generating XDL from lists of hardware, reagents and steps.
    """

    def __init__(self, steps, hardware, reagents):
        """
        Generate XDL from steps, hardware and reagents.
        
        Args:
            steps {List[Step]} -- List of Step objects
            hardware {Hardware} -- Hardware object.
            reagents {List[Reagent]} -- List of Reagent objects
        """
        self.hardware, self.reagents, self.steps = hardware, reagents, steps
        self._generate_xdl()

    def _generate_xdl(self):
        """Generate XDL tree."""
        self.xdltree = etree.Element('Synthesis')
        self._append_hardware_tree()
        self._append_reagents_tree()
        self._append_procedure_tree()

    def _append_hardware_tree(self):
        """Create and add Hardware section to XDL tree."""
        hardware_tree = etree.Element('Hardware')
        for component in self.hardware:
            component_tree = etree.Element('Component')
            for prop, val in component.properties.items():
                if val != None:
                    component_tree.attrib[prop] = str(val)
            hardware_tree.append(component_tree)
        self.xdltree.append(hardware_tree)

    def _append_reagents_tree(self):
        """Create and add Reagents section to XDL tree."""
        reagents_tree = etree.Element('Reagents')
        for reagent in self.reagents:
            reagent_tree = etree.Element('Reagent')
            for prop, val in reagent.properties.items():
                if val != None:
                    reagent_tree.attrib[prop] = str(val)
            reagents_tree.append(reagent_tree)
        self.xdltree.append(reagents_tree)

    def _append_procedure_tree(self):
        """Create and add Procedure section to XDL tree."""
        procedure_tree = etree.Element('Procedure')
        for step in self.steps:
            step_tree = etree.Element(step.name)
            for prop, val in step.properties.items():
                if val != None:
                    step_tree.attrib[prop] = str(val)
                    if type(val) == list:
                        step_tree.attrib[prop] = ' '.join(
                            [str(item) for item in val])
            procedure_tree.append(step_tree)
        self.xdltree.append(procedure_tree)

    def save(self, save_file):
        """Save XDL tree to given file path."""
        with open(save_file, 'w') as fileobj:
            fileobj.write(self.as_string())

    def as_string(self):
        """Return XDL tree as XML string."""
        return get_xdl_string(self.xdltree)

def get_xdl_string(xdltree):
    """Convert XDL etree to pretty XML string.
    
    Args:
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
                if val != None:
                    s += f'{indent * indent_level}{attr}="{val}"\n'
            s = s[:-1] + ' />\n'
            indent_level -= 1
        indent_level -= 1
        s += f'{indent * indent_level}</{element.tag}>\n\n'
    s += '</Synthesis>\n'
    return s
