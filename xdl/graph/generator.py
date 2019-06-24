from typing import Dict, Tuple, Any, Union
import json
import copy

from .constants  import *
from ..hardware import Component

if False:
    from .. import XDL
from ..hardware import Component

class GraphGenerator(object):
    """Class to generate a basic graph from a XDL object that should be
    sufficient for passing to xdl.prepare_for_execution.
    
    Args:
        xdl (XDL): XDL object to generate graph from.
    """
    def __init__(self, xdl: 'XDL') -> None:
        self._xdl = xdl
        self._nodes = []
        self._edges = []
        self._valves = []
        # self._components is list of filters, reactors, separators and rotavaps.
        self._components = [
            item
            for item in xdl.hardware
            if item.component_type in [
                'ChemputerFilter',
                'ChemputerReactor',
                'ChemputerSeparator',
                'IKARV10',
                'filter',
                'reactor',
                'separator',
                'rotavap']]
        for step in xdl.steps:
            if (step.name in ['FilterThrough', 'RunColumn']
                and step.from_vessel == step.to_vessel):
                self._components.append(
                    Component(id='buffer_flask', component_type='reactor'))
        self._reagents = copy.deepcopy([reagent.id for reagent in xdl.reagents])
        if xdl.filter_dead_volume_method == 'inert_gas':
            self._reagents.append('nitrogen')
        elif (xdl.filter_dead_volume_method == 'solvent'
              and xdl.filter_dead_volume_solvent):
            self._reagents.append(xdl.filter_dead_volume_solvent)
            
        if xdl.organic_cleaning_solvent not in self._reagents:
            self._reagents.append(xdl.organic_cleaning_solvent)
        # ID number incremented by 1 for every node/edge added in
        # _get_internal_id.
        self._internal_id = -1

        # Positioning constants
        # valve_y and valve_spacing * backbone_i are used to position valves.
        # Everything else is positioned relative to the valve it is attached to.
        self._gridsize = 40
        self._valve_y = 200
        self._valve_spacing = 9
        self._waste_x_offset = self._gridsize * -2
        self._waste_y_offset = self._gridsize * -2
        self._component_y_offset = self._gridsize * 4
        self._pump_y_offset = self._gridsize * -3
        self._flask_offsets = [
            (self._gridsize * -4, self._gridsize * 2),
            (self._gridsize * -2, self._gridsize * 2),
            (self._gridsize * 2, self._gridsize * 2),
            (self._gridsize * 4, self._gridsize * 2),
        ]


    ########################
    ### GRAPH GENERATION ###
    ########################

    def generate_graph(self, save_path: str = None) -> None:
        """Generate the graph, and save it if save_path is specified. This
        method is destructive and can only be called once per GraphGenerator
        object.
        
        Args:
            save_path (str): Optional. Path to save node link JSON graph to.
        """
        backbone_i = 0
        while len(self._components) > 0 or len(self._reagents) > 0:
            # Add valve
            valve = self._get_valve(f'valve{backbone_i + 1}', backbone_i)
            self._nodes.append(valve)
            self._valves.append(valve)
            valve_connections = 0

            # Add waste
            waste = self._get_waste(f'waste{backbone_i + 1}', backbone_i)
            self._nodes.append(waste)
            self._add_edge(valve, waste, 0, 0)
            valve_connections += 1

            # Add pump
            pump = self._get_pump(f'pump{backbone_i + 1}', backbone_i)
            self._nodes.append(pump)
            self._add_edge(valve, pump, -1, 0, both_ways=True)
            valve_connections += 1
            
            # Add special component, i.e. 'filter', 'separator
            if len(self._components) > 0:
                component = self._get_component(self._components.pop(), backbone_i)
                self._nodes.append(component)
                if component['type'] in ['filter', 'separator']:
                    self._add_edge(valve, component, 1, 'top')
                    self._add_edge(valve, component, 2, 'bottom', both_ways=True)
                    valve_connections += 2

                elif component['type'] == 'reactor':
                    self._add_edge(valve, component, 1, 0, both_ways=True)
                    valve_connections += 1

                elif component['type'] == 'rotavap':
                    self._add_edge(valve, component, 1, 'evaporate')
                    self._add_edge(component, valve, 'collect', 2)
                    valve_connections += 2
                
            # Add connection to previous valve in backbone.
            if backbone_i > 0:
                self._add_edge(
                    valve,
                    self._valves[backbone_i - 1],
                    valve_connections - 1,
                    5, both_ways=True)
                valve_connections += 1

            flask_i = 0
            # Add flasks leaving space for connection to next valve in backbone.
            while valve_connections < 6 and len(self._reagents) > 0:
                reagent = self._reagents.pop()
                flask = self._get_flask(
                    f'flask_{reagent}', reagent, backbone_i, flask_i)
                self._nodes.append(flask)
                self._add_edge(flask, valve, 0, valve_connections - 1)
                valve_connections += 1
                flask_i += 1

            # If only one more flask to add, add it and stop.
            if len(self._components) == 0 and len(self._reagents) == 1:
                reagent = self._reagents.pop()
                flask = self._get_flask(
                    f'flask_{reagent}', reagent, backbone_i, flask_i)
                self._nodes.append(flask)
                self._add_edge(flask, valve, 0, valve_connections - 1)
                valve_connections += 1
                flask_i += 1
            # If lots more flasks/components to add extend backbone.
            else:
                backbone_i += 1
                continue
        # Make graph dict and save it if save path specified.
        self.graph = {'nodes': self._nodes, 'links': self._edges}
        if save_path:
            self.save(save_path)


    #####################
    ### NODE CREATION ###
    #####################

    def _get_component(
        self, component: Component, backbone_i: int) -> Dict[str, Any]:
        """Given Component object, return dict ready to save as node in JSON
        graph file.
        
        Args:
            component (Component): Component to convert to node dict.
            backbone_i (int): Position of valve component is attached to in
                backbone. i.e. first valve, backbone_i == 0.
        
        Returns:
            Dict[str, Any]: Node dict ready for saving in node list in JSON
                graph file.
        """
        # Get position of component and internal ID.
        x, y = self._get_component_position(backbone_i)
        internal_id = self._get_internal_id()
        # Make base dict applicable to filters, separators, rotavaps and
        # reactors.
        cdict = {
            "id": component.id,
            "type": "filter",
            "x": x,
            "y": y,
            "class": TYPE_COMPONENT_DICT[component.component_type],
            "name": component.id,
            "current_volume": 0,
            "max_volume": 0,
            "internalId": internal_id,
            "label": component.id,
        }
        # Update base dict with specific for each component type.
        params = {
            'filter': {
                'dead_volume': DEFAULT_FILTER_DEAD_VOLUME,
                'max_volume': DEFAULT_FILTER_MAX_VOLUME,
                'current_volume': DEFAULT_FILTER_CURRENT_VOLUME,
                'type': 'filter',
            },
            'separator': {
                'max_volume': DEFAULT_SEPARATOR_MAX_VOLUME,
                'current_volume': DEFAULT_SEPARATOR_CURRENT_VOLUME,
                'type': 'separator',
            },
            'reactor': {
                'max_volume': DEFAULT_REACTOR_MAX_VOLUME,
                'current_volume': DEFAULT_REACTOR_CURRENT_VOLUME,
                'type': 'reactor',
            },
            'rotavap': {
                'current_volume': DEFAULT_ROTAVAP_CURRENT_VOLUME,
                'max_volume': DEFAULT_ROTAVAP_MAX_VOLUME,
                'port': PORT,
                'type': 'rotavap',
            }
        }
        for k, v in params[
            COMPONENT_TYPE_DICT[component.component_type]].items():
            cdict[k] = v
        return cdict

    def _get_valve(self, id: str, backbone_i: int) -> Dict[str, Any]:
        """Given id and backbone position, return node dict for valve.
        
        Args:
            id (str): Name of valve i.e. 'valve1'.
            backbone_i (int): Position in backbone, i.e. for the first valve
                backbone_i == 0.
        
        Returns:
            Dict[str, Any]: Node dict ready for saving in node list in JSON
                graph file.
        """
        internal_id = self._get_internal_id()
        x, y = self._get_valve_position(backbone_i)
        return {
            'id': id,
            'type': 'valve',
            'x': x,
            'y': y,
            'class': 'ChemputerValve',
            'name': id,
            'address': IP_ADDRESS,
            'max_volume': DEFAULT_VALVE_MAX_VOLUME,
            'internalId': internal_id,
            'label': id,
        }

    def _get_waste(self, id: str, backbone_i: int) -> Dict[str, Any]:
        """Given id and backbone position, return node dict for waste.
        
        Args:
            id (str): Name of waste i.e. 'waste1'.
            backbone_i (int): Position of attached valve in backbone, i.e. for
                the first valve backbone_i == 0.
        
        Returns:
            Dict[str, Any]: Node dict ready for saving in node list in JSON
                graph file.
        """
        x, y = self._get_waste_position(backbone_i)
        internal_id = self._get_internal_id()
        return {
            'id': id,
            'type': 'waste',
            'x': x,
            'y': y,
            'class': 'ChemputerWaste',
            'name': id,
            'current_volume': DEFAULT_WASTE_CURRENT_VOLUME,
            'max_volume': DEFAULT_WASTE_MAX_VOLUME,
            'internalId': internal_id,
            'label': id,
        }

    def _get_pump(self, id: str, backbone_i: int) -> Dict[str, Any]:
        """Given id and backbone position, return node dict for pump.
        
        Args:
            id (str): Name of pump i.e. 'pump1'.
            backbone_i (int): Position of attached valve in backbone, i.e. for
                the first valve backbone_i == 0.
        
        Returns:
            Dict[str, Any]: Node dict ready for saving in node list in JSON
                graph file.
        """
        x, y = self._get_pump_position(backbone_i)
        internal_id = self._get_internal_id()
        return {
            'id': id,
            'type': 'pump',
            'x': x,
            'y': y,
            'class': 'ChemputerPump',
            'name': id,
            'address': IP_ADDRESS,
            'max_volume': DEFAULT_PUMP_MAX_VOLUME,
            'internalId': internal_id,
            'label': id,
        }

    def _get_flask(
        self,
        id: str,
        chemical: str,
        backbone_i: int,
        flask_i: int
    ) -> Dict[str, Any]:
        """Given id and backbone position, return node dict for flask.
        
        Args:
            id (str): Name of flask i.e. 'flask1'.
            backbone_i (int): Position of attached valve in backbone, i.e. for
                the first valve backbone_i == 0.
        
        Returns:
            Dict[str, Any]: Node dict ready for saving in node list in JSON
                graph file.
        """
        x, y = self._get_flask_position(backbone_i, flask_i)
        internal_id = self._get_internal_id()
        return {
            'id': id,
            'type': 'flask',
            'x': x,
            'y': y,
            'class': 'ChemputerFlask',
            'name': id,
            'chemical': chemical,
            'current_volume': DEFAULT_FLASK_CURRENT_VOLUME,
            'max_volume': DEFAULT_FLASK_MAX_VOLUME,
            'internalId': internal_id,
            'label': id
        }


    #####################
    ### EDGE CREATION ###
    #####################

    def _add_edge(
        self,
        from_node: Dict[str, Any],
        to_node: Dict[str, Any],
        from_port: Union[str, int],
        to_port: Union[str, int],
        both_ways: bool = False
    ) -> None:
        """Add edge to self._edges between from_node (from_port) and to_node
        (to_port). Add reverse edge as well if both_ways is True.
        
        Args:
            from_node (Dict[str, Any]): Node dict for source node.
            to_node (Dict[str, Any]): Node dict for target node.
            from_port (Union[str, int]): Port for source node.
            to_port (Union[str, int]): Port for targe node.
            both_ways (bool): If True, reverse edge will also be added.
        """
        internal_id = self._get_internal_id()
        self._edges.append({
            'id': internal_id,
            'sourceInternal': from_node['internalId'],
            'targetInternal': to_node['internalId'],
            'source': from_node['id'],
            'target': to_node['id'],
            'port': f'({from_port},{to_port})'
        })
        if both_ways:
            internal_id = self._get_internal_id()
            self._edges.append({
                'id': internal_id,
                'sourceInternal': to_node['internalId'],
                'targetInternal': from_node['internalId'],
                'source': to_node['id'],
                'target': from_node['id'],
                'port': f'({to_port},{from_port})'
            })


    ###################
    ### POSITIONING ###
    ###################

    def _get_valve_position(self, backbone_i: int) -> Tuple[int, int]:
        """Get position of valve based on backbone position.
        
        Args:
            backbone_i (int): Index of valve in backbone, i.e. first valve
                backbone_i == 0.
        
        Returns:
            Tuple[int, int]: (x, y) position of valve.
        """
        return (self._gridsize * self._valve_spacing * backbone_i, self._valve_y)

    def _get_pump_position(self, backbone_i: int) -> Tuple[int, int]:
        """Get position of pump based on backbone position.
        
        Args:
            backbone_i (int): Index of attached valve in backbone, i.e.
                first valve backbone_i == 0.
        
        Returns:
            Tuple[int, int]: (x, y) position of pump.
        """
        x, y = self._get_valve_position(backbone_i)
        y += self._pump_y_offset
        return x, y

    def _get_waste_position(self, backbone_i: int) -> Tuple[int, int]:
        """Get position of waste based on backbone position.
        
        Args:
            backbone_i (int): Index of attached valve in backbone, i.e.
                first valve backbone_i == 0.
        
        Returns:
            Tuple[int, int]: (x, y) position of waste.
        """
        x, y = self._get_valve_position(backbone_i)
        x += self._waste_x_offset
        y += self._waste_y_offset
        return (x, y)

    def _get_component_position(self, backbone_i: int) -> Tuple[int, int]:
        """Get position of component (filter, reactor, separator or rotavap)
        based on backbone position.
        
        Args:
            backbone_i (int): Index of attached valve in backbone, i.e.
                first valve backbone_i == 0.
        
        Returns:
            Tuple[int, int]: (x, y) position of component.
        """
        x, y = self._get_valve_position(backbone_i)
        y += self._component_y_offset
        return (x, y)

    def _get_flask_position(
        self, backbone_i: int, flask_i: int) -> Tuple[int, int]:
        """Get position of flask based on backbone position and number of flasks
        already attached to valve.
        
        Args:
            backbone_i (int): Index of attached valve in backbone, i.e.
                first valve backbone_i == 0.
            flask_i (int): Represents how many flasks have already been attached
                to valve at backbone_i. flask_i == 0 means first flask to be
                attached, flask_i == 1 means second flask etc. flask_i > 3 will
                throw an error as only 4 flask positions are specified. This
                should be fine as you'll never be able to attach more than 4
                flasks to a valve if it also has pump/valve/waste connections.
        
        Returns:
            Tuple[int, int]: (x, y) position of waste.
        """
        x, y = self._get_valve_position(backbone_i)
        x += self._flask_offsets[flask_i][0]
        y += self._flask_offsets[flask_i][1]
        return x, y


    ############
    ### MISC ###
    ############

    def _get_internal_id(self) -> None:
        """Increment self._internal_id by 1 and return it. Internal ID is
        a unique ID used by ChemputerApp for nodes/edges.
        
        Returns:
            int: Unique ID to use for internalId attribute of nodes/edges.
        """
        self._internal_id += 1
        return self._internal_id

    def save(self, save_path: str) -> None:
        """Save JSON node link graph to save_path. Must be called after
        generate_graph.
        
        Args:
            save_path (str): Path to save graph JSON file to.
        """
        with open(save_path, 'w') as fileobj:
            json.dump(self.graph, fileobj)
            