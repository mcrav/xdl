# Steps

## Add
Add given volume of given reagent to given vessel.
### Constructor Arguments
* reagent {str} -- Reagent to add.  
* volume {float} -- Volume of reagent to add.  
* vessel {str} -- Vessel name to add reagent to.  
* time {float} -- Time to spend doing addition in seconds. (optional)  
* move_speed {float} -- Speed in mL / min to move liquid at. (optional)  
* clean_tubing {bool} -- Clean tubing before and after addition. (optional)  
- - -
## Breakpoint
Introduces a breakpoint in the script. The execution is halted until the operator  
- - -
## Chill
Chill vessel to given temperature.
### Constructor Arguments
* vessel {str} -- Vessel name to chill.  
* temp {float} -- Temperature in °C to chill to.  
- - -
## ChillBackToRT
Chill given vessel back to room temperature.
### Constructor Arguments
* vessel {str} -- Vessel name to chill.  
- - -
## ChillReact
Add given volumes of given reagents to given vessel, chill to given temperature,
### Constructor Arguments
* reagents {list} -- List of reagents to add to vessel.  
* volumes {list} -- List of volumes corresponding to list of reagents.  
* vessel {str} -- Vessel name to add reagents to and chill.  
* temp {float} -- Temperature to chill vessel to in °C.  
* time {int} -- Time to leave reagents for in seconds.  
- - -
## ChillerWaitForTemp
Delays the script execution until the current temperature of the chiller is within
### Constructor Arguments
* vessel {str} -- Vessel to wait for temperature. Name of the node the chiller is attached to.  
- - -
## CleanTubing
Clean tubing with given reagent.
### Constructor Arguments
* reagent {str} -- Reagent to clean tubing with.  
* volume {float} -- Volume to clean tubing with in mL. (optional)  
- - -
## CleanVessel
Clean given vessel.
### Constructor Arguments
* vessel {str} -- Vessel to clean.  
* solvent {str} -- Solvent to clean with. (optional)  
* volume {str} -- Volume of solvent to clean with in mL. (optional)  
* stir_rpm {str} -- RPM to stir vessel at during cleaning. (optional)  
* stir_time {str} -- Time to stir once solvent has been added. (optional)  
- - -
## Dry
Dry given vessel by applying vacuum for given time.
### Constructor Arguments
* vessel {str} -- Vessel name to dry.  
* time {str} -- Time to dry vessel for in seconds. (optional)  
- - -
## Extract
Extract contents of from_vessel using given amount of given solvent.
### Constructor Arguments
* from_vessel {str} -- Vessel name with contents to be extracted.  
* separation_vessel {str} -- Separation vessel name.  
* solvent {str} -- Solvent to extract with.  
* solvent_volume {float} -- Volume of solvent to extract with.  
* n_separations {int} -- Number of separations to perform.  
- - -
## Filter
Filter contents of from_vessel in filter_vessel. Apply vacuum for given time.
### Constructor Arguments
* from_vessel {str} -- Vessel to filter contents of.  
* filter_vessel {str} -- Filter vessel.  
* time {str} -- Time to leave vacuum on filter vessel after contents have been moved. (optional)  
- - -
## GetVacSp
Reads the current vacuum setpoint.
### Constructor Arguments
* vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.  
- - -
## HeatAndReact
Under stirring, heat given vessel to given temp and wait for given time
### Constructor Arguments
* vessel {str} -- Vessel to heat.  
* time {float} -- Time to leave vessel under heating/stirring in seconds.  
* temp {float} -- Temperature to heat to in °C.  
* stir_rpm {int} -- RPM to stir at. (optional)  
- - -
## InitVacPump
Initialises the vacuum pump controller.
### Constructor Arguments
* vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.  
- - -
## LiftArmDown
Lifts the rotary evaporator down.
### Constructor Arguments
* rotavap_name {str} -- Name of the node representing the rotary evaporator.  
- - -
## LiftArmUp
Lifts the rotary evaporator arm up.
### Constructor Arguments
* rotavap_name {str} -- Name of the node representing the rotary evaporator.  
- - -
## MakeSolution
Make solution in given vessel of given solutes in given solvent.
### Constructor Arguments
* solute {str or list} -- Solute(s).  
* solvent {str} -- Solvent.  
* solute_mass {str or list} -- Mass(es) corresponding to solute(s)  
* solvent_volume {[type]} -- Volume of solvent to use in mL.  
* vessel {[type]} -- Vessel name to make solution in.  
- - -
## Move
Moves a specified volume from one node in the graph to another. Moving from and to
### Constructor Arguments
* from_vessel {str} -- Vessel name to move from.  
* to_vessel {str} -- Vessel name to move to.  
* volume {float} -- Volume to move in mL. 'all' moves everything.  
* move_speed -- Speed at which liquid is moved in mL / min. (optional)  
* aspiration_speed -- Speed at which liquid aspirates from from_vessel. (optional)  
* dispense_speed -- Speed at which liquid dispenses from from_vessel. (optional)  
- - -
## Prime
Moves the tube volume of every node with "flask" as class to waste.
### Constructor Arguments
* aspiration_speed {float} -- Speed in mL / min at which material should be withdrawn.  
- - -
## PrimePumpForAdd
Prime pump attached to given reagent flask in anticipation of Add step.
### Constructor Arguments
* reagent {str} -- Reagent to prime pump for addition.  
* move_speed {str} -- Speed to move reagent at. (optional)  
- - -
## RampChiller
Causes the chiller to ramp the temperature up or down. Only available for Petite
### Constructor Arguments
* vessel {str} -- Vessel to ramp chiller on. Name of the node the chiller is attached to.  
* ramp_duration {int} -- Desired duration of the ramp in seconds.  
* end_temperature {float} -- Final temperature of the ramp in °C.  
- - -
## Reflux
Reflux given vessel at given temperature for given time.
### Constructor Arguments
* vessel {str} -- Vessel to heat to reflux.  
* temp {float} -- Temperature to heat vessel to in °C.  
* time {int} -- Time to reflux vessel for in seconds.  
- - -
## ResetRotavap

### Constructor Arguments
* rotavap_name {str} -- Name of the node representing the rotary evaporator.  
- - -
## Rotavap
Rotavap contents of given vessel at given temp and given pressure for given time.
### Constructor Arguments
* vessel {str} -- Vessel with contents to be rotavapped.  
* temp {float} -- Temperature to set rotary evaporator water bath to in °C.  
* pressure {float} -- Pressure to set rotary evaporator vacuum to in mbar.  
* time {int} -- Time to rotavap for in seconds.  
- - -
## RvWaitForTemp
Delays the script execution until the current temperature of the heating bath is
### Constructor Arguments
* rotavap_name {str} -- Name of the node representing the rotary evaporator.  
- - -
## Separate
Launches a phase separation sequence. The name of the separator is currently
### Constructor Arguments
* lower_phase_vessel {str} -- Vessel name the lower phase should be transferred to.  
* upper_phase_vessel {str} -- Vessel name the upper phase should be transferred to.  
* If "separator_top" is specified, the upper phase is left in the separator.  
- - -
## SetBathTemp
Sets the temperature setpoint for the heating bath.
### Constructor Arguments
* rotavap_name {str} -- Name of the node representing the rotary evaporator.  
* temp {float} -- Temperature in °C.  
- - -
## SetChiller
Sets the temperature setpoint.
### Constructor Arguments
* vessel {str} -- Vessel to set chiller temperature. Name of the node the chiller is attached to.  
* temp {float} -- Temperature in °C.  
- - -
## SetCoolingPower
Sets the cooling power (0-100%). Only available for CF41.
### Constructor Arguments
* vessel -- Vessel to set cooling power of chiller. Name of the node the chiller is attached to.  
* cooling_power -- Desired cooling power in percent.  
- - -
## SetInterval
Sets the interval time for the rotary evaporator, causing it to periodically switch
### Constructor Arguments
* rotavap_name {str} -- Name of the node representing the rotary evaporator.  
* interval {int} -- Interval time in seconds.  
- - -
## SetRecordingSpeed
Sets the timelapse speed of the camera module.
### Constructor Arguments
* recording_speed {float} -- Factor by which the recording should be sped up, i.e. 2 would mean twice the normal speed. 1 means normal speed.  
- - -
## SetRvRotationSpeed
Sets the rotation speed setpoint for the rotary evaporator.
### Constructor Arguments
* rotavap_name {str} -- Name of the node representing the rotary evaporator.  
* rotation_speed {str} -- Rotation speed setpoint in RPM.  
- - -
## SetSpeedSp
Sets the speed of the vacuum pump (0-100%).
### Constructor Arguments
* vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.  
* vacuum_pump_speed {float} -- Vacuum pump speed in percent.  
- - -
## SetStirRpm
Sets the stirring speed setpoint of a hotplate or overhead stirrer.
### Constructor Arguments
* vessel {str} -- Vessel name to set stir speed.  
* stir_rpm {float} -- Stir speed in RPM.  
- - -
## SetTemp
Sets the temperature setpoint of a hotplate stirrer. This command is NOT available
### Constructor Arguments
* vessel {str} -- Vessel name to set temperature of hotplate stirrer.  
* temp {float} -- Temperature in °C  
- - -
## SetVacSp
Sets a new vacuum setpoint.
### Constructor Arguments
* vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.  
* vacuum_pressure {float} -- Vacuum pressure setpoint in mbar.  
- - -
## StartChiller
Starts the recirculation chiller.
### Constructor Arguments
* vessel {str} -- Vessel to chill. Name of the node the chiller is attached to.  
- - -
## StartHeat
Starts the heating operation of a hotplate stirrer.
### Constructor Arguments
* vessel {str} -- Vessel name to heat.  
- - -
## StartHeat
Start heating given vessel at given temperature.
### Constructor Arguments
* vessel {str} -- Vessel name to heat.  
* temp {float} -- Temperature to heat to in °C.  
- - -
## StartHeaterBath
Starts the heating bath of a rotary evaporator.
### Constructor Arguments
* rotavap_name {str} -- Name of the node representing the rotary evaporator.  
- - -
## StartRotation
Starts the rotation of a rotary evaporator.
### Constructor Arguments
* rotavap_name {str} -- Name of the node representing the rotary evaporator.  
- - -
## StartStir
Starts the stirring operation of a hotplate or overhead stirrer.
### Constructor Arguments
* vessel {str} -- Vessel name to stir.  
- - -
## StartStir
Start stirring given vessel.
### Constructor Arguments
* vessel {str} -- Vessel name to stir.  
* stir_rpm {int} -- Speed in RPM to stir at. (optional)  
- - -
## StartVac
Starts the vacuum pump.
### Constructor Arguments
* vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.  
- - -
## StartVacuum
Start vacuum pump attached to given vessel.
### Constructor Arguments
* vessel {str} -- Vessel name to start vacuum on.  
- - -
## StirAndTransfer
Stir vessel while transfering contents to another vessel.
### Constructor Arguments
* from_vessel {str} -- Vessel name to transfer from.  
* to_vessel {str} -- Vessel name to transfer to.  
* volume {float} -- Volume to transfer in mL.  
* stir_rpm {str} -- Speed to stir from_vessel at in RPM.  
- - -
## StirToRT
Set vessel temperature to room temperature, and continue stirring until
### Constructor Arguments
* vessel {str} -- Vessel to continue stirring until room temperature is reached.  
- - -
## StirrerWaitForTemp
Delays the script execution until the current temperature of the hotplate is within
### Constructor Arguments
* vessel {str} -- Vessel name to wait for temperature.  
- - -
## StopChiller
Stops the recirculation chiller.
### Constructor Arguments
* vessel {str} -- Vessel to stop chilling. Name of the node the chiller is attached to.  
- - -
## StopHeat
Starts the stirring operation of a hotplate stirrer. This command is NOT available
### Constructor Arguments
* vessel {str} -- Vessel name to stop heating.  
- - -
## StopHeaterBath
Stops the heating bath of a rotary evaporator.
### Constructor Arguments
* rotavap_name {str} -- Name of the node representing the rotary evaporator.  
- - -
## StopRotation
Stops the rotation of a rotary evaporator.
### Constructor Arguments
* rotavap_name {str} -- Name of the node representing the rotary evaporator.  
- - -
## StopStir
Stops the stirring operation of a hotplate or overhead stirrer.
### Constructor Arguments
* vessel {str} -- Vessel name to stop stirring.  
- - -
## StopVac
Stops the vacuum pump.
### Constructor Arguments
* vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.  
- - -
## StopVacuum
Stop vacuum pump attached to given vessel.
### Constructor Arguments
* vessel {str} -- Vessel name to stop vacuum on.  
- - -
## SwitchCartridge
Switches a cartridge carousel to the specified position.
### Constructor Arguments
* vessel {str} -- Name of the node the vacuum valve is logically attacked to (e.g. "rotavap")  
* cartridge {int} -- Number of the position the carousel should be switched to (0-5)  
- - -
## SwitchChiller
Switches the solenoid valve.
### Constructor Arguments
* solenoid_valve_name -- {str} Name of the node the solenoid valve is attached to.  
* state {str} -- Is either "on" or "off"  
- - -
## SwitchColumn
Switches a fractionating valve attached to a chromatography column.
### Constructor Arguments
* column {str} -- Name of the column in the graph  
* destination {str} -- Either "collect" or "waste"  
- - -
## SwitchVacuum
Switches a vacuum valve between backbone and vacuum.
### Constructor Arguments
* vessel {str} -- Name of the node the vacuum valve is logically attacked to (e.g. "filter_bottom")  
* destination {str} -- Either "vacuum" or "backbone"  
- - -
## VentVac
Vents the vacuum pump to ambient pressure.
### Constructor Arguments
* vacuum_pump_name {str} -- Name of the node the vacuum pump is attached to.  
- - -
## Wait
Delays execution of the script for a set amount of time. This command will
### Constructor Arguments
* time -- Time to wait in seconds.  
- - -
## Wash
Wash filter cake with given volume of given solvent.
### Constructor Arguments
* filter_vessel {str} -- Filter vessel name to wash.  
* solvent {str} -- Solvent to wash with.  
* volume {float} -- Volume of solvent to wash with. (optional)  
* move_speed {str} -- Speed to move solvent in mL / min. (optional)  
* wait_time {str} -- Time to wait after moving solvent to filter flask. (optional)  
- - -
