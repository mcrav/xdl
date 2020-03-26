import sys

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

class XDLValueError(Exception):
    pass
