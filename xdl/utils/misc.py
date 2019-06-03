from typing import Any, Optional

def get_port_str(port: str) -> str:
    """Get str representing port for using in human_readable strings.
    
    Args:
        port (str): Port name
    
    Returns:
        str: if port is 'top' return '(port top)' if port is None return ''
    """
    if port:
        return '(port {0})'.format(port)
    return ''

def format_property(
    prop: str, val: Any, human_readable: Optional[bool] = True) -> str:
    """Given property key and value in standard units, convert value
    to sensitive units and return str ready for putting in XDL.
    E.g. time: 3600 -> '1 hr', volume 2000 -> '2 l'.
    If no modifications are required just return str of val.
    
    Args:
        prop (str): Property name.
        val (Any): Property value.
        human_readable (Optional[bool]): If True, ports will be represented as
            (port top) as they should be in human readable sentences, if False,
            will be unaltered as it is for XDL file generation.
    
    Returns:
        str: Value converted to nice units if necessary and returned
            as neat str ready for outputting.
    """
    if val == None:
        return None

    if 'time' in prop:
        return format_time(val)
    
    elif 'volume' in prop:
        return format_volume(val)

    elif 'mass' in prop:
        return format_mass(val)

    elif 'temp' in prop:
        return format_temp(val)
    
    elif 'pressure' in prop:
        return format_pressure(val)

    elif 'port' in prop and human_readable:
        return get_port_str(val)

    elif 'stir_rpm' in prop:
        return format_stir_rpm(val)

    elif prop in ['n_separations', 'repeat', 'cleans', 'eluting_repeats']:
        return format_int(val)

    elif type(val) == list:
        return ' '.join([str(item) for item in val])

    return str(val)
    
def format_int(val) -> str:
    if val != None:
        return str(int(val))

def format_stir_rpm(val: float) -> str:
    """Return formatted stir speed in RPM.
    
    Args:
        val (float): Stir speed in RPM.
    
    Returns:
        str: Formatted stir speed in RPM.
    """
    return f'{val} RPM'

def format_pressure(val_mbar: float)  -> str:
    """Return formatted pressure in sensible units.
    
    Args:
        val_mbar (float): Pressure in mbar.
    
    Returns:
        str: Formatted pressure in sensible units.
    """
    return f'{val_mbar} mbar'

def format_volume(val_ml: float) -> str:
    """Return formatted volume in sensible units.
    
    Args:
        val_ml (float): Volume in mL.
    
    Returns:
        str: Formatted volume in sensible units.
    """
    if val_ml == 'all':
        return val_ml
    # litres
    if val_ml > 1000:
        l = val_ml / 1000
        return f'{format_val(l)} l'
    # microlitres
    elif val_ml < 0.1:
        ul = val_ml * 1000
        return f'{format_val(ul)} ul'
    # millilitres
    return f'{format_val(val_ml)} mL'

def format_time(val_seconds: float) -> str:
    """Return formatted time in sensible units.
    
    Args:
        val_seconds (float): Time in seconds.
    
    Returns:
        str: Formatted time in sensible units.
    """
    val = val_seconds
    if val_seconds > 60:
        minutes = val_seconds / 60
        # hours
        if minutes > 60:
            hours = minutes / 60
            val_str = f'{format_val(hours)} hrs'
            val = hours
        # minutes
        else:
            val_str = f'{format_val(minutes)} mins'
            val = minutes
    # seconds
    else:
        val_str = f'{format_val(val_seconds)} secs'
    # Convert '1 hrs' to '1 hr'.
    if val == 1:
        val_str = val_str[:-1]
    return val_str
    
def format_mass(val_grams: float) -> str:
    """Return formatted mass in sensible units.
    
    Args:
        val_grams (float): Mass in grams.
    
    Returns:
        str: Formatted mass in sensible units.
    """
    if val_grams > 1000:
        # kilograms
        kg = val_grams / 1000
        return f'{format_val(kg)} kg'
    elif val_grams < 0.1:
        # milligrams
        mg = val_grams * 1000
        return f'{format_val(mg)} mg'
    # grams
    return f'{format_val(val_grams)} g'

def format_temp(val_celsius: float) -> str:
    """Return formatted temperature.
    
    Args:
        val_celsius (float): Temperature in °C.
    
    Returns:
        str: Formatted temperature. 
    """
    if type(val_celsius) == str: # 'reflux' or 'None'
        return val_celsius
    else:
        return f'{format_val(val_celsius)}°C'

def format_val(val: float) -> str:
    """Format float and return as str. Rules are round to two decimal places,
    then remove any trailing 0s and decimal point if necessary.
    
    Args:
        val (float): Number to format.
    
    Returns:
        str: Number rounded to two decimal places with trailing '0' and '.'
            removed.
    """
    hours_str = f'{val:.2f}'
    return hours_str.rstrip('0').rstrip('0').rstrip('.')
    