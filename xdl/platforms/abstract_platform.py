from typing import Optional, Callable, Union, List, Dict, Any
import json
import abc
from ..utils.schema import generate_schema
from ..steps import Step
from ..reagents import Reagent
from ..hardware import Component

class AbstractPlatform(object):
    """Container class to hold everything necessary for a platform to be used
    with the XDL framework.
    """
    def __init__(self):
        pass

    @property
    @abc.abstractmethod
    def executor(self):
        return None

    @property
    @abc.abstractmethod
    def step_library(self):
        return None

    @abc.abstractmethod
    def graph(
        self,
        graph_template: Optional[str] = None,
        save: Optional[str] = None,
        **kwargs
    ):
        return

    @property
    def schema(self):
        return generate_schema(self.step_library)

    @property
    def localisation(self):
        return {}

    @property
    def declaration(self):
        type_str_dict = {
            str: 'str',
            int: 'int',
            float: 'float',
            bool: 'bool',
            Callable: 'func',
            Union[str, int]: 'str or int',
            List[str]: 'List[str]',
            Union[bool, str]: 'bool or str',
            Union[Step, List[Step]]: 'List[Step] or Step',
            List[Any]: 'List[Any]',
            Dict[str, Any]: 'Dict[str, Any]',
        }
        return {
            'steps': [
                {
                    'name': step_name,
                    'PROP_TYPES': {
                        k: type_str_dict[v] for k, v in step.PROP_TYPES.items()
                    },
                    'DEFAULT_PROPS': step.DEFAULT_PROPS,
                    'INTERNAL_PROPS': step.INTERNAL_PROPS,
                    'ALWAYS_WRITE': step.ALWAYS_WRITE,
                    'PROP_LIMITS': {
                        prop: {
                            'regex': prop_limit.regex,
                            'hint': prop_limit.hint,
                            'default': prop_limit.default,
                        }
                        for prop, prop_limit in step.PROP_LIMITS.items()
                    },
                    'localisation': self.localisation.get(step_name, {})
                }
                for step_name, step in self.step_library.items()
                if (hasattr(step, 'PROP_TYPES')
                    and not step_name.startswith('Abstract'))
            ],
            'Reagent': {
                'name': 'Reagent',
                'PROP_TYPES': {
                    k: type_str_dict[v] for k, v in Reagent.PROP_TYPES.items()
                },
                'DEFAULT_PROPS': Reagent.DEFAULT_PROPS,
                'INTERNAL_PROPS': Reagent.INTERNAL_PROPS,
                'ALWAYS_WRITE': Reagent.ALWAYS_WRITE,
                'PROP_LIMITS': {
                    prop: {
                        'regex': prop_limit.regex,
                        'hint': prop_limit.hint,
                        'default': prop_limit.default,
                    }
                    for prop, prop_limit in Reagent.PROP_LIMITS.items()
                }
            },
            'Component': {
                'name': 'Component',
                'PROP_TYPES': {
                    k: type_str_dict[v] for k, v in Component.PROP_TYPES.items()
                },
                'DEFAULT_PROPS': Component.DEFAULT_PROPS,
                'INTERNAL_PROPS': Component.INTERNAL_PROPS,
                'ALWAYS_WRITE': Component.ALWAYS_WRITE,
                'PROP_LIMITS': {
                    prop: {
                        'regex': prop_limit.regex,
                        'hint': prop_limit.hint,
                        'default': prop_limit.default,
                    }
                    for prop, prop_limit in Component.PROP_LIMITS.items()
                }
            }
        }

    def save_declaration(self, save_path):
        with open(save_path, 'w') as fd:
            json.dump(self.declaration, fd, indent=2)
