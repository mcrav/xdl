# Should match, '1', '11', '1.1', '1.01', '13.12' etc.
float_regex: str = r'([0-9]+([.][0-9]+)?)'

def parse_bool(s: str) -> bool:
    """Parse string for bool."""
    if s.strip().lower() in ['true', '1']:
        return True
    elif s.strip().lower() in ['false', '0']:
        return False
    return None
