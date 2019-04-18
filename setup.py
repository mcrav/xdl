from distutils.core import setup

setup(name='xdl',
      version='0.1.0',
      description='Package for working with XDL (chemical descriptive language).',
      author='Matthew Craven',
      author_email='matthew.craven@glasgow.ac.uk',
      packages=[
            'xdl', 
            'xdl.steps',
            'xdl.steps.steps_synthesis',
            'xdl.steps.steps_base',
            'xdl.steps.steps_utility',
            'xdl.reagents', 
            'xdl.utils', 
            'xdl.hardware', 
            'xdl.safety',
            'xdl.execution',
            'xdl.readwrite',
            'xdl.graph',
      ],
)