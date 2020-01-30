===================
Making Custom Steps
===================

Any custom steps should inherit `xdl.steps.AbstractStep`.

Methods to implement:

- `__init__`: Take `properties` argument and call `super().__init__(locals())`
- `get_steps`: Return a list of steps to be executed when the step is executed.
- `requirements` (optional): Override this property method if step requires anything listed in table below. Returns dictionary of requirement and value.
- `human_readable` (optional): If not overridden the class name will be returned as human_readable. Method should take `language='en'` keyword argument and return human_readable based on language code.

Requirements options are as follows:

+------------+------------+
| Requirement|   Default  |
+============+============+
| heatchill  |   False    |
+------------+------------+
| filter     |   False    |
+------------+------------+
| separator  |   False    |
+------------+------------+
| rotavap    |   False    |
+------------+------------+
| temp       |      []    |
+------------+------------+

Examples
--------

.. code-block:: python

    from xdl.steps import AbstractStep, Add, Stir

    class AddAndStir(AbstractStep):

        def __init__(self, properties: Dict[str, Any]):
            super().__init__(locals())

        def get_steps(self):
            return [
                Add(reagent=self.reagent, vessel=self.vessel, volume=self.volume),
                Stir(vessel=self.vessel, time=self.stir_time)
            ]

.. code-block:: python

    from xdl.steps import AbstractStep, Add, HeatChill

    class AddAndHeat(AbstractStep):

        def __init__(self, properties: Dict[str, Any]):
            super().__init__(locals())

        def get_steps(self):
            return [
                Add(reagent=self.reagent, vessel=self.vessel, volume=self.volume),
                HeatChill(vessel=self.vessel, temp=self.temp, time=self.time)
            ]

        @property
        def requirements(self):
            return {
                'heatchill': True,
                'temp': [self.temp]
            }

        def human_readable(self, language: str = 'en'):
            return f'Add {self.reagent} ({self.volume} mL) to {self.vessel} and heat {self.vessel} at {self.temp} °C for {self.time / 60} mins.'
