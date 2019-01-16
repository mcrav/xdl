from distutils.core import setup
from dev_utils import add_getters, add_literal_chempiler_code

add_literal_chempiler_code('xdl/steps/steps_chasm.py')

setup(name='xdl',
      version='0.2',
      description='XDL library',
      author='Matthew Craven',
      author_email='matthew.craven@glasgow.ac.uk',
      packages=[
            'xdl', 
            'xdl.steps', 
            'xdl.reagents', 
            'xdl.utils', 
            'xdl.hardware', 
            'xdl.safety',
            'xdl.execution',
            'xdl.readwrite'
      ],
)