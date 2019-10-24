from typing import Dict, List
import json
import os
import copy
from ..steps import FilterThrough

HERE = os.path.abspath(os.path.dirname(__file__))

def load_template() -> Dict:
    """Load template JSON from file.

    Returns:
        Dictionary of form {'nodes': [...], 'edges': [...]}
    """
    with open(os.path.join(HERE, 'chemputer_std6.json')) as fd:
        return json.load(fd)

def get_n_reagent_flasks(template: Dict) -> int:
    """Get the number of reagent flasks contained in the template, ignoring
    buffer flasks or flasks where the chemical is already specified, e.g. inert
    gas flasks.

    Returns:
        int: Number of reagent flasks contained in the template.
    """
    i = 0
    for node in template['nodes']:
        if (node['type'] == 'flask'
            and not node['name'] == 'buffer_flask'
            and not node['chemical']):
            i += 1
    return i

def add_reagents(
    template: Dict, reagents: List[str], cartridge_reagents: [List[str]]) -> Dict:
    """Add reagents to reagent flasks in template.

    Args:
        template (Dict): Loaded template to add chemical property to reagent
            flasks.
        reagents (List[str]): List of reagents to add to reagent flasks in
            template.

    Returns:
        Dict: Template with reagents added to reagent flasks.
    """
    max_n_reagents = get_n_reagent_flasks(template)
    if len(reagents) > max_n_reagents:
        raise(
            ValueError(f'{len(reagents)} in procedure. Not enough space in template for more than {max_n_reagents} reagents'))

    reagents = copy.deepcopy(list(set(reagents)))
    for node in template['nodes']:
        if (node['type'] == 'flask'
            and not node['name'] == 'buffer_flask'):
            if reagents:
                node['chemical'] = reagents.pop()
            elif not node['chemical']:
                # Need this so flasks aren't used as buffer flask
                node['chemical'] = 'None'

        elif node['type'] == 'cartridge':
            if cartridge_reagents:
                node['chemical'] = cartridge_reagents.pop()

    return template

def get_graph(reagents: List[str], cartridge_reagents: List[str] = []) -> Dict:
    """Get a template graph with all passed reagents added to reagent flasks.

    Args:
        reagents (List[str]): List of reagents to add to template.

    Returns:
        Dict: Graph with all passed reagents in reagent flasks.
    """
    return add_reagents(load_template(), reagents, cartridge_reagents)

def save_graph(reagents: List[str], save_file: str) -> None:
    """Save template graph with all passed reagents added to reagent flasks.

    Args:
        reagents (List[str]): List of reagents to add to template.
        save_file (str): File path to save JSON graph to.
    """
    with open(save_file, 'w') as fd:
        json.dump(get_graph(reagents), fd)
