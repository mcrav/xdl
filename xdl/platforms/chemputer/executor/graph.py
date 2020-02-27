from typing import Dict

from networkx import MultiDiGraph, NetworkXNoPath, MultiGraph
from networkx.algorithms.shortest_paths.generic import shortest_path_length

from ....hardware.components import Component, Hardware

def hardware_from_graph(graph: MultiDiGraph) -> Hardware:
    """Given networkx graph return a Hardware object corresponding to
    setup described in the graph.

    Args:
        graph (networkx.MultiDiGraph): networx graph of setup.

    Returns:
        Hardware: Hardware object containing graph described in input given.
    """
    components = []
    for node in graph.nodes():
        props = graph.nodes[node]
        props['type'] = props['class']
        component = Component(node, props['type'])
        if props['type'] == 'ChemputerFlask' and 'chemical' not in props:
            props['chemical'] = ''
        component.properties.update(props)
        components.append(component)
    return Hardware(components)

def make_vessel_map(
    graph: MultiDiGraph, target_vessel_class: str
) -> Dict[str, str]:
    """Given graph, make dict with nodes as keys and nearest waste vessels to
    each node as values, i.e. {node: nearest_waste_vessel}.

    Args:
        graph (networkx.MultiDiGraph): networkx graph of setup.

    Returns:
        Dict[str, str]: dict with nodes as keys and nearest waste vessels as
                        values.
    """
    # Make graph undirected so actual closest waste vessels are found, not
    # closest in liquid flow path. As long as vessels are all attached to a
    # valve which is attached to a waste vessel this should be fine.
    undirected_graph = MultiGraph(graph)
    vessel_map = {}
    target_vessels = [
        node for node in undirected_graph.nodes()
        if (undirected_graph.nodes[node]['type']
            == target_vessel_class)
    ]
    for node in undirected_graph.nodes():
        node_info = undirected_graph.nodes[node]
        if node_info['type'] != target_vessel_class:

            shortest_path_found = 100000
            closest_target_vessel = None
            for target_vessel in target_vessels:
                try:
                    shortest_path_to_target_vessel = shortest_path_length(
                        undirected_graph, source=node, target=target_vessel)
                    if shortest_path_to_target_vessel < shortest_path_found:
                        shortest_path_found = shortest_path_to_target_vessel
                        closest_target_vessel = target_vessel
                except NetworkXNoPath:
                    pass

            vessel_map[node] = closest_target_vessel
    return vessel_map

def get_unused_valve_port(valve_node: str, graph: MultiDiGraph) -> int:
    """Given a valve, return a position where the valve isn't connected to
    anything.

    Args:
        valve_node (str): Name of the valve on which to find an unused port.
        graph (MultiDiGraph): Graph that contains valve.

    Returns:
        int: Valve position which is not connected to anything. If there is no
            unconnected position then None is returned.
    """
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

def vacuum_device_attached_to_flask(
    flask_node: str, graph: MultiDiGraph
) -> bool:
    """Return True if given vacuum flask is attached to a vacuum device. If it
    is attached to nothing (i.e. vacuum line in fumehood) return False.

    Args:
        flask_node (str): Name of vacuum flask node.
        graph (MultiDiGraph): Graph containing flask_node.

    Returns:
        bool: True if vacuum flask is attached to vacuum device not just vacuum
            line in fumehood.
    """
    for src_node, _ in graph.in_edges(flask_node):
        if graph.nodes[src_node]['class'] == 'CVC3000':
            return src_node
    return None
