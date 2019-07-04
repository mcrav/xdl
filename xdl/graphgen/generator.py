import json
import os
import copy

HERE = os.path.abspath(os.path.dirname(__file__))

def load_template():
    with open(os.path.join(HERE, 'chemputer_std6.json')) as fd:
        return json.load(fd)

def get_n_reagent_flasks(template):
    i = 0
    for node in template['nodes']:
        if (node['type'] == 'flask'
            and not node['name'] == 'buffer_flask'):
            i += 1
    return i

def add_reagents(template, reagents):
    max_n_reagents = get_n_reagent_flasks(template)
    if len(reagents) > max_n_reagents:
        raise(
            ValueError(f'{len(reagents)} in procedure. Not enough space in template for more than {max_n_reagents} reagents'))

    reagents = copy.deepcopy(reagents)
    for node in template['nodes']:
        if (node['type'] == 'flask'
            and not node['name'] == 'buffer_flask'):
            if reagents:
                node['chemical'] = reagents.pop()
            else:
                # Need this so flasks aren't used as buffer flask
                node['chemical'] = 'None'

    return template

def get_graph(reagents):
    return add_reagents(load_template(), reagents)

def save_graph(reagents, save_file):
    with open(save_file, 'w') as fd:
        json.dump(get_graph(reagents), fd)
