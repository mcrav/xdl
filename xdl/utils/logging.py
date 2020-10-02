"""The main purpose of this module is to provide the ``get_logger`` function
that can be used from anywhere within the package to obtain the xdl logger.
"""
from typing import Callable
import logging
import os
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

#########################
# Duration File Handler #
#########################

duration_file_handler: logging.FileHandler = None

def duration_filter(record):
    if record.funcName != 'log_duration':
        return False
    return True


def get_logger(log_folder=None) -> logging.Logger:
    """Get logger for logging xdl messages."""
    logger = logging.getLogger('xdl')

    # Initialize file handlers if log folder given and handlers have not been
    # already added.
    if not duration_file_handler and log_folder:
        initialize_duration_file_handler(log_folder)

    # Add console handler
    logger.addHandler(console_handler)

    # Add duration file handler if it has been initialized.
    if duration_file_handler:
        logger.addHandler(duration_file_handler)

    return logger


def initialize_duration_file_handler(log_folder: str) -> None:
    """Initialize file handlers with given log folder."""
    global duration_file_handler

    # Initialize duration file handler
    duration_file_handler = logging.FileHandler(
        os.path.join(log_folder, 'step-durations.tsv'))
    formatter = logging.Formatter('%(message)s')
    duration_file_handler.setFormatter(formatter)
    duration_file_handler.setLevel(logging.INFO)
    duration_file_handler.addFilter(duration_filter)

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
        f'{start_or_end}\t{step.uuid}\t{step.name}\t{json.dumps(props)}\
\t{time.time()}'
    )
