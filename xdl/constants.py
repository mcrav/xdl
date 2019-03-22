from typing import Dict, List, Any

##########################
### DEFAULT PARAMETERS ###
##########################

##########
## Move ##
##########
#: Default speed to move liquid in mL / min.
DEFAULT_MOVE_SPEED: int = 40

#: Default aspiration speed (speed pulling liquid into pump) in mL / min. Lower
#: than move speed to avoid air getting sucked in.
DEFAULT_ASPIRATION_SPEED: int = 10

#: Default dispence speed (speed pushing liquid out of pump) in mL / min.
DEFAULT_DISPENSE_SPEED: int = DEFAULT_MOVE_SPEED

#: Default volume of reagent to move to waste to prime the tubes before Add step.
DEFAULT_PUMP_PRIME_VOLUME: int = 3 # mL

DEFAULT_AIR_FLUSH_TUBE_VOLUME = 5 # mL

################
## Separation ##
################
#: Default solvent volume to use in separation in mL.
DEFAULT_SEPARATION_SOLVENT_VOLUME: int = 30

#: Default time to stir separation mixture for at high speed.
DEFAULT_SEPARATION_FAST_STIR_TIME: int = 5 * 60

#: Default time to stir separation mixture for at slow speed.
DEFAULT_SEPARATION_SLOW_STIR_TIME: int = 2 * 60

#: Default speed in RPM to stir separation mixture during fast stir.
DEFAULT_SEPARATION_FAST_STIR_RPM: int = 600

#: Default speed in RPM to stir separation mixture during slow stir.
DEFAULT_SEPARATION_SLOW_STIR_RPM: int = 30

#: Default time to allow separation mixture to settle after stirring.
DEFAULT_SEPARATION_SETTLE_TIME: int = 60 * 5

##############
## Cleaning ##
##############
#: Default value for auto_clean, determines whether clean backbone steps are
#: inserted between appropriate steps.
DEFAULT_AUTO_CLEAN: bool = True

#: Default solvent to use for organic cleaning steps.
DEFAULT_ORGANIC_CLEANING_SOLVENT: str = 'ether'

#: Default solvent to use for aqueous cleaning steps.
DEFAULT_AQUEOUS_CLEANING_SOLVENT: str = 'water'

#: Default volume in mL of cleaning solvent to transfer to waste during cleaning
#: step.
DEFAULT_CLEAN_BACKBONE_VOLUME: int = 3

#: Default volume in mL of solvent to clean vessel with.
DEFAULT_CLEAN_VESSEL_VOLUME: int = 10 # mL

#: Default time in seconds to stir vessel during CleanVessel step.
DEFAULT_CLEAN_VESSEL_STIR_TIME: int = 60

#############
## Rotavap ##
#############
#: Default pressure in mbar for rotavap degassing.
DEFAULT_ROTAVAP_DEGAS_PRESSURE: int = 900

#: Default time in seconds for rotavap degassing.
DEFAULT_ROTAVAP_DEGAS_TIME: int = 300 # s

#: Default time in seconds for rotavap venting.
DEFAULT_ROTAVAP_VENT_TIME: int = 10

#: Default time in seconds for evaporating mixture to dryness.
DEFAULT_ROTAVAP_DRYING_TIME: int = 2* 60 * 60

#: Default rotation speed in RPM for rotavap.
DEFAULT_ROTAVAP_ROTATION_SPEED: int = 280

###############
## Filtering ##
###############
#: Default time in seconds to wait with vacuum on while filtering.
DEFAULT_FILTER_WAIT_TIME: int = 60*2

#: Default volume of solvent to use when washing a filter cake.
DEFAULT_WASHFILTERCAKE_VOLUME: int = 20

#: Default time to stir mixture for after adding solvent but before filtering.
DEFAULT_WASHFILTERCAKE_STIR_SOLVENT_TIME: int = 30

#: Default time in seconds to wait for with vacuum on when washing a filter cake.
DEFAULT_WASHFILTERCAKE_WAIT_TIME: int = 10 

#: Default volume factor to remove solvent after washing filter cake,
# i.e. 1.5 means remove 1.5x the solvent volume.
DEFAULT_FILTER_EXCESS_REMOVE_FACTOR: float = 1.5

#: Default time in seconds to wait for with vacuum on when drying a filter cake.
DEFAULT_DRY_TIME: int = 60*60

#: Default volume in mL to transfer from bottom of filter flask to waste after
#: drying filter cake.
DEFAULT_DRY_WASTE_VOLUME: int = 5

#########
## Add ##
#########
#: Default time in seconds to wait with stirring after addition of a reagent.
DEFAULT_AFTER_ADD_WAIT_TIME: int = 10

##############
## Stirring ##
##############
#: Default speed in RPM to stir at.
DEFAULT_STIR_RPM: int = 400

###########
## Video ##
###########
#: Default recording speed in multiples of real time speed.
DEFAULT_RECORDING_SPEED: int = 14

#: Default recording speed during wait step in multiples of real time speed.
DEFAULT_WAIT_RECORDING_SPEED: int = 2000

#: Dictionary of default values to provide to steps if no explicit values are
#: given.
DEFAULT_VALS: Dict[str, Dict[str, Any]] = {
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
    'Separate': {
        'solvent_volume': DEFAULT_SEPARATION_SOLVENT_VOLUME,
    },
    'Filter': {
        'wait_time': DEFAULT_FILTER_WAIT_TIME,
        'aspiration_speed': DEFAULT_ASPIRATION_SPEED,
    },
    'Dry': {
        'time': DEFAULT_DRY_TIME,
        'aspiration_speed': DEFAULT_ASPIRATION_SPEED,
    },
    'WashFilterCake': {
        'volume': DEFAULT_WASHFILTERCAKE_VOLUME,
        'move_speed': DEFAULT_MOVE_SPEED,
        'wait_time': DEFAULT_WASHFILTERCAKE_WAIT_TIME,
        'aspiration_speed': DEFAULT_ASPIRATION_SPEED,
    },
    'Transfer': {
        'stir_rpm': DEFAULT_STIR_RPM,
        'aspiration_speed': DEFAULT_ASPIRATION_SPEED,
    },
    'Add': {
        'move_speed': DEFAULT_MOVE_SPEED,
        'aspiration_speed': DEFAULT_ASPIRATION_SPEED,
        'stir_rpm': DEFAULT_STIR_RPM,
    },
    'CleanVessel': {
        'volume': DEFAULT_CLEAN_VESSEL_VOLUME,
        'stir_rpm': DEFAULT_STIR_RPM,
        'stir_time': DEFAULT_CLEAN_VESSEL_STIR_TIME,
    },
    'CStartStir': {
        'stir_rpm': DEFAULT_STIR_RPM,
    },
    'CSetStirRpm': {
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
        'time': DEFAULT_ROTAVAP_DRYING_TIME,
    },
    'StirAtRT': {
        'stir_rpm': DEFAULT_STIR_RPM,
    },
    'StartStir': {
        'stir_rpm': DEFAULT_STIR_RPM,
    },
    'Stir': {
        'stir_rpm': DEFAULT_STIR_RPM,
    }
}


####################################
### CHEMPUTER DEVICE CLASS NAMES ###
####################################

CHEMPUTER_REACTOR_CLASS_NAME: str = 'ChemputerReactor'
CHEMPUTER_SEPARATOR_CLASS_NAME: str = 'ChemputerSeparator'
CHEMPUTER_FILTER_CLASS_NAME: str = 'ChemputerFilter'
CHEMPUTER_FLASK_CLASS_NAME: str = 'ChemputerFlask'
CHEMPUTER_WASTE_CLASS_NAME: str = 'ChemputerWaste'
CHEMPUTER_VACUUM_CLASS_NAME: str = 'ChemputerVacuum'
CHEMPUTER_PUMP_CLASS_NAME: str = 'ChemputerPump'
CHEMPUTER_VALVE_CLASS_NAME: str = 'ChemputerValve'

BOTTOM_PORT: str = 'bottom'
TOP_PORT: str = 'top'


############
### MISC ###
############

#: Room temperature in °C
ROOM_TEMPERATURE: int = 25

#: Keywords that if found in reagent name signify that the reagent is aqueous.
AQUEOUS_KEYWORDS: List[str] = ['water', 'aqueous', 'acid', '_m_']
