from typing import Dict
import json
import os
from .constants import (
    REMOVE_SRC_PORT,
    REMOVE_DEST_PORT,
    SRC_PORT_INVALID,
    DEST_PORT_INVALID,
    SWITCH_TO_IN_EDGE,
    SWITCH_TO_OUT_EDGE
)
from .issue_fixers import (
    fix_issue_remove_src_port,
    fix_issue_remove_dest_port,
    fix_issue_src_port_invalid,
    fix_issue_dest_port_invalid,
    fix_issue_switch_to_in_edge,
    fix_issue_switch_to_out_edge
)
from .check_graph_spec import check_graph_spec
from .get_graph_spec import get_graph_spec
from .apply_graph_spec import apply_spec_to_template

from ....utils.errors import XDLError
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

def graph_from_template(
    xdl_obj,
    template=None,
    save=None,
    auto_fix_issues=False,
    ignore_errors=[]
):
    graph = node_link_graph(load_template(template), directed=True)
    graph_spec = get_graph_spec(xdl_obj)
    fixable_issues, errors = check_graph_spec(graph_spec, graph)

    errors = [error for error in errors if error['error'] not in ignore_errors]
    if errors:
        error_str = '\n  -- '.join([error['msg'] for error in errors])
        error_str = '  -- ' + error_str
        raise XDLError(f'Graph template supplied cannot be used for this\
 procedure. Errors:\n{error_str}')

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
                    raise XDLError(f'Graph template supplied cannot be used for\
 this procedure. Issue: {issue["msg"]}')

        for issue in fixable_issues:
            FIXABLE_ISSUES[issue['issue']](graph, issue)

    apply_spec_to_template(graph_spec, graph, fixable_issues)
    if save:
        data = node_link_data(graph)
        with open(save, 'w') as fd:
            json.dump(data, fd, indent=2)
    return graph
