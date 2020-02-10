from typing import Tuple, List, Dict
from networkx import MultiDiGraph
from ....utils.graph import undirected_neighbors
from ....constants import VACUUM_CLASSES, INERT_GAS_SYNONYMS

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

def get_buffer_flasks(graph: MultiDiGraph) -> List[str]:
    buffer_flasks = []
    for node, data in graph.nodes(data=True):
        if data['class'] == 'ChemputerFlask' and not data['chemical']:
            buffer_flasks.append(node)
    return buffer_flasks

def get_neighboring_vacuum(graph: MultiDiGraph, vessel: str) -> str:
    for neighbor, data in undirected_neighbors(graph, vessel, data=True):
        neighbor_class = data['class']
        if neighbor_class == 'ChemputerVacuum':
            return neighbor
        elif neighbor_class == 'ChemputerValve':
            for valve_neighbor, valve_neighbor_data in undirected_neighbors(
                    graph, neighbor, data=True):
                if valve_neighbor_data['class'] == 'ChemputerVacuum':
                    return neighbor
    return None
