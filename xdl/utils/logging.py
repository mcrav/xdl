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
    handler.addFilter(console_filter)
    return handler

def get_duration_file_handler(log_folder) -> logging.FileHandler:
    handler = logging.FileHandler(
        os.path.join(log_folder, 'step-durations.tsv'))
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    handler.addFilter(duration_filter)
    return handler

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

def console_filter(record):
    if record.funcName == 'log_duration':
        return False
    return True

def duration_filter(record):
    if record.funcName != 'log_duration':
        return False
    return True
