ROOM_TEMPERATURE = 25

# DEFAULT PARAMETERS

DEFAULT_STIR_RPM = 400 # rpm
DEFAULT_MOVE_SPEED = 20 # mL/min
DEFAULT_ASPIRATION_SPEED = DEFAULT_MOVE_SPEED
DEFAULT_DISPENSE_SPEED = DEFAULT_MOVE_SPEED
DEFAULT_CLEAN_STIR_TIME = 60 # seconds
DEFAULT_PUMP_PRIME_VOLUME = 3 # mL
DEFAULT_CLEAN_TUBING_VOLUME = 2.5 # mL
DEFAULT_CLEAN_TUBING_SOLVENT = 'water'
DEFAULT_CLEAN_VESSEL_SOLVENT = 'water'
DEFAULT_CLEAN_VESSEL_VOLUME = 10 # mL
DEFAULT_WASH_QUANTITY = 20
DEFAULT_DRY_TIME = 60
DEFAULT_FILTER_TIME = 60
DEFAULT_EXTRACTION_VOLUME = 30 # mL
DEFAULT_WASH_WAIT_TIME = 600 # s
DEFAULT_WASH_VOLUME = 10 # mL

ROUND_BOTTOM_FLASK = 'RoundBottomFlask'

DEFAULT_VALS = {
    'Move': {
        'move_speed': DEFAULT_MOVE_SPEED,
        'aspiration_speed': DEFAULT_ASPIRATION_SPEED,
        'dispense_speed': DEFAULT_DISPENSE_SPEED,
    },
    'Home': {
        'move_speed': DEFAULT_MOVE_SPEED, 
    },
    'Prime': {
        'aspiration_speed': DEFAULT_ASPIRATION_SPEED,
    },
    'Extract': {
        'solvent_volume': DEFAULT_EXTRACTION_VOLUME,
    },
    'Filter': {
        'time': DEFAULT_FILTER_TIME,
    },
    'Dry': {
        'time': DEFAULT_DRY_TIME,
    },
    'Wash': {
        'volume': DEFAULT_WASH_VOLUME,
        'move_speed': DEFAULT_MOVE_SPEED,
        'wait_time': DEFAULT_WASH_WAIT_TIME,
    },
    'StirAndTransfer': {
        'stir_rpm': DEFAULT_STIR_RPM,
    },
    'Add': {
        'move_speed': DEFAULT_MOVE_SPEED,
        'clean_tubing': True,
    },
    'HeatAndReact': {
        'stir_rpm': DEFAULT_STIR_RPM,
    },
    'CleanTubing': {
        'volume': DEFAULT_CLEAN_TUBING_VOLUME,
        'reagent': DEFAULT_CLEAN_TUBING_SOLVENT,
    },
    'CleanVessel': {
        'solvent': DEFAULT_CLEAN_VESSEL_SOLVENT,
        'volume': DEFAULT_CLEAN_VESSEL_VOLUME,
        'stir_rpm': DEFAULT_STIR_RPM,
        'stir_time': DEFAULT_CLEAN_STIR_TIME,
    },
    'SetRpmAndStartStir': {
        'stir_rpm': DEFAULT_STIR_RPM,
    },

    'Reactor': {
        'reactor_type': ROUND_BOTTOM_FLASK,
    }
}

