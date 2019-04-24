from typing import Union, Dict
import json

from networkx.readwrite import json_graph
from networkx import MultiDiGraph, read_graphml, NetworkXNoPath, relabel_nodes
from networkx.algorithms.shortest_paths.generic import shortest_path_length

from ..hardware.components import Component, Hardware
from ..constants import CHEMPUTER_WASTE_CLASS_NAME

def get_graph(graph_file: Union[str, Dict]) -> MultiDiGraph:
    """Given one of the args available, return a networkx Graph object.

    Args:
        graph_file (str, optional): Path to graph file. May be GraphML file,
            JSON file with graph in node link format, or dict containing graph
            in same format as JSON file.
    
    Returns:
        networkx.classes.multidigraph: MultiDiGraph object.
    """
    graph = None
    if type(graph_file) == str:
        if graph_file.lower().endswith('.graphml'):
            graph = MultiDiGraph(read_graphml(graph_file))
            name_mapping = {}
            for node in graph.nodes():
                name_mapping[node] = graph.node[node]['label']
            graph = relabel_nodes(graph, name_mapping)

        elif graph_file.lower().endswith('.json'):
            with open(graph_file) as fileobj:
                json_data = json.load(fileobj)
                graph = json_graph.node_link_graph(
                    json_data, directed=True, multigraph=True)

    elif type(graph_file) == dict:
        graph = json_graph.node_link_graph(
            graph_file, directed=True, multigraph=True)
    for edge in graph.edges:
        if 'port' in graph.edges[edge]:
            port_str = graph.edges[edge]['port']
            graph.edges[edge]['port'] = port_str[1:-1].split(',')
    return graph

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
        props = graph.node[node]
        props['type'] = props['class']
        component = Component(node, props['type'])
        component.properties.update(props)
        components.append(component)
    return Hardware(components)

def make_vessel_map(
    graph: MultiDiGraph, target_vessel_class: str) -> Dict[str, str]:
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
    undirected_graph = graph.to_undirected()
    vessel_map = {}
    target_vessels = [
        node for node in undirected_graph.nodes() 
        if (undirected_graph.node[node]['type'] 
            == target_vessel_class)
    ]
    for node in undirected_graph.nodes():
        node_info = undirected_graph.node[node]
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

def make_filter_inert_gas_map(graph: MultiDiGraph):
    """Given graph, make dict with filter_vessel IDs as keys and nearest
    inert gas flasks as values. i.e. { 'filter1': 'flask_nitrogen' }.
    
    Args:
        graph (networkx.MultiDiGraph): networkx graph of setup.
    
    Returns:
        Dict[str, str]: dict with filter vessels as keys and nearest nitrogen
            flasks as values.
    """
    filter_vessels = [node for node in graph.nodes()
                      if graph.node[node]['type'] == 'ChemputerFilter']
    nitrogen_flasks = [
        node
        for node in graph.nodes()
        if (graph.node[node]['type'] == 'ChemputerFlask'
            and graph.node[node]['chemical'].lower() in ['nitrogen', 'argon',
                                                         'n2', 'ar'])
    ]
    filter_inert_gas_map = {}
    for filter_vessel in filter_vessels:
        shortest_path_found = 100000
        closest_nitrogen_flask = None
        for nitrogen_flask in nitrogen_flasks:
            try:
                shortest_path_to_nitrogen_flask = shortest_path_length(
                    graph, source=nitrogen_flask, target=filter_vessel)
                if shortest_path_to_nitrogen_flask < shortest_path_found:
                    shortest_path_found = shortest_path_to_nitrogen_flask
                    closest_nitrogen_flask = nitrogen_flask
            except NetworkXNoPath:
                pass

        filter_inert_gas_map[filter_vessel] = closest_nitrogen_flask
    return filter_inert_gas_map

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
    for i in range(-1, 6): # Possible valve ports are -1, 0, 1, 2, 3, 4, 5.
        if i not in used_ports:
            return i
    return None

def flask_attached_to_vacuum(flask_node: str, graph: MultiDiGraph) -> bool:
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
            return True
    return False