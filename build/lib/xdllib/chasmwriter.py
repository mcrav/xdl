from lxml import etree
import tempfile
import subprocess as sub

class Chasm(object):
    """Object for writing ChASM code."""
    
    def __init__(self, steps=[]):
        """Create ChASM code in self.code.
        
        Keyword Arguments:
            steps {list} -- List of Step objects.
        """
        self.code = ''
        if steps:
            self.add_start_main()
            for step in steps:
                self.add_comment(step.name)
                self.add_comment(step.human_readable)
                self.add_step(step, blank_line_before=True)
            self.add_end_main()

    def add_start_main(self):
        """Start main function."""
        self.code += 'MAIN {\n'

    def add_end_main(self):
        """End main function."""
        self.code += '\n}'
        self._indent_main()

    def add_line(self, line):
        """Add code line."""
        self.code += line + ';\n'

    def add_comment(self, comment):
        """Add comment line."""
        self.code += '\n# ' + comment

    def add_inline_comment(self, comment):
        """Add comment without starting new line."""
        self.code = self.code.strip() + f' # {comment}\n'

    def add_step(self, step, blank_line_before=False):
        """Add Step object as ChASM to self.code."""
        if blank_line_before:
            self.code += '\n'
        self.code += step.as_chasm()

    def add_for(self, for_count, steps):
        """Add for loop.
        
        Arguments:
            for_count {int} -- Number of iterations of for loops.
            steps {list} -- list of Step objects to put in for loop.
        """
        self.code += 'FOR(' + str(for_count) + ') {\n'
        for step in steps:
            self.add_step(step)
        self.code += '}\n'

    def _indent_main(self, indentation='    '):
        """Indent main function."""
        indented_chasm = ''
        if self.code.count('{') == self.code.count('}'):
            main = False
            open_count = 0
            closed_count = 0
            for line in self.code.split('\n'):
                if '}' in line:
                    closed_count += 1
                    if open_count > 0 and closed_count == open_count:
                        indented_chasm += line
                        break
                if main:
                    line = ((open_count - closed_count) * indentation) + line
                if '{' in line:
                    open_count += 1
                if line.startswith('MAIN'):
                    main = True
                indented_chasm += line + '\n'
        self.code = indented_chasm

    # def simulate(self, graphml_file):
    #     chasm_file = tempfile.TemporaryFile()
    #     chasm_file.write(self.code)
    #     chempiler = Chempiler(graphml_file, chasm_file, crash_dump=False, simulation=True)
    #     chempiler.run_platform()
    #     chasm_file.close()