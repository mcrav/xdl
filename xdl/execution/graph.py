from networkx.readwrite import json_graph
from networkx import MultiDiGraph, read_graphml, NetworkXNoPath
from networkx.algorithms.shortest_paths.generic import shortest_path_length
import json
from ..hardware.components import Component, Hardware
from ..constants import CHEMPUTER_WASTE_CLASS_NAME

def get_graph(graph_file):
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

        elif graph_file.lower().endswith('.json'):
            with open(graph_file) as fileobj:
                json_data = json.load(fileobj)
                graph = json_graph.node_link_graph(
                    json_data, directed=True, multigraph=True)

    elif type(graph_file) == dict:
        graph = json_graph.node_link_graph(
            graph_file, directed=True, multigraph=True)
    return graph

def hardware_from_graph(graph):
    """Given networkx graph return a Hardware object corresponding to
    setup described in the graph.

    Args:
        graph (networkx.MultiDiGraph): networx graph of setup.
    
    Returns:
        Hardware: Hardware object containing graph described in input given.
    """
    components = []
    for node in graph.nodes():
        print('NODE', graph.node[node])
        props = graph.node[node]
        props['type'] = props['class']
        components.append(Component(node, props))
    return Hardware(components)

def make_vessel_map(graph, target_vessel_class):
    """Given graph, make dict with nodes as keys and nearest waste vessels to 
    each node as values, i.e. {node: nearest_waste_vessel}.
    
    Args:
        graph (networkx.MultiDiGraph): networkx graph of setup.
    
    Returns:
        Dict[str, str]: dict with nodes as keys and nearest waste vessels as
                        values.
    """
    vessel_map = {}
    target_vessels = [
        node for node in graph.nodes() 
        if (graph.node[node]['type'] 
            == target_vessel_class)
    ]
    for node in graph.nodes():
        node_info = graph.node[node]
        if node_info['type'] != target_vessel_class:

            shortest_path_found = 100000
            closest_target_vessel = None
            for target_vessel in target_vessels:
                try:
                    shortest_path_to_target_vessel = shortest_path_length(
                        graph, source=node, target=target_vessel)
                    if shortest_path_to_target_vessel < shortest_path_found:
                        shortest_path_found = shortest_path_to_target_vessel
                        closest_target_vessel = target_vessel
                except NetworkXNoPath:
                    pass

            vessel_map[node] = closest_target_vessel
    return vessel_map
