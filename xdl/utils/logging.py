"""The main purpose of this module is to provide the ``get_logger`` function
that can be used from anywhere within the package to obtain the xdl logger.
"""

import logging

def get_logger() -> logging.Logger:
    """Get logger for logging xdl messages."""
    logger = logging.getLogger('xdl')
    if not logger.hasHandlers():
        logger.addHandler(get_handler())
    return logger

def get_handler() -> logging.StreamHandler:
    """Get handler for XDL logger."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter('XDL: %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    return handler
