HEATER_CHILLER_TEMP_RANGES = {
    'JULABOCF41': (-40, 100),
    'IKARV10': (18, 180),  # https://www.wilmad-labglass.com/uploadedFiles/Main_Site/Content/Literature_Center/RV10_WEB.pdf
    'IKARCTDigital': (18, 360), # https://www.ika.com/en/Products-Lab-Eq/Magnetic-Stirrers-Hot-Plate-Lab-Mixer-Stirrer-Blender-csp-188/RCT-basic-cpdt-3810000/
    'Huber': (-40, 100),
}

REMOVE_SRC_PORT = 'remove_src_port'
REMOVE_DEST_PORT = 'remove_dest_port'
SRC_PORT_INVALID = 'src_port_invalid'
DEST_PORT_INVALID = 'dest_port_invalid'
SWITCH_TO_IN_EDGE = 'switch_to_in_edge'
SWITCH_TO_OUT_EDGE = 'switch_to_out_edge'

INVALID_PORT_ERROR = 'invalid_port_error'
NOT_ENOUGH_SPARE_PORTS_ERROR = 'not_enough_spare_ports_error'
MISSING_COMPONENT_TYPE_ERROR = 'missing_component_type_error'
MISSING_HEATER_OR_CHILLER_ERROR = 'missing_heater_or_chiller_error'
CANNOT_REACH_TARGET_TEMP_ERROR = 'cannot_reach_target_temp_error'

DEFAULT_BUFFER_FLASK_VOLUME: int = 500 # mL
DEFAULT_REAGENT_FLASK_VOLUME: int = 100 # mL
