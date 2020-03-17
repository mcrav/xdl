from typing import Union, Dict
import copy
import json
from networkx.readwrite import json_graph
from networkx import MultiDiGraph, read_graphml, relabel_nodes

def undirected_neighbors(graph, node, data=False):
    yielded_neighbors = []
    for src, dest in graph.edges():
        if src == node and dest not in yielded_neighbors:
            yielded_neighbors.append(dest)
            if data:
                yield dest, graph.nodes[dest]
            else:
                yield dest

        elif dest == node and src not in yielded_neighbors:
            yielded_neighbors.append(src)
            if data:
                yield src, graph.nodes[src]
            else:
                yield src

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
            raw_graph = copy.deepcopy(graph)
            name_mapping = {}
            for node in graph.nodes():
                name_mapping[node] = graph.nodes[node]['label']
            graph = relabel_nodes(graph, name_mapping)

        elif graph_file.lower().endswith('.json'):
            with open(graph_file) as fileobj:
                json_data = json.load(fileobj)
                graph = json_graph.node_link_graph(
                    json_data, directed=True, multigraph=True)
            raw_graph = copy.deepcopy(graph)

    elif type(graph_file) == dict:
        graph = json_graph.node_link_graph(
            graph_file, directed=True, multigraph=True)
        raw_graph = copy.deepcopy(graph)

    elif type(graph_file) == MultiDiGraph:
        graph = graph_file
        raw_graph = None

    for edge in graph.edges:
        if 'port' in graph.edges[edge]:
            port_str = graph.edges[edge]['port']
            if type(port_str) == str:
                graph.edges[edge]['port'] = port_str[1:-1].split(',')
    return graph, raw_graph
