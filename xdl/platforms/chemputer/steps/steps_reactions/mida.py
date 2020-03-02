from typing import Optional

from ..steps_synthesis import (
    Add,
    Dissolve,
    Evaporate
)
from ..steps_utility import (
    Evacuate,
    HeatChillToTemp,
    Transfer,
    Stir,
    StartStir
)

from .....step_utils.special_steps import Repeat

from .....step_utils.base_steps import AbstractStep
from ..base_step import ChemputerStep

from ...utils.execution import (
    get_nearest_node, get_inert_gas_vessel, get_reagent_vessel)
from ...constants import CHEMPUTER_WASTE
from .....utils.misc import SanityCheck
from networkx import MultiDiGraph

# Class must inherit AbstractStep, ChemputerStep
class MIDACoupling(ChemputerStep, AbstractStep):

    DEFAULT_PROPS = {
        'solvent': 'THF',
        'solvent_volume': '28 mL',
        'rxn_temp': '55°C',
        'rxn_time': '12 hrs',
        'addition_speed': '4 hrs',
        'evacuations': 3,
        'after_inert_gas_wait_time': '1 minute',
        'after_vacuum_wait_time': '1 minute',
        'boronic_acid_solution_volume': '20 mL',
        'rinses': 2,
    }

    PROP_TYPES = {
        'reactor': str,
        'holding_flask': str,
        'rotavap': str,
        'boronic_acid': str,
        'boronic_acid_mass': float,
        'base': str,
        'base_mass': float,
        'halide': str,
        'halide_mass': float,
        'catalyst': str,
        'catalyst_mass': float,
        'solvent': str,
        'solvent_volume': float,
        'rxn_temp': float,
        'rxn_time': float,
        'addition_speed': float,
        'evacuations': int,
        'after_inert_gas_wait_time': float,
        'after_vacuum_wait_time': float,
        'boronic_acid_solution_volume': float,
        'rinses': int,
        'solvent_vessel': str,
        'inert_gas': str,
        'waste_vessel': str,
    }

    INTERNAL_PROPS = [
        'waste_vessel',
        'solvent_vessel',
        'inert_gas',
    ]

    def __init__(
        self,

        # Platform vessels
        reactor: Optional[str],
        holding_flask: Optional[str],
        rotavap: Optional[str],  # obviously platform specific

        # Reagent related properties
        boronic_acid: Optional[str] = None,
        boronic_acid_mass: Optional[float] = None,  # should really be equiv.
        base: Optional[str] = None,
        base_mass: Optional[float] = None,
        halide: Optional[str] = None,
        halide_mass: Optional[float] = None,  # should have 'scale' property
        catalyst: Optional[str] = None,
        catalyst_mass: Optional[float] = None,
        solvent: Optional[str] = 'default',

        # Process related properties
        solvent_volume: Optional[float] = 'default',  # should be concentration
        rxn_temp: Optional[float] = 'default',
        rxn_time: Optional[float] = 'default',
        addition_speed: Optional[float] = 'default',
        evacuations: Optional[int] = 'default',
        after_inert_gas_wait_time: Optional[float] = 'default',
        after_vacuum_wait_time: Optional[float] = 'default',
        boronic_acid_solution_volume: Optional[float] = 'default',
        rinses: Optional[int] = 'default',

        # Internal props
        solvent_vessel: str = None,
        waste_vessel: str = None,
        inert_gas: str = None,
        **kwargs
    ):
        super().__init__(locals())

    def on_prepare_for_execution(self, graph: MultiDiGraph):
        self.waste_vessel = get_nearest_node(
            graph, self.reactor, CHEMPUTER_WASTE)

        self.inert_gas = get_inert_gas_vessel(graph, self.reactor)

        self.solvent_vessel = get_reagent_vessel(graph, self.solvent)

    def sanity_checks(self, graph: MultiDiGraph):
        """Check all properties make sense."""
        return [
            SanityCheck(
                condition=self.solvent_volume > 0,
                error_msg='Solvent volume must be > 0.'
            ),

            SanityCheck(
                condition=self.boronic_acid_mass > 0,
                error_msg=f'Boronic acid mass must be > 0 g.'
            ),

            SanityCheck(
                condition=self.base_mass > 0,
                error_msg=f'Base mass must be > 0 g.'
            ),


        ]

    def get_steps(self):
        """Return steps to be executed."""
        return [
            # Deoxygenate reactor
            Evacuate(
                vessel=self.reactor,
                evacuations=self.evacuations,
                after_inert_gas_wait_time=self.after_inert_gas_wait_time,
                after_vacuum_wait_time=self.after_vacuum_wait_time,
            ),

            # Deoxygenate holding flask
            Evacuate(
                vessel=self.holding_flask,
                evacuations=self.evacuations,
                after_inert_gas_wait_time=self.after_inert_gas_wait_time,
                after_vacuum_wait_time=self.after_vacuum_wait_time,
            ),

            # Deoxygenate backbone
            Transfer(
                from_vessel=self.inert_gas,
                to_vessel=self.waste_vessel,  # obviously not transferable
                volume='125 mL',
            ),

            # Add boronic acid to holding flask
            Add(
                vessel=self.holding_flask,
                reagent=self.boronic_acid,
                mass=self.boronic_acid_mass,  # obviously not general of ICC
                stir=False,
            ),

            # Add base to reactor
            Add(
                vessel=self.reactor,
                reagent=self.base,
                mass=self.base_mass,
                stir=False,
            ),

            # Add catalyst to reactor
            Add(
                vessel=self.reactor,
                reagent=self.catalyst,
                mass=self.catalyst_mass,
                stir=False,
            ),

            # Add halide to reactor
            Add(
                vessel=self.reactor,
                reagent=self.halide,
                mass=self.halide_mass,
                stir=False,
            ),

            # Dissolve boronic acid
            Dissolve(
                vessel=self.holding_flask,
                solvent=self.solvent,
                volume=self.boronic_acid_solution_volume,
            ),

            # Deoxygenate holding flask
            Evacuate(
                vessel=self.holding_flask,
                evacuations=self.evacuations,
                after_inert_gas_wait_time=self.after_inert_gas_wait_time,
                after_vacuum_wait_time=self.after_vacuum_wait_time,
            ),

            # Deoxygenate reactor
            Evacuate(
                vessel=self.reactor,
                evacuations=self.evacuations,
                after_inert_gas_wait_time=self.after_inert_gas_wait_time,
                after_vacuum_wait_time=self.after_vacuum_wait_time,
            ),

            # Add solvent to reactor
            Add(
                reagent=self.solvent,
                vessel=self.reactor,
                volume=self.solvent_volume,
                stir=True,
            ),

            # Deoxygenate reactor
            Evacuate(
                vessel=self.reactor,
                evacuations=self.evacuations,
                after_inert_gas_wait_time=self.after_inert_gas_wait_time,
                after_vacuum_wait_time=self.after_vacuum_wait_time,
            ),

            # Heat reactor to temperature
            HeatChillToTemp(
                vessel=self.reactor,
                temp=self.rxn_temp,
            ),

            # Slow addition of boronic acid to reactor
            Transfer(
                from_vessel=self.holding_flask,
                to_vessel=self.reactor,
                volume='all',
                time=self.addition_speed,
            ),

            # Rinse holding flask
            Repeat(
                repeats=self.rinses,
                children=[
                    Add(
                        reagent=self.solvent,
                        vessel=self.holding_flask,
                        volume='5 mL',
                        stir=True,
                    ),
                    Transfer(
                        from_vessel=self.holding_flask,
                        to_vessel=self.reactor,
                        volume='5 mL'
                    )
                ]
            ),

            # stir reaction mixture for length of reaction
            Stir(
                vessel=self.reactor,
                time=self.rxn_time,
            ),

            # reduce speed for in-line filtration
            StartStir(
                vessel=self.reactor,
                stir_speed=50,
            ),

            # in-line filtration
            # possibly have to add through_node='filtration_cartridge"
            Transfer(
                from_vessel=self.reactor,
                to_vessel=self.rotavap,
                volume='100 mL',  # higher than actual volume but needed
                aspiration_speed=5,
            ),

            # Rinse reactor and make sure reactor is empty
            # possibly have to add through_node='filtration_cartridge"
            Repeat(
                repeats=self.rinses,
                children=[
                    Add(
                        reagent=self.solvent,
                        vessel=self.reactor,
                        volume='10 mL',
                        stir=True,
                    ),
                    Transfer(
                        from_vessel=self.reactor,
                        to_vessel=self.rotavap,
                        volume='100 mL',
                        aspiration_speed=5,
                    ),
                ],
            ),

            # Evaporate solvent
            Evaporate(
                mode='auto',
                time='30 mins',
                pressure='249 mbar',
                temp='50°C',
                rotavap_name=self.rotavap,
            ),
        ]
