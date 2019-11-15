from .utils import parse_port, undirected_neighbors
from ..constants import VALID_PORTS
from ..utils.errors import XDLError

def fix_issue_src_port_invalid(graph, issue):
    for src, _, data in graph.edges(data=True):
        src_port, dest_port = parse_port(data['port'])
        if issue['src_port'] == src_port and issue['dest_port'] == dest_port:
            src_class = graph.node[src]['class']
            assert src_class in VALID_PORTS
            assert len(VALID_PORTS[src_class]) == 1
            data['port'] = f'({VALID_PORTS[src_class][0]},{dest_port})'
            return

def fix_issue_dest_port_invalid(graph, issue):
    for _, dest, data in graph.edges(data=True):
        src_port, dest_port = parse_port(data['port'])
        if issue['src_port'] == src_port and issue['dest_port'] == dest_port:
            dest_class = graph.node[dest]['class']
            assert dest_class in VALID_PORTS
            assert len(VALID_PORTS[dest_class]) == 1
            data['port'] = f'({src_port},{VALID_PORTS[dest_class][0]})'
            return

def fix_issue_replace_flask_with_cartridge(graph, issue):
    for neighbor in undirected_neighbors(graph, issue['valve']):
        print(neighbor, issue)
        if graph.node[neighbor]['class'] == 'ChemputerFlask':
            graph.remove_node(neighbor)
            return
    raise XDLError(f'No flask found connected to {issue["valve"]} for removal to make way for cartridge.')

def reverse_edge(graph, issue):
    edge_to_reverse = None
    for src, dest, data in graph.edges(data=True):
        if src == issue['src'] and dest == issue['dest']:
            src_port, dest_port = parse_port(data['port'])
            edge_to_reverse = (src, dest, data)
            break
    assert edge_to_reverse
    reversed_data = edge_to_reverse[2]
    reversed_data['port'] = f'({dest_port},{src_port})'
    graph.remove_edge(src, dest)
    graph.add_edge(dest, src, **reversed_data)

def fix_issue_switch_to_in_edge(graph, issue):
    reverse_edge(graph, issue)

def fix_issue_switch_to_out_edge(graph, issue):
    reverse_edge(graph, issue)

def fix_issue_remove_src_port(graph, issue):
    for src, dest, data in graph.edges(data=True):
        if src == issue['src'] and dest == issue['dest']:
            _, dest_port = parse_port(data['port'])
            data['port'] = f'(,{dest_port})'

def fix_issue_remove_dest_port(graph, issue):
    for src, dest, data in graph.edges(data=True):
        if src == issue['src'] and dest == issue['dest']:
            src_port, _ = parse_port(data['port'])
            data['port'] = f'({src_port},)'
