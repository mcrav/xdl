================
Making New Steps
================

All steps should inherit :code:`xdl.steps.AbstractStep`.

Attributes to implement:

- :code:`PROP_TYPES`: The types of all __init__ arguments except self and
  **kwargs.
- :code:`DEFAULT_PROPS`: Default values for any keyword arguments with the
  default set as 'default'.
- :code:`INTERNAL_PROPS`: Internal properties that are filled in using the graph
  in :code:`on_prepare_for_execution`. These properties are never written when
  outputting XDL files.
- :code:`ALWAYS_WRITE`: Usually properties are not written to file if there
  value is the same as the value defined in :code:`DEFAULT_PROPS`. If the
  property is included here, it will always be written even if it is the
  default.

Methods to implement:

- :code:`__init__`: Take properties with type annotations as arguments
  and call :code:`super().__init__(locals())`
- :code:`get_steps`: Return a list of steps to be executed when the step is executed.
- :code:`on_prepare_for_execution`: Make any graph specific changes to the steps
  required. Note: For the Chemputer, a lot is done by the executor,
  so this should just be anything that needs to be done in addition to that.
- :code:`sanity_checks`: This returns a list of xdl.utils.misc.SanityCheck
  objects which are checked at the end of :code:`prepare_for_execution`. If the
  condition is not matched an error is raised with the associated message.
  :code:`prepare_for_execution` sequence. It should raise informative errors if
  any of the final set of properties don't make sense.

Example
-------

.. code-block:: python

    from xdl.steps import AbstractStep, Add, Stir, Transfer
    from networkx import MultiDiGraph

    # Class must inherit AbstractStep
    class QuantitativeTransfer(AbstractStep):

        # Define any properties to be given if 'default' given as value.
        DEFAULT_PROPS = {
            'solvent_volume': '50 mL',
            'stir_time': '1 min'
        }

        # Types of all properties
        PROP_TYPES = {
            'from_vessel': str,
            'to_vessel': str,
            'solvent': str,
            'solvent_volume': float,
            'stir_time': float,
        }

        INTERNAL_PROPS = []

        # __init__ method must contain properties with type annotations and **kwargs.
        def __init__(
            self,
            from_vessel: str,
            to_vessel: str,
            solvent: str,
            solvent_volume: float = 'default',
            stir_time: float = 'default'
        ):
            # Super call converts all args to standard units / types and creates
            # self.properties dict.
            # After this all properties supplied to __init__ will be available as
            # member variables, i.e. self.from_vessel, self.to_vessel etc.
            super().__init__(locals())

        def on_prepare_for_execution(self, graph: MultiDiGraph):
            """Fill in any properties that can only be taken from the graph."""
            # In this case nothing needs to be done.
            return

        def final_sanity_check(self, graph: MultiDiGraph):
            """Check all properties make sense."""
            try:
                assert self.from_vessel
            except AssertionError:
                raise XDLError('No from_vessel given.')

            try:
                assert self.to_vessel
            except AssertionError:
                raise XDLError('No to_vessel given.')

            try:
                assert self.solvent
            except AssertionError:
                raise XDLError('No solvent given.')

            try:
                assert self.solvent_volume > 0
            except AssertionError:
                raise XDLError('Solvent volume must be > 0.')

        def get_steps(self):
            """Return steps to be executed."""
            return [
                # Transfer liquid to target flask.
                Transfer(
                    from_vessel=self.from_vessel,
                    to_vessel=self.to_vessel,
                    volume='all',
                ),

                # Add solvent to source flask.
                Add(
                    vessel=self.from_vessel,
                    reagent=self.solvent,
                    volume=self.solvent_volume,
                ),

                # Stir solvent in source flask.
                Stir(
                    vessel=self.vessel,
                    time=self.stir_time,
                ),

                # Transfer solvent / washings to target flask.
                Transfer(
                    from_vessel=self.from_vessel,
                    to_vessel=self.to_vessel,
                    volume=self.solvent_volume,
                ),
            ]
