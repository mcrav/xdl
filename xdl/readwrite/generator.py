from typing import List
from lxml import etree
from ..reagents import Reagent
from ..hardware import Hardware
from ..steps import Step
from ..constants import INTERNAL_PROPERTIES, XDL_VERSION
from .constants import ALWAYS_WRITE
from ..utils.misc import format_property
from ..utils.sanitisation import convert_val_to_std_units

class XDLGenerator(object):
    """
    Class for generating XDL from lists of hardware, reagents and steps.
    """

    def __init__(
        self,
        steps: List[Step],
        hardware: Hardware,
        reagents: List[Reagent],
        full_properties: bool = False,
        full_tree: bool = False,
        graph_hash: int = None,
    ) -> None:
        """
        Generate XDL from steps, hardware and reagents.

        Args:
            steps (List[xdl.steps.Step]): List of Step objects
            hardware (xdl.hardware.Hardware): Hardware object.
            reagents (List[xdl.reagents.Reagent]): List of Reagent objects
            full_properties (bool): If True, all properties will be included.
                If False, only properties that differ from their default values
                and that aren't internal properties will be included.
                Including full properties is recommended for making XDL files
                that will stand the test of time, as defaults may change in new
                versions of XDL.
        """
        self.hardware, self.reagents, self.steps = hardware, reagents, steps
        self.full_properties, self.full_tree = full_properties, full_tree
        self.graph_hash = graph_hash
        self._generate_xdl()

    def _generate_xdl(self) -> None:
        """Generate XDL tree."""
        self.xdltree = etree.Element('Synthesis')
        if self.graph_hash:
            self.xdltree.attrib['graph_sha256'] = self.graph_hash
        self._append_hardware_tree()
        self._append_reagents_tree()
        self._append_procedure_tree()

    def _append_hardware_tree(self) -> None:
        """Create and add Hardware section to XDL tree."""
        hardware_tree = etree.Element('Hardware')
        for component in self.hardware:
            component_tree = etree.Element('Component')
            for prop, val in component.properties.items():
                if val is not None:
                    if prop == 'component_type':
                        component_tree.attrib['type'] = str(val)
                    else:
                        component_tree.attrib[prop] = str(val)
            hardware_tree.append(component_tree)
        self.xdltree.append(hardware_tree)

    def _append_reagents_tree(self) -> None:
        """Create and add Reagents section to XDL tree."""
        reagents_tree = etree.Element('Reagents')
        for reagent in self.reagents:
            reagent_tree = etree.Element('Reagent')
            for prop, val in reagent.properties.items():
                if val:
                    reagent_tree.attrib[prop] = str(val)
            reagents_tree.append(reagent_tree)
        self.xdltree.append(reagents_tree)

    def _append_procedure_tree(self) -> None:
        """Create and add Procedure section to XDL tree."""
        procedure_tree = etree.Element('Procedure')
        for step in self.steps:
            procedure_tree.append(self.get_step_tree(step))
        self.xdltree.append(procedure_tree)

    def get_step_tree(self, step):
        step_tree = etree.Element(step.name)
        children = False
        for prop, val in step.properties.items():
            if prop == 'children' and val:
                children = True
                children_tree = etree.Element('Children')
                for child in val:
                    child_tree = self.get_step_tree(child)
                    children_tree.append(child_tree)
                step_tree.append(children_tree)
            else:
                if val is not None or self.full_properties:
                    # if self.full_properties is False ignore some properties.
                    if not self.full_properties:

                        # Don't write properties that are the same as the
                        # default.
                        if (prop in step.DEFAULT_PROPS
                                and convert_val_to_std_units(
                                    step.DEFAULT_PROPS[prop]) == val):

                            # Some things should always be written even if they
                            # are default.
                            if (not (step.name in ALWAYS_WRITE
                                     and prop in ALWAYS_WRITE[step.name])):
                                continue

                        # Don't write internal properties.
                        if (step.name in INTERNAL_PROPERTIES
                                and prop in INTERNAL_PROPERTIES[step.name]):
                            continue
                    # Convert value to nice units and add to element attrib.
                    formatted_property = format_property(
                        prop, val, human_readable=False)

                    if formatted_property is None:
                        formatted_property = str(formatted_property)

                    step_tree.attrib[prop] = formatted_property
        if self.full_tree:
            # Nested elements like Repeat have Steps and Children instead of
            # just raw steps
            if children:
                children_steps_tree = etree.Element('Steps')
                for substep in step.steps:
                    children_steps_tree.append(self.get_step_tree(substep))
                step_tree.append(children_steps_tree)
            else:
                for substep in step.steps:
                    step_tree.append(self.get_step_tree(substep))
        return step_tree

    def save(self, save_file: str) -> None:
        """Save XDL tree to given file path."""
        with open(save_file, 'w') as fileobj:
            fileobj.write(self.as_string())

    def as_string(self) -> str:
        """Return XDL tree as XML string."""
        return get_xdl_string(self.xdltree)

def get_element_xdl_string(
        element: etree._ElementTree, indent_level=0, indent='  ') -> str:
    s = ''
    s += f'{indent * indent_level}<{element.tag}\n'
    has_children = list(element.findall('*'))
    indent_level += 1
    # Element Properties
    for attr, val in element.attrib.items():
        if val is not None:
            s += f'{indent * indent_level}{attr}="{val}"\n'
    if has_children:
        s = s[:-1] + '>\n'
    else:
        s = s[:-1] + ' />\n'
    for subelement in element.findall('*'):
        s += get_element_xdl_string(
            subelement, indent_level=indent_level, indent=indent)
    indent_level -= 1
    if has_children:
        s += f'{indent * indent_level}</{element.tag}>\n'
    return s

def get_xdl_string(xdltree: etree._ElementTree) -> str:
    """Convert XDL etree to pretty XML string.

    Args:
        xdltree (etree.ElementTree): etree of XDL

    Returns:
        str: XML string
    """
    indent = '  '
    # Synthesis tag
    s = f'<?xdl version="{XDL_VERSION}" ?>\n\n'
    s += '<Synthesis'
    if xdltree.attrib:
        s += '\n'
        for prop in xdltree.attrib:
            s += f'{indent}{prop}="{xdltree.attrib[prop]}"\n'
    s += '>\n'
    indent_level = 1
    # Hardware, Reagents and Procedure tags
    for element in xdltree.findall('*'):
        s += f'{indent * indent_level}<{element.tag}>\n'
        indent_level += 1
        # Component, Reagent and Step tags
        for element2 in element.findall('*'):
            s += get_element_xdl_string(
                element2, indent=indent, indent_level=indent_level)
        indent_level -= 1
        s += f'{indent * indent_level}</{element.tag}>\n\n'
    s += '</Synthesis>\n'
    return s
