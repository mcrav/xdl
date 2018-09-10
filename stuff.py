from steps_generic import *
from steps_chasm import *
from steps_xdl import *

rufinamide_steps = [
    Add(reagent='sodium_azide', volume=60, vessel='reactor_reactor', comment='Add sodium azide to reactor'),
    HeatAndReact(vessel='reactor_reactor', time=12*60*60, temp=75, comment='Heat to 75C and wait for 12h'),

    Add(reagent='water', volume=15, vessel='flask_filter_bottom', clean_tubing=False, comment='Add water to filter flask bottom'),
    StirAndTransfer(from_vessel='reactor_reactor', to_vessel='filter_filter_top', volume=100, comment='Transfer reaction mixture to filter flask top'),
    StartStir(name='filter_filter_top'),
    Add(reagent='methyl_propiolate', volume=3.21, vessel='filter_filter_top', comment='Add methyl propiolate to filter flask top'),
    Chill(vessel='filter_filter_top', temp=65),
    Wait(time=4*60*60),
    ChillBackToRT(vessel='filter_filter_top'),
    StopStir(name='filter_filter_top'),

    Add(reagent='water', volume=15, vessel='flask_filter_bottom', clean_tubing=False, comment='Add water to filter flask bottom'),
    StartStir(name='filter_filter_top'),
    Add(reagent='ammonia', vessel='filter_filter_top', volume=60, clean_tubing=True),
    Chill(vessel='filter_filter_top', temp=75),
    Wait(time=12*60*60),
    Add(reagent='water', vessel='flask_filter_bottom', volume=5),
    ChillBackToRT(vessel='filter_filter_top'),

    Move(src='flask_filter_bottom', dest='waste_solvents', volume=200),
    Repeat(3, Wash(solvent='water', vessel='filter_filter_top', volume=20)),
    StopStir(name='filter_filter_top'),

    StartVacuum(vessel='flask_filter_bottom'),
    Chill(vessel='filter_filter_top', temp=75),
    Wait(time=12*60*60),
    ChillBackToRT(vessel='filter_filter_top'),
    StopVacuum(vessel='flask_filter_bottom'),
]

nytol_excerpt_steps = [
    
]