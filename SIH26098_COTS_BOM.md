# SIH26098 — COTS Bill of Materials (Bench Demonstrator, v2)

**Version:** 2.0 | **Date:** 2026-08-29 | **Scope:** the active `PGK_155mm.FCStd` exhibition demonstrator only
**Boundary:** Inert, non-launchable exhibition kit. No energetics, no live fuze electronics, no launch-compatible interface. All flight performance is simulation (`cad_models/simulate_trajectory_155.py`). Everything on this BOM is ≤5 V logic, bench-grade, and publicly sourced COTS.

> Machine-readable copy for the submission portal: `SIH26098_COTS_BOM.csv`
> **v2 change:** the demonstrator now builds the *real* avionics story from the CAD — single 61811 de-spin bearing, Ø86 ring motor (FOC, regen), detent solenoid, 2× BlackPill STM32F405, ICM-42688 + MMC-5983, NEO-M9N + Ø25 patch, 6× 14430 bay — replacing the v1 ESP32/AS5600/N20/supercap props. Budget rises accordingly and honestly.

---

## Budget check

| Bucket | BOM total (₹) |
|---|---|
| B1 Structures & printed parts | 1,310 |
| B2 Bearing isolation (single 61811) | 1,100 |
| B3 Ring motor + detent (torque & regen) | 3,530 |
| B4 GNC electronics (2× BlackPill, IMU, mag, GNSS) | 5,590 |
| B5 Battery bay (6× 14430 + charge/boost) | 1,430 |
| B7 Bench stand (guarded) | 3,500 |
| B8 Consumables, tools, signage | 1,200 |
| **Demo total** | **17,660** |
| Spares/contingency ~10% | +1,700 |
| **Submission ceiling** | **≈ 19,400** |

Prices are typical Robu.in / Evelta / Robocraze / Mouser-India / local-supplier rates (Aug 2026) and are estimates, not quotes.

---

## B1 — Structures & printed parts (in-house print, COTS consumables)

| # | Item | Spec | Qty | Unit ₹ | Total ₹ | Maps to CAD |
|---|---|---|---|---|---|---|
| 1.1 | PLA/PETG filament 1.75 mm | Stator body, 4 strakes, rotor hub + simulated STANAG thread insert, shelf, standoffs @0.2 mm | 1.5 kg | 500 | 750 | `PGK_Stator_Body`, `PGK_Strakes`, `PGK_Rotor_Adapter(001)`, `Shelf` |
| 1.2 | Spare print budget | 2 spare strake sets + 1 spare dome nose | lot | 500 | 500 | |
| 1.3 | O-ring seal | Ø96 × 2.4 mm, NBR | 2 | 30 | 60 | `PGK_Seal_ORing` |
| | | | | | **1,310** | |

## B2 — Bearing isolation (THE A↔B frame split — now one bearing, per CAD)

| # | Item | Spec | Qty | Unit ₹ | Total ₹ | Maps to CAD |
|---|---|---|---|---|---|---|
| 2.1 | Thin-section ball bearing | **61811 (55×72×9)** open/2RS | 2 (1 spare) | 450 | 900 | `PGK_Bearing_61811` + `_Balls` |
| 2.2 | Lithium grease | bearing pack | 1 | 100 | 100 | |
| 2.3 | Shim washer set | 0.05 mm steps for preload | 1 | 100 | 100 | |
| | | | | | **1,100** | |

Notes: v1 used two 45×52×5 races; the CAD consolidated to a single 61811 — fewer parts, one failure point, and it matches the flight BOM (§2.6).

## B3 — Ring motor + detent (the A→B steer bridge AND the power story)

| # | Item | Spec | Qty | Unit ₹ | Total ₹ | Maps to CAD |
|---|---|---|---|---|---|---|
| 3.1 | Flat brushless gimbal motor | Ø86 class, ~11–12 poles — stator stands in for the Ø84 12-coil ring | 1 | 2,200 | 2,200 | `PGK_RingMotor_Coils` |
| 3.2 | Rotor magnet ring | 10× N52 block magnets 3×3×2 on printed rotor hub ring | 10 | 20 | 200 | magnets in `PGK_Rotor_Adapter` |
| 3.3 | FOC driver | SimpleFOC-class 3-phase driver board (DRV8302/L6234 class) | 1 | 600 | 600 | `FOC_Driver` |
| 3.4 | Solenoid | D12×20 push type, 5–12 V | 1 | 250 | 250 | `Detent_Solenoid` |
| 3.5 | Detent pawl | printed pawl + return spring, engages rotor-hub notches | 1 | (printed) | 0 | `PGK_Detent_Pawl` |
| 3.6 | Hall sensors | SOIC-8 latching Hall ×2 (index A/B) + flag magnets | 2 | 40 | 80 | `Hall_A`, `Hall_B` |
| 3.7 | Enameled Cu wire | 0.2 mm spare for winding experiments | 100 g | 200 | 200 | — |
| | | | | | **3,530** | |

Notes: one motor now does BOTH demo acts — FOC torque mode steers FRAME B anti-spin; drag/regen mode into the battery bay shows "power from spin". Replaces v1's N20 + face-gear pair and the separate alternator props.

## B4 — GNC electronics (all ≤5 V, display-grade — the real stack, miniaturized)

| # | Item | Spec | Qty | Unit ₹ | Total ₹ | Maps to CAD |
|---|---|---|---|---|---|---|
| 4.1 | BlackPill STM32F405 | GNC controller (attitude + steering loop) | 1 | 550 | 550 | `BlackPill_A` |
| 4.2 | BlackPill STM32F405 | Power/detent controller (independent path) | 1 | 550 | 550 | `BlackPill_B` |
| 4.3 | ICM-42688 breakout | 6-axis IMU, SPI | 1 | 650 | 650 | `ICM42688` |
| 4.4 | MMC-5983 breakout | 3-axis magnetometer, I²C | 1 | 450 | 450 | `MMC5983` |
| 4.5 | u-blox NEO-M9N + Ø25 patch | multi-constellation GNSS + ceramic patch | 1 | 2,400 | 2,400 | `NEO_M9N` + `GPS_Patch` |
| 4.6 | Custom PCB fab | Ø87 4-layer carrier board (JLCPCB class) | 1 lot | 600 | 600 | `Carrier_PCB_D87` |
| 4.7 | Passives + headers + JST | LDO 3V3, R/C/L, standoffs | 1 lot | 390 | 390 | |
| | | | | | **5,590** | |

Notes: v1's ESP32 + AS5600 + OLED props are gone — the flight GNC story (dual MCU lockstep, IMU/mag, Hall index, GNSS on the roll axis) is now told with the actual part classes named in the flight BOM §2.

## B5 — Battery bay (6× 14430 hexagon, per CAD)

| # | Item | Spec | Qty | Unit ₹ | Total ₹ | Maps to CAD |
|---|---|---|---|---|---|---|
| 5.1 | 14430 Li-ion cells | Ø14 × 43 mm, protected | 6 (6+2 spares) | 90 | 720 | `Cell_14430_1..6` |
| 5.2 | 14430 holders / contacts | hex-bay solder contacts | 1 lot | 120 | 120 | |
| 5.3 | Charge + protection | TP4056 + protection board | 1 | 180 | 180 | |
| 5.4 | Boost/LDO board | cell → 5 V/3.3 V rails | 1 | 150 | 150 | |
| 5.5 | Fuses + switch | bench-safe discharge path | 1 lot | 260 | 260 | |
| | | | | | **1,430** | |

Notes: replaces v1 supercap harvest. Discharge cells through the fuse+resistor before handling.

## B7 — Bench stand (safety-critical, guarded 600 rpm)

| # | Item | Spec | Qty | Unit ₹ | Total ₹ | Maps to |
|---|---|---|---|---|---|---|
| 7.1 | 775 DC motor + mount | stand drive, drives FRAME A only | 1 | 450 | 450 | I2 interface |
| 7.2 | PWM DC motor controller | 10–30 A, speed cap 600 rpm | 1 | 250 | 250 | |
| 7.3 | Belt + pulleys 1:2 | HTD-3M class | 1 | 400 | 400 | |
| 7.4 | Laser/optical tachometer | verifies ≤600 rpm (the guardrail number) | 1 | 500 | 500 | |
| 7.5 | E-stop + relay | mushroom e-stop breaking motor supply | 1 | 400 | 400 | |
| 7.6 | Polycarbonate guard tube | covers full Ø155 × 916 mm rotating envelope | 1 | 700 | 700 | |
| 7.7 | 12 V 5 A bench adapter | no bare Li-ion on the drive side | 1 | 400 | 400 | |
| 7.8 | Spindle cup + printed keeper ring | positive retention vs axial walk | 1 | 300 | 300 | |
| 7.9 | Stand frame | plywood/extrusion base | 1 | 100 | 100 | |
| | | | | | **3,500** | |

## B8 — Consumables, tools, signage

| # | Item | Spec | Qty | Unit ₹ | Total ₹ |
|---|---|---|---|---|---|
| 8.1 | Solder, hook-up wire, heatshrink | | lot | 400 | 400 |
| 8.2 | M2/M3 fastener + standoff kit | | lot | 300 | 300 |
| 8.3 | Balance tape weights + protractor | TIR balance check, index-angle verification | lot | 150 | 150 |
| 8.4 | Signage prints | "INERT EXHIBITION MODEL · NON-LAUNCHABLE · PERFORMANCE FIGURES ARE SIMULATION" + E-stop placard | lot | 350 | 350 |
| | | | | **1,200** | |

## B9 — Excluded / zero-cost

| Item | Note |
|---|---|
| Laptop + dashboard | existing; runs `simulate_trajectory_155.py` + telemetry |
| Phone/tablet setter mock app | concept UI render only, no hardware |
| 3D printer | existing/institutional |
| SAFE/SET/ARMED indication | the detent pawl position IS the state display — printed, tied to the display state machine only (fuze boundary) |

---

## Reference-only (NOT purchased, NOT on the demo BOM)

Flight-article equivalents judges may ask about — quoted as public reference points, never as demo hardware:

| Flight-article item | Demo proxy on this BOM | Why not bought |
|---|---|---|
| ~15,000 g-rated ring torque motor | Ø86 gimbal motor + FOC (B3.1/3.3) | Bench runs ≤600 rpm; gun-launch survival is not tested |
| Tactical GNSS/NavIC receiver | NEO-M9N receiver-only (B4.5) | Display-grade only per boundary |
| Gun-hard IMU (≤10°/h class) | ICM-42688 breakout (B4.3) | Same — sensor *story*, not sensor *spec* |
| Thermal battery | 6× 14430 bay + regen (B5) | Energetics excluded |
| STANAG 2916 threaded fuze interface | Printed simulated thread ring (B1.1) | No launch-compatible interface by design |

## Vendor quick-list (India)

- **Robu.in / Robocraze:** BlackPill F405, FOC driver, gimbal motor, solenoid, Hall, 14430 cells, 775 motor, tach
- **Evelta:** ICM-42688, MMC-5983, LDOs, protection boards
- **Mouser/DigiKey India:** u-blox NEO-M9N + patch, precision passives
- **Local bearing shop / VXB:** 61811 thin-section
- **Local:** NdFeB magnets, enameled wire, acrylic/polycarb, fasteners
