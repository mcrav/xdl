import os

from xdl import XDL

HERE = os.path.abspath(os.path.dirname(__file__))

def test_prepare_for_execution():
    folder = os.path.join(HERE, 'prepare_for_execution_files')
    files = [os.path.join(folder, f) for f in sorted(os.listdir(folder))]
    i = 0
    while i + 1 < len(files):
        print(files[i])
        x = XDL(files[i])
        x.prepare_for_execution(files[i+1]) 
        i += 2

test_prepare_for_execution()