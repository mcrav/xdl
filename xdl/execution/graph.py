from networkx.readwrite import json_graph
from networkx import MultiDiGraph, read_graphml, NetworkXNoPath
from networkx.algorithms.shortest_paths.generic import shortest_path_length
import json
from ..hardware.components import Component, Hardware
from ..constants import CHEMPUTER_WASTE_CLASS_NAME

def get_graph(graphml_file=None, json_graph_file=None, json_graph_dict=None):
    """Given one of the args available, return a networkx Graph object.

    Args:
        graphml_file (str, optional): Path to graphML file.
        json_graph_file (str, optional): Path to file containing node link JSON 
                                         graph.
        json_graph_str (str, optional): Graph in node link JSON format.
    
    Returns:
        networkx.classes.multidigraph: MultiDiGraph object.
    """
    graph = None
    if graphml_file != None:
        graph = MultiDiGraph(read_graphml(graphml_file))

    elif json_graph_file:
        with open(json_graph_file) as fileobj:
            json_data = json.load(fileobj)
            graph = json_graph.node_link_graph(json_data, directed=True)
            
    elif json_graph_dict:
        graph = json_graph.node_link_graph(json_graph_dict, directed=True)
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

def make_waste_map(graph):
    """Given graph, make dict with nodes as keys and nearest waste vessels to 
    each node as values, i.e. {node: nearest_waste_vessel}.
    
    Args:
        graph (networkx.MultiDiGraph): networkx graph of setup.
    
    Returns:
        Dict[str, str]: dict with nodes as keys and nearest waste vessels as
                        values.
    """
    waste_map = {}
    # Get all waste nodes.
    wastes = [
        node for node in graph.nodes() 
        if (graph.node[node]['type'] 
            == CHEMPUTER_WASTE_CLASS_NAME)
    ]
    for node in graph.nodes():
        node_info = graph.node[node]
        if node_info['type'] != CHEMPUTER_WASTE_CLASS_NAME:
            # Find out which waste has shortest path through graph from node.
            shortest_path_found = 100000
            closest_waste_vessel = None
            for waste in wastes:
                try:
                    shortest_path_to_waste = shortest_path_length(
                        graph, source=node, target=waste)
                    if shortest_path_to_waste < shortest_path_found:
                        shortest_path_found = shortest_path_to_waste
                        closest_waste_vessel = waste
                except NetworkXNoPath:
                    pass
            waste_map[node] = closest_waste_vessel
    return waste_map