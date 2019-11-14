import logging
import sys
from ..constants import VALID_PORTS

class XDLError(Exception):
    pass

class IllegalPortError(Exception):
    pass

def raise_error(e, msg=''):
    """Given an exception and a message raise the exception with an extra
    message added.

    Args:
        e (Exception): Exception to raise.
        msg (str): Message to add to exception.
    """
    raise type(e)(f'{e} {msg}').with_traceback(sys.exc_info()[2])

def initialise_logger(logger: logging.Logger) -> logging.Logger:
    """Initialise logger. Should only be called if handler hasn't already been
    added,

    Args:
        logger (logging.Logger): Logger to add handler to.

    Returns:
       logging.Logger: Logger with handler added.
    """
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('XDL %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
