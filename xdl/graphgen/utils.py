def parse_port(port_str):
    src_port, dest_port = port_str[1:-1].split(',')
    return src_port, dest_port

def get_backbone_valve(graph, node):
    for neighbor in undirected_neighbors(graph, node):
        if graph.nodes[neighbor]['class'] == 'ChemputerValve':
            # Only look for valve with pump attached
            for valve_neighbor in graph.neighbors(neighbor):
                if graph.nodes[valve_neighbor]['class'] == 'ChemputerPump':
                    return neighbor
    return None

def get_all_backbone_valves(graph):
    backbone_valves = []
    for src, dest in graph.edges():
        if (graph.nodes[src]['class'] == 'ChemputerValve'
            and graph.nodes[dest]['class'] == 'ChemputerPump'):
            backbone_valves.append(src)
    return backbone_valves

def undirected_neighbors(graph, node):
    already_yielded = []
    for src, dest in graph.edges():
        if src == node:
            if not dest in already_yielded:
                already_yielded.append(dest)
                yield dest
        elif dest == node:
            if not src in already_yielded:
                already_yielded.append(src)
                yield src

def get_valve_unused_ports(graph, valve):
    used_ports = []
    for src, dest, data in graph.edges(data=True):
        if src == valve:
            src_port, dest_port = parse_port(data['port'])
            used_ports.append(src_port)
        elif dest == valve:
            src_port, dest_port = parse_port(data['port'])
            used_ports.append(dest_port)
    return [str(i) for i in range(6) if str(i) not in used_ports]

def get_new_edge_id(graph):
    used_edge_ids = []
    for _, _, data in graph.edges(data=True):
        used_edge_ids.append(data['id'])
    i = 0
    while i in used_edge_ids:
        i += 1
    return i

def get_new_node_id(graph):
    used_node_ids = []
    for _, data in graph.nodes(data=True):
        used_node_ids.append(data['internalId'])
    i = 0
    while i in used_node_ids:
        i += 1
    return i

def get_nearest_unused_ports(graph, valve, avoid=[]):
    unused_ports = get_valve_unused_ports(graph, valve)
    backbone_valves = get_all_backbone_valves(graph)
    if not unused_ports:
        for neighbor in undirected_neighbors(graph, valve):
            if neighbor in backbone_valves and not neighbor in avoid:
                unused_ports = get_valve_unused_ports(graph, neighbor)
                if unused_ports:
                    valve = neighbor
                    break
    if not unused_ports:
        for backbone_valve in backbone_valves:
            if not backbone_valve in avoid:
                unused_ports = get_valve_unused_ports(graph, backbone_valve)
                if unused_ports:
                    valve = backbone_valve
                    break
    return valve, unused_ports
