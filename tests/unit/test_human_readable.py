
import os
from xdl import XDL

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

def test_human_readable():
    """Test that human_readable generation works."""
    xdl_f = os.path.join(FOLDER, 'lidocaine.xdl')
    graph_f = os.path.join(FOLDER, 'lidocaine_graph.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    assert len(x.human_readable()) > 0 # No language given
    assert len(x.human_readable(language='en')) > 0 # Default language
    assert x.human_readable(language='cz') == '' # Unsupported language
    # assert len(x.human_readable(language='zh')) > 0 # Non default language

def test_human_readable_step():
    """Test that human_readable generation works for individual steps."""
    xdl_f = os.path.join(FOLDER, 'lidocaine.xdl')
    graph_f = os.path.join(FOLDER, 'lidocaine_graph.json')
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f, interactive=False)
    for step in x.steps:
        assert len(step.human_readable()) > 0 # No language given
        assert len(step.human_readable(language='en')) > 0 # Default language
        assert step.human_readable(language='cz') == step.__class__.__name__ # Unsupported language
        # assert len(x.human_readable(language='zh')) > 0 # Non default language
