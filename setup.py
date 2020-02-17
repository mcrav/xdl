from distutils.core import setup
from setuptools import find_packages

setup(
    name='xdl',
    version='0.3.0',
    description='Package for working with XDL (chemical descriptive language).',
    author='Matthew Craven',
    author_email='matthew.craven@glasgow.ac.uk',
    packages=find_packages(),
    package_data={
        'xdl': [
            'localisation/special_steps.txt',
            'localisation/chemputer/steps_utility/heatchill.txt',
            'localisation/chemputer/steps_utility/filter_dead_volume.txt',
            'localisation/chemputer/steps_utility/vacuum.txt',
            'localisation/chemputer/steps_utility/pneumatic_controller.txt',
            'localisation/chemputer/steps_utility/rotavap.txt',
            'localisation/chemputer/steps_utility/cleaning.txt',
            'localisation/chemputer/steps_utility/liquid_handling.txt',
            'localisation/chemputer/steps_utility/evacuate.txt',
            'localisation/chemputer/steps_utility/general.txt',
            'localisation/chemputer/steps_utility/shutdown.txt',
            'localisation/chemputer/steps_utility/stirring.txt',
            'localisation/chemputer/steps_synthesis/heatchill.txt',
            'localisation/chemputer/steps_synthesis/clean_vessel.txt',
            'localisation/chemputer/steps_synthesis/add.txt',
            'localisation/chemputer/steps_synthesis/separate.txt',
            'localisation/chemputer/steps_synthesis/dry.txt',
            'localisation/chemputer/steps_synthesis/dissolve.txt',
            'localisation/chemputer/steps_synthesis/filter_through.txt',
            'localisation/chemputer/steps_synthesis/evaporate.txt',
            'localisation/chemputer/steps_synthesis/wash_solid.txt',
            'localisation/chemputer/steps_synthesis/filter.txt',
            'localisation/chemputer/steps_synthesis/add_corrosive.txt',
            'localisation/chemputer/steps_synthesis/recrystallize.txt',
            'localisation/chemputer/steps_synthesis/precipitate.txt',
            'localisation/chemputer/steps_synthesis/column.txt',
            'localisation/chemputer/unimplemented_steps.txt',

            'graphgen_deprecated/chemputer_std6.json',
            'graphgen/template.json'
        ]
    },
    include_package_data=True,
    install_requires=[
        'lxml>=4',
        'networkx>=2',
        'appdirs>=1',
        'termcolor>=1',
    ]
)
