import re
import itertools
import lxml.etree as etree
from .constants import DEFAULT_VALS

class XDLElement(object):
    """Base object for Step, Component and Reagent objects."""

    def __init__(self):
        self.name = ''
        self.properties = {}

    def load_properties(self, properties):
        """Load dict of properties.
        
        Arguments:
            properties {dict} -- dict of property names and values.
        """
        for prop in self.properties:
            if prop in properties:
                self.properties[prop] = properties[prop]
        self.update()

    def update(self):
        """Reinitialise. Should be called after property dict is updated."""
        self.__init__(**self.properties)

    def get_defaults(self):
        """Replace 'default' strings with default values from constants.py."""
        for k in self.properties:
            if self.properties[k] == 'default':
                try:
                    self.properties[k] = DEFAULT_VALS[self.name][k]
                except KeyError as e:
                    print(self.name)
                    print(k)
                    raise KeyError
                    
class Step(XDLElement):
    """Base class for all step objects."""
    
    def __init__(self):
        self.name = ''
        self.properties = {}
        self.steps = []

    def as_xdl(self, as_str=False):
        """
        Return self as a XDL lxml.etree._Element,
        or if as_str=True as a XDL str.
        """
        step = etree.Element('step')
        step.set('name', self.name)
        for prop, val in self.properties.items():
            if val != '':
                element = etree.SubElement(step, 'property')
                element.set('name', prop)
                element.text = str(val)
        if as_str:
            return etree.dump(step)
        else:
            return step

    def execute(self, chempiler):
        """
        Execute self with given Chempiler object.
        
        Arguments:
            chempiler {chempiler.Chempiler} -- Initialised Chempiler object.
        """
        for step in self.steps:
            keep_going = step.execute(chempiler)
            if not keep_going:
                return False
        return True

float_regex = r'([0-9]+([.][0-9]+)?)' # Should match, '1', '11', '1.1', '1.01', '13.12' etc.

### Unit Words ###

VOLUME_CL_UNIT_WORDS = ('cl', 'cL',)
VOLUME_ML_UNIT_WORDS = ('cc', 'ml','mL', 'cm3')
VOLUME_DL_UNIT_WORDS = ('dl', 'dL')
VOLUME_L_UNIT_WORDS = ('l', 'L')

MASS_G_UNIT_WORDS = ('g', 'grams')
MASS_KG_UNIT_WORDS = ('kg', 'kilograms')
MASS_MG_UNIT_WORDS = ('mg', 'milligrams')
MASS_UG_UNIT_WORDS = ('ug', 'micrograms')


### Convert quantity strs to floats with standard units ###

def convert_time_str_to_seconds(time_str):
    """Convert time str to float with unit seconds i.e. '2hrs' -> 7200."""
    time_str = time_str.lower()
    if time_str.endswith(('h', 'hr', 'hrs', 'hour', 'hours', )):
        multiplier = 3600
    elif time_str.endswith(('m', 'min', 'mins', 'minute', 'minutes')):
        multiplier = 60
    elif time_str.endswith(('s', 'sec', 'secs', 'second', 'seconds',)):
        multiplier = 1
    else:
        multiplier = 1
    return float(re.match(float_regex, time_str).group(1)) * multiplier

def convert_volume_str_to_ml(volume_str):
    """Convert volume str to float with unit mL i.e. '1l' -> 1000.""" 
    volume_str = volume_str.lower()
    if volume_str.endswith(VOLUME_ML_UNIT_WORDS):
        multiplier = 1
    elif volume_str.endswith(VOLUME_L_UNIT_WORDS):
        multiplier = 1000
    elif volume_str.endswith(VOLUME_DL_UNIT_WORDS):
        multiplier = 100
    elif volume_str.endswith(VOLUME_CL_UNIT_WORDS):
        multiplier = 10
    return float(re.match(float_regex, volume_str).group(1)) * multiplier

def convert_mass_str_to_g(mass_str):
    """Convert mass str to float with unit grams i.e. '20mg' -> 0.02."""
    mass_str = mass_str.lower()
    if mass_str.endswith(MASS_G_UNIT_WORDS):
        multiplier = 1
    elif mass_str.endswith(MASS_KG_UNIT_WORDS):
        multiplier = 1000
    elif mass_str.endswith(MASS_MG_UNIT_WORDS):
        multiplier = 1e-3
    elif mass_str.endswith(MASS_UG_UNIT_WORDS):
        multiplier = 1e-6
    return float(re.match(float_regex, mass_str).group(1)) * multiplier

def find_reagent_obj(reagent_id, reagents):
    """Return reagent object, given reagent_id and list of reagents."""
    reagent_obj = None
    for reagent in reagents:
        if reagent_id == reagent.properties['id']:
            reagent_obj = reagent
            break
    return reagent_obj

def cas_str_to_int(cas_str):
    """Convert CAS str to int. i.e. '56-43-1' -> 56431"""
    if cas_str:
        return int(cas_str.replace('-', ''))
    else:
        return None