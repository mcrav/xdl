from distutils.core import setup
from dev_utils import add_getters

add_getters('xdllib/steps/steps_xdl.py')
add_getters('xdllib/steps/steps_chasm.py')
# add_getters('xdllib/reagents.py')

setup(name='xdllib',
      version='0.2',
      description='XDL library',
      author='Matthew Craven',
      author_email='matthew.craven@glasgow.ac.uk',
      packages=['xdllib', 'xdllib.steps'],
     )