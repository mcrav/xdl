from ..constants import *
from ..utils.misc import get_port_str
from .base_step import Step
from .steps_base import *
from .steps_utility import *

##################
### MOVE STEPS ###
##################

class Add(Step):
    """Add given volume of given reagent to given vessel.

    Args:
        reagent (str): Reagent to add.
        volume (float): Volume of reagent to add.
        vessel (str): Vessel name to add reagent to.
        time (float): Time to spend doing addition in seconds. (optional)
        move_speed (float): Speed in mL / min to move liquid at. (optional)
        clean_tubing (bool): Clean tubing before and after addition. (optional)
    """
    def __init__(self, reagent, volume, vessel, port=None, time=None,
                       move_speed='default', reagent_vessel=None, 
                       waste_vessel=None):

        self.properties = {
            'reagent': reagent,
            'reagent_vessel': reagent_vessel,
            'volume': volume,
            'vessel': vessel,
            'port': port,
            'time': time,
            'move_speed': move_speed,
            'waste_vessel': waste_vessel,
        }
        self.get_defaults()

        self.steps = []
        self.steps.append(PrimePumpForAdd(
            reagent=self.reagent, volume='default', 
            waste_vessel=self.waste_vessel))
        self.steps.append(
            CMove(from_vessel=self.reagent_vessel, to_vessel=self.vessel, 
                  to_port=self.port, volume=self.volume,
                  move_speed=self.move_speed))
        self.steps.append(Wait(time=DEFAULT_AFTER_ADD_WAIT_TIME))

        self.human_readable = 'Add {0} ({1} mL) to {2} {3}'.format(
            self.reagent, self.volume, self.vessel, get_port_str(self.port))
        if time:
            self.human_readable += ' over {0}'.format(self.time)
        self.human_readable += '.'

class AddCorrosive(Step):
    """Add corrosive reagent that can't come into contact with a valve.

    Args:
        reagent (str): Reagent to add.
        vessel (str): Vessel to add reagent to.
        volume (float): Volume of reagent to add.
        reagent_vessel (str): Used internally. Vessel containing reagent.
        air_vessel (str): Used internally. Vessel containing air.
    """

    def __init__(
        self,
        reagent: str,
        vessel: str,
        volume: float,
        reagent_vessel: str = None,
        air_vessel: str = None
    ) -> None:

        self.properties = {
            'reagent': reagent,
            'vessel': vessel,
            'volume': volume,
            'reagent_vessel': reagent_vessel,
            'air_vessel': air_vessel,
        }

        self.steps = [
            Transfer(from_vessel=self.air_vessel,
                     to_vessel=self.reagent_vessel,
                     volume=self.volume)
        ]

        self.human_readable = 'Transfer corrosive reagent {0} ({1} mL) to {2}.'.format(
            self.reagent, self.volume, self.vessel,)

class MakeSolution(Step):
    """Make solution in given vessel of given solutes in given solvent.

    Args:
        solute (str or list): Solute(s).
        solvent (str): Solvent.
        solute_mass (str or list): Mass(es) corresponding to solute(s)
        solvent_volume (float): Volume of solvent to use in mL.
        vessel (str): Vessel name to make solution in.
    """
    def __init__(self, solutes=None, solvent=None, solute_masses=None, solvent_volume=None, vessel=None):

        self.properties = {
            'solutes': solutes,
            'solvent': solvent,
            'solute_masses': solute_masses,
            'solvent_volume': solvent_volume,
            'vessel': vessel,
        }

        self.steps = []
        if not isinstance(solutes, list):
            solutes = [solutes]
        if not isinstance(solute_masses, list):
            solute_masses = [solute_masses]
        self.steps.append(
            Add(reagent=solvent, volume=solvent_volume, vessel=vessel))

        self.human_readable = f'Make solution of '
        for s, m in zip(solutes, solute_masses):
            self.human_readable += '{0} ({1} g), '.format(s, m)
        self.human_readable = self.human_readable[:-2] + ' in {solvent} ({solvent_volume} mL) in {vessel}.'.format(
            **self.properties)


####################
### FILTER STEPS ###
####################

class Filter(Step):
    """Filter contents of filter_vessel_top. Apply vacuum for given time.
    Assumes filter_filter_bottom already filled with solvent and stuff already in filter_vessel_top.

    Args:
        filter_vessel (str): Filter vessel.
        filter_top_volume (float): Volume (mL) of contents of filter top.
        filter_bottom_volume (float): Volume (mL) of the filter bottom.
        waste_vessel (float): Node to move waste material to.
        time (str): Time to leave vacuum on filter vessel after contents have been moved. (optional)
    """
    def __init__(self, filter_vessel, filter_top_volume=None, 
                       filter_bottom_volume=None, waste_vessel=None,
                       vacuum=None, wait_time='default'):

        self.properties = {
            'filter_vessel': filter_vessel,
            'filter_top_volume': filter_top_volume,
            'filter_bottom_volume': filter_bottom_volume,
            'waste_vessel': waste_vessel,
            'vacuum': vacuum,
            'wait_time': wait_time,
        }
        self.get_defaults()

        self.steps = [
            # Remove dead volume from bottom of filter vessel.
            CMove(
                from_vessel=self.filter_vessel, to_vessel=self.waste_vessel,
                volume=self.filter_bottom_volume),
            # Connect the vacuum.
            CConnect(from_vessel=self.filter_vessel, to_vessel=self.vacuum,
                     from_port=BOTTOM_PORT),
            Wait(time=self.wait_time),
            # Move the filter top volume from the bottom to the waste.
            CMove(
                from_vessel=self.filter_vessel, to_vessel=self.waste_vessel,
                from_port=BOTTOM_PORT, volume=self.filter_top_volume),
        ]

        self.human_readable = 'Filter contents of {filter_vessel}.'.format(
            **self.properties)

        self.movements = [
            (self.filter_vessel, self.waste_vessel, 'all'),
        ]

class WashFilterCake(Step):
    """Wash filter cake with given volume of given solvent.

    Args:
        filter_vessel (str): Filter vessel name to wash.
        solvent (str): Solvent to wash with.
        volume (float): Volume of solvent to wash with. (optional)
        wait_time (str): Time to wait after moving solvent to filter flask.
                           (optional)
    """
    def __init__(self, filter_vessel=None, solvent=None, volume='default',
                       waste_vessel=None, vacuum=None, wait_time='default'):

        self.properties = {
            'solvent': solvent,
            'filter_vessel': filter_vessel,
            'volume': volume,
            'waste_vessel': waste_vessel,
            'vacuum': vacuum,
            'wait_time': wait_time,
        }
        self.get_defaults()

        self.steps = [
            CConnect(from_vessel=self.filter_vessel, to_vessel=self.vacuum,
                     from_port=BOTTOM_PORT),
            Add(reagent=self.solvent, volume=self.volume,
                vessel=self.filter_vessel, port=TOP_PORT, 
                waste_vessel=self.waste_vessel),
            Wait(self.wait_time),
            CMove(from_vessel=self.filter_vessel, from_port=BOTTOM_PORT,
                  to_vessel=self.waste_vessel, volume=self.volume)
        ]

        self.human_readable = 'Wash {filter_vessel} with {solvent} ({volume} mL).'.format(
            **self.properties)

class Dry(Step):
    """Dry given vessel by applying vacuum for given time.

    Args:
        vessel (str): Vessel name to dry.
        time (str): Time to dry vessel for in seconds. (optional)
    """
    def __init__(self, filter_vessel=None, waste_vessel=None, vacuum=None,
                       wait_time='default'):

        self.properties = {
            'filter_vessel': filter_vessel,
            'waste_vessel': waste_vessel,
            'vacuum': vacuum,
            'wait_time': wait_time,
        }
        self.get_defaults()

        self.steps = [
            # Connect the vacuum.
            CConnect(from_vessel=self.filter_vessel, to_vessel=self.vacuum,
                     from_port=BOTTOM_PORT),
            Wait(self.wait_time),
            # Move any liquid that has dripped through to waste.
            CMove(from_vessel=self.filter_vessel, from_port=BOTTOM_PORT,
                  to_vessel=self.waste_vessel, volume=DEFAULT_DRY_WASTE_VOLUME)
        ]

        self.human_readable = 'Dry substance in {filter_vessel} for {wait_time} s.'.format(
            **self.properties)

class PrepareFilter(Step):
    """Fill bottom of filter vessel with solvent in anticipation of the filter top being used.

    Args:
        filter_vessel (str): Filter vessel name to prepare (generic name 'filter' not 'filter_filter_bottom').
        solvent (str): Solvent to fill filter bottom with.
        volume (int): Volume of filter bottom.
        waste_vessel (str): Vessel to put waste material.
    """
    def __init__(self, filter_vessel, solvent=None, volume=10, 
                       waste_vessel=None):

        self.properties = {
            'filter_vessel': filter_vessel,
            'solvent': solvent,
            'volume': volume,
            'waste_vessel': waste_vessel,
        }
        self.steps = [
            Add(reagent=self.solvent, volume=self.volume,
                vessel=self.filter_vessel, port=BOTTOM_PORT, 
                waste_vessel=waste_vessel)
        ]

        self.human_readable = 'Fill bottom of {filter_vessel} with {solvent} ({volume} mL).'.format(
            **self.properties)


########################
### SEPARATION STEPS ###
########################

class Separate(Step):
    """Extract contents of from_vessel using given amount of given solvent.
    NOTE: If n_separations > 1, to_vessel/to_port must be capable of giving
    and receiving material.

    Args:
        from_vessel (str): Vessel name with contents to be extracted.
        separation_vessel (str): Separation vessel name.
        solvent (str): Solvent to extract with.
        solvent_volume (float): Volume of solvent to extract with.
        n_separations (int): Number of separations to perform.
    """
    def __init__(self, purpose=None, from_vessel=None, from_port=None,
                       separation_vessel=None, to_vessel=None, to_port=None,
                       solvent=None, solvent_volume=None, n_separations=1,
                       product_bottom=True, waste_vessel=None,
                       waste_phase_to_vessel=None, waste_phase_to_port=None):

        self.properties = {
            'purpose': purpose,
            'from_vessel': from_vessel,
            'from_port': from_port,
            'separation_vessel': separation_vessel,
            'to_vessel': to_vessel,
            'to_port': to_port,
            'solvent': solvent,
            'solvent_volume': solvent_volume,
            'n_separations': n_separations,
            'product_bottom': product_bottom,
            'waste_phase_to_vessel': waste_phase_to_vessel,
            'waste_phase_to_port': waste_phase_to_port,
            'waste_vessel': waste_vessel, # set in prepare_for_execution
        }
        self.get_defaults()

        if not waste_phase_to_vessel and waste_vessel:
            self.waste_phase_to_vessel = waste_vessel

        if not self.n_separations:
            n_separations = 1
        else:
            n_separations = int(self.n_separations)

        self.steps = []
        self.steps.extend([
            # Move from from_vessel to separation_vessel
            Transfer(
                from_vessel=self.from_vessel, from_port=self.from_port, 
                to_vessel=self.separation_vessel, to_port=TOP_PORT, 
                volume='all'),
            # Move solvent to separation_vessel.
            Add(reagent=self.solvent, volume=self.solvent_volume, 
                vessel=self.separation_vessel, port=BOTTOM_PORT, 
                waste_vessel=self.waste_vessel),
            # Stir separation_vessel
            Stir(vessel=self.separation_vessel, 
                     time=DEFAULT_SEPARATION_FAST_STIR_TIME, 
                     stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
            Stir(vessel=self.separation_vessel, 
                     time=DEFAULT_SEPARATION_SLOW_STIR_TIME, 
                     stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
            # Wait for phases to separate
            Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
        ])

        if self.from_vessel == self.separation_vessel:
            self.steps.pop(0)

        remove_volume = 2

        # If product in bottom phase
        if self.product_bottom:
            if n_separations > 1:
                for _ in range(n_separations - 1):
                    self.steps.extend([
                        Transfer(from_vessel=self.separation_vessel, 
                                 from_port=BOTTOM_PORT, 
                                 to_vessel=self.waste_vessel, 
                                 volume=remove_volume),
                        CSeparatePhases(lower_phase_vessel=self.to_vessel, 
                                  lower_phase_port=self.to_port,
                                  upper_phase_vessel=self.waste_phase_to_vessel,
                                  upper_phase_port=self.waste_phase_to_port,
                                  separation_vessel=self.separation_vessel, 
                                  dead_volume_target=self.waste_vessel),
                        # Move to_vessel to separation_vessel
                        CMove(from_vessel=to_vessel, 
                              to_vessel=self.separation_vessel, volume='all'),
                        # Move solvent to separation_vessel. 
                        # Bottom port as washes any reagent from previous 
                        # separation back into funnel.
                        Add(reagent=self.solvent, volume=self.solvent_volume, 
                            vessel=self.separation_vessel, port=BOTTOM_PORT, 
                            waste_vessel=self.waste_vessel),
                        # Stir separation_vessel
                        Stir(vessel=self.separation_vessel, 
                                 time=DEFAULT_SEPARATION_FAST_STIR_TIME, 
                                 stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
                        Stir(vessel=self.separation_vessel, 
                                 time=DEFAULT_SEPARATION_SLOW_STIR_TIME, 
                                 stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
                        # Wait for phases to separate
                        Wait(time=DEFAULT_SEPARATION_SETTLE_TIME)
                    ])


            self.steps.extend([
                Transfer(from_vessel=self.separation_vessel, 
                         from_port=BOTTOM_PORT, to_vessel=self.waste_vessel, 
                         volume=remove_volume),
                CSeparatePhases(
                    separation_vessel=self.separation_vessel,
                    lower_phase_vessel=self.to_vessel,
                    lower_phase_port=self.to_port,
                    upper_phase_vessel=self.waste_phase_to_vessel,
                    upper_phase_port=self.waste_phase_to_port,
                    dead_volume_target=self.waste_vessel),
            ])
        else:
            if n_separations > 1:
                for _ in range(n_separations - 1):
                    self.steps.extend([
                        Transfer(from_vessel=self.separation_vessel, 
                                 from_port=BOTTOM_PORT, 
                                 to_vessel=self.waste_vessel,
                                 volume=remove_volume),
                        CSeparatePhases(
                            lower_phase_vessel=self.waste_phase_to_vessel,
                            lower_phase_port=self.waste_phase_to_port,
                            upper_phase_vessel=self.separation_vessel,
                            separation_vessel=self.separation_vessel,
                            dead_volume_target=self.waste_vessel),
                        # Move solvent to separation_vessel
                        Add(reagent=self.solvent, vessel=self.separation_vessel, 
                            port=BOTTOM_PORT, volume=self.solvent_volume, 
                            waste_vessel=self.waste_vessel),
                        # Stir separation_vessel
                        Stir(vessel=self.separation_vessel, 
                                 time=DEFAULT_SEPARATION_FAST_STIR_TIME, 
                                 stir_rpm=DEFAULT_SEPARATION_FAST_STIR_RPM),
                        Stir(vessel=self.separation_vessel, 
                                 time=DEFAULT_SEPARATION_SLOW_STIR_TIME, 
                                 stir_rpm=DEFAULT_SEPARATION_SLOW_STIR_RPM),
                        # Wait for phases to separate
                        Wait(time=DEFAULT_SEPARATION_SETTLE_TIME),
                    ])

            self.steps.extend([
                Transfer(from_vessel=self.separation_vessel, 
                         from_port=BOTTOM_PORT, to_vessel=self.waste_vessel, 
                         volume=remove_volume),
                CSeparatePhases(lower_phase_vessel=self.waste_phase_to_vessel, 
                          lower_phase_port=self.waste_phase_to_port, 
                          upper_phase_vessel=self.to_vessel,
                          upper_phase_port=self.to_port,
                          separation_vessel=self.separation_vessel,
                          dead_volume_target=self.waste_vessel),
            ])

        self.human_readable = 'Separate contents of {0} {1} with {2} ({3}x{4} mL). Transfer waste phase to {5} {6} and product phase to {7} {8}.'.format(
            self.from_vessel, get_port_str(self.from_port), self.solvent,
            self.n_separations, self.solvent_volume, self.waste_phase_to_vessel,
            get_port_str(self.waste_phase_to_port), self.to_vessel, self.to_port)


########################
### HEAT/CHILL STEPS ###
########################

class Heat(Step):
    """Heat given vessel at given temperature for given time.

    Args:
        vessel (str): Vessel to heat to reflux.
        temp (float): Temperature to heat vessel to in °C.
        time (int): Time to reflux vessel for in seconds.
    """
    def __init__(self, vessel=None, temp=None, time=None):

        self.properties = {
            'vessel': vessel,
            'temp': temp,
            'time': time,
        }

        self.steps = [
            StartHeat(vessel=self.vessel, temp=self.temp),
            Wait(time=self.time),
            StopHeat(vessel=self.vessel),
        ]
        self.human_readable = 'Heat {vessel} to {temp} °C and reflux for {time} s.'.format(
            **self.properties)


#####################
### ROTAVAP STEPS ###
#####################

class Rotavap(Step):
    """Rotavap contents of given vessel at given temp and given pressure for
    given time.

    Args:
        vessel (str): Vessel with contents to be rotavapped.
        temp (float): Temperature to set rotary evaporator water bath to in °C.
        pressure (float): Pressure to set rotary evaporator vacuum to in mbar.
        time (int): Time to rotavap for in seconds.
    """
    def __init__(self, rotavap_vessel=None, temp=None, vacuum_pressure=None,
                       time='default', rotation_speed=None, waste_vessel=None,
                       distillate_volume=None):

        self.properties = {
            'rotavap_vessel': rotavap_vessel,
            'temp': temp,
            'vacuum_pressure': vacuum_pressure,
            'rotation_speed': rotation_speed,
            'waste_vessel': waste_vessel,
            'distillate_volume': distillate_volume,
            'time': time,
        }
        self.get_defaults()

        # Steps incomplete
        self.steps = [
            # Lower flask start rotation.
            CSwitchCartridge(self.rotavap_vessel, 0),
            CLiftArmDown(self.rotavap_vessel),
            CSetRvRotationSpeed(self.rotavap_vessel, self.rotation_speed),
            CStartRotation(self.rotavap_vessel),

            # Degas
            CSetVacSp(self.rotavap_vessel, DEFAULT_ROTAVAP_DEGAS_PRESSURE),
            CStartVac(self.rotavap_vessel),
            CSetBathTemp(self.rotavap_vessel, self.temp),
            CStartHeaterBath(self.rotavap_vessel),
            Wait(DEFAULT_ROTAVAP_DEGAS_TIME),

            # Main distillation
            CSetVacSp(self.rotavap_vessel, self.vacuum_pressure),
            Wait(self.time),

            # Vent and empty
            CLiftArmUp(self.rotavap_vessel),
            CWait(DEFAULT_ROTAVAP_VENT_TIME),
            StopVacuum(self.rotavap_vessel),
            CVentVac(self.rotavap_vessel),
            CMove(from_vessel=self.rotavap_vessel, from_port=BOTTOM_PORT,
                  to_vessel=self.waste_vessel, volume=self.distillate_volume),
            
            # Dry
            CLiftArmDown(self.rotavap_vessel),
            CSetVacSp(self.rotavap_vessel, self.vacuum_pressure),
            CStartVac(self.rotavap_vessel),
            CWait(self.time),
            
            # Recover flask and vent
            CLiftArmUp(self.rotavap_vessel),
            Wait(DEFAULT_ROTAVAP_VENT_TIME),
            CStopVac(self.rotavap_vessel),
            CVentVac(self.rotavap_vessel),
            CStopRotation(self.rotavap_vessel),
            CStopHeaterBath(self.rotavap_vessel),
            CMove(from_vessel=self.rotavap_vessel, from_port=BOTTOM_PORT,
                  to_vessel=self.waste_vessel, volume=self.distillate_volume),
            Wait(DEFAULT_ROTAVAP_VENT_TIME),
        ]

        self.human_readable = 'Rotavap contents of {rotavap_vessel} at {temp} °C for {time}.'.format(
            **self.properties)

class Column(Step):

    def __init__(self):
        self.properties = {

        }
        
        self.steps = [

        ]

        self.human_readable = 'Run column.'

class Recrystallization(Step):

    def __init__(self):
        self.properties = {

        }

        self.steps = [

        ]

        self.human_readable = 'Do recrystallisation.'

class VacuumDistillation(Step):

    def __init__(self):
        self.properties = {

        }

        self.steps = [

        ]

        self.human_readable = 'Do vacuum distillation.'
