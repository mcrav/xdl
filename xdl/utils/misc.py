def get_port_str(port):
    """Get str representing port for using in human_readable strings.
    
    Args:
        port (str): Port name
    
    Returns:
        str: if port is 'top' return '(port top)' if port is None return ''
    """
    if port:
        return '(port {0})'.format(port)
    return ''