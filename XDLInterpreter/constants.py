# SOLVENTS

WATER = 'water'
METHANOL = 1
ETHANOL = 2
DMSO = 3
DCM = 4
ACETONE = 5

# DEFAULT PARAMETERS

DEFAULT_STIR_RPM = 400 # rpm
DEFAULT_MOVE_SPEED = 20 # mL/min
DEFAULT_ASPIRATION_SPEED = DEFAULT_MOVE_SPEED
DEFAULT_DISPENSE_SPEED = DEFAULT_MOVE_SPEED
DEFAULT_CLEAN_STIR_TIME = 60 # seconds
DEFAULT_PUMP_PRIME_VOLUME = 3 # mL
DEFAULT_CLEAN_TUBING_VOLUME = 2.5 # mL
DEFAULT_CLEAN_TUBING_SOLVENT = WATER

# MISC

ROOM_TEMPERATURE = 25

'''
expreader.py constants

Constants used to classify different parts of natural language as 
experimental parameters or operations.
'''

end_phrase_words = ['then'] 

METHANOL = 'Methanol'
WATER = 'Water'

solvent_keywords = {
    'methanol': METHANOL,
    'meoh': METHANOL,
    'water': WATER,
    'h2o': WATER,
}

# Operations
OP_ADD = 'OP_ADD'
OP_DRY = 'OP_DRY'
OP_FILTER = 'OP_FILTER'
OP_STIR = 'OP_STIR'
OP_WASH = 'OP_WASH'
OP_WAIT = 'OP_WAIT'


operation_groups = {
    'dried': OP_DRY,
    'washed': OP_WASH,
    'filtered': OP_FILTER,
    'stirred': OP_STIR, 
    'stirring': OP_STIR,
    'added': OP_ADD,
    'treated': OP_ADD,
    'addition of': OP_ADD,
    'suspended in': OP_ADD,
    'loaded': OP_ADD,
    'charged': OP_ADD,
}

operation_is_with_words = ['loaded', 'charged', 'washed', 'treated']
operation_is_to_words = ['added',]



operation_keywords = operation_groups.keys()
operation_add_keywords = [item for item in operation_keywords if operation_groups[item] == OP_ADD]
operation_wash_keywords = [item for item in operation_keywords if operation_groups[item] == OP_WASH]

ROUND_BOTTOM_FLASK = 'RoundBottomFlask'

vessel_groups = {
    r'[r|R]ound[ |-][b|B]ottom(ed)?[ |-][f|F]lask': ROUND_BOTTOM_FLASK,
}

vessel_keywords = vessel_groups.values()

# Units
TIME_MIN = 'TIME_MIN'
TIME_HOUR = 'TIME_HOUR'
TIME_UNITS = [TIME_MIN, TIME_HOUR]

TEMP_CELSIUS = 'TEMP_CELSIUS'
TEMP_UNITS = [TEMP_CELSIUS]

PERCENT = 'PERCENT'

MOL = 'MOL'
MMOL = 'MMOL'

VOLUME_ML = 'VOLUME_ML'

MASS_G = 'MASS_G'
MASS_MG = 'MASS_MG'

unit_groups = {
    'm': TIME_MIN,
    'mins': TIME_MIN,
    'minutes': TIME_MIN,
    'hours': TIME_HOUR,
    'hrs': TIME_HOUR,
    'h': TIME_HOUR,

    'mol': MOL,
    'mole': MOL,
    'moles': MOL,
    'mmol': MMOL,
    'mmole': MMOL,
    'mmoles': MMOL,

    'ml': VOLUME_ML,
    'mL': VOLUME_ML,

    'g': MASS_G,
    'grams': MASS_G,
    'mg': MASS_MG,
    'milligrams': MASS_MG,

    '°C': TEMP_CELSIUS,
    '° C': TEMP_CELSIUS,

    '%': PERCENT,
    'percent': PERCENT,
}

no_space_units = ['°C', '° C', '%']
units = unit_groups.keys()
