# Steps

## Add
### Attributes
* reagent
* volume
* vessel
* time (optional)
* move_speed (optional)
* clean_tubing (optional)
* comment (optional)


## Breakpoint
### Attributes
* comment (optional)


## Chill
### Attributes
* vessel
* temp
* comment (optional)


## ChillBackToRT
### Attributes
* vessel
* comment (optional)


## ChillReact
### Attributes
* reagents
* volumes
* vessel
* temp
* comment (optional)


## ChillerWaitForTemp
### Attributes
* vessel
* comment (optional)


## CleanTubing
### Attributes
* vessel
* solvent (optional)
* volume (optional)
* comment (optional)


## CleanVessel
### Attributes
* vessel
* solvent (optional)
* volume (optional)
* stir_rpm (optional)
* comment (optional)


## Comment
### Attributes
* comment (optional)


## Dry
### Attributes
* vessel
* time (optional)


## Extract
### Attributes
* from_vessel
* solvent
* solvent_volume
* n_separations


## Filter
### Attributes
* from_vessel
* vessel
* time (optional)


## GetVacSp
### Attributes
* vacuum_pump_name
* comment (optional)


## HeatAndReact
### Attributes
* vessel
* time
* temp
* stir_rpm (optional)
* comment (optional)


## InitVacPump
### Attributes
* vacuum_pump_name
* comment (optional)


## LiftArmDown
### Attributes
* rotavap_name
* comment (optional)


## LiftArmUp
### Attributes
* rotavap_name
* comment (optional)


## MakeSolution
### Attributes
* solute
* solvent
* solute_mass
* solvent_volume
* vessel
* comment (optional)


## Move
### Attributes
* from_vessel
* to_vessel
* volume
* move_speed (optional)
* aspiration_speed (optional)
* dispense_speed (optional)
* comment (optional)


## Prime
### Attributes
* aspiration_speed (optional)
* comment (optional)


## PrimePumpForAdd
### Attributes
* reagent
* move_speed (optional)


## RampChiller
### Attributes
* vessel
* ramp_duration
* end_temperature
* comment (optional)


## Reflux
### Attributes
* vessel
* temp
* time
* comment (optional)


## Repeat
### Attributes
* repeat_n_times
* steps
* comment (optional)


## ResetRotavap
### Attributes
* rotavap_name
* comment (optional)


## Rotavap
### Attributes
* vessel
* temp
* pressure
* time


## RvWaitForTemp
### Attributes
* rotavap_name
* comment (optional)


## Separate
### Attributes
* lower_phase_target
* upper_phase_target
* comment (optional)


## SetBathTemp
### Attributes
* rotavap_name
* temp
* comment (optional)


## SetChiller
### Attributes
* vessel
* temp
* comment (optional)


## SetCoolingPower
### Attributes
* vessel
* cooling_power
* comment (optional)


## SetInterval
### Attributes
* rotavap_name
* interval
* comment (optional)


## SetRecordingSpeed
### Attributes
* recording_speed
* comment (optional)


## SetRvRotationSpeed
### Attributes
* rotavap_name
* rotation_speed
* comment (optional)


## SetSpeedSp
### Attributes
* vacuum_pump_name
* set_point
* comment (optional)


## SetStirRpm
### Attributes
* vessel
* stir_rpm
* comment (optional)


## SetTemp
### Attributes
* vessel (optional)
* temp (optional)
* comment (optional)


## SetVacSp
### Attributes
* vacuum_pump_name
* set_point
* comment (optional)


## StartChiller
### Attributes
* vessel
* comment (optional)


## StartHeat
### Attributes
* vessel
* comment (optional)


## StartHeat
### Attributes
* vessel
* temp
* comment (optional)


## StartHeaterBath
### Attributes
* rotavap_name
* comment (optional)


## StartRotation
### Attributes
* rotavap_name
* comment (optional)


## StartStir
### Attributes
* vessel
* comment (optional)


## StartStir
### Attributes
* vessel
* stir_rpm (optional)
* comment (optional)


## StartVac
### Attributes
* vacuum_pump_name
* comment (optional)


## StartVacuum
### Attributes
* vessel
* comment (optional)


## StirAndTransfer
### Attributes
* from_vessel
* to_vessel
* volume
* stir_rpm (optional)
* comment (optional)


## StirToRT
### Attributes
* vessel
* comment (optional)


## StirrerWaitForTemp
### Attributes
* vessel
* comment (optional)


## StopChiller
### Attributes
* vessel
* comment (optional)


## StopHeat
### Attributes
* vessel (optional)
* comment (optional)


## StopHeaterBath
### Attributes
* rotavap_name
* comment (optional)


## StopRotation
### Attributes
* rotavap_name
* comment (optional)


## StopStir
### Attributes
* vessel
* comment (optional)


## StopVac
### Attributes
* vacuum_pump_name
* comment (optional)


## StopVacuum
### Attributes
* vessel
* comment (optional)


## SwitchCartridge
### Attributes
* flask
* cartridge
* comment (optional)


## SwitchChiller
### Attributes
* solenoid_valve_name
* state
* comment (optional)


## SwitchColumn
### Attributes
* column
* destination
* comment (optional)


## SwitchVacuum
### Attributes
* vessel
* destination
* comment (optional)


## VentVac
### Attributes
* vacuum_pump_name
* comment (optional)


## Wait
### Attributes
* time
* comment (optional)


## Wash
### Attributes
* solvent
* vessel
* volume (optional)
* move_speed (optional)
* wait_time (optional)
* comment (optional)


