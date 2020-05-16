from typing import Dict, Any, List, Union
from .sanitisation import clean_properties
from .logging import get_logger
from ..errors import XDLMissingDefaultPropError
from ..utils.prop_limits import PropLimit

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
    called. This sanitizes values and adds defaults as necessary.

    Editing the properties dict directly should be avoided as it means prop
    sanitization and validation is skipped. If this is necessary, for example
    you wish to update a lot of properties and then update for performance
    reasons, then you can update the properties dict directly, but you must call
    update afterwards.

    This system is quite weird when you're not used to it. It seems like
    witchcraft accessing member variables that don't seem to be initialized
    anywhere. But once you're used to it, it speeds up development massively as
    you can very quickly access / change properties with minimal typing.
    """

    # Prop specification variables

    # List of properties that should always be written, even if they are the
    # same as default values. For example, you may have default 20 mL volume for
    # WashSolid. This does not mean that you don't want to write it, otherwise
    # the XDL is unclear over how much solvent is used when reading it.
    ALWAYS_WRITE: List[str] = []

    # Dictionary of values to pass in for properties when their value is given
    # as 'default'.
    DEFAULT_PROPS: Dict[str, Any] = {}

    # List of properties that should never be passed in as args, and are instead
    # calculated automatically from the graph during on_prepare_for_execution.
    INTERNAL_PROPS: List[str] = []

    # PROP_TYPES gives the type of every prop
    #
    # Explicitly handled types:
    #   str       Remains unchanged
    #   int       Parsed as int
    #   float     Either parsed as float, or units removed from string such as
    #             '2 mL' and remainer of string parsed as float and converted to
    #             standard units based on units in string
    #   bool      Parsed as bool
    #   List[str] Parsed as space separated list of strings
    #   'vessel'  Vessel declared in Hardware section of XDL
    #   'reagent' Reagent declared in Reagents section of XDL
    #
    # Any other type will just remain unchanged during sanitization.
    PROP_TYPES: Dict[str, Union[type, str]] = {}

    # Defines detailed validation criteria for all props in the form of
    # PropLimit objects. If no prop limit is given for a prop, then a default
    # prop limit will be used based on the prop type.
    PROP_LIMITS: Dict[str, PropLimit] = {}

    # properties dict. Holds all current values of the properties of the step,
    # as described by the prop specification variables above.
    properties: Dict[str, Any] = {}

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

        Means that whenever new props are supplied they are sanitized and
        defaults added.

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
        self.update. The purpose of this is that so whenever a property is
        changed, it is sanitized and default values are added.

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
