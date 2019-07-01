from distutils.core import setup
from setuptools import find_packages

setup(name='xdl',
      version='0.1.0',
      description='Package for working with XDL (chemical descriptive language).',
      author='Matthew Craven',
      author_email='matthew.craven@glasgow.ac.uk',
      packages=find_packages(),
      package_data={'xdl': ['localisation/xdl_translations.txt']},
      include_package_data=True,
)
