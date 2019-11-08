from xdl.xdl_controller import make_xdl_controller
from chempiler import Chempiler
import ChemputerAPI

chempiler = Chempiler(
    graph_file='/home/group/ChemputerExperiments/orgsyn_v87p0016/orgsyn_v87p0016_graph.json',
    device_modules=[ChemputerAPI],
    simulation=True,
    output_dir='/home/group/Desktop',
    experiment_code='test_live_controller',
)
x = make_xdl_controller()(chempiler)
print(dir(x))
