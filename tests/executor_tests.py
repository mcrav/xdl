from xdl import XDL
from xdl.execution import XDLExecutor
import os
from chempiler import Chempiler
import SerialLabware
import ChemputerAPI

HERE = os.path.abspath(os.path.dirname(__file__))

def test_xdl_executor():
    folder = os.path.join(HERE, 'test_files/run_scripts')
    graphml_file = os.path.join(HERE, 'test_files/run_scripts/graph.graphml')
    json_graph_file = os.path.join(HERE, 'test_files/run_scripts/graph.json')
    output_dir = os.path.join(HERE, 'chempiler_output')
    passed_count = 0
    for f in os.listdir(folder):
        f_path = os.path.join(folder, f)
        if f_path.endswith('.xdl'):
            xdl = XDL(f_path)
            xdlExecutor = XDLExecutor(xdl)
            # xdlExecutor.prepare_for_execution(
            #     graphml_file=graphml_file)
            # chempiler = Chempiler(
            #     experiment_code="test_exp", output_dir=output_dir, 
            #     simulation=True, graphml_file=graphml_file, device_modules=[
            #         SerialLabware, ChemputerAPI
            #     ])
            xdlExecutor.prepare_for_execution(
                json_graph_file=json_graph_file)
            chempiler = Chempiler(
                experiment_code="test_exp", output_dir=output_dir, 
                simulation=True, json_graph_file=json_graph_file, device_modules=[
                    SerialLabware, ChemputerAPI
                ])
            xdlExecutor.execute(chempiler)
            passed_count += 1
    return passed_count / len(os.listdir(folder))