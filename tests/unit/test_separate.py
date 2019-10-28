import os
from xdl import XDL
from xdl.steps import Transfer, Add, Stir, Wait, CSeparatePhases, Separate
from ..utils import generic_chempiler_test

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, 'files')

correct_step_info = [
    # Product bottom, single wash
    [
        (Transfer, {}), # Reaction mixture
        (Add, {}), # Solvent
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'lower_phase_vessel': 'rotavap',
            'lower_phase_port': 'evaporate',
            'upper_phase_vessel': 'waste_separator'
        }),
    ],
    # Product top, single wash
    [
        (Transfer, {}), # Reaction mixture
        (Add, {}), # Solvent
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'lower_phase_vessel': 'waste_separator',
            'upper_phase_vessel': 'rotavap',
            'upper_phase_port': 'evaporate',
        }),
    ],
    # Product bottom, single extraction
    [
        (Transfer, {}), # Reaction mixture
        (Add, {}), # Solvent
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'lower_phase_vessel': 'rotavap',
            'lower_phase_port': 'evaporate',
            'upper_phase_vessel': 'waste_separator'
        }),
    ],
    # Product top, single extraction
    [
        (Transfer, {}), # Reaction mixture
        (Add, {}), # Solvent
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'lower_phase_vessel': 'waste_separator',
            'upper_phase_vessel': 'rotavap',
            'upper_phase_port': 'evaporate',
        }),
    ],
    # Product bottom, 2 washes
    [
        (Transfer, {}), # Reaction mixture
        (Add, {}), # Solvent
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'lower_phase_vessel': 'rotavap',
            'lower_phase_port': 'evaporate',
            'upper_phase_vessel': 'waste_separator',
        }),
        (Transfer, {
            'from_vessel': 'rotavap',
            'to_vessel': 'separator',
        }),
        (Add, {}),
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'lower_phase_vessel': 'rotavap',
            'lower_phase_port': 'evaporate',
            'upper_phase_vessel': 'waste_separator'
        }),
    ],
    # Product top, 2 washes
    [
        (Transfer, {}), # Reaction mixture
        (Add, {}), # Solvent
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'lower_phase_vessel': 'waste_separator',
            'upper_phase_vessel': 'separator',
        }),
        (Add, {}),
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'upper_phase_vessel': 'rotavap',
            'upper_phase_port': 'evaporate',
            'lower_phase_vessel': 'waste_separator'
        }),
    ],
    # Product bottom, 2 extractions
    [
        (Transfer, {}), # Reaction mixture
        (Add, {}), # Solvent
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'lower_phase_vessel': 'rotavap',
            'lower_phase_port': 'evaporate',
            'upper_phase_vessel': 'separator',
        }),
        (Add, {}),
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'upper_phase_vessel': 'waste_separator',
            'lower_phase_port': 'evaporate',
            'lower_phase_vessel': 'rotavap'
        }),
    ],
    # Product top 2, extractions
    [
        (Transfer, {}), # Reaction mixture
        (Add, {}), # Solvent
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'lower_phase_vessel': 'buffer_flask',
            'upper_phase_vessel': 'rotavap',
            'upper_phase_port': 'evaporate',
        }),
        (Transfer, {
            'from_vessel': 'buffer_flask',
            'to_vessel': 'separator',
        }),
        (Add, {}),
        (Stir, {}),
        (Stir, {}),
        (Wait, {}),
        (CSeparatePhases, {
            'upper_phase_vessel': 'rotavap',
            'upper_phase_port': 'evaporate',
            'lower_phase_vessel': 'waste_separator'
        }),
    ],
]

def test_separate():
    """Test separating then moving through a cartridge to the final vessel."""
    xdl_f = os.path.join(FOLDER, 'separate.xdl')
    graph_f = os.path.join(FOLDER, 'bigrig.json')
    generic_chempiler_test(xdl_f, graph_f)
    x = XDL(xdl_f)
    x.prepare_for_execution(graph_f)
    i = 0
    for step in x.steps:
        if type(step) == Separate:
            current_step_info = correct_step_info[i]
            for j, substep in enumerate(step.steps):
                assert type(substep) == current_step_info[j][0]
                for k, v in current_step_info[j][1].items():
                    assert substep.properties[k] == v
            i += 1
