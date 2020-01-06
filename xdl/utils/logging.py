import logging
        

def get_logger():
    logger = logging.getLogger('xdl')
    if not logger.hasHandlers():
        logger.addHandler(get_info_handler())
        logger.addHandler(get_debug_handler())
    return logger

def get_info_handler():
    info_handler = logging.StreamHandler()
    info_formatter = logging.Formatter('XDL: %(message)s')
    info_handler.setFormatter(info_formatter)
    return info_handler

def get_debug_handler():
    debug_handler = logging.StreamHandler()
    debug_formatter = logging.Formatter('XDL:%(asctime)s: %(message)s')
    debug_handler.setFormatter(debug_formatter)
    return debug_handler