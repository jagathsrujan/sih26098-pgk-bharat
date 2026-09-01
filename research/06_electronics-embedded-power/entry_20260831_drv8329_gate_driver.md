---
id: E06-20260831-drv8329-gate-driver
category: 06_electronics-embedded-power
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
3-phase gate driver: TI DRV8329 (4.5–60 V — the part that works on a 5 V bus)

## Summary (2-3 lines)
The de-spin bus is the 5 V boost rail (3.7 V battery → boost, report §5). Popular smart
gate drivers do NOT reach it: DRV8323R VM min 6 V, TMC6200 VM min 8 V. The DRV8329 drives
three external half-bridges from 4.5–60 V using bootstrap + trickle charge pump, is
hardware-configurable (no SPI consumed), integrates a 3.3 V LDO and a low-side current-sense
amplifier (bus-current monitor), and adds the fault diagnostics (VDS monitor) a braking
stage needs.

## Source (MANDATORY - no URL = reject)
- URL: https://www.ti.com/lit/ds/symlink/drv8329.pdf (DRV8329 4.5-to-60 V Three-phase
  BLDC Gate Driver, Rev *)
- Product/package: https://www.ti.com/product/DRV8329/part-details/DRV8329AREER
  (DRV8329AREER, 36-WQFN 5×4)
- Accessed: 2026-08-31
- Quote: "integrated gate driver for three-phase applications … three half-bridge gate
  drivers … internal charge pump … bootstrap circuit … trickle charge pump"; "integrated
  accurate 3.3 V LDO … low-side current sense amp that allows current sensing for the sum
  of the current from each phase".

## Evidence
- Rejected on the 5 V bus: **DRV8323R** (6–60 V), **TMC6200** (8–60 V), DRV835x (9–100 V),
  IR2136-class bootstrap drivers (10–20 V VCC). DRV8329 VM min 4.5 V is the only mainstream
  smart 3-phase driver that regulates at 5.0 V ± ripple.
- FOC architecture: gate driver is config-only (HW pins); the current loop reads the
  INA240A2 per-phase CSAs directly on the G431 ADC — the DRV8329 integrated low-side CSA
  is used as the bus-current monitor for the A7b chopper tie-in and fault logic, not for FOC.
- Trickle charge pump keeps the high side alive at 100 % duty — needed for the
  roll-hold (continuous torque at a fixed azimuth) operating point.

## Indian Path
TI via Arrow/Avnet/Mouser India stock (2024 part, active family).

## Pros / Cons
- Pros: 4.5 V VM floor matches the bus; external-FET (sizes to the 40 A braking current);
  HW-configurable = fewer pins, no SPI dependency in the safety path; VDS overcurrent
  monitoring; integrated LDO can power logic refs.
- Cons: no integrated per-phase CSAs (kept — the INA240A2 gives PWM-rejected in-line
  sensing the integrated PGAs would not); 36-WQFN needs fine-pitch assembly (A6 is SMT
  0402+ class already).

## Cost Estimate (lakhs)
≈ US$2.5–3 @1k → ≈ ₹250–300; proto ≈ ₹400. New A6 row.

## Recommendation
**Select DRV8329AREER.** Runner-up: TMC6200 (excellent integrated sense amps — but 8 V
VM minimum fails the 5 V bus; recorded as the 12/24 V-bus variant option if the power
architecture is ever re-bussed).

## Links to Code/CAD
- cleansheet/06_ELECTRONICS_ARCHITECTURE.md §4 (drive domain block), §7 (BOM deltas)
- cleansheet/03_DESIGN_REPORT.md §4.3 (motor drive chain)
