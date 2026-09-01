---
id: E06-20260831-dome-rails-buck-ldo
category: 06_electronics-embedded-power
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
Dome power rails: TI TPS62933 buck (5→3.3 V digital) + TLV757P LDO (3.3→3.0 V RF/analog)

## Summary (2-3 lines)
The dome (rotor frame) is fed ≈1.5 W-class from the 5 V boost rail through the 3-contact
slip ring. Rail plan: **TPS62933** synchronous buck (3.8–30 V in, 3 A, SOT583) makes the
3.3 V digital rail (MCU/IMU/flash); **TLV757P** 1 A LDO makes a low-noise 3.0 V RF/analog
rail (GNSS module, ADXL1004, comparator reference) with ~300 mV dropout headroom from the
buck's 3.3 V — keeping buck switching noise off the RF and signature paths.

## Source (MANDATORY - no URL = reject)
- Buck: https://www.ti.com/lit/ds/symlink/tps62933.pdf (TPS6293x 3.8-V to 30-V, 2-A/3-A
  Synchronous Buck Converters, SOT583)
- LDO: https://www.ti.com/lit/ds/symlink/tlv757p.pdf (TLV757P 1-A Low-IQ LDO, 1.45–5.5 V)
- Accessed: 2026-08-31
- Quote (buck): "input voltage range of 3.8 V to 30 V … 3-A continuous output current".
- Quote (LDO): "low quiescent current LDO that sources 1A … input voltage range from
  1.45 V to 5.5 V … fixed output voltages ranging from 0.6 V to 5 V".

## Evidence
- Topology rationale: 5 V is also the K-LD7 radar supply (3.2–5.5 V class, 05 §5) — the
  radar stays on the noisy 5 V entry rail behind a ferrite + bulk; the buck takes logic;
  the LDO isolates the RF/sensor analog domain. Buck minimum input 3.8 V > worst slip-ring
  dip with the 470 µF ride-through (06 §2 sequencing).
- 3.0 V output is inside every rail spec: NEO-F10N 2.7–3.6 V, ICM-45686 1.71–3.6 V,
  ADXL1004 3.0–3.6 V (min edge — flagged as a schematic-capture check vs the ADXL1004 DS).
- LDO dissipation: (3.3−3.0 V) × ~0.13 A ≈ 40 mW — keeps the dome budget inside gate (b).

## Indian Path
TI via Mouser/Arrow India (both are catalog SOT-583/SOT-23-5 parts).

## Pros / Cons
- Pros: buck 3 A ≫ dome ~0.15 A logic need (2×+ derating margin, low cost); SOT583 is
  hand-layoutable; LDO PSRR covers the buck's 2.2 MHz switching ripple at the GNSS.
- Cons: two-stage conversion costs ~5 % efficiency — irrelevant at 0.5 W total.

## Cost Estimate (lakhs)
TPS62933 ≈ ₹90; TLV757P ≈ ₹60; magnetics/caps ≈ ₹80. New D3 rows (rails).

## Recommendation
**Select TPS62933DRLR + TLV757P** (fixed 3.3 V and 3.0 V variants). Runner-up: MPS
MP2315 buck + ADI ADP7142 LDO (equivalent class; TI single-vendor rail simplifies sourcing).

## Links to Code/CAD
- cleansheet/06_ELECTRONICS_ARCHITECTURE.md §2 (power tree + per-rail budget), §3
- cleansheet/05_SENSOR_SELECTION.md §5 (rail notes carried forward)
