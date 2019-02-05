##########################
### DEFAULT PARAMETERS ###
##########################


# Move
# mL/min Different to move speed as 40 mL / min aspiration speed means air gets sucked in.
DEFAULT_MOVE_SPEED = 40 # mL/min
DEFAULT_ASPIRATION_SPEED = 10
DEFAULT_DISPENSE_SPEED = DEFAULT_MOVE_SPEED
DEFAULT_PUMP_PRIME_VOLUME = 3 # mL

# Separation
DEFAULT_SEPARATION_SOLVENT_VOLUME = 30 # mL
DEFAULT_SEPARATION_FAST_STIR_TIME = 5 * 60
DEFAULT_SEPARATION_SLOW_STIR_TIME = 2 * 60
DEFAULT_SEPARATION_FAST_STIR_RPM = 600
DEFAULT_SEPARATION_SLOW_STIR_RPM = 30
DEFAULT_SEPARATION_SETTLE_TIME = 60 * 5

# Cleaning
DEFAULT_AUTO_CLEAN = True
DEFAULT_ORGANIC_CLEANING_SOLVENT = 'ether'
DEFAULT_AQUEOUS_CLEANING_SOLVENT = 'water'
DEFAULT_CLEAN_BACKBONE_VOLUME = 3
DEFAULT_CLEAN_VESSEL_SOLVENT = 'water'
DEFAULT_CLEAN_VESSEL_VOLUME = 10 # mL
DEFAULT_CLEAN_STIR_TIME = 60 # seconds

# Rotavap
DEFAULT_ROTAVAP_TIME = 60 * 5

# Filtering
DEFAULT_FILTER_WAIT_TIME = 60
DEFAULT_WASHFILTERCAKE_VOLUME = 20
DEFAULT_WASHFILTERCAKE_WAIT_TIME = 60*2 # s
DEFAULT_DRY_TIME = 60*5
DEFAULT_DRY_WASTE_VOLUME = 5 # mL

# Add
DEFAULT_AFTER_ADD_WAIT_TIME = 10 # s (time to wait for stirring after addition)

# Stirring
DEFAULT_STIR_RPM = 400 # rpm

# Video
DEFAULT_RECORDING_SPEED = 14
DEFAULT_WAIT_RECORDING_SPEED = 2000

DEFAULT_VALS = {
    'CMove': {
        'move_speed': DEFAULT_MOVE_SPEED,
        'aspiration_speed': DEFAULT_ASPIRATION_SPEED,
        'dispense_speed': DEFAULT_DISPENSE_SPEED,
    },
    'CHome': {
        'move_speed': DEFAULT_MOVE_SPEED, 
    },
    'CPrime': {
        'aspiration_speed': DEFAULT_ASPIRATION_SPEED,
    },
    'Separation': {
        'solvent_volume': DEFAULT_SEPARATION_SOLVENT_VOLUME,
    },
    'Filter': {
        'wait_time': DEFAULT_FILTER_WAIT_TIME,
    },
    'Dry': {
        'wait_time': DEFAULT_DRY_TIME,
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
    'CleanVessel': {
        'solvent': DEFAULT_CLEAN_VESSEL_SOLVENT,
        'volume': DEFAULT_CLEAN_VESSEL_VOLUME,
        'stir_rpm': DEFAULT_STIR_RPM,
        'stir_time': DEFAULT_CLEAN_STIR_TIME,
    },
    'CStartStir': {
        'stir_rpm': DEFAULT_STIR_RPM,
    },
    'PrimePumpForAdd': {
        'volume': DEFAULT_PUMP_PRIME_VOLUME,
    },
    'Wait': {
        'wait_recording_speed': DEFAULT_WAIT_RECORDING_SPEED,
        'after_recording_speed': DEFAULT_RECORDING_SPEED,
    },
    'Rotavap': {
        'time': DEFAULT_ROTAVAP_TIME,
    },
    'StirAtRT': {
        'stir_rpm': DEFAULT_STIR_RPM,
    },
    'StartStir': {
        'stir_rpm': DEFAULT_STIR_RPM,
    }
}


####################################
### CHEMPUTER DEVICE CLASS NAMES ###
####################################

CHEMPUTER_REACTOR_CLASS_NAME = 'ChemputerReactor'
CHEMPUTER_SEPARATOR_CLASS_NAME = 'ChemputerSeparator'
CHEMPUTER_FILTER_CLASS_NAME = 'ChemputerFilter'
CHEMPUTER_FLASK_CLASS_NAME = 'ChemputerFlask'
CHEMPUTER_WASTE_CLASS_NAME = 'ChemputerWaste'
CHEMPUTER_VACUUM_CLASS_NAME = 'ChemputerVacuum'
CHEMPUTER_PUMP_CLASS_NAME = 'ChemputerPump'
CHEMPUTER_VALVE_CLASS_NAME = 'ChemputerValve'

BOTTOM_PORT = 'bottom'
TOP_PORT = 'top'

XDL_HARDWARE_CHEMPUTER_CLASS_MAP = {
    'Filter': CHEMPUTER_FILTER_CLASS_NAME,
    'Reactor': CHEMPUTER_REACTOR_CLASS_NAME,
    'Separator': CHEMPUTER_SEPARATOR_CLASS_NAME,
    'Flask': CHEMPUTER_FLASK_CLASS_NAME,
    'Waste': CHEMPUTER_WASTE_CLASS_NAME,
    'Vacuum': CHEMPUTER_VACUUM_CLASS_NAME,
    'Pump': CHEMPUTER_PUMP_CLASS_NAME,
    'Valve': CHEMPUTER_VALVE_CLASS_NAME
}


############
### MISC ###
############

ROOM_TEMPERATURE = 25

AQUEOUS_KEYWORDS = ['water', 'aqueous', 'acid', '_m_']
