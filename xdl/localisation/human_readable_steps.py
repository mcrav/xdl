import os

HERE = os.path.abspath(os.path.dirname(__file__))

def read_localisation_file(f):
    with open(f) as fd:
        lines = [line.strip() for line in fd.readlines() if line.strip()]
    step_localisations = []
    current = {}
    language = None
    for line in lines:
        if line.startswith('!'):
            if current:
                step_localisations.append(current)
            current = {'name': line[1:]}

        elif line.startswith('#'):
            continue

        elif len(line) == 2:
            language = line

        else:
            if language:
                current[language] = line
            else:
                raise ValueError(f'Language is none ({current}) {f}')

    if current:
        step_localisations.append(current)

    return step_localisations

def load_localisations():
    steps_utility = os.path.join(HERE, 'chemputer', 'steps_utility')
    steps_synthesis = os.path.join(HERE, 'chemputer', 'steps_synthesis')

    localisations = []
    for folder in [steps_utility, steps_synthesis]:
        for f in os.listdir(folder):
            f_path = os.path.join(folder, f)
            localisations.extend(read_localisation_file(f_path))

    localisations.extend(
        read_localisation_file(os.path.join(HERE, 'chemputer', 'unimplemented_steps.txt')))
    localisations.extend(
        read_localisation_file(os.path.join(HERE, 'special_steps.txt')))

    localisation_dict = {}
    for localisation in localisations:
        name = localisation['name']
        del localisation['name']
        localisation_dict[name] = localisation
    return localisation_dict

HUMAN_READABLE_STEPS = load_localisations()
