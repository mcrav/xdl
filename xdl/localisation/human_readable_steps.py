import os

def load_human_readable_steps():
    here = os.path.abspath(os.path.dirname(__file__))
    human_readable_steps = {}

    # Need to specify encoding='utf-8' otherwise it throws an error on Windows
    with open(os.path.join(here, 'xdl_translations.txt'),
              encoding='utf-8') as fileobj:
        lines = [line.strip() for line in fileobj.readlines() if line]

    current_step = None
    for i in range(len(lines)):

        if lines[i].startswith('en'):
            current_step = lines[i-1]
            human_readable_steps[current_step] = {}
            human_readable_steps[current_step]['en'] = lines[i+1]

        elif len(lines[i]) == 2:
            human_readable_steps[current_step][lines[i]] = lines[i+1]

    return human_readable_steps

HUMAN_READABLE_STEPS = load_human_readable_steps()
