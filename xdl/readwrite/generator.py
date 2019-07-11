from typing import List, Any
from lxml import etree
from ..reagents import Reagent
from ..hardware import Hardware
from ..steps import Add, Step
from ..constants import DEFAULT_VALS, INTERNAL_PROPERTIES, XDL_VERSION
from ..utils.misc import format_property

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
        self.full_properties = full_properties
        self._generate_xdl()

    def _generate_xdl(self) -> None:
        """Generate XDL tree."""
        self.xdltree = etree.Element('Synthesis')
        self._append_hardware_tree()
        self._append_reagents_tree()
        self._append_procedure_tree()

    def _append_hardware_tree(self) -> None:
        """Create and add Hardware section to XDL tree."""
        hardware_tree = etree.Element('Hardware')
        for component in self.hardware:
            component_tree = etree.Element('Component')
            for prop, val in component.properties.items():
                if val != None:
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
                if val != None:
                    reagent_tree.attrib[prop] = str(val)
            reagents_tree.append(reagent_tree)
        self.xdltree.append(reagents_tree)

    def _append_procedure_tree(self) -> None:
        """Create and add Procedure section to XDL tree."""
        procedure_tree = etree.Element('Procedure')
        for step in self.steps:
            step_tree = etree.Element(step.name)
            for prop, val in step.properties.items():
                if val != None:
                    # if self.full_properties is False ignore some properties.
                    if not self.full_properties:
                        # Don't write properties that are the same as the default.
                        if (step.name in DEFAULT_VALS
                            and prop in DEFAULT_VALS[step.name]
                            and DEFAULT_VALS[step.name][prop] == val):
                            continue

                        # Don't write internal properties.
                        if (step.name in INTERNAL_PROPERTIES
                            and prop in INTERNAL_PROPERTIES[step.name]):
                            continue
                    # Convert value to nice units and add to element attrib.
                    step_tree.attrib[prop] = format_property(
                        prop, val, human_readable=False)

            procedure_tree.append(step_tree)
        self.xdltree.append(procedure_tree)

    def save(self, save_file: str) -> None:
        """Save XDL tree to given file path."""
        with open(save_file, 'w') as fileobj:
            fileobj.write(self.as_string())

    def as_string(self) -> str:
        """Return XDL tree as XML string."""
        return get_xdl_string(self.xdltree)

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
    s += '<Synthesis>\n'
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
