# XDL

This package provides code relevant to the chemical description language (XDL) standard. It provides a XDL object which can be instantiated from a XDL file or from appropriate objects, then execute itself or write itself to a file.


### Use in Python script

```
from xdl import XDL
from chempiler import Chempiler
import ChemputerAPI

x = XDL('/path/to/file.xdl')

graph = x.graph()
x.prepare_for_execution(graph)

chempiler = Chempiler(
    experiment_code='exp',  
    output_dir='/path/to/exp_dir',  
    simulation=True,  
    graph_file=graph_file,  
    device_modules=[ChemputerAPI])

x = XDL('/path/to/file.xdlexe')

x.execute(chempiler)
```