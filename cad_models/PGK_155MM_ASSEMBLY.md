# PGK 155mm — Active Assembly (PGK_155mm.FCStd)

This is the **active mechanical baseline**: a detailed, inert CAD envelope of the
Precision Guidance Kit mated to a reference 155mm shell. Source of truth:
`PGK_155mm.FCStd` (repo root). Verified exports + renders: `cad_models/out_pgk/`
(regenerate with `freecadcmd render_pgk_155mm.py` from `cad_models/`).

It is a public-architecture paper+CAD design — **not** an exact teardown of any
fielded product, and not a flight-capable fuze. No energetics anywhere.

## Architecture in one line

Shell (FRAME A, spins at ~250 rev/s) → threaded fuze-well insert → rotor hub →
**one thin-section 61811 bearing** → de-spun stator (FRAME B) carrying 4 fixed
strakes, the ring-motor coil ring, the GNC stack, a 6× 14430 battery bay and the
GNSS antenna — steering = ring-motor roll torque holding FRAME B anti-spin.

## Vertical stack (z in mm, shell base = 0)

| z-range | Part | Role |
|---|---|---|
| 0–778.5 | `Projectile_Body` | REF M107-class body, Ø155, std fuze well (FIXED) |
| 70–100 | `REF_Driving_Band` | Copper band, Ø157.5 — drives FRAME A spin |
| 748.5–791 | `PGK_Rotor_Adapter001` | Ø56 STANAG 2916 fuze-well thread insert |
| 747.8–814 | `PGK_Rotor_Adapter` | Ø63 spin-side hub: rotor magnets + detent notches |
| 776.8–779.2 | `PGK_Seal_ORing` | Ø96 environmental seal of the bearing bay |
| 781–790 | `PGK_Bearing_61811` (+`_Balls`) | **single** thin-section de-spin bearing 55×72×9 |
| 788.1–875.9 | `PGK_Strakes` | 4 fixed strakes, Ø148 envelope, on FRAME B |
| 792–806 | `PGK_RingMotor_Coils` | 12-pole coil ring Ø84 — torque **and** regen power |
| 806–816 | `PGK_Detent_Pawl` | Launch lock rotor↔stator (release = armed) |
| 818–820.5 | `Carrier_PCB_D87` | Ø87 GNC board |
| 820.5–824 | `BlackPill_A/B` | 2× STM32F405 (GNC + power/detent, independent paths) |
| 824.5–826.5 | `FOC_Driver` | 3-phase ring-motor driver |
| 812.5–814 | `Hall_A` / `Hall_B` | Redundant per-rev index (A→B relative angle) |
| 825–830.5 | `ICM42688`, `MMC5983` | IMU + magnetometer on the carrier PCB |
| 820.5–863.5 | `Cell_14430_1..6` | Battery bay: 6× Ø14×43 cells in hexagon @ r36.5 |
| 865–867.4 | `NEO_M9N` | u-blox GNSS receiver |
| 868–871 | `Shelf` | Ø87 antenna shelf, closes the bay |
| 871.5–875.5 | `GPS_Patch` | Ø25 patch at dome apex |
| 778.5–915.5 | `PGK_Stator_Body` | Ø106 dome-nosed de-spun stator (FRAME B) |

Kit envelope above the shell nose: **Ø148 × 168 mm**. COTS part geometry lives in
`COTS_Library.FCStd` (NEO-M9N, patch, BlackPill, ICM-42688, MMC-5983, 61811 +
balls, solenoid D12×20, FOC driver, Hall SOIC8, 18650 refs).

`SEC_*` objects are half-section cutaways of every part — set them visible for
the cutaway view (see `out_pgk/preview_section*.png`).

## Why this beats the legacy printed demo

| | old common-carrier demo | this model |
|---|---|---|
| Steering frame | printed carrier + 4 canards, 2 printed-race bearings | machined stator + 4 strakes, **one** 61811 |
| Torque actuator | 2× N20 + face gears | 1 ring motor (12 coils, FOC, regen-capable) |
| Launch lock | manual S&A slider | detent pawl + solenoid |
| Power story | alternator props + supercap | ring-motor regen + 6× 14430 bay |
| Electronics | ESP32 + AS5600 props | 2× BlackPill F405, ICM-42688, MMC-5983, NEO-M9N |

Old concept preserved in `legacy/old_common_carrier_demo/`; the earlier
two-motor concept in `legacy/old_two_motor_design/`.

## Safe demonstration sequence

1. Open `PGK_155mm.FCStd`, keep the `SEC_*` cutaway set visible for the internal
   walkthrough (Left view shows the cut face).
2. Frame story: FRAME A (shell + band + rotor hub) spins; FRAME B (stator,
   strakes, stack) stays put on the 61811.
3. Ring motor: coils (B) act on rotor magnets (A) — torque to hold B anti-spin;
   same coils regenerate spin power into the 14430 bay.
4. Detent pawl + solenoid = the launch-lock release (the "armed" event).
5. GNSS story: NEO-M9N + patch under the dome apex, IMU/mag + dual Hall index
   for navigation between fixes.

Everything here is display-grade COTS or paper spec: no propellant, primer,
detonator, booster, live fuze electronics, or launch-compatible interface.
