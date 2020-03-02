from distutils.core import setup
from setuptools import find_packages

setup(
    name='xdl',
    version='0.3.1',
    description='Package for working with XDL (chemical descriptive language).',
    author='Matthew Craven',
    author_email='matthew.craven@glasgow.ac.uk',
    packages=find_packages(),
    package_data={
        'xdl': [
            'platforms/chemputer/localisation/special_steps.txt',
            'platforms/chemputer/localisation/steps_utility/heatchill.txt',
            'platforms/chemputer/localisation/steps_utility/filter_dead_volume\
.txt',
            'platforms/chemputer/localisation/steps_utility/vacuum.txt',
            'platforms/chemputer/localisation/steps_utility/\
pneumatic_controller.txt',
            'platforms/chemputer/localisation/steps_utility/rotavap.txt',
            'platforms/chemputer/localisation/steps_utility/cleaning.txt',
            'platforms/chemputer/localisation/steps_utility/liquid_handling\
.txt',
            'platforms/chemputer/localisation/steps_utility/evacuate.txt',
            'platforms/chemputer/localisation/steps_utility/general.txt',
            'platforms/chemputer/localisation/steps_utility/shutdown.txt',
            'platforms/chemputer/localisation/steps_utility/stirring.txt',
            'platforms/chemputer/localisation/steps_utility/modular_wheel.txt',
            'platforms/chemputer/localisation/steps_synthesis/heatchill.txt',
            'platforms/chemputer/localisation/steps_synthesis/clean_vessel.txt',
            'platforms/chemputer/localisation/steps_synthesis/add.txt',
            'platforms/chemputer/localisation/steps_synthesis/separate.txt',
            'platforms/chemputer/localisation/steps_synthesis/dry.txt',
            'platforms/chemputer/localisation/steps_synthesis/dissolve.txt',
            'platforms/chemputer/localisation/steps_synthesis/filter_through\
.txt',
            'platforms/chemputer/localisation/steps_synthesis/evaporate.txt',
            'platforms/chemputer/localisation/steps_synthesis/wash_solid.txt',
            'platforms/chemputer/localisation/steps_synthesis/filter.txt',
            'platforms/chemputer/localisation/steps_synthesis/add_corrosive\
.txt',
            'platforms/chemputer/localisation/steps_synthesis/recrystallize\
.txt',
            'platforms/chemputer/localisation/steps_synthesis/precipitate.txt',
            'platforms/chemputer/localisation/steps_synthesis/column.txt',
            'platforms/chemputer/localisation/steps_base/general.txt',
            'platforms/chemputer/localisation/unimplemented_steps.txt',

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
