def undirected_neighbors(graph, node, data=False):
    yielded_neighbors = []
    for src, dest in graph.edges():
        if src == node and dest not in yielded_neighbors:
            if data:
                yield graph.node[dest]
            else:
                yield dest

        elif dest == node and src not in yielded_neighbors:
            if data:
                yield graph.node[src]
            else:
                yield src
