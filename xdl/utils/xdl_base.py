from ..constants import DEFAULT_VALS

class XDLBase(object):
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

    def __setattr__(self, name, value):
        """
        If name is in self.properties do self.properties[name] = value
        Otherwise set attribute as normal.
        """
        if 'properties' in self.__dict__:
            if name in self.properties:
                self.properties[name] = value
                self.update()
            else:
                object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        """
        If name is in self.properties return self.properties[name].
        Otherwise return attribute as normal.
        """

        if 'properties' in self.__dict__:
            if name in self.properties:
                return self.properties[name]
            else:
                return object.__getattribute__(self, name)
        else:
            return object.__getattribute__(self, name)