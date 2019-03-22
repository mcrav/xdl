from ..constants import DEFAULT_VALS
from .misc import clean_properties
from typing import Dict, Any

class XDLBase(object):
    """Base object for Step, Component and Reagent objects."""

    def __init__(self, param_dict):
        params = {k: v
                  for k, v in param_dict.items()
                  if k != 'self' and not k.startswith('_')}
        if 'kwargs' in params:
            params.update(params['kwargs'])
            del params['kwargs']
        self.properties = {}
        for param in clean_properties(type(self), params):
            if param != 'self':
                self.properties[param] = params[param]
        self.get_defaults()

    def load_properties(self, properties: Dict[str, Any]) -> None:
        """Load dict of properties.
        
        Arguments:
            properties (dict): dict of property names and values.
        """
        properties = clean_properties(type(self), properties)
        for prop in self.properties:
            if prop in properties:
                self.properties[prop] = properties[prop]
        self.update()

    def update(self) -> None:
        """Reinitialise. Should be called after property dict is updated."""
        self.__init__(**self.properties)

    def get_defaults(self) -> None:
        """Replace 'default' strings with default values from constants.py."""
        for k in self.properties:
            if self.properties[k] == 'default':
                self.properties[k] = DEFAULT_VALS[self.name][k]
        
    def set_property(self, property: str, value: Any) -> None:
        self.__setattr__(property, value)

    def __setattr__(self, name: str, value: Any) -> None:
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

    def __getattr__(self, name: str) -> None:
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

    @property
    def name(self) -> str:
        """Get class name."""
        return type(self).__name__