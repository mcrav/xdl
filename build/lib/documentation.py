import os

def get_steps_info():
    """Read steps py files and get info about Step subclasses."""
    HERE = os.path.dirname(os.path.realpath(__file__))
    step_folder = os.path.join(HERE, 'xdllib/steps')
    step_files = [os.path.join(step_folder, f) 
                    for f in os.listdir(step_folder) 
                    if f.endswith('.py') and not f.startswith('__')]
    steps_info = []                    
    for f in step_files:
        steps_info.extend(read_steps_file(f))
    return sorted(steps_info, key=lambda step: step['name'])

def read_steps_file(file_path):
    """Read step info from given steps py file."""
    steps_info = []
    with open(file_path, 'r') as fileobj:
        lines = fileobj.readlines()
    step_info = {}
    properties = False
    docstring = False
    for line in lines:
        if line.startswith('class'):
            if step_info:
                steps_info.append(step_info)
                step_info = {}
            print(line)
            continue
        elif line.strip().startswith('"""'):
            docstring = not docstring
            if docstring:
                step_info['description'] = line.strip().replace('"""', '')
            continue
        elif docstring:
            if 'kwargs' in step_info and line.strip():
                step_info['kwargs'] = line.strip()
            if line.strip().startswith('Keyword'):
                step_info['kwargs'] = []
            # Need to get description and args out of docstrings 

        elif line.strip().startswith('self.name'):
            step_info['name'] = line.split('=')[1].strip().replace("'",'')
            print(step_info['name'])

        elif properties:
            if line.strip().startswith('}'):
                properties = False
                continue
            else:
                step_info.setdefault('properties', []).append((line.split("'")[1], int('compulsory' in line)))
    steps_info.append(step_info)
    return steps_info

def make_steps_doc():
    """Make docs/steps.md."""
    steps = get_steps_info()
    md = '# Steps\n\n'
    for step in steps:
        print(step)
        md += f"## {step['name']}\n"
        md += f"{step['description']}\n"
        md += f'### Attributes\n'
        for prop in step['kwargs']:
            md += f'* {prop}'
            # if not prop:
            #     md += ' (optional)'
            md += '\n'
        md += '\n\n'

    with open('docs/steps.md', 'w') as fileobj:
        fileobj.write(md)

def main():
    make_steps_doc()

if __name__ == '__main__':
    main()