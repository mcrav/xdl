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
            'graphgen_deprecated/chemputer_std6.json'
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
