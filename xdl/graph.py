import networkx

def graphml_hardware_from_file(graphml_file):
    """Return Hardware object given graphML_file path."""
    components = []
    with open(graphml_file, 'r') as fileobj:
        soup = bs4.BeautifulSoup(fileobj, 'xml')
    dead_volume_id = soup.find('key', {'attr.name': 'dead_volume'})['id']
    max_volume_id = soup.find('key', {'attr.name': 'max_volume'})['id']
    nodes = soup.findAll('node', {'yfiles.foldertype': ''})
    for node in nodes:
        component = None
        node_label = node.find("y:NodeLabel").text.strip()
        if node_label.startswith('reactor'):
            component = Reactor(cid=node_label)

        elif node_label.startswith(('filter')):
            if 'bottom' in node_label:
                dead_volume = node.find('data', {'key': dead_volume_id},) #, {'key': 'd13'})d
                component = FilterFlask(cid=node_label, dead_volume=float(dead_volume.string))

        elif node_label.startswith(('separator', 'flask_separator')):
            component = SeparatingFunnel(cid=node_label)

        elif node_label.startswith('flask'):
            component = Flask(cid=node_label)

        elif node_label.startswith('waste'):
            component = Waste(cid=node_label)
        if component:
            component.max_volume = float(node.find('data', {'key': max_volume_id}).string)
            components.append(component)
    return Hardware(components)

def _get_graph(self, graphml_file=None, json_file=None, json_data=None):
    graph = None
    if graphml_file != None:
        graph = nx.MultiDiGraph(nx.read_graphml(graphml_file))
    elif json_file:
        with open(json_file) as fileobj:
            json_data = json.load(fileobj)
            graph = nx.readwrite.json_graph.node_link_graph(json_data, directed=True)
    elif json_data:
        graph = nx.readwrite.json_graph.node_link_graph(json_data, directed=True)
    return graph

def hardware_from_graph(graphml_file=None, json_file=None, json_data=None):
    components = []
    graph = self._get_graph(graphml_file=graphml_file, json_file=json_file, json_data=json_data)
    for node in graph.nodes():
        components.append(self._component_from_node(graph.node[node]))
    return Hardware(components)