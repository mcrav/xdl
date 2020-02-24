from typing import Tuple, Dict, Union, Optional
from networkx import MultiDiGraph, NetworkXNoPath
from networkx.algorithms import shortest_path_length
from ....utils.graph import undirected_neighbors
from ....constants import INERT_GAS_SYNONYMS
from ..constants import (
    VACUUM_CLASSES,
    CHEMPUTER_FLASK,
    CHEMPUTER_CARTRIDGE,
    STIRRER_CLASSES,
    HEATER_CLASSES,
    CHILLER_CLASSES,
    FILTER_CLASSES,
    REACTOR_CLASSES,
    ROTAVAP_CLASSES,
    SEPARATOR_CLASSES,
    FLASK_CLASSES,
)

def get_unused_valve_port(graph, valve_node):
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

def get_pneumatic_controller(
    graph: MultiDiGraph, vessel: str, port: str = None
) -> Tuple[str, int]:
    """Given vessel, return pneumatic controller node that is a direct neighbour
    of the vessel in the graph, with the pneumatic controller port number.

    Args:
        vessel (str): Vessel to find attached pneumatic controller
        graph (MultiDiGraph): Graph containing vessel

    Returns:
        Tuple[str, int]: (pneumatic_controller_node, pneumatic_controller_port)
    """
    for src_node, _, info in graph.in_edges(vessel, data=True):
        if graph.nodes[src_node]['class'] == 'PneumaticController':
            if port is not None:
                ports = info['port']
                if not port or ports[1] == port:
                    return src_node, info['port'][0]
            else:
                return src_node, info['port'][0]
    return None, None

def get_vacuum_configuration(
        graph: MultiDiGraph, vessel: str) -> Dict[str, str]:
    """Get node names and ports to fully describe vacuum setup as follows:
    vessel <-> ChemputerValve -> ChemputerVacuum <-(Optional vacuum device)

    Args:
        graph (MultiDiGraph): Graph
        vessel (str): Vessel to get vacuum configuration.

    Returns:
        Dict[str, str]: Dictionary containing node names and ports:
            {
                valve: ,  # Valve connecting vessel and vacuum
                source: ,  # ChemputerVacuum attached to valve
                device: ,  # Optional CVC3000 vacuum device attached to source.
                valve_unused_port: ,  # Unused port on valve.
                valve_inert_gas_port: ,  # Port on valve connected to inert gas.
            }
    """
    valve = source = device = valve_unused_port = valve_inert_gas = None
    for neighbor, neighbor_data in undirected_neighbors(
            graph, vessel, data=True):

        # Find valve
        if not valve and neighbor_data['class'] == 'ChemputerValve':

            for valve_neighbor, valve_neighbor_data in undirected_neighbors(
                    graph, neighbor, data=True):

                # Find vacuum
                if valve_neighbor_data['class'] == 'ChemputerVacuum':

                    # Only assign valve as attached valve connected to vacuum
                    valve = neighbor
                    source = valve_neighbor

                    # Find vacuum device if there.
                    for source_neighbor, source_neighbor_data in\
                            undirected_neighbors(
                                graph, source, data=True):
                        if source_neighbor_data['class'] in VACUUM_CLASSES:
                            device = source_neighbor

                # Find inert gas
                elif valve_neighbor_data['class'] == 'ChemputerFlask':
                    if valve_neighbor_data['chemical'] in INERT_GAS_SYNONYMS:
                        valve_inert_gas = valve_neighbor

    if valve:
        valve_unused_port = get_unused_valve_port(graph, valve)

    return {
        'valve': valve,
        'source': source,
        'device': device,
        'valve_unused_port': valve_unused_port,
        'valve_inert_gas': valve_inert_gas,
    }

def get_buffer_flask(
        graph: MultiDiGraph, vessel: str, return_single=True) -> str:
    """Get buffer flask closest to given vessel.

    Args:
        vessel (str): Node name in graph.

    Returns:
        str: Node name of buffer flask (unused reactor) nearest vessel.
    """
    # Get all reactor IDs
    flasks = [
        flask
        for flask, data in graph_flasks(graph, data=True)
        if not data['chemical']
    ]

    # From remaining reactor IDs, return nearest to vessel.
    if flasks:
        if len(flasks) == 1:
            if return_single:
                return flasks[0]
            else:
                return [flasks[0]]
        else:
            shortest_paths = []
            for flask in flasks:
                shortest_paths.append((
                    flask,
                    shortest_path_length(
                        graph, source=vessel, target=flask)))
            if return_single:
                return sorted(shortest_paths, key=lambda x: x[1])[0][0]
            else:
                return [
                    item[0]
                    for item in sorted(shortest_paths, key=lambda x: x[1])
                ]
    if return_single:
        return None
    else:
        return [None, None]

def get_heater_chiller(graph, node):
    heater, chiller = None, None
    neighbors = undirected_neighbors(graph, node)
    for neighbor in neighbors:
        if graph.nodes[neighbor]['class'] in HEATER_CLASSES:
            heater = neighbor
        elif graph.nodes[neighbor]['class'] in CHILLER_CLASSES:
            chiller = neighbor
    return heater, chiller

def get_nearest_node(graph: MultiDiGraph, src: str, target_vessel_class: str):
    # Make graph undirected so actual closest waste vessels are found, not
    # closest in liquid flow path. As long as vessels are all attached to a
    # valve which is attached to a waste vessel this should be fine.
    target_vessels = [
        node for node in graph.nodes()
        if (graph.nodes[node]['class']
            == target_vessel_class)
    ]
    shortest_path_found = 100000
    closest_target_vessel = None
    for target_vessel in target_vessels:
        try:
            shortest_path_to_target_vessel = shortest_path_length(
                graph, source=src, target=target_vessel)
            if shortest_path_to_target_vessel < shortest_path_found:
                shortest_path_found = shortest_path_to_target_vessel
                closest_target_vessel = target_vessel
        except NetworkXNoPath:
            pass

    return closest_target_vessel

def get_vessel_stirrer(graph, vessel):
    for neighbor, data in undirected_neighbors(graph, vessel, data=True):
        if data['class'] in STIRRER_CLASSES:
            return neighbor
    return None

def get_reagent_vessel(
        graph: MultiDiGraph, reagent: str) -> Union[str, None]:
    """Get vessel containing given reagent.

    Args:
        reagent (str): Name of reagent to find vessel for.

    Returns:
        str: ID of vessel containing given reagent.
    """
    for node, data in graph.nodes(data=True):
        if data['class'] == CHEMPUTER_FLASK:
            if data['chemical'] == reagent:
                return node
    return None

def get_flush_tube_vessel(graph) -> Optional[str]:
    """Look for gas vessel to flush tube with after Add steps.

    Returns:
        str: Flask to use for flushing tube.
            Preference is nitrogen > air > None.
    """
    inert_gas_flask = None
    air_flask = None
    for flask, data in graph_flasks(graph, data=True):
        if data['chemical'].lower() in INERT_GAS_SYNONYMS:
            inert_gas_flask = flask
        elif data['chemical'].lower() == 'air':
            air_flask = flask
    if inert_gas_flask:
        return inert_gas_flask
    elif air_flask:
        return air_flask
    return None

def get_vessel_type(graph, vessel):
    vessel_class = graph.nodes[vessel]['class']
    if vessel_class in FILTER_CLASSES:
        return 'filter'
    elif vessel_class in ROTAVAP_CLASSES:
        return 'rotavap'
    elif vessel_class in REACTOR_CLASSES:
        return 'reactor'
    elif vessel_class in SEPARATOR_CLASSES:
        return 'separator'
    elif vessel_class in FLASK_CLASSES:
        return 'flask'
    return None

def node_in_graph(graph, node):
    return node in graph.nodes()

def get_cartridge(graph, chemical):
    for cartridge, data in graph_cartridges(graph, data=True):
        if data['chemical'] == chemical:
            return cartridge
    return None

def graph_flasks(graph, data=False):
    """Generator to iterate through all ChemputerFlasks in graph.

    Args:
        graph (MultiDiGraph): Graph
        data (bool): Give node data in (node, data) tuple. Defaults to False.
    """
    for item in graph_iter_class(graph, CHEMPUTER_FLASK, data=data):
        yield item

def graph_cartridges(graph, data=False):
    """Generator to iterate through all ChemputerCartridges in graph.

    Args:
        graph (MultiDiGraph): Graph
        data (bool): Give node data in (node, data) tuple. Defaults to False.
    """
    for item in graph_iter_class(graph, CHEMPUTER_CARTRIDGE, data=data):
        yield item


def graph_iter_class(graph, target_class, data=False):
    for node, data in graph.nodes(data=True):
        if data['class'] == target_class:
            if data:
                yield node, data
            else:
                yield node
