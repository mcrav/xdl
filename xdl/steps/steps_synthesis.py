from typing import Optional, List, Union

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
        port (str): vessel port to use.
        move_speed (float): Speed in mL / min to move liquid at. (optional)
        aspiration_speed (float): Aspiration speed (speed at which liquid is
            pulled out of reagent_vessel).
        dispense_speed (float): Dispense speed (speed at which liquid is pushed
            from pump into vessel).
        time (float): Time to spend dispensing liquid. Works by changing
            dispense_speed. Note: The time given here will not be the total step
            execution time, it will be the total time spent dispensing from the
            pump into self.vessel during the addition.
        stir (bool): If True, stirring will be started before addition.
        stir_rpm (float): RPM to stir at, only relevant if stir = True.
        reagent_vessel (str): Given internally. Vessel containing reagent.
        waste_vessel (str): Given internally. Vessel to send waste to.
        flush_tube_vessel (str): Given internally. Air/nitrogen vessel to use to 
            flush liquid out of the valve -> vessel tube.
    """
    def __init__(
        self,
        reagent: str,
        vessel: str,
        volume: Optional[float] = None,
        mass: Optional[float] = None,
        port: Optional[str] = None,
        move_speed: Optional[float] = 'default',
        aspiration_speed: Optional[float] = 'default',
        dispense_speed: Optional[float] = 'default',
        time: Optional[float] = None,
        stir: Optional[bool] = False,
        stir_rpm: Optional[float] = None,
        reagent_vessel: Optional[str] = None, 
        waste_vessel: Optional[str] = None,
        flush_tube_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        # Solid addition
        if self.mass:
            self.steps = [Confirm(f'Is {reagent} ({mass} g) in {vessel}?')]
            self.human_readable = 'Add {0} ({1} g) to {2} {3}.'.format(
                self.reagent, self.mass, self.vessel, get_port_str(self.port))
            return

        if self.time:
            # dispense_speed (mL / min) = volume (mL) / time (min)
            self.dispense_speed = self.volume / (self.time / 60)

        # Liquid addition
        else:
            self.steps = [
                PrimePumpForAdd(
                    reagent=self.reagent,
                    volume='default',
                    waste_vessel=self.waste_vessel),
                CMove(
                    from_vessel=self.reagent_vessel,
                    to_vessel=self.vessel, 
                    to_port=self.port,
                    volume=self.volume,
                    move_speed=self.move_speed,
                    aspiration_speed=self.aspiration_speed,
                    dispense_speed=self.dispense_speed),
                Wait(time=DEFAULT_AFTER_ADD_WAIT_TIME)
            ]

            if self.flush_tube_vessel:
                self.steps.append(CMove(
                    from_vessel=self.flush_tube_vessel,
                    to_vessel=self.vessel,
                    to_port=self.port,
                    volume=DEFAULT_AIR_FLUSH_TUBE_VOLUME,))

            if self.stir:
                self.steps.insert(0, CStir(vessel=self.vessel))
                if self.stir_rpm:
                    self.steps.insert(
                        0, CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm))
                else:
                    self.steps.insert(
                        0, CSetStirRate(vessel=self.vessel, stir_rpm='default'))
            else:
                self.steps.insert(0, CStopStir(vessel=self.vessel))

            self.human_readable = 'Add {0} ({1} mL) to {2} {3}.'.format(
                self.reagent, self.volume, self.vessel, get_port_str(self.port))

        self.requirements = {
            'vessel': {
                'stir': self.stir,
            }
        }

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
        reagent_vessel: Optional[str] = None,
        air_vessel: Optional[str] = None,
        stir: Optional[bool] = True,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            Transfer(
                from_vessel=self.air_vessel,
                to_vessel=self.vessel,
                through=self.reagent_vessel,
                volume=self.volume)
        ]
        if self.stir:
            self.steps.insert(0, CStir(vessel=self.vessel))
        else:
            self.steps.insert(0, CStopStir(vessel=self.vessel))

        self.human_readable = 'Transfer corrosive reagent {0} ({1} mL) to {2}.'.format(
            self.reagent, self.volume, self.vessel,)

class MakeSolution(Step):
    """Make solution in given vessel of given solutes in given solvent.

    Args:
        solutes (str or list): Solute(s).
        solvent (str): Solvent.
        solute_masses (str or list): Mass(es) corresponding to solute(s)
        vessel (str): Vessel name to make solution in.
        solvent_volume (float): Volume of solvent to use in mL.
    """
    def __init__(
        self,
        solutes: Union[str, List[str]],
        solute_masses: Union[str, List[str]],
        solvent: str,
        vessel: str,
        solvent_volume: Optional[float] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = []
        self.steps.append(
            Add(reagent=solvent, volume=solvent_volume, vessel=vessel))

        self.human_readable = f'Make solution of '
        for s, m in zip(solutes, solute_masses):
            self.human_readable += '{0} ({1} g), '.format(s, m)
        self.human_readable = self.human_readable[:-2] + ' in {solvent} ({solvent_volume} mL) in {vessel}.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'stir': True,
            }
        }


####################
### FILTER STEPS ###
####################

class Filter(Step):
    """Filter contents of filter_vessel_top. Apply vacuum for given time.
    Assumes filter_filter_bottom already filled with solvent and stuff already in filter_vessel_top.

    Args:
        filter_vessel (str): Filter vessel.
        filter_top_volume (float): Volume (mL) of contents of filter top.
        wait_time (float): Time to leave vacuum on filter vessel after contents
            have been moved. (optional)
        aspiration_speed (float): Speed in mL / min to draw liquid from
            filter_vessel.
        waste_vessel (float): Given internally. Vessel to move waste material to.
        vacuum (str): Given internally. Name of vacuum flask.
        inert_gas (str): Given internally. Name of node supplying inert gas.
            Only used if inert gas filter dead volume method is being used.
    """
    def __init__(
        self,
        filter_vessel: str,
        filter_top_volume: Optional[float] = 0,
        wait_time: Optional[float] = 'default',
        aspiration_speed: Optional[float] = 'default',
        waste_vessel: Optional[str] = None,
        vacuum: Optional[str] = None,
        inert_gas: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            StopStir(vessel=self.filter_vessel),
            # Move the filter top volume from the bottom to the waste.
            CMove(
                from_vessel=self.filter_vessel,
                to_vessel=self.waste_vessel,
                from_port=BOTTOM_PORT,
                volume=self.filter_top_volume * DEFAULT_FILTER_EXCESS_REMOVE_FACTOR,
                aspiration_speed=self.aspiration_speed),
            # Connect the vacuum.
            CConnect(from_vessel=self.filter_vessel, to_vessel=self.vacuum,
                     from_port=BOTTOM_PORT),
            Wait(time=self.wait_time),
        ]

        if self.inert_gas:
            self.steps.append(
                CConnect(
                    from_vessel=self.inert_gas, to_vessel=self.filter_vessel))

        self.human_readable = 'Filter contents of {filter_vessel}.'.format(
            **self.properties)

        self.movements = [
            (self.filter_vessel, self.waste_vessel, 'all'),
        ]

        self.requirements = {
            'filter_vessel': {
                'filter': True
            }
        }

class WashFilterCake(Step):
    """Wash filter cake with given volume of given solvent.

    Args:
        filter_vessel (str): Filter vessel name to wash.
        solvent (str): Solvent to wash with.
        volume (float): Volume of solvent to wash with.
        vacuum_time (float): Time to wait after vacuum connected.
        stir (Union[float, str]): True, 'solvent' or False. True means stir from
            the start until the solvent has been removed. 'solvent' means stir
            after the solvent has been added and stop before it is removed.
            False means don't stir.
        stir_time (float): Time to stir for after solvent has been added. Only
            relevant if stir is True or 'solvent'.
        stir_rpm (float): Speed to stir at in RPM. Only relevant if stir is True
            or 'solvent'.
        waste_vessel (str): Given internally. Vessel to send waste to.
        aspiration_speed (float): Speed to remove solvent from filter_vessel.
        vacuum (str): Given internally. Name of vacuum flask.
        inert_gas (str): Given internally. Name of node supplying inert gas.
            Only used if inert gas filter dead volume method is being used.
    """
    def __init__(
        self,
        filter_vessel: str,
        solvent: str,
        volume: Optional[float] = 'default',
        vacuum_time: Optional[float] = 'default',
        stir: Optional[Union[bool, str]] = 'solvent', 
        stir_time: Optional[float] = 'default',
        stir_rpm: Optional[float] =  'default',
        waste_vessel: Optional[str] = None,
        aspiration_speed: Optional[float] = 'default',
        vacuum: Optional[str] = None,
        inert_gas: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            # Add solvent
            Add(reagent=self.solvent, volume=self.volume,
                vessel=self.filter_vessel, port=TOP_PORT, 
                waste_vessel=self.waste_vessel),
            # Stir (or not if stir=False) filter cake and solvent briefly.
            Wait(self.stir_time),
            # Remove solvent.
            CMove(
                from_vessel=self.filter_vessel,
                from_port=BOTTOM_PORT,
                to_vessel=self.waste_vessel,
                volume=self.volume * DEFAULT_FILTER_EXCESS_REMOVE_FACTOR,
                aspiration_speed=self.aspiration_speed),
            # Briefly dry under vacuum.
            CConnect(from_vessel=self.filter_vessel, to_vessel=self.vacuum,
                     from_port=BOTTOM_PORT),
            Wait(self.vacuum_time),
        ]
        # Start stirring before the solvent is added and stop stirring after the
        # solvent has been removed but before the vacuum is connected.
        if self.stir == True:
            self.steps.insert(
                0, StartStir(vessel=self.filter_vessel, stir_rpm=self.stir_rpm))
            self.steps.insert(-2, StopStir(vessel=self.filter_vessel))
        # Only stir after solvent is added and stop stirring before it is
        # removed.
        elif self.stir == 'solvent':
            self.steps.insert(
                1, StartStir(vessel=self.filter_vessel, stir_rpm=self.stir_rpm))
            self.steps.insert(-3, StopStir(vessel=self.filter_vessel))

        if self.inert_gas:
            self.steps.append(
                CConnect(
                    from_vessel=self.inert_gas, to_vessel=self.filter_vessel))

        self.human_readable = 'Wash {filter_vessel} with {solvent} ({volume} mL).'.format(
            **self.properties)

        self.requirements = {
            'filter_vessel': {
                'filter': True
            }
        }

class Dry(Step):
    """Dry given vessel by applying vacuum for given time.

    Args:
        filter_vessel (str): Vessel name to dry.
        time (float): Time to dry vessel for in seconds. (optional)
        temp (float): Temperature to dry at.
        waste_vessel (str): Given internally. Vessel to send waste to.
        vacuum (str): Given internally. Vacuum flask.
        inert_gas (str): Given internally. Name of node supplying inert gas.
            Only used if inert gas filter dead volume method is being used.
    """
    def __init__(
        self,
        filter_vessel: str,
        time: Optional[float] = 'default',
        temp: Optional[float] = None,
        waste_vessel: Optional[str] = None,
        aspiration_speed: Optional[float] = 'default',
        vacuum: Optional[str] = None,
        inert_gas: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

        self.steps = [
            StopStir(vessel=self.filter_vessel),
            # Move bulk of liquid to waste.
            CMove(
                from_vessel=self.filter_vessel,
                from_port=BOTTOM_PORT,
                to_vessel=self.waste_vessel,
                volume=DEFAULT_DRY_WASTE_VOLUME,
                aspiration_speed=self.aspiration_speed),
            # Connect the vacuum.
            CConnect(from_vessel=self.filter_vessel, to_vessel=self.vacuum,
                     from_port=BOTTOM_PORT),
            Wait(self.time),
        ]
        if self.temp != None:
            self.steps.insert(0, HeatChillToTemp(
                vessel=self.filter_vessel,
                temp=self.temp,
                vessel_type='ChemputerFilter'))

        if self.inert_gas:
            self.steps.append(
                CConnect(
                    from_vessel=self.inert_gas, to_vessel=self.filter_vessel))

        self.human_readable = 'Dry substance in {filter_vessel} for {time} s.'.format(
            **self.properties)

        self.requirements = {
            'filter_vessel': {
                'filter': True
            }
        }

########################
### SEPARATION STEPS ###
########################

class Separate(Step):
    """Extract contents of from_vessel using given amount of given solvent.
    NOTE: If n_separations > 1, to_vessel/to_port must be capable of giving
    and receiving material.

    Args:
        purpose (str): 'extract' or 'wash'. Used in iter_vessel_contents.
        from_vessel (str): Vessel name with contents to be separated.
        from_port (str): from_vessel port to use.
        separation_vessel (str): Separation vessel name.
        to_vessel (str): Vessel to send product phase to.
        to_port (str): to_vessel port to use.
        solvent (str): Solvent to extract with.
        solvent_volume (float): Volume of solvent to extract with.
        product_bottom (bool): True if product in bottom phase, otherwise False.
        n_separations (int): Number of separations to perform.
        waste_phase_to_vessel (str): Vessel to send waste phase to.
        waste_phase_to_port (str): waste_phase_to_vessel port to use.
        waste_vessel (str): Given internally. Vessel to send waste to.
    """
    def __init__(
        self,
        purpose: str,
        from_vessel: str,
        separation_vessel: str,
        to_vessel: str,
        solvent: str,
        product_bottom: bool,
        from_port: Optional[str] = None,
        to_port: Optional[str] = None,
        solvent_volume: Optional[float] = 'default',
        n_separations: Optional[float] = 1,
        waste_phase_to_vessel: Optional[str] = None,
        waste_phase_to_port: Optional[str] = None,
        waste_vessel: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())

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
                                dead_volume_target=self.waste_vessel)
            ])

        self.human_readable = 'Separate contents of {0} {1} with {2} ({3}x{4} mL). Transfer waste phase to {5} {6} and product phase to {7} {8}.'.format(
            self.from_vessel, get_port_str(self.from_port), self.solvent,
            self.n_separations, self.solvent_volume, self.waste_phase_to_vessel,
            get_port_str(self.waste_phase_to_port), self.to_vessel, self.to_port)

        self.requirements = {
            'separation_vessel': {
                'separator': True,
            }
        }

########################
### HEAT/CHILL STEPS ###
########################

class Heat(Step):
    """Heat given vessel at given temperature for given time.

    Args:
        vessel (str): Vessel to heat to reflux.
        temp (float): Temperature to heat vessel to in °C.
        time (float): Time to reflux vessel for in seconds.
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        time: float,
        stir: Optional[bool] = True,
        stir_rpm: Optional[float] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())
        print('Heat step is deprecated. Please start using HeatChill.')
        self.steps = [
            HeatToTemp(vessel=self.vessel, temp=self.temp, stir=False),
            Wait(time=self.time),
            StopHeat(vessel=self.vessel),
        ]
        if self.stir:
            self.steps.insert(0, CStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm='default'))
        else:
            self.steps.insert(0, CStopStir(vessel=self.vessel))

        self.human_readable = 'Heat {vessel} to {temp} °C for {time} s.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp],
            }
        }

class Chill(Step):
    """Chill given vessel at given temperature for given time.

    Args:
        vessel (str): Vessel to chill.
        temp (float): Temperature to chill vessel to in °C.
        time (float): Time to chill vessel for in seconds.
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        time: float,
        stir: Optional[bool] = True,
        stir_rpm: Optional[float] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())
        print('Chill step is deprecated. Please start using HeatChill.')
        self.steps = [
            ChillToTemp(vessel=self.vessel, temp=self.temp, stir=False),
            Wait(time=self.time),
            StopChiller(vessel=self.vessel)
        ]
        if self.stir:
            self.steps.insert(0, CStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm='default'))
        else:
            self.steps.insert(0, CStopStir(vessel=self.vessel))

        self.human_readable = 'Chill {vessel} to {temp} °C for {time} s.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp],
            }
        }

class HeatChill(Step):
    """Heat or chill vessel to given temp for given time.
    
    Args:
        vessel (str): Vessel to heat/chill.
        temp (float): Temperature to heat/chill vessel to in °C.
        time (float): Time to heat/chill vessel for in seconds.
        stir (bool): True if step should be stirred, otherwise False.
        stir_rpm (float): Speed to stir at in RPM. Only use if stir == True.
        vessel_type (str): Given internally. Vessel type so the step knows what
            base steps to use. 'ChemputerFilter' or 'ChemputerReactor'.
    """
    def __init__(
        self,
        vessel: str,
        temp: float,
        time: float,
        stir: bool = True, 
        stir_rpm: float = 'default',
        vessel_type: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(locals())
        self.steps = [
            HeatChillToTemp(
                vessel=self.vessel,
                temp=self.temp,
                stir=self.stir,
                stir_rpm=self.stir_rpm,
                vessel_type=self.vessel_type),
            Wait(time=self.time),
            StopHeatChill(vessel=self.vessel, vessel_type=self.vessel_type),
        ]
        if self.stir:
            self.steps.insert(0, CStir(vessel=self.vessel))
            if self.stir_rpm:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm=self.stir_rpm))
            else:
                self.steps.insert(
                    0, CSetStirRate(vessel=self.vessel, stir_rpm='default'))
        else:
            self.steps.insert(0, CStopStir(vessel=self.vessel))

        self.human_readable = 'Heat/Chill {vessel} to {temp} °C for {time} s.'.format(
            **self.properties)

        self.requirements = {
            'vessel': {
                'heatchill': True,
                'temp': [self.temp],
            }
        }

#####################
### ROTAVAP STEPS ###
#####################

class Rotavap(Step):
    """Rotavap contents of given vessel at given temp and given pressure for
    given time.

    Args:
        rotavap_name (str): Name of rotavap vessel.
        temp (float): Temperature to set rotavap water bath to in °C.
        vacuum_pressure (float): Pressure to set rotavap vacuum to in mbar.
        time (float): Time to rotavap for in seconds.
        rotation_speed (float): Speed in RPM to rotate flask at.
    """
    def __init__(
        self,
        rotavap_name: str,
        temp: float,
        pressure: float,
        time: Optional[float] = 'default',
        rotation_speed: Optional[float] = 'default',
        **kwargs
    ):
        super().__init__(locals())

        self.steps = [
            # Start rotation
            CRotavapSetRotationSpeed(self.rotavap_name, self.rotation_speed),
            CRotavapStartRotation(self.rotavap_name),

            # Lower flask into bath.
            CRotavapLiftDown(self.rotavap_name),

            # Start heating
            CRotavapSetTemp(self.rotavap_name, self.temp),
            CRotavapStartHeater(self.rotavap_name),

            # Start vacuum
            CSetVacuumSetPoint(self.rotavap_name, self.pressure),
            CStartVacuum(self.rotavap_name),
            
            # Wait for evaporation to happen.
            Wait(time=self.time),

            # Stop evaporation.
            CStopVacuum(self.rotavap_name),
            CVentVacuum(self.rotavap_name),
            CRotavapStopRotation(self.rotavap_name),
            CRotavapStopHeater(self.rotavap_name),
            CRotavapLiftUp(self.rotavap_name),            
        ]

        self.human_readable = 'Rotavap contents of {rotavap_name} at {temp} °C and {pressure} mbar for {time}.'.format(
            **self.properties)

        self.requirements = {
            'rotavap_name': {
                'rotavap': True,
            }
        }

class Column(Step):

    def __init__(self):
        super().__init__(locals())
        
        self.steps = [

        ]

        self.human_readable = 'Run column.'

class Recrystallization(Step):

    def __init__(self):
        super().__init__(locals())

        self.steps = [

        ]

        self.human_readable = 'Do recrystallisation.'

class VacuumDistillation(Step):

    def __init__(self):
        super().__init__(locals())

        self.steps = [

        ]

        self.human_readable = 'Do vacuum distillation.'
