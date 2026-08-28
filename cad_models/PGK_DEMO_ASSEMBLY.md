# Active PGK exhibition demonstrator

This is the active mechanical baseline for the inert exhibition model. It is a public-architecture demonstrator, not an exact teardown of the M1156 and not a flight-capable fuze.

## Assembly concept

```text
Printed projectile shell / display spindle
                    │
           outer PGK housing (spin side)
                    │
        front + rear coaxial bearing seats
                    │
        common canard carrier (de-spun side)
             ├── fixed canard 1
             ├── fixed canard 2
             ├── fixed canard 3
             └── fixed canard 4
                    │
   rotor on housing ↔ stator on carrier (alternator concept)
                    │
      rectifier → supercapacitor → LEDs/controller
```

The shell and outer housing are the spin-side frame. The carrier is the only
common steering member: all four canards are attached to it and move together.
The bearings permit relative rotation; they do not make the carrier a
permanently locked part. The single torque-emulator placeholder represents the
relative-rotation actuator/brake used by the demonstration.

## Current printed parts

| Part group | Active model role |
|---|---|
| `01_DemoShankAdapter` | Nonfunctional slip-fit interface to the printed shell |
| `02_Supercapacitor_Display` / `03_PowerConditioning_DisplayPCB` | Safe display power store and conditioning placeholders |
| `04_Inert_Status_Slider` | Empty mechanical status indicator; no firing path |
| `10_OuterHousing_SpinSide` | Outer spin-coupled housing with inspection window |
| `12_FrontBearing_Demo` / `13_RearBearing_Demo` | Visible coaxial de-spin bearing pair |
| `14_CommonCanardCarrier` | Single inner carrier for all four fixed canards |
| `20_FixedCanard_01`–`04` | Four fixed, illustrative display fins |
| `22_Torque_Emulator_LowVoltage` | One low-voltage exhibition actuator placeholder |
| `40_AlternatorRotor_ShellSide` | Shell-side magnet/rotor concept |
| `41_AlternatorStator_CarrierSide` | Carrier-side coil/stator concept |
| `30`–`35` electronics parts | Controller, sensor, antenna, index-marker placeholders |
| `50_TopPlate` / `51_GNSS_Antenna...` / `60_NoseCap...` | Cover, antenna placeholder, and inert radome |

## Safe demonstration sequence

1. Mount the lightweight printed shell in a guarded, low-speed stand.
2. Rotate the shell and outer housing by hand or with a benign display drive.
3. Show that the canard carrier can remain at a different orientation.
4. Illuminate an LED when the shell-side rotor passes the carrier-side stator.
5. Use the low-voltage torque emulator to make the whole carrier rotate as one
   unit; do not actuate individual fins.
6. Use the index marker and sensor to display the relative angle on a screen.

The model must remain physically incapable of firing: no propellant, primer,
detonator, booster, live fuze electronics, or launch-compatible interface.
