from xdllib import XDL
import os
from xdllib import XDLSyntaxValidator
from xdllib.namespace import STEP_OBJ_DICT
from xdllib import XDLGenerator

HERE = os.path.dirname(os.path.realpath(__file__))

def run_tests():
    return [
        ('Syntax Validation', test_syntax_validation()),
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

def test_syntax_validation():
    """
    Test XDLSyntaxValidator works.
    Return fraction between 0-1 indicating pass rate.
    """
    files = os.listdir('test_files/syntax_validation')
    passed_count = 0
    for f in files:
        with open(os.path.join('test_files/syntax_validation', f), 'r') as fileobj:
            validator = XDLSyntaxValidator(fileobj.read(), validate=False)

        if f.startswith('has_three_tags'):
            res = validator.has_three_base_tags()
        elif f.startswith('all_reagents_declared'):
            res = validator.all_reagents_declared()
        elif f.startswith('all_vessels_declared'):
            res = validator.all_vessels_declared()
        elif f.startswith('steps_in_namespace'):
            res = validator.steps_in_namespace()
        elif f.startswith('components_in_namespace'):
            res = validator.hardware_in_namespace()
        elif f.startswith('check_quantities'):
            res = validator.check_quantities()
        # Unimplemented cos is unfinished
        elif f.startswith('check_step_attributes'):
            res = validator.check_step_attributes()
            
        if (res and 'pos' in f) or (not res and 'neg' in f):
            passed_count += 1
        else:
            print(f'SYNTAX VALIDATION FAILED: {f}')
    return passed_count / len(files)

def test_safety_check():
    pass

def main():
    full_test()

if __name__ == '__main__':
    main()