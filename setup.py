from distutils.core import setup
from dev_utils import add_getters, add_literal_chempiler_code

add_literal_chempiler_code('xdl/steps/steps_chasm.py')

setup(name='xdllib',
      version='0.2',
      description='XDL library',
      author='Matthew Craven',
      author_email='matthew.craven@glasgow.ac.uk',
      packages=['xdl', 'xdl.steps'],
     )