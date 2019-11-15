from typing import Dict, List
import json
import os
import copy
import re
from .constants import (
    HEATER_CHILLER_TEMP_RANGES,
    REMOVE_SRC_PORT,
    REMOVE_DEST_PORT,
    SRC_PORT_INVALID,
    DEST_PORT_INVALID,
    SWITCH_TO_IN_EDGE,
    SWITCH_TO_OUT_EDGE
)
from .utils import parse_port, get_backbone_valve, undirected_neighbors
from .issue_fixers import (
    fix_issue_remove_src_port,
    fix_issue_remove_dest_port,
    fix_issue_src_port_invalid,
    fix_issue_dest_port_invalid,
    fix_issue_replace_flask_with_cartridge,
    fix_issue_switch_to_in_edge,
    fix_issue_switch_to_out_edge
)
from .check_graph_spec import check_graph_spec
from .get_graph_spec import get_graph_spec
from .apply_graph_spec import apply_spec_to_template

from ..utils.errors import XDLError
from ..constants import INERT_GAS_SYNONYMS, VALID_PORTS
from networkx.readwrite import node_link_data, node_link_graph

HERE = os.path.abspath(os.path.dirname(__file__))
DEFAULT_TEMPLATE = os.path.join(HERE, 'template.json')

FIXABLE_ISSUES = {
    REMOVE_SRC_PORT: fix_issue_remove_src_port,
    REMOVE_DEST_PORT: fix_issue_remove_dest_port,
    SRC_PORT_INVALID: fix_issue_src_port_invalid,
    DEST_PORT_INVALID: fix_issue_dest_port_invalid,
    SWITCH_TO_IN_EDGE: fix_issue_switch_to_in_edge,
    SWITCH_TO_OUT_EDGE: fix_issue_switch_to_out_edge,
}

def load_template(template=DEFAULT_TEMPLATE) -> Dict:
    """Load template JSON from file.

    Returns:
        Dictionary of form {'nodes': [...], 'edges': [...]}
    """
    if not template:
        template = DEFAULT_TEMPLATE
    with open(template) as fd:
        return json.load(fd)

def graph_from_template(xdl_obj, template=None, save=None, auto_fix_issues=False, ignore_errors=[]):
    graph = node_link_graph(load_template(template), directed=True)
    graph_spec = get_graph_spec(xdl_obj)
    fixable_issues, errors = check_graph_spec(graph_spec, graph)

    errors = [error for error in errors if error['error'] not in ignore_errors]
    if errors:
        error_str = '\n  -- '.join([error['msg'] for error in errors])
        error_str = '  -- ' + error_str
        raise XDLError(f'Graph template supplied cannot be used for this procedure. Errors:\n{error_str}')

    if fixable_issues:
        if not auto_fix_issues:
            for issue in fixable_issues:
                assert issue['issue'] in FIXABLE_ISSUES
                question = f'{issue["msg"]}. Fix automatically? [Y/n]'
                answer = input(question)
                while answer not in ['y', 'Y', 'n', 'N', '']:
                    answer = input(question)
                if not answer or answer in ['y', 'Y']:
                    continue
                elif answer in ['n', 'N']:
                    raise XDLError(f'Graph template supplied cannot be used for this procedure. Issue: {issue["msg"]}')

        for issue in fixable_issues:
            FIXABLE_ISSUES[issue['issue']](graph, issue)

    apply_spec_to_template(graph_spec, graph, fixable_issues)
    if save:
        data = node_link_data(graph)
        with open(save, 'w') as fd:
            json.dump(data, fd, indent=2)
    return graph

######################################
### Old SynthReader GraphGen stuff ###
######################################

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
            and not node['name'].startswith('buffer_flask')
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
            and not node['name'].startswith('buffer_flask')):
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
