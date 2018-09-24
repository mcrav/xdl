# Namespace

## Components
* Reactor
* FilterFlask
* Separating Funnel
* RotaryEvaporator

## Steps
### ChASM 
#### Pump
* CMove
* CHome (no execute method)
* CSeparate
* CPrime
* CSwitchVacuum
* CSwitchCartridge
* CSwitchColumn

#### Stirrer
* CStartStir
* CStartHeat
* CStopStir
* CStopHeat
* CSetTemp
* CSetStirRpm
* CStirrerWaitForTemp

#### Rotavap
* CStartHeaterBath
* CStopHeaterBath
* CStartRotation
* CStopRotation
* CLiftArmUp
* CLiftArmDown
* CResetRotavap
* CSetBathTemp
* CSetRvRotationSpeed
* CRvWaitForTemp
* CSetInterval

#### Vacuum Pump
* CInitVacPump
* CGetVacSp
* CSetVacSp
* CStartVac
* CStopVac
* CVentVac
* CSetSpeedSp

#### Chiller
* CStartChiller
* CStopChiller
* CSetChiller
* CChillerWaitForTemp
* CRampChiller
* CSwitchChiller
* CSetCoolingPower

#### Camera
* CSetRecordingSpeed

#### Generic
* CWait
* CBreakpoint

### XDL
Name - level (how far up tree Step is)
* StartStir - 1
* StartHeat - 1
* StartVacuum - 1
* StopVacuum - 1
* ContinueStirToRT - 1 
* Chill - 1
* ChillBackToRT - 1
* CleanTubing - 1

* CleanVessel - 2 (StartStir)
* HeatAndReact - 2 (StartStir, StartHeat)
* StirAndTransfer - 2 (StartStir)
* ChillReact - 2 (StartStir, Chill, ChillBackToRT)
* Add - 2 (CleanTubing)
* Reflux - 2 (StartStir, StartHeat)
* Dry - 2 (StartVacuum, StopVacuum)
* Wash - 2 (StartStir, Add,)

* Filter - 3 (StirAndTransfer, StopVacuum)
* Extract - Unimplemented
* MakeSolution - Unimplemented

* Rotavap - Unimplemented