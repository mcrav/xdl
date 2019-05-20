from typing import List
from ..steps import *

################
### CLEANING ###
################

#: Fraction of vessel max volume to use as solvent volume in CleanVessel step.
CLEAN_VESSEL_VOLUME_FRACTION: float = 0.5

#: Solvents that shouldn't be used for cleaning backbone.
#: Toluene tends to dissolve glue in syringe pumps.
CLEANING_SOLVENT_BLACKLIST: List[str] = ['toluene']

#: Solvents that can be used but aren't ideal. Used to decide what solvent to
#: use for final CleanBackbone step at end of procedure.
CLEANING_SOLVENT_PREFER_NOT_TO_USE: List[str] = ['ether']

SOLVENT_CONTAINING_STEPS: List[type] = [
    Add, Dissolve, WashSolid, Separate, AddFilterDeadVolume]

# Steps after which backbone should be cleaned
CLEAN_BACKBONE_AFTER_STEPS: List[type] = [
    Add,
    Separate,
    WashSolid,
    Filter,
    Dry,
    AddFilterDeadVolume,
    RemoveFilterDeadVolume,
    Dissolve,
    CleanVessel,
    Transfer,
    FilterThrough,
]

#: Steps which should not trigger a backbone clean if the solvent used in the
# step is the same as the solvent used for cleaning.
NO_DUPLICATE_CLEAN_STEPS: List[type] = [
    Add,
    Dissolve,
    AddFilterDeadVolume,
]

COMMON_SOLVENT_NAMES = [
    'acetic acid',
    'acetone',
    'acetonitrile',
    'mecn',
    'benzene',
    '1-butanol',
    'n-butanol',
    'butanol',
    'n-butyl alcohol',
    '2-butanol',
    'sec-butanol',
    '2-butyl alcohol',
    '2-butanone',
    'tba',
    't-butyl alcohol',
    'tert-butyl alcohol',
    'ccl4',
    'carbon tetrachloride',
    'tetrachloromethane',
    'chlorobenzene',
    'chloroform',
    'chcl3',
    'cyclohexane',
    'dcm',
    'dichloromethane',
    'methylene dichloride',
    'methylene chloride',
    '1,2-dichloroethane',
    'ethylene dichloride',
    'diethylene glycol',
    'deg',
    'diethyl ether',
    'et2o',
    'ether',
    'diglyme',
    'dipe',
    'diisopropyl ether',
    'dmf',
    'dimethylformamide',
    'dimethyl-formamide',
    'dimethyl formamide',
    'n,n-dimethylfoormamide',
    'dmso',
    '(ch3)2so',
    'dimethyl sulfoxide',
    'dioaxane',
    '1,4-dioxane',
    'ethanol',
    'etoh',
    'ethyl alcohol',
    'ethyl acetate',
    'etoac',
    'ea',
    'ethylene glycol',
    '1,2-ethanediol',
    'ethane-1,2-diol',
    'glycerin',
    'glyme',
    'monoglyme',
    'dme',
    'dimethyl glycol',
    'dimethyl ether',
    'dimethyl cellosolve',
    'heptane',
    'hmpa',
    'hexamethylphosphoramide',
    'hexametapol',
    'hmpt',
    'hexane',
    'methanol',
    'meoh',
    'methyl alcohol',
    'mtbe',
    'tbme',
    't-buome',
    'tert-buome',
    'methyl-butyl methyl ether',
    'tert-butyl methyl ether',
    'nmp',
    'nitromethane',
    'ch3no2',
    'nitroethane',
    'pentane',
    'petroleum ether',
    'pet ether',
    '1-propanol',
    'propan-1-ol',
    'n-propylalcohol',
    'proh',
    'n-proh',
    'nproh',
    'n-propanol',
    '1-propyl alcohol',
    'n-propyl alcohol',
    '1-propylalcohol',
    'propylalcohol',
    'propyl alcohol',
    '2-propanol',
    'isopropanol',
    'propan-2-ol',
    'iproh',
    'i-proh',
    'i-propanol',
    'ipa',
    'isopropyl alcohol',
    'pyridine',
    'thf',
    'tetrahydrofuran',
    'toluene',
    'trichloroethene',
    'trichloroethylene',
    'tce',
    'triethylamine',
    'tea',
    'net3',
    'et3n',
    'water',
    'h2o',
    'o-xylene',
    'm-xylene',
    'p-xylene',
]
COMMON_SOLVENT_NAMES.extend(
    [f'anhydrous {name}' for name in COMMON_SOLVENT_NAMES])
INERT_GAS_SYNONYMS: List[str] = ['nitrogen', 'n2', 'ar', 'argon']