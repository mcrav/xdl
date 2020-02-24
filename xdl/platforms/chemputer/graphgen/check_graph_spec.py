from .utils import (
    parse_port,
    undirected_neighbors,
    get_all_backbone_valves
)
from .constants import (
    HEATER_CHILLER_TEMP_RANGES,
    REMOVE_SRC_PORT,
    REMOVE_DEST_PORT,
    SRC_PORT_INVALID,
    DEST_PORT_INVALID,
    SWITCH_TO_IN_EDGE,
    SWITCH_TO_OUT_EDGE,

    CANNOT_REACH_TARGET_TEMP_ERROR,
    INVALID_PORT_ERROR,
    NOT_ENOUGH_SPARE_PORTS_ERROR,
    MISSING_COMPONENT_TYPE_ERROR,
    MISSING_HEATER_OR_CHILLER_ERROR,
)
from ....constants import INERT_GAS_SYNONYMS
from ..constants import VALID_PORTS

def check_graph_spec(graph_spec, graph):
    fixable_issues, errors = [], []

    # Check template
    template_fixable_issues, template_errors = check_template(graph)
    fixable_issues += template_fixable_issues
    errors += template_errors

    # Check space for cartridges
    cartridge_fixable_issues, cartridge_errors = check_cartridges(
        graph_spec['cartridges'], graph)
    fixable_issues += cartridge_fixable_issues
    errors += cartridge_errors

    # Check enough flasks for reagents and buffer flasks
    flask_fixable_issues, flask_errors = check_flasks(
        graph_spec['reagents'],
        graph_spec['buffer_flasks'],
        graph_spec['cartridges'],
        graph
    )
    fixable_issues += flask_fixable_issues
    errors += flask_errors

    # Check vessels can be heated/chilled to required temps
    vessel_fixable_issues, vessel_errors = check_vessel_spec(
        graph_spec['vessels'], graph)
    fixable_issues += vessel_fixable_issues
    errors += vessel_errors

    return fixable_issues, errors

def check_template(graph):
    fixables_issues, errors = [], []

    port_fixable_issues, port_errors = check_template_ports(graph)
    fixables_issues += port_fixable_issues
    errors += port_errors

    edge_fixable_issues, edge_errors = check_template_edges(graph)
    fixables_issues += edge_fixable_issues
    errors += edge_errors

    return fixables_issues, errors

def check_template_ports(graph):
    fixable_issues, errors = [], []
    for src, dest, data in graph.edges(data=True):

        # Unpack edge
        src_port, dest_port = parse_port(data['port'])
        src_node = graph.nodes[src]
        dest_node = graph.nodes[dest]
        src_class = src_node['class']
        dest_class = dest_node['class']

        # Find port errors
        src_port_fixables_issues, src_port_errors = check_port(
            'src', src, dest, src_port, dest_port, src_class, dest_class)
        dest_port_fixables_issues, dest_port_errors = check_port(
            'dest', src, dest, src_port, dest_port, src_class, dest_class)

        # Add port errors to lists
        fixable_issues += src_port_fixables_issues
        fixable_issues += dest_port_fixables_issues
        errors += src_port_errors
        errors += dest_port_errors

    return fixable_issues, errors

def check_port(
        src_or_dest, src, dest, src_port, dest_port, src_class, dest_class):
    fixable_issues = []
    errors = []

    if src_or_dest == 'src':
        port = src_port
        node_class = src_class
    elif src_or_dest == 'dest':
        port = dest_port
        node_class = dest_class
    else:
        raise ValueError(
            'Only "src" or "dest" may be passed as argument src_or_dest')

    # port should be specified
    if ((src_class in VALID_PORTS and dest_class in VALID_PORTS)
            or (node_class == 'ChemputerValve')):
        node_valid_ports = VALID_PORTS[node_class]

        # port is valid
        if str(port) in node_valid_ports:
            pass

        # port not valid
        else:
            # More than one valid port, raise error
            if len(node_valid_ports) > 1:
                errors.append({
                    'error': INVALID_PORT_ERROR,
                    'msg': f'{port} is an invalid port for {node_class}. Valid\
 ports: {", ".join(node_valid_ports)}'
                })

            # Only one valid port, offer to fix automatically
            else:
                if src_or_dest == 'src':
                    issue = SRC_PORT_INVALID
                else:
                    issue = DEST_PORT_INVALID
                fixable_issues.append({
                    'src': src,
                    'dest': dest,
                    'src_port': src_port,
                    'dest_port': dest_port,
                    'issue': issue,
                    'msg': f'{port} is an invalid port for {node_class}. Valid\
 ports: {", ".join(node_valid_ports)}'
                })

    # port shouldn't be specified
    else:
        if port:
            if src_or_dest == 'src':
                issue = REMOVE_SRC_PORT
            else:
                issue = REMOVE_DEST_PORT
            fixable_issues.append({
                'src': src,
                'dest': dest,
                'src_port': src_port,
                'dest_port': dest_port,
                'issue': issue,
                'msg': f"Port doesn't need to be specified for {node_class} on\
 edge {src} -> {dest}."
            })
    return fixable_issues, errors

def check_template_edges(graph):
    fixable_issues, errors = [], []

    for src, dest in graph.edges():
        # Unpack edge
        src_node = graph.nodes[src]
        dest_node = graph.nodes[dest]

        # No edges leading out of vacuum
        if src_node['class'] == 'ChemputerVacuum':
            fixable_issues.append({
                'src': src,
                'dest': dest,
                'issue': SWITCH_TO_IN_EDGE,
                'msg': 'out edge not allowed on ChemputerVacuum.',
            })

        # No edges leading into inert gas flask
        if (dest_node['class'] == 'ChemputerFlask'
                and dest_node['chemical'].lower() in INERT_GAS_SYNONYMS):
            fixable_issues.append({
                'src': src,
                'dest': dest,
                'issue': SWITCH_TO_OUT_EDGE,
                'msg': f'in edge not allowed on inert gas flask ({dest}).',
            })

    return fixable_issues, errors

def get_n_available_backbone_valve_ports(graph):
    backbone_valves = get_all_backbone_valves(graph)
    total_available_ports = 0
    for valve in backbone_valves:
        neighbors = list(undirected_neighbors(graph, valve))
        available_ports = 7 - len(neighbors)
        total_available_ports += available_ports
    return total_available_ports

def check_flasks(reagents_spec, buffer_flask_spec, cartridge_spec, graph):
    fixable_issues, errors = [], []

    n_available_ports = get_n_available_backbone_valve_ports(graph)
    n_reagent_flasks_required = len(reagents_spec)
    if buffer_flask_spec:
        n_buffer_flasks_required = max(
            buffer_flask_spec,
            key=lambda item: item['n_required']
        )['n_required']
    else:
        n_buffer_flasks_required = 0
    total_n_ports_required = (
        n_reagent_flasks_required
        + n_buffer_flasks_required
        + (2 * len(cartridge_spec))
    )
    if total_n_ports_required > n_available_ports:
        errors.append({
            'error': NOT_ENOUGH_SPARE_PORTS_ERROR,
            'msg': f'{n_reagent_flasks_required} reagent flasks required,\
 {len(cartridge_spec)} cartridges and {n_buffer_flasks_required} empty buffer\
 flasks required but only {n_available_ports} spare ports present in graph.',
        })

    return fixable_issues, errors

def check_cartridges(cartridge_spec, graph):
    fixable_issues, errors = [], []
    return fixable_issues, errors

def check_vessel_spec(vessel_spec, graph):
    fixable_issues, errors = [], []
    available_vessels = [
        node for node in graph
        if graph.nodes[node]['class'] in [
            'ChemputerSeparator',
            'ChemputerReactor',
            'ChemputerFilter',
            'IKARV10'
        ]
    ]

    type_mapping = {
        'filter': 'ChemputerFilter',
        'reactor': 'ChemputerReactor',
        'separator': 'ChemputerSeparator',
        'rotavap': 'IKARV10',
    }

    vessel_map = {}

    for component_id, component_type in vessel_spec['types']:
        if component_type in type_mapping:
            found_type = False
            for i in range(len(available_vessels)):
                node_class = graph.nodes[available_vessels[i]]['class']
                if node_class == type_mapping[component_type]:
                    found_type = True
                    vessel_map[component_id] = available_vessels[i]
                    available_vessels.pop(i)
                    break
            if not found_type:
                errors.append({
                    'error': MISSING_COMPONENT_TYPE_ERROR,
                    'msg': f"Couldn't find {component_type} in graph."
                })

    for vessel, temps in vessel_spec['temps'].items():
        if temps:
            max_temp_required = max(temps)
            min_temp_required = min(temps)
            if max_temp_required <= 25 and min_temp_required >= 18:
                continue
            else:
                if vessel in vessel_map:
                    temp_range = get_vessel_temp_range(
                        vessel_map[vessel], graph
                    )
                    if not temp_range:
                        errors.append({
                            'error': MISSING_HEATER_OR_CHILLER_ERROR,
                            'msg': f"Can't find heater/chiller attached to\
 {vessel_map[vessel]}."
                        })
                    else:
                        min_temp_possible, max_temp_possible = temp_range
                        if min_temp_required < min_temp_possible:
                            errors.append({
                                'error': CANNOT_REACH_TARGET_TEMP_ERROR,
                                'msg': f'{vessel_map[vessel]} cannot go to\
 {min_temp_required} °C as required. Min possible temp: {min_temp_possible} °C'
                            })
                        if max_temp_required > max_temp_possible:
                            errors.append({
                                'error': CANNOT_REACH_TARGET_TEMP_ERROR,
                                'msg': f'{vessel_map[vessel]} cannot go to\
 {max_temp_required} °C as required. Max possible temp: {max_temp_possible} °C'
                            })

    return fixable_issues, errors

def get_vessel_temp_range(node, graph):
    if graph.nodes[node]['class'] == 'IKARV10':
        return HEATER_CHILLER_TEMP_RANGES['IKARV10']
    for neighbor in undirected_neighbors(graph, node):
        neighbor_class = graph.nodes[neighbor]['class']
        if neighbor_class in HEATER_CHILLER_TEMP_RANGES:
            return HEATER_CHILLER_TEMP_RANGES[neighbor_class]
    return None
