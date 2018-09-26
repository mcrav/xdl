import os

def get_steps_info():
    HERE = os.path.dirname(os.path.realpath(__file__))
    step_folder = os.path.join(HERE, 'xdllib/steps')
    step_files = [os.path.join(step_folder, f) 
                    for f in os.listdir(step_folder) 
                    if f.endswith('.py') and not f.startswith('__')]
    steps_info = []                    
    for f in step_files:
        steps_info.extend(read_steps_file(f))
    return steps_info

def read_steps_file(file_path):
    steps_info = []
    with open(file_path, 'r') as fileobj:
        lines = fileobj.readlines()
    step_info = {}
    properties = False
    for line in lines:
        if line.startswith('class'):
            if step_info:
                steps_info.append(step_info)
                step_info = {}
            step_info['name'] = line.replace('class ', '').split('(')[0]
            continue
        elif line.strip().startswith('self.properties ='):
            properties = True
            continue
        elif properties:
            if line.strip().startswith('}'):
                properties = False
                continue
            else:
                print(step_info['name'])
                step_info.setdefault('properties', []).append(line.split(':')[1].strip().replace(',', ''))
    steps_info.append(step_info)
    return steps_info

def make_steps_doc():
    steps = get_steps_info()
    md = '# Steps\n\n'
    for step in steps:
        md += f"## {step['name']}\n"
        md += f'### Attributes\n'
        for prop in step['properties']:
            md += f'* {prop}\n'

    with open('docs/steps.md', 'w') as fileobj:
        fileobj.write(md)

def main():
    make_steps_doc()

if __name__ == '__main__':
    main()