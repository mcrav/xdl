from .sanitisation import clean_properties
from .logging import get_logger
from ..errors import XDLMissingDefaultPropError
from typing import Dict, Any

class XDLBase(object):
    """Base object for Step, Component and Reagent objects. The functionality
    this class provides is all based around the properties dict. This class has
    a variables self.properties. This is initialized with whatever is passed to
    the constructor of the subclass, according to the prop specification of
    the subclass (PROP_TYPES, DEFAULT_PROPS) etc.

    This is where XDLBase subclasses become funky. After initialization,
    everything in the properties dict, so everything that was passed to the
    constructor == everything in PROP_TYPES, can be accessed as a class
    attribute, due to the __getattr__ and __setattr__ overrides here.

    So taking a step as an example:

    `step.volume` is exactly the same value as `step.properties[volume]`

    In the case of getting one of these variables, you could use either of those
    syntaxes and get exactly the same result. This is not the case however when
    setting the values of properties.

    `step.volume = 15` is not the same as `step.properties[volume] = 15`

    The override of __setattr__ means that when any value in the properties dict
    is set, as well as updating the properties dict, the update method is
    called. In this class just updates the properties dict with the new value,
    sanitizing values and adding defaults as necessary. But in AbstractStep,
    update is overridden, so that any updates to the properties dict also update
    the steps list in AbstractStep subclasses.

    So `step.volume = 15` updates the properties dict, and then updates the
    steps list in AbstractStep. AbstractStep is the only XDLBase subclass that
    overrides update. Even for other classes however, editing the properties
    dict directly should be avoided as it means prop sanitization and validation
    is skipped. If this is necessary, for example you wish to update a lot of
    properties and then update for performance reasons, then you can update the
    properties dict directly, but you must call update afterwards.

    This system is quite weird when you're not used to it. It seems like
    witchcraft accessing member variables that don't seem to be initialized
    anywhere. But once you're used to it, it speeds up development massively as
    you can very quickly access / change properties with minimal typing, and
    without worrying about updating the underlying step list in AbstractStep
    subclasses.
    """

    # Prop specification variables
    DEFAULT_PROPS = {}
    INTERNAL_PROPS = []
    PROP_TYPES = {}
    ALWAYS_WRITE = []
    PROP_LIMITS = {}

    # properties dict
    properties = {}

    def __init__(self, param_dict: Dict[str, Any]) -> None:
        """Initialize properties dict and loggger."""
        # Remove stuff like self that isn't a property as param dict comes from
        # `locals()`
        properties = {
            k: v for k, v in param_dict.items() if k in self.PROP_TYPES
        }

        # Initialize properties dict
        self.properties = {}

        # Load properties into self.properties
        self.load_properties(properties)

        # Initialize logger
        self.logger = get_logger()

    @property
    def name(self) -> str:
        """Get class name."""
        return type(self).__name__

    def get_defaults(self, properties: Dict[str, Any]) -> None:
        """Replace 'default' strings with default values from DEFAULT_PROPS.

        Args:
            properties (Dict[str, Any]): properties dict to add default values
                to.

        Raises:
            XDLMissingDefaultPropError: If 'default' given for property but no
                default value given in DEFAULT_PROPS
        """
        # Use DEFAULT_PROPS dict in step class if it exists.

        for k in properties:
            # 'default' given as value for prop
            if properties[k] == 'default':

                # Default value found in DEFAULT_PROPS, update properties
                if k in self.DEFAULT_PROPS:
                    properties[k] = self.DEFAULT_PROPS[k]

                # Default value not found in DEFAULT_PROPS, raise error
                else:
                    raise XDLMissingDefaultPropError(self.name, k)

    def load_properties(self, properties: Dict[str, Any]) -> None:
        """Load dict of properties into self.properties.
        Add default values from DEFAULT_PROPS where 'default' is given as value.
        Sanitize properties according to PROP_LIMITS.

        Arguments:
            properties (Dict[str, Any]): dict of property names and values.
        """
        # If property given as 'default' add in value from DEFAULT_PROPS
        self.get_defaults(properties)

        # Sanitise properties according to PROP_LIMITS
        properties = clean_properties(type(self), properties)

        # Add new properties to self.properties
        for prop in self.PROP_TYPES:
            if prop in properties:
                self.properties[prop] = properties[prop]

    def update(self, properties={}) -> None:
        """update is called whenever __setattr__ updates the properties dict, so
        for example `step.volume = 15` would cause this to be called. It can
        also be called explicitly if the properties dict is edited directly.

        Here it is just a wrapper round load_properties, but the purpose of this
        is that in AbstractStep it is overridden and triggers the step list to
        be updated after the property dict has changed.

        Args:
            properties (Dict[str, Any]): New properties to load into
                self.properties. If empty, assuume that self.properties has been
                changed directly and reload self.properties.
        """
        # If properties dict not given assume self.properties has been changed
        # directly and updated using this.
        if not properties:
            properties = self.properties

        # Load properties
        self.load_properties(properties)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        If name is in self.properties do self.properties[name] = value and call
        self.update. The purpose of this is that AbstractStep overrides update,
        and recreates its steps list whenever a property is changed. This means
        you can do `step.volume = 15` and update the internal step list under
        the hood.

        If attr is not in self.properties just set attribute as normal.
        """
        # attr in self.properties, add to properties dict and update
        if name in self.properties:
            self.properties[name] = value
            self.update()

        # attr not in self.properties, update as normal
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name: str) -> None:
        """
        If name is in self.properties return self.properties[name].
        Otherwise return attribute as normal.
        """
        # attr in self.properties, return value from self.properties
        if name in self.properties:
            return self.properties[name]

        # attr not in self.properties, return as normal
        else:
            return object.__getattribute__(self, name)
