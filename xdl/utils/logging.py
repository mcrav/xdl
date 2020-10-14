"""The main purpose of this module is to provide the ``get_logger`` function
that can be used from anywhere within the package to obtain the xdl logger.
"""
from typing import Callable
import logging
import json
import time
if False:
    from ..steps import Step

# The reason for having all handlers as global variables is to avoid adding
# duplicate handlers when you do repeated calls of `logger.addHandler(handler)`.
# `logging.addHandler(handler)` will not add the handler if the exact handler
# object is already in `logger.handlers`.

###################
# Console Handler #
###################

def console_filter(record):
    if record.funcName == 'log_duration':
        return False
    return True


console_handler: logging.StreamHandler = logging.StreamHandler()
formatter = logging.Formatter('XDL: %(message)s')
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
console_handler.addFilter(console_filter)


def get_logger() -> logging.Logger:
    """Get logger for logging xdl messages."""
    logger = logging.getLogger('xdl')

    # Add console handler
    logger.addHandler(console_handler)

    return logger

def log_duration(step: 'Step', start_or_end: str):
    """Log start and end of step execution with timestamps for the purpose of
    later determining step duration.

    step (Step): Step being executed.
    start_or_end (str): One of 'start' or 'end',  depending on whether the step
        is beginning or ending.
    """
    # Don't log duration for these special wrapper steps.
    if step.name in ['Callback', 'Repeat', 'Loop']:
        return

    # Get logger
    logger = logging.getLogger('xdl')

    # Filter props not to include non JSON serializable props.
    props = {
        k: v
        for k, v in step.properties.items()
        if k != 'children' and step.PROP_TYPES[k] != Callable
    }

    # Log line to duration tsv file
    logger.info(
        f'{start_or_end}\t{time.time():.2f}\t{step.uuid}\t{step.name}\t\
{json.dumps(props)}'
    )
