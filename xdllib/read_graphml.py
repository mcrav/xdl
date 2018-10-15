import networkx as nx

def load_graph(file):
    """
    Loads a .graphml file containing the architecture, discards unnecessary information and relabels the nodes.

    Args:
        file: GraphML file containing the architecture

    Returns:
        sanitised graph object
    """
    graph = nx.read_graphml(file)
    mapping = {}
    for node in graph.nodes():
        label = graph.node[node].pop("label", "NaN")
        mapping[node] = label
    graph = nx.relabel_nodes(graph, mapping)
    for node in graph.nodes():
        graph.node[node].pop("x", None)
        graph.node[node].pop("y", None)
        
    return graph

