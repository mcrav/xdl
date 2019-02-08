# XDL Steps

## Transfer steps
* *Add* -- Add given reagent to given vessel. Not much use, just slightly nicer to think like Add(acetone, reactor1, 20) than Move(flask_acetone, reactor1, 20).
* *MakeSolution* -- Add solvent to vessel and prompt user to make sure solutes are already present. Not much use atm but once solid handling is implemented this step will change.
* *Transfer* -- Move liquid from one vessel to another.

## Heating/Cooling
* *Chill* -- Set temperature on chiller start chiller and wait for the temp to be reached.
* *ChillerReturnToRT* -- Turn off chiller and wait for it to reach room temp.
* *Reflux* -- Heat given vessel and wait for given time.
* *StartHeat* -- Start heating given vessel.
* *StopHeat* -- Stop heating given vessel.
* *StartStir* -- Start stirring given vessel.
* *StopStir* -- Stop stirring given vessel.
* *StirAtRT* -- Stir given vessel without heating.

## Filtering
* *Filter* -- Connect filter flask to vacuum and draw through volume of liquid contained in it.
* *WashFilterCake* -- Add liquid to top of filter flask under vacuum.
* *Dry* -- Connect vacuum to filter flask wait then disconnect it.
* *StartVacuum* -- Connect vacuum to filter flask.
* *StopVacuum* -- Disconnect vacuum from filter flask.

## Other
* *Recrystallization* -- Unimplemented
* *Rotavap* -- Rotavap contents of a vessel to dryness and deposit them into another vessel.
* *Separate* -- Separate contents of a vessel and move product and waste phases to specified vessels.
* *VacuumDistillation* -- Unimplemented
* *Column* -- Unimplemented

## Cleaning steps
* *CleanBackbone* -- Move cleaning reagent to all waste vessels.
* *CleanVessel* -- Move cleaning reagent to given vessel, stir if possible, then move it to waste.

## Utility steps
* *Confirm* -- Ask user for confirmation of something before continuing execution.
* *Wait* -- Wait a given time.
* *PrimePumpForAdd* -- Send small amount to waste before add step.
* *PrepareFilter* -- Fill up bottom of filter vessel before adding to top.
* *RemoveFilterDeadVolume* -- Remove solvent added to bottom of filter vessel in PrepareFilter.
