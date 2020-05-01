import sys

class XDLError(Exception):
    pass

class XDLCompilationError(XDLError):
    pass

class IllegalPortError(XDLError):
    pass

class XDLValueError(XDLError):
    pass

# Graph
class XDLGraphError(XDLError):
    pass

class XDLGraphInvalidFileTypeError(XDLGraphError):
    def __init__(self, graph_file):
        self.graph_file = graph_file

    def __str__(self):
        return f'Graph file "{self.graph_file}" has any invalid file type.\
 Valid file types: .json, .graphml'

class XDLGraphFileNotFoundError(XDLGraphError):
    def __init__(self, graph_file):
        self.graph_file = graph_file

    def __str__(self):
        return f'Graph file "{self.graph_file}" does not exist.'

class XDLGraphTypeError(XDLGraphError):
    def __init__(self, graph_file):
        self.graph_file = graph_file

    def __str__(self):
        return f'{type(self.graph_file)} is not a valid type to load a graph\
 Accepted objects: Paths to .json or .graphml graph files. Contents of .json\
 graph as dict. Networkx MultiDiGraph.'

class XDLVesselNotDeclaredError(XDLError):
    def __init__(self, vessel):
        self.vessel = vessel

    def __str__(self):
        return f'"{self.vessel}" used as vessel in procedure but not declared\
 in <Hardware> section of XDL'

class XDLReagentNotDeclaredError(XDLError):
    def __init__(self, reagent):
        self.reagent = reagent

    def __str__(self):
        return f'"{self.reagent}" used as reagent in procedure but not declared\
 in <Reagents> section of XDL'
