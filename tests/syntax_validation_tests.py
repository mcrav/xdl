from xdl.readwrite.syntax_validation import XDLSyntaxValidator
import os

HERE = os.path.abspath(os.path.dirname(__file__))

def test_syntax_validation():
    """
    Test XDLSyntaxValidator works.
    Return fraction between 0-1 indicating pass rate.
    """
    folder = os.path.join(HERE, 'test_files/syntax_validation')
    files = os.listdir(folder)
    passed_count = 0
    for f in files:
        print('Validating file {0}\n---------------'.format(f))
        with open(os.path.join(folder, f), 'r') as fileobj:
            validator = XDLSyntaxValidator(fileobj.read())
            
        if ((validator.valid and 'pos' in f) 
            or (not validator.valid and 'neg' in f)):
            passed_count += 1
        else:
            print(f'SYNTAX VALIDATION FAILED: {f}\n\n')
    return passed_count / len(files)