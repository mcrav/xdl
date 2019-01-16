ROOM_TEMPERATURE = 25

# DEFAULT PARAMETERS

DEFAULT_STIR_RPM = 400 # rpm
DEFAULT_MOVE_SPEED = 40 # mL/min
 # mL/min Different to move speed as 40 mL / min aspiration speed means air gets sucked in.
DEFAULT_ASPIRATION_SPEED = 10
DEFAULT_DISPENSE_SPEED = DEFAULT_MOVE_SPEED
DEFAULT_CLEAN_STIR_TIME = 60 # seconds
DEFAULT_PUMP_PRIME_VOLUME = 3 # mL
DEFAULT_CLEAN_TUBING_VOLUME = 2.5 # mL
DEFAULT_CLEAN_TUBING_SOLVENT = 'water'
DEFAULT_CLEAN_VESSEL_SOLVENT = 'water'
DEFAULT_CLEAN_VESSEL_VOLUME = 10 # mL
DEFAULT_WASH_QUANTITY = 20
DEFAULT_WASHFILTERCAKE_WAIT_TIME = 60*2 # s
DEFAULT_DRY_TIME = 60*5
DEFAULT_FILTER_TIME = 60
DEFAULT_EXTRACTION_VOLUME = 30 # mL
DEFAULT_SEPARATION_FAST_STIR_TIME = 5 * 60
DEFAULT_SEPARATION_SLOW_STIR_TIME = 2 * 60
DEFAULT_SEPARATION_FAST_STIR_RPM = 600
DEFAULT_SEPARATION_SLOW_STIR_RPM = 30
DEFAULT_SEPARATION_SETTLE_TIME = 60 * 5
DEFAULT_ORGANIC_CLEANING_SOLVENT = 'ether'
DEFAULT_CLEAN_BACKBONE_VOLUME = 3
DEFAULT_ROTAVAP_TIME = 60 * 5

DEFAULT_TRANSFER_EXTRA_VOLUME = 5

DEFAULT_WASH_VOLUME = 50 # mL
DEFAULT_WASHFILTERCAKE_VOLUME = 20

DEFAULT_FILTER_MOVE_VOLUME = 5 # mL
DEFAULT_FILTER_ASPIRATION_SPEED = 5 # mL / min

DEFAULT_AFTER_ADD_WAIT_TIME = 10 # s (time to wait for stirring after addition)

ROUND_BOTTOM_FLASK = 'RoundBottomFlask'

DEFAULT_RECORDING_SPEED = 14
DEFAULT_WAIT_RECORDING_SPEED = 2000

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
    'WashFilterCake': {
        'volume': DEFAULT_WASHFILTERCAKE_VOLUME,
        'move_speed': DEFAULT_MOVE_SPEED,
        'wait_time': DEFAULT_WASHFILTERCAKE_WAIT_TIME,
    },
    'Transfer': {
        'stir_rpm': DEFAULT_STIR_RPM,
    },
    'Add': {
        'move_speed': DEFAULT_MOVE_SPEED,
        'clean_tubing': True,
        'start_stir': True,
        'stop_stir': True,
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
    'StartStir': {
        'stir_rpm': DEFAULT_STIR_RPM,
    },

    'Reactor': {
        'reactor_type': ROUND_BOTTOM_FLASK,
    },
    'PrimePumpForAdd': {
        'move_speed': DEFAULT_MOVE_SPEED,
    },
    'Wait': {
        'wait_recording_speed': DEFAULT_WAIT_RECORDING_SPEED,
        'after_recording_speed': DEFAULT_RECORDING_SPEED,
    },
    'Rotavap': {
        'time': DEFAULT_ROTAVAP_TIME,
    },
    'Wash': {
        'solvent_volume': DEFAULT_WASH_VOLUME,
    },
    'StirAtRT': {
        'stir_rpm': DEFAULT_STIR_RPM,
    },
}

####################################
### CHEMPUTER DEVICE CLASS NAMES ###
####################################

CHEMPUTER_REACTOR_CLASS_NAME = 'chemputer_reactor'
CHEMPUTER_SEPARATOR_CLASS_NAME = 'chemputer_separator'
CHEMPUTER_FILTER_CLASS_NAME = 'chemputer_filter'
CHEMPUTER_FLASK_CLASS_NAME = 'chemputer_flask'
CHEMPUTER_WASTE_CLASS_NAME = 'chemputer_waste'
CHEMPUTER_VACUUM_CLASS_NAME = 'chemputer_vacuum'
CHEMPUTER_PUMP_CLASS_NAME = 'chemputer_pump'
CHEMPUTER_VALVE_CLASS_NAME = 'chemputer_valve'

AQUEOUS_KEYWORDS = ['water', 'aqueous', 'acid', '_m_']
