import os
import shutil

HERE = os.path.abspath(os.path.dirname(__file__))
STEPS_FOLDER = os.path.join(os.path.dirname(HERE), 'xdl', 'steps')

TARGET_FOLDER = os.path.join(HERE, 'reference', 'steps')

if os.path.isdir(TARGET_FOLDER):
    shutil.rmtree(TARGET_FOLDER)
os.makedirs(TARGET_FOLDER)

for item in ['steps_base', 'steps_utility', 'steps_synthesis']:
    os.makedirs(os.path.join(TARGET_FOLDER, item))
    step_files = [
        f
        for f in os.listdir(os.path.join(STEPS_FOLDER, item))
        if not f.startswith('_')
    ]
    len_module_name = len('xdl.steps.') + len(item)
    s = ('=' * len_module_name) + '\n'
    s += 'xdl.steps.' + item + '\n'
    s += ('=' * len_module_name) + '\n'
    s += '\n'
    s += '.. toctree::\n'
    s += '\n'
    for f in step_files:
        s += f'   {f[:-3]}\n'
        with open(
            os.path.join(TARGET_FOLDER, item, f[:-3] + '.rst'), 'w'
        ) as fileobj:
            len_module_name = len('xdl.steps.') + len(item) + len(f'.{f[:-3]})')
            fs = ('=' * len_module_name) + '\n'
            fs += f'xdl.steps.{item}.{f[:-3]}\n'
            fs += ('=' * len_module_name) + '\n'
            fs += '\n'
            fs += f'.. automodule:: xdl.steps.{item}.{f[:-3]}\n'
            fs += '    :members:\n'
            fs += '\n'
            fileobj.write(fs)
    s += '\n'

    with open(os.path.join(TARGET_FOLDER, item, 'index.rst'), 'w') as fileobj:
        fileobj.write(s)

with open(os.path.join(TARGET_FOLDER, 'index.rst'), 'w') as fileobj:
    fileobj.write('=========\nxdl.steps\n=========\n.. toctree::\n\n   \
steps_synthesis/index\n   steps_utility/index\n   steps_base/index\n\n')
