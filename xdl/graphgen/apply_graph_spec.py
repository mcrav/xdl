from .constants import DEFAULT_BUFFER_FLASK_VOLUME, DEFAULT_REAGENT_FLASK_VOLUME

from ..constants import INERT_GAS_SYNONYMS
from .utils import (
    get_backbone_valve,
    undirected_neighbors,
    get_valve_unused_ports,
    get_new_edge_id,
    get_new_node_id,
    get_all_backbone_valves,
    get_nearest_unused_ports
)

def apply_spec_to_template(graph_spec, graph, fixable_issues):
    reset_flasks(graph)
    apply_buffer_flasks(graph, graph_spec['buffer_flasks'])
    apply_reagent_flasks(graph, graph_spec['reagents'])
    apply_cartridge(graph, graph_spec['cartridges'])
    return graph

def reset_flasks(graph):
    for node in graph.nodes():
        full_node = graph.nodes[node]
        if (full_node['class'] == 'ChemputerFlask'
                and full_node['chemical'].lower() not in INERT_GAS_SYNONYMS):
            full_node['chemical'] = 'none'

def apply_buffer_flasks(graph, buffer_flask_spec):
    buffer_flasks_added = 0
    for buffer_flask in buffer_flask_spec:
        connected_node = buffer_flask['connected_node']
        n_required = buffer_flask['n_required']
        for _ in range(n_required):
            connected_valve = get_backbone_valve(graph, connected_node)
            connected_valve, unused_ports = get_nearest_unused_ports(
                graph, connected_valve)
            buffer_flask_name = f'buffer_flask{buffer_flasks_added+1}'
            add_buffer_flask(
                graph,
                buffer_flask_name,
                connected_valve,
                unused_ports[0]
            )
            add_buffer_flask_edges(
                graph, connected_valve, buffer_flask_name, unused_ports[0])
            buffer_flasks_added += 1

def get_used_node_positions(graph):
    used_pos = []
    for _, data in graph.nodes(data=True):
        used_pos.append((data['x'], data['y']))
    return used_pos

def get_flask_position(graph, valve):
    used_pos = get_used_node_positions(graph)
    valve_x = graph.nodes[valve]['x']
    valve_y = graph.nodes[valve]['y']
    gridsize = 40
    offset = gridsize * 2
    possible_pos = [
        (valve_x - offset, valve_y - offset),
        (valve_x - offset, valve_y + offset),
        (valve_x + offset, valve_y + offset),
        (valve_x + offset, valve_y - offset),
        (valve_x - offset, valve_y),
        (valve_x + offset, valve_y),
    ]
    for pos in possible_pos:
        if pos not in used_pos:
            return pos
    return (0, 0)

def add_buffer_flask(graph, node_name, valve, port):
    x, y = get_flask_position(graph, valve)
    graph.add_node(
        node_name,
        **{
            'class': 'ChemputerFlask',
            'type': 'flask',
            'x': x,
            'y': y,
            'id': node_name,
            'label': node_name,
            'name': node_name,
            'max_volume': DEFAULT_BUFFER_FLASK_VOLUME,
            'current_volume': 0,
            'chemical': '',
            'internalId': get_new_node_id(graph),
        }
    )

def add_buffer_flask_edges(graph, valve, flask, valve_port):
    flask_id = graph.nodes[flask]['internalId']
    valve_id = graph.nodes[valve]['internalId']
    in_data = {
        'id': get_new_edge_id(graph),
        'source': valve,
        'target': flask,
        'sourceInternal': valve_id,
        'targetInternal': flask_id,
        'port': f'({valve_port},0)'
    }
    graph.add_edge(valve, flask, **in_data)
    out_data = {
        'id': get_new_edge_id(graph),
        'source': flask,
        'target': valve,
        'sourceInternal': flask_id,
        'targetInternal': valve_id,
        'port': f'(0,{valve_port})'
    }
    graph.add_edge(flask, valve, **out_data)

def apply_reagent_flasks(graph, reagent_spec):
    for reagent in reagent_spec:
        flask_name = f'flask_{reagent}'
        available_valves = get_all_backbone_valves(graph)
        for valve in available_valves:
            unused_ports = get_valve_unused_ports(graph, valve)
            if unused_ports:
                add_reagent_flask(graph, valve, flask_name, reagent)
                add_reagent_flask_edge(
                    graph, valve, flask_name, unused_ports[0])
                break

def add_reagent_flask(graph, valve, node_name, reagent):
    x, y = get_flask_position(graph, valve)
    graph.add_node(node_name, **{
        'type': 'flask',
        'x': x,
        'y': y,
        'max_volume': DEFAULT_REAGENT_FLASK_VOLUME,
        'current_volume': 0,
        'class': 'ChemputerFlask',
        'chemical': reagent,
        'name': node_name,
        'label': node_name,
        'id': node_name,
        'internalId': get_new_node_id(graph)
    })

def add_reagent_flask_edge(graph, valve, flask, valve_port):
    valve_id = graph.nodes[valve]['internalId']
    flask_id = graph.nodes[flask]['internalId']
    graph.add_edge(flask, valve, **{
        'port': f'(0,{valve_port})',
        'source': flask,
        'target': valve,
        'sourceInternal': flask_id,
        'targetInternal': valve_id,
        'id': get_new_edge_id(graph),
    })

def get_cartridge_node_position(graph, from_valve, to_valve):
    used_positions = []
    for node, data in graph.nodes(data=True):
        used_positions.append((data['x'], data['y']))
    from_x = graph.nodes[from_valve]['x']
    from_y = graph.nodes[from_valve]['y']
    to_x = graph.nodes[to_valve]['x']
    to_y = graph.nodes[to_valve]['y']
    min_x = min(from_x, to_x)
    min_y = min(from_y, to_y)
    max_x = max(from_x, to_x)
    pos = (min_x + ((max_x - min_x) / 2), min_y * 2)
    while pos in used_positions:
        pos = (pos[0] + 80, pos[1])
    return pos

def get_nearest_buffer_flask_valve(graph, backbone_valve):
    backbone_valves = get_all_backbone_valves(graph)
    buffer_flasks = get_buffer_flasks_on_valve(graph, backbone_valve)
    if buffer_flasks:
        return buffer_flasks[0]
    avoid = [backbone_valve]
    buffer_flasks, tried = get_buffer_flasks_from_neighbors(
        graph, backbone_valve, avoid)
    if buffer_flasks:
        return buffer_flasks[0]
    avoid.extend(tried)
    while (len([item for item in avoid if item in backbone_valves])
           < len(backbone_valves)):
        for valve in tried:
            if valve in backbone_valves:
                buffer_flasks, tried = get_buffer_flasks_from_neighbors(
                    graph, backbone_valve, avoid)
                if buffer_flasks:
                    return buffer_flasks[0]
                avoid.extend(tried)

def get_buffer_flasks_from_neighbors(graph, valve, avoid=[]):
    buffer_flasks, tried = [], []
    for neighbor in undirected_neighbors(graph, valve):
        if graph.nodes[neighbor]['class'] == 'ChemputerValve':
            buffer_flasks.extend(get_buffer_flasks_on_valve(graph, neighbor))
            tried.append(neighbor)
    return buffer_flasks, tried

def get_buffer_flasks_on_valve(graph, valve):
    buffer_flasks = []
    for node in undirected_neighbors(graph, valve):
        if (graph.nodes[node]['class'] == 'ChemputerFlask'
                and not graph.nodes[node]['chemical']):
            buffer_flasks.append(node)
    return buffer_flasks

def apply_cartridge(graph, cartridge_spec):
    for cartridge in cartridge_spec:
        chemical = cartridge['chemical']
        from_valve = get_backbone_valve(graph, cartridge['from'])
        to_valve = get_backbone_valve(graph, cartridge['to'])
        if cartridge['from'] == cartridge['to']:
            to_valve = get_nearest_buffer_flask_valve(graph, from_valve)
        cartridge_node_name = f'cartridge_{chemical}'
        cartridge_internal_id = get_new_node_id(graph)

        # Make in edge
        from_valve, unused_ports = get_nearest_unused_ports(
            graph, from_valve, avoid=[to_valve])
        in_edge_data = {
            'id': get_new_edge_id(graph),
            'port': f"({unused_ports[0]},in)",
            'source': from_valve,
            'target': cartridge_node_name,
            'sourceInternal': graph.nodes[from_valve]['internalId'],
            'targetInternal': cartridge_internal_id,
        }

        # Make out edge
        to_valve, unused_ports = get_nearest_unused_ports(
            graph, to_valve, avoid=[from_valve])
        out_edge_data = {
            'id': None,
            'port': f"(out,{unused_ports[0]})",
            'source': cartridge_node_name,
            'target': to_valve,
            'sourceInternal': cartridge_internal_id,
            'targetInternal': graph.nodes[to_valve]['internalId'],
        }

        x, y = get_cartridge_node_position(graph, from_valve, to_valve)
        node_data = {
            'id': cartridge_node_name,
            'label': cartridge_node_name,
            'name': cartridge_node_name,
            'chemical': chemical,
            'type': 'cartridge',
            'class': 'ChemputerCartridge',
            'internalId': cartridge_internal_id,
            'x': x,
            'y': y
        }

        graph.add_node(cartridge_node_name, **node_data)
        graph.add_edge(from_valve, cartridge_node_name, **in_edge_data)
        out_edge_data['id'] = get_new_edge_id(graph)
        graph.add_edge(cartridge_node_name, to_valve, **out_edge_data)
