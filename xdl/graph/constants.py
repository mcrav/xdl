DEFAULT_VALVE_MAX_VOLUME = 100

DEFAULT_WASTE_CURRENT_VOLUME = 0
DEFAULT_WASTE_MAX_VOLUME = 250

DEFAULT_PUMP_MAX_VOLUME = 25

DEFAULT_FLASK_CURRENT_VOLUME = 100
DEFAULT_FLASK_MAX_VOLUME = 100

DEFAULT_FILTER_CURRENT_VOLUME = 0
DEFAULT_FILTER_MAX_VOLUME = 200
DEFAULT_FILTER_DEAD_VOLUME = 10

DEFAULT_REACTOR_MAX_VOLUME = 200
DEFAULT_REACTOR_CURRENT_VOLUME = 0

DEFAULT_SEPARATOR_MAX_VOLUME = 200
DEFAULT_SEPARATOR_CURRENT_VOLUME = 0

DEFAULT_ROTAVAP_CURRENT_VOLUME = 0
DEFAULT_ROTAVAP_MAX_VOLUME = 250

PORT = 'COM15'
IP_ADDRESS = 'IP ADDRESS HERE'

COMPONENT_TYPE_DICT = {
    'ChemputerFilter': 'filter',
    'ChemputerReactor': 'reactor',
    'IKARV10': 'rotavap',
    'ChemputerSeparator': 'separator',
    'filter': 'filter',
    'reactor': 'reactor',
    'rotavap': 'rotavap',
    'separator': 'separator',
}

TYPE_COMPONENT_DICT = {
    'filter': 'ChemputerFilter',
    'reactor': 'ChemputerReactor',
    'rotavap': 'IKARV10',
    'separator': 'ChemputerSeparator',
}