from distutils.core import setup
from dev_utils import add_getters

add_getters('xdllib/steps/steps_xdl.py')
add_getters('xdllib/steps/steps_chasm.py')

setup(name='xdllib',
      version='0.1',
      description='XDL library',
      author='Matthew Craven',
      author_email='matthew.craven@glasgow.ac.uk',
      packages=['xdllib', ''],
     )