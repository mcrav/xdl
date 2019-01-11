##########################
Making custom step classes
##########################

All step classes inherit the class :class:`xdl.utils.Step`.

Three member variables must be set in the `__init__` function: `properties`, `steps` and `human_readable`.

.. code-block:: python

    from xdl import Step
    from xdl.steps import Add, StirAtRT

    class AddAndStir(Step):
        
        def __init__(self):
        
            self.properties = {
                'volume': volume,
                'vessel': vessel,
                'reagent': reagent,
                'stir_time': stir_time,
            }

            self.steps = [
                Add(reagent=reagent, vessel=vessel, volume=volume),
                StirAtRT(vessel=vessel, time=stir_time)
            ]

            self.human_readable = 'Add {0} ({1} mL) to {2} and stir for {3} minutes.'.format(
                add_vessel, volume, stir_vessel, stir_time / 60)