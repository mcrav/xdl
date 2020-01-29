from typing import Tuple, List
from networkx import MultiDiGraph
from ....utils.graph import undirected_neighbors

def get_unused_valve_port(graph, valve_node):
    used_ports = []
    # Get connected valve positions.
    for _, _, edge_data in graph.in_edges(valve_node, data=True):
        if 'port' in edge_data:
            used_ports.append(int(edge_data['port'][1]))

    for _, _, edge_data in graph.out_edges(valve_node, data=True):
        if 'port' in edge_data:
            used_ports.append(int(edge_data['port'][0]))

    # Return first found unconnected valve positions.
    for i in range(-1, 6):  # Possible valve ports are -1, 0, 1, 2, 3, 4, 5.
        if i not in used_ports:
            return i
    return None

def get_pneumatic_controller(
    graph: MultiDiGraph, vessel: str, port: str = None
) -> Tuple[str, int]:
    """Given vessel, return pneumatic controller node that is a direct neighbour
    of the vessel in the graph, with the pneumatic controller port number.

    Args:
        vessel (str): Vessel to find attached pneumatic controller
        graph (MultiDiGraph): Graph containing vessel

    Returns:
        Tuple[str, int]: (pneumatic_controller_node, pneumatic_controller_port)
    """
    for src_node, _, info in graph.in_edges(vessel, data=True):
        if graph.nodes[src_node]['class'] == 'PneumaticController':
            if port is not None:
                ports = info['port']
                if not port or ports[1] == port:
                    return src_node, info['port'][0]
            else:
                return src_node, info['port'][0]
    return None, None

def get_buffer_flasks(graph: MultiDiGraph) -> List[str]:
    buffer_flasks = []
    for node, data in graph.nodes(data=True):
        if data['class'] == 'ChemputerFlask' and not data['chemical']:
            buffer_flasks.append(node)
    return buffer_flasks

def get_neighboring_vacuum(graph: MultiDiGraph, vessel: str) -> str:
    for neighbor, data in undirected_neighbors(graph, vessel, data=True):
        neighbor_class = data['class']
        if neighbor_class == 'ChemputerVacuum':
            return neighbor
        elif neighbor_class == 'ChemputerValve':
            for valve_neighbor, valve_neighbor_data in undirected_neighbors(
                    graph, neighbor, data=True):
                if valve_neighbor_data['class'] == 'ChemputerVacuum':
                    return neighbor
    return None
