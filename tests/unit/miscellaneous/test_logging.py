import logging
import os
import pytest
import re
import time
from xdl import XDL
from chempiler.tools.logging import console_filter
from ...utils import get_chempiler

HERE = os.path.abspath(os.path.dirname(__file__))
FOLDER = os.path.join(HERE, '..', 'files')

os.makedirs('chempiler_output', exist_ok=True)
TEMP_LOG_FILE = 'chempiler_output/logging-test.txt'

TESTS = [
    ('async.xdl', 'bigrig.json'),
    ('repeat_parent.xdl', 'bigrig.json'),
    ('async_advanced.xdl', 'async_advanced.json')
]

class RemoveANSIFormatter(logging.Formatter):
    """Formatter to remove ANSI codes introduced by user of ``termcolor``.

    Necessary for saving logs to file.
    """
    ansi_re = re.compile(r'\x1b\[[0-9;]*m')

    def format(self, record):
        return re.sub(self.ansi_re, '', record.msg)


test_handler = logging.FileHandler(TEMP_LOG_FILE)
test_handler.setFormatter(RemoveANSIFormatter())
test_handler.addFilter(console_filter)
test_handler.setLevel(logging.INFO)

def add_logging_handler():
    """Add logging handler to xdl logger that will save logs to a temporary
    test file for verification.
    """
    logger = logging.getLogger('xdl')
    # Make folder that will be git ignored
    logger.addHandler(test_handler)

def remove_logging_handler():
    """Remove test logging handler."""
    logger = logging.getLogger('xdl')
    logger.removeHandler(test_handler)

@pytest.mark.unit
def test_logging_step_indexes():
    """Test that there are no irregular patterns in step indexes in execution
    logs.
    """
    # Add test handler to save logs to file
    add_logging_handler()

    # Go through all tests
    for xdl_f, graph_f in TESTS:
        # Try to run the test and verify the logs
        try:
            graph_full_f = os.path.join(FOLDER, graph_f)

            # Reset test log file
            if os.path.exists(TEMP_LOG_FILE):
                with open(TEMP_LOG_FILE, 'w') as fd:
                    fd.write('')

            # Execute test file execution
            c = get_chempiler(graph_full_f)
            x = XDL(os.path.join(FOLDER, xdl_f))
            x.prepare_for_execution(graph_full_f, testing=True)
            x.execute(c)

            # Wait for all threads to finish
            if xdl_f.startswith('async'):
                time.sleep(2)

            # Verify the logs
            verify_logs()

        # In the case an exception is thrown during the test, log the test files
        # that failed before raising the exception.
        except Exception as e:
            logger = logging.getLogger('xdl')
            logger.exception(f'Failed: {xdl_f} {graph_f}')
            raise e

    # Cleanup. Remove the temporary log file and the test logging handler.
    os.remove(TEMP_LOG_FILE)
    remove_logging_handler()

def verify_logs():
    """Verify log files contain no errors. Conditions checked for:

    1. All step starts have a corresponding step end.
    2. There are no duplicate step starts or step ends.
    """
    # Get step starts / ends in format [('start', '1.4'), ('end', '1.4')...] in
    # the order that they appear in the log file.
    step_index_rows = parse_logs()
    open_indexes = []
    all_indexes = []
    for start_or_finish, step_index in step_index_rows:
        # Store all step indexes encountered
        all_indexes.append(step_index)

        # Track which steps have been started and finished to check that there
        # is a start and finish for all steps.
        if start_or_finish == 'start':
            open_indexes.append(step_index)
        else:
            try:
                open_indexes.remove(step_index)
            except ValueError:
                raise ValueError(
                    f'Step finish logged without corresponding step start\
{step_index}'
                )
    # Assert condition 1, all step starts have a corresponding step end.
    assert not open_indexes

    # Assert condition 2, there are no duplicate step starts or step ends.
    assert len(set(all_indexes)) == len(all_indexes) / 2

def parse_logs():
    """Convert logs to list of step starts and ends in format:
    [('start', '1'), ('start', '1.1'), ('end', '1.1'), ('end', '1')...]
    """
    # Searches for 2.2.1 etc. Allows 30 levels of depth.
    index_re = r'[0-9]' + r'(\.)?[0-9]?' * 30

    # Extract lines
    with open(TEMP_LOG_FILE, 'r') as fd:
        lines = [line.strip() for line in fd.readlines() if line.strip()]

    # Extract lines containing step starts / finishes
    step_index_lines = []
    for line in lines:
        if line.startswith(('Executing step', 'Finished executing step')):
            step_index_lines.append(line)

    # Convert step starts and finishes to (start/end, step_index) format.
    step_index_rows = []
    for line in step_index_lines:
        if line.startswith('Executing step'):
            step_index_rows.append(
                ('start', re.search(index_re, line)[0])
            )
        else:
            step_index_rows.append(
                ('end', re.search(index_re, line)[0])
            )
    return step_index_rows
