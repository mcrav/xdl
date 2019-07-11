
import os
from xdl import XDL
from xdl.steps import AbstractBaseStep

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

files = [
    (os.path.join(FOLDER, 'lidocaine.xdl'),
     os.path.join(FOLDER, 'lidocaine_graph.json')),

    (os.path.join(FOLDER, 'alkyl_fluor_step4.xdl'),
     os.path.join(FOLDER, 'alkyl_fluor_step4.graphml'))
]

def test_human_readable():
    """Test that human_readable generation works."""
    for xdl_f, graph_f in files:
        x = XDL(xdl_f)
        x.prepare_for_execution(graph_f, interactive=False)
        for step in x.steps:
            if not isinstance(step, AbstractBaseStep):
                assert step.human_readable() not in  [step.name, None] # No language given
                assert step.human_readable(language='en') not in [step.name, None] # Default language
                assert step.human_readable(language='cz') == step.__class__.__name__ # Unsupported language
                assert step.human_readable(language='zh') not in  [step.name, None] # Non default language
                for prop in step.properties:
                    assert not '{' + prop + '}' in step.human_readable('en')
                    assert not '{' + prop + '}' in step.human_readable('zh')
        x.human_readable()
        x.human_readable('zh')
