from xdl import XDL
import os
from syntax_validation_tests import test_syntax_validation
from executor_tests import test_xdl_executor

HERE = os.path.dirname(os.path.realpath(__file__))

def run_tests():
    return [
        # ('Syntax Validation', test_syntax_validation()),
        ('XDLExecutor', test_xdl_executor())
    ]

def full_test():
    """Run all tests and print results in nice, neat table."""
    test_res = run_tests()
    print('\n')
    print(' |' + '–'*37 + '|')
    print(f' |{"Test":25} | {"Score"}    |')
    print(' |' + '–'*37 + '|')
    for test_name, res in test_res:
        res_percent = f'{res*100:.2f} %'
        print(f' |{test_name:<25} | {res_percent:<8} |')
    print(' |' + '–'*37 + '|')
    print('\n')

def simulate_all_files():
    files = os.listdir('test_files')
    for f in files:
        if f.lower().endswith('graphml'):
            graphml_file = os.path.join('test_files', f)
    for f in files:
        if f.endswith('xdl'):
            xdlobj = XDL(xdl_file=os.path.join('test_files', f))
            xdlobj.simulate(graphml_file)


def test_safety_check():
    pass

def main():
    full_test()

if __name__ == '__main__':
    main()