from typing import Dict, List

######################
# DEFAULT PARAMETERS #
######################

########
# Move #
########

DEFAULT_AIR_FLUSH_TUBE_VOLUME = 5  # mL

#: Default aspiration speed for viscous liquids.
DEFAULT_VISCOUS_ASPIRATION_SPEED = 2  # mL / min

##############
# Separation #
##############
#: Default solvent volume to use in separation in mL.
DEFAULT_SEPARATION_SOLVENT_VOLUME: int = 30

#: Default time to stir separation mixture for at high speed.
DEFAULT_SEPARATION_FAST_STIR_TIME: int = 5 * 60

#: Default time to stir separation mixture for at slow speed.
DEFAULT_SEPARATION_SLOW_STIR_TIME: int = 2 * 60

#: Default speed in RPM to stir separation mixture during fast stir.
DEFAULT_SEPARATION_FAST_STIR_SPEED: int = 600

#: Default speed in RPM to stir separation mixture during slow stir.
DEFAULT_SEPARATION_SLOW_STIR_SPEED: int = 30

#: Default time to allow separation mixture to settle after stirring.
DEFAULT_SEPARATION_SETTLE_TIME: int = 60 * 5

############
# Cleaning #
############
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

###########
# Rotavap #
###########

#: Default rotation speed in RPM for the rotavap when dissolving something.
DEFAULT_DISSOLVE_ROTAVAP_ROTATION_SPEED: int = 250

#: Default time to wait for bath to heat up with rotavap.
DEFAULT_ROTAVAP_WAIT_FOR_TEMP_TIME: int = 60 * 5

#############
# Filtering #
#############

#: Default pressure to set vacuum to while filtering.
DEFAULT_FILTER_VACUUM_PRESSURE: int = 400  # mbar

#: Default volume factor to remove solvent after washing filter cake,
# i.e. 1.5 means remove 1.5x the solvent volume.
DEFAULT_FILTER_EXCESS_REMOVE_FACTOR: float = 1.5

#: Default volume in mL to transfer from bottom of filter flask to waste after
#: drying filter cake.
DEFAULT_DRY_WASTE_VOLUME: int = 5


#############
# WashSolid #
#############

DEFAULT_FILTER_ANTICLOGGING_ASPIRATION_SPEED: int = 2

#######
# Add #
#######
#: Default time in seconds to wait with stirring after addition of a reagent.
DEFAULT_AFTER_ADD_WAIT_TIME: int = 10

############
# Stirring #
############
#: Default speed in RPM to stir at.
DEFAULT_STIR_SPEED: int = 250

#: Default speed to stir reagents that specify stirring in reagent flask.
DEFAULT_STIR_REAGENT_FLASK_SPEED: int = 200

################################
# CHEMPUTER DEVICE CLASS NAMES #
################################

CHEMPUTER_REACTOR_CLASS_NAME: str = 'ChemputerReactor'
CHEMPUTER_SEPARATOR_CLASS_NAME: str = 'ChemputerSeparator'
CHEMPUTER_FILTER_CLASS_NAME: str = 'ChemputerFilter'
CHEMPUTER_FLASK_CLASS_NAME: str = 'ChemputerFlask'
CHEMPUTER_WASTE_CLASS_NAME: str = 'ChemputerWaste'
CHEMPUTER_VACUUM_CLASS_NAME: str = 'ChemputerVacuum'
CHEMPUTER_PUMP_CLASS_NAME: str = 'ChemputerPump'
CHEMPUTER_VALVE_CLASS_NAME: str = 'ChemputerValve'

CHEMPUTER_FILTER: str = 'ChemputerFilter'
CHEMPUTER_REACTOR: str = 'ChemputerReactor'
CHEMPUTER_CARTRIDGE: str = 'ChemputerCartridge'
CHEMPUTER_WASTE: str = 'ChemputerWaste'
CHEMPUTER_FLASK: str = 'ChemputerFlask'
CHEMPUTER_VACUUM: str = 'ChemputerVacuum'
CHEMPUTER_SEPARATOR: str = 'ChemputerSeparator'
CHEMPUTER_VALVE: str = 'ChemputerValve'
CHEMPUTER_PUMP: str = 'ChemputerPump'

JULABO_CF41_CLASS_NAME: str = 'JULABOCF41'
HUBER_PETITE_FLEUR_CLASS_NAME: str = 'Huber'
IKA_RCT_DIGITAL_CLASS_NAME: str = 'IKARCTDigital'
IKA_RET_CONTROL_VISC: str = 'IKARETControlVisc'
IKA_RV_10 = "IKARV10"
CVC3000 = "CVC3000"
IKA_MICROSTAR_75 = "IKAmicrostar75"
RZR_2052 = "RZR_2052"
HEIDOLPH_TORQUE_100 = "HeiTORQUE_100"


HEATER_CLASSES: List[str] = [IKA_RCT_DIGITAL_CLASS_NAME, IKA_RET_CONTROL_VISC]
CHILLER_CLASSES: List[str] = [
    JULABO_CF41_CLASS_NAME, HUBER_PETITE_FLEUR_CLASS_NAME]

ROTAVAP_CLASSES: List[str] = [IKA_RV_10]
VACUUM_CLASSES: List[str] = [CVC3000]
STIRRER_CLASSES: List[str] = [IKA_MICROSTAR_75, RZR_2052, HEIDOLPH_TORQUE_100]
FILTER_CLASSES: List[str] = [CHEMPUTER_FILTER]
REACTOR_CLASSES: List[str] = [CHEMPUTER_REACTOR]
SEPARATOR_CLASSES: List[str] = [CHEMPUTER_SEPARATOR]
FLASK_CLASSES: List[str] = [CHEMPUTER_FLASK]

CHILLER_MIN_TEMP: int = -40
CHILLER_MAX_TEMP: int = 140
HEATER_MAX_TEMP: int = 360

# Filter, separator ports
BOTTOM_PORT: str = 'bottom'
TOP_PORT: str = 'top'
# Rotavap ports
EVAPORATE_PORT: str = 'evaporate'
COLLECT_PORT: str = 'collect'

VALID_PORTS = {
    'ChemputerReactor': ['0', '1', '2'],
    'ChemputerSeparator': ['top', 'bottom'],
    'ChemputerFilter': ['top', 'bottom'],
    'IKARV10': ['evaporate', 'collect'],
    'ChemputerValve': ['-1', '0', '1', '2', '3', '4', '5'],
    'ChemputerPump': ['0'],
    'ChemputerWaste': ['0'],
    'ChemputerFlask': ['0'],
    'ChemputerCartridge': ['in', 'out'],
    'ChemputerVacuum': ['0'],
    'CommanduinoLabwareDevice': ['0'],
}

DEFAULT_PORTS: Dict[str, Dict[str, str]] = {
    'ChemputerSeparator': {'from': 'bottom', 'to': 'bottom'},
    'ChemputerReactor': {'from': 0, 'to': 0},
    'ChemputerFilter': {'from': 'bottom', 'to': 'top'},
    'ChemputerPump': {'from': 0, 'to': 0},
    'IKARV10': {'from': 'evaporate', 'to': 'evaporate'},
    'ChemputerFlask': {'from': 0, 'to': 0},
    'ChemputerWaste': {'from': 0, 'to': 0},
    'CommanduinoLabwareDevice': {'from': 0, 'to': 0}
}

FILTER_DEAD_VOLUME_INERT_GAS_METHOD: str = 'inert_gas'
FILTER_DEAD_VOLUME_LIQUID_METHOD: str = 'solvent'

#: Time to wait during venting of vacuum to ambient pressure.
DEFAULT_VACUUM_VENT_WAIT_TIME: float = 60

#: Default time to wait for rotavap arm lift/descend.
DEFAULT_ROTAVAP_WAIT_FOR_ARM_TIME: int = 5
