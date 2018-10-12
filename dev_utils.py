import os
import re
import argparse
from xdllib.constants import *

def print_step_obj_dict():
    s = '{\n'
    regex = re.compile(r'class (.*?)\(')
    for f in os.listdir(os.getcwd()):
        if f.startswith('synclasses') or f.startswith('chasm_classes.py'):
            with open(f, 'r') as fileobj:
                for line in fileobj.readlines():
                    if line.startswith('class'):
                        class_name = regex.findall(line)[0]
                        s += f"    '{class_name}': {class_name},\n"
    s += '}'
    print(s)
    
def add_literal_chempiler_code(steps_chasm_file):
    with open(steps_chasm_file, 'r') as fileobj:
        lines = fileobj.readlines()
    new_lines = []
    execute = False
    code = []
    for line in lines:
        if execute:
            if not line.strip() or line.strip().startswith('return'):
                execute = False
                new_lines.append("        self.literal_code = f'" + ' '.join([
                    re.sub(r'(self.[a-zA-Z_]+)', '{\g<1>}', line.strip()) for line in code[1:]
                    ]) + "'")
                new_lines.append('')
                new_lines.extend(code)
                new_lines.append(line.rstrip())
                code = []
                continue
            else:
                code.append(line.rstrip())
        if line.strip().startswith('def execute'):
            execute = True
            code.append(line.rstrip())
        if not execute:
            if line.strip().startswith('self.literal_code'):
                new_lines.pop()
            else:
                new_lines.append(line.rstrip())
    with open(steps_chasm_file, 'w') as fileobj:
        fileobj.write('\n'.join(new_lines))

def add_getters(steps_file):
    """
    Add getter methods to given steps_file.
    Getter will be added for everything in self.properties dict.
    """
    with open(steps_file, 'r') as fileobj:
        lines = fileobj.readlines()
    new_lines = []
    props = []
    read_props = False
    indent = '    '
    getter = False
    for line in lines:
        if line.startswith('class'):
            if props:
                for prop in props:
                    new_lines.append(f'{indent}@property')
                    new_lines.append(f'{indent}def {prop}(self):')
                    new_lines.append(f"{indent*2}return self.properties['{prop}']\n")

                    new_lines.append(f'{indent}@{prop}.setter')
                    new_lines.append(f'{indent}def {prop}(self, val):')
                    new_lines.append(f"{indent*2}self.properties['{prop}'] = val")
                    new_lines.append(f'{indent*2}self.update()\n')
                props = []

        if '}' in line:
            read_props = False
            
        if read_props:
            props.append(re.search(r': ([a-zA-Z0-9_]+)(,)?(\n|( #))', line).group(1))

        if 'self.properties = {' in line:
            read_props = True

        if not line.strip():
            if getter:
                getter = False
                continue

        if '@' in line:
            getter = True

        if not getter:
            new_lines.append(line.rstrip())
    
    for prop in props:
        new_lines.append(f'{indent}@property')
        new_lines.append(f'{indent}def {prop}(self):')
        new_lines.append(f"{indent*2}return self.properties['{prop}']\n")

        new_lines.append(f'{indent}@{prop}.setter')
        new_lines.append(f'{indent}def {prop}(self, val):')
        new_lines.append(f"{indent*2}self.properties['{prop}'] = val")
        new_lines.append(f'{indent*2}self.update()\n')
        
    with open(steps_file, 'w') as fileobj:
        fileobj.write('\n'.join(new_lines))
        

class StepClassCodeGenerator(object):
    """Generate Step class code from ChASM docs markdown.
    """
    def __init__(self, mkdown):
        self.mkdown = mkdown
        self.lines = mkdown.split('\n')
        self.get_class_code()

    def get_class_code(self):
        self.get_class_name()
        self.get_class_properties()
        self.get_class_docstring()
        self.get_property_definitions()

        self.class_code = self.write_class_definition()
        self.class_code += self.write_init()
        self.class_code += self.write_as_chasm()

    def get_class_name(self):
        self.raw_name = self.lines[0].split('## ')[1].split(' (')[0]
        name_list = self.raw_name.split('_')
        self.class_name = ''.join(s.title() for s in name_list)

    def get_class_properties(self):
        self.class_properties = [item for item in 
            self.lines[0].split('(')[1].split(')')[0].replace(' ','').replace('{','').replace('}','').split(',')
        if item]

    def get_class_docstring(self):
        self.class_docstring = self.lines[2].replace('*', '')
        self.class_docstring = self.format_ds(self.class_docstring)

    def get_property_definitions(self):
        self.property_definitions = {}
        for line in self.lines[4:]:
            if line.strip():
                prop = line.split('}**')[0].split('{')[1]
                definition = line.split('}** ')[1]
                definition = definition.replace('is the ','')
                definition = definition[0].upper() + definition[1:]
                self.property_definitions[prop] = definition
        
    def write_class_definition(self):
        return f'class {self.class_name}(Step):\n{self.write_class_docstring()}\n'

    def write_init(self):
        indent = '    '
        code = indent + 'def __init__(self, '
        for prop in self.class_properties:
            code += prop + '=None, '
        code += "comment=''):\n"
        code += self.write_init_docstring()
        code += indent*2 + f"self.name = '{self.class_name}'\n"
        code += indent*2 + 'self.properties = ' + '{\n'
        for prop in self.class_properties:
            code += indent*3 + f"'{prop}': {prop},\n"
        code += indent*3 + "'comment': comment\n"
        code += indent*2 + "}\n\n"
        return code

    def write_as_chasm(self):
        indent = '    '
        code = indent + 'def as_chasm(self):\n' + self.write_as_chasm_docstring() + indent*2 + 'chasm = self.get_chasm_stub()\n'
        code += indent*2 + f'chasm.add_line(f"S {self.raw_name}('
        for prop in self.class_properties:
            code += '{' + f"self.properties['{prop}']" + '}, '
        if len(self.class_properties) > 0:
            code = code[:-2] 
        code += ')")\n'
        code += indent*2 + 'return chasm.code'
        return code

    def write_class_docstring(self):
        return '    """\n    ' + self.class_docstring + '\n    """'

    def write_init_docstring(self):
        indent = '    '
        ds = indent*2 + '"""\n'
        for prop, definition in self.property_definitions.items():
            ds += f'{indent*2}{prop} -- {definition}\n'
        ds += indent*2 + '"""\n'
        return ds 

    def write_as_chasm_docstring(self):
        indent = '    '
        ds = indent*2 + '"""Return step as ChASM code (str)."""\n'
        return ds

    def format_ds(self, ds):
        # print('---')
        # print(ds)
        split_ds = ds.split('\n')
        # print(split_ds)
        if len(split_ds[-1]) > 85:
            i = 85
            while split_ds[-1][i] != ' ':
                i -= 1
            split_ds[-1] = split_ds[-1][:i] + '\n    ' + split_ds[-1][i+1:]
            ds = '\n'.join(split_ds)
            ds = self.format_ds(ds)
        return ds

def add_default_vals(code):
    code = code.replace('move_speed=None', f'move_speed={DEFAULT_MOVE_SPEED}')
    code = code.replace('aspiration_speed=None', f'aspiration_speed={DEFAULT_ASPIRATION_SPEED}')
    code = code.replace('dispense_speed=None', f'dispense_speed={DEFAULT_DISPENSE_SPEED}')
    return code


def get_all_chasm_class_code(mkdown_file, save_file):
    with open(mkdown_file, 'r') as fileobj:
        mkdown = fileobj.read()
    command_mkdowns = []
    i = 0
    command = False
    command_lines = []
    for line in mkdown.split('\n'):
        if command:
            command_lines.append(line)
            if not line.strip():
                i += 1
                if i == 3:
                    command = False
                    i = 0
                    command_mkdowns.append('\n'.join(command_lines))
                    command_lines = []
        if line.startswith('###'):
            command = True
            command_lines.append(line)
    code = '''from chasmwriter import Chasm\nfrom constants import *\nfrom synclasses_generic import Step\n\n'''
    for mkdown in command_mkdowns:
   
        codeGenerator = StepClassCodeGenerator(mkdown)
        code += codeGenerator.class_code + '\n\n'
    code = add_default_vals(code)
    with open(save_file, 'w') as fileobj:
        fileobj.write(code)
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--step_obj_dict', help='Print step obj dict', action='store_true')
    parser.add_argument('--chasm_classes', help='Write chasm_classes.py', action='store_true')
    parser.add_argument('--getters', help='Add getters to classes', action='store_true')
    args = parser.parse_args()

    if args.chasm_classes:
        get_all_chasm_class_code('stuff/chasm_commands.md', 'chasm_classes.py')

    elif args.step_obj_dict:
        print_step_obj_dict()

    elif args.getters:
        add_getters('/home/group/xdllib/xdllib/steps_chasm.py')
        add_getters('/home/group/xdllib/xdllib/steps_xdl.py')

if __name__ == '__main__':
    main()