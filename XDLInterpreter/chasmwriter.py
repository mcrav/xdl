import abc
from lxml import etree

class Reaction(object):
    
    def __init__(self, reaxys_obj):
        self.steps = []

    def as_chasm(self):
        return Chasm(self.steps).code
        
    def as_xdl(self, as_str=False):
        reaction = etree.Element('reaction')
        for step in self.steps:
            reaction.append(step.as_xdl())
        tree = etree.ElementTree(reaction)
        if as_str:
            return etree.dump(reaction)
        else:
            return tree
        
    def save_xdl(self, save_path):
        tree = self.as_xdl()
        tree.write(save_path, pretty_print=True)

    def shopping_list(self):
        pass



class Chasm(object):
    
    def __init__(self, steps=[]):
        self._code = ''
        if steps:
            self.add_start_main()
            for step in steps:
                self.add_step(step, blank_line_before=True)
            self.add_end_main()

    def add_start_main(self):
        self._code += 'MAIN {\n'

    def add_end_main(self):
        self._code += '\n}'
        self._indent_main()

    def add_line(self, line):
        self._code += line + ';\n'

    def add_comment(self, comment):
        self._code += '# ' + comment + '\n'

    def add_step(self, step, blank_line_before=False):
        if blank_line_before:
            self._code += '\n'
        self._code += step.as_chasm()

    def add_for(self, for_count, steps):
        self._code += 'FOR(' + str(for_count) + ') {\n'
        for step in steps:
            self.add_step(step)
        self._code += '}\n'

    def _indent_main(self, indentation='    '):
        indented_chasm = ''
        if self._code.count('{') == self._code.count('}'):
            main = False
            open_count = 0
            closed_count = 0
            for line in self._code.split('\n'):
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
    
    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, new_code):
        self._code = new_code

    def save(self, file_path):
        with open(file_path, 'w') as fileobj:
            fileobj.write(self._code)



def main():
    from stuff import rufinamide_steps
    reaction = Reaction('')
    reaction.steps = rufinamide_steps
    reaction.as_xdl()
    reaction.save_xdl('/home/group/ReaxysChemputerInterface/stuff/rufinamide.xdl')

    chasm = Chasm(rufinamide_steps)
    chasm.save('/home/group/ReaxysChemputerInterface/stuff/rufinamide.chasm')

    # print(React(reactor='reactor', time=12*60*60, temp=75, comment='Heat to 75C and wait for 12h').as_xdl())

if __name__ == '__main__':
    main()