---
id: E06-20260831-ina240-current-sense
category: 06_electronics-embedded-power
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
FOC current sensing: 3× TI INA240A2 (20 V/V, enhanced PWM rejection) + 2 mΩ in-line shunts

## Summary (2-3 lines)
The 15 kHz PWM environment demands a CSA with strong PWM-rejection; the INA240 senses
across in-line shunts with a −4 V to 80 V common-mode range independent of supply —
built for exactly this topology. Gain 20 V/V: 40 A peak through 2 mΩ = 80 mV → 1.6 V
span centered on REF — a clean match to the G431 12-bit ADC at 3.3 V.

## Source (MANDATORY - no URL = reject)
- URL: https://www.ti.com/lit/ds/symlink/ina240.pdf (INA240 −4-V to 80-V, Bidirectional,
  Ultra-Precise Current Sense Amplifier with Enhanced PWM Rejection)
- Accessed: 2026-08-31
- Quote: "voltage-output, current-sense amplifier with enhanced PWM rejection that can
  sense drops across shunt resistors over a wide common-mode voltage range from −4 V to
  80 V, independent of the supply voltage".

## Evidence
- Shunts: 3× 2.0 mΩ 2512 power shunts (Vishay WSL2512R0020FEA class,
  https://www.vishay.com/docs/30108/wsl2512.pdf — accessed 2026-08-31); in-line in
  phases U/V/W. Full-scale: ±80 mV → ±1.6 V after gain — 40 A uses ~48 % of the ADC span
  (headroom for asymmetry/fault transients).
- Third-channel note: FOC needs ≥2 phase currents (third reconstructed); all three are
  sensed for fault symmetry (phase-loss detect) at +₹150.
- The DRV8329's integrated low-side CSA (bus-return shunt, 5 mΩ) is reserved for the
  bus-current monitor feeding the A7b chopper + safe-state logic — it does not need
  PWM rejection (static low-side node).

## Indian Path
TI via Mouser/Arrow India; the INA240 family is a high-volume automotive part.

## Pros / Cons
- Pros: PWM rejection spec'd for in-line placement at motor-PWM frequencies; bidirectional
  (braking current reverses through the bridge); 2.9–5.5 V supply from the drive 3.3/5 V
  rail; ultra-precise offset (±200 µV class) — good down to sub-amp roll-hold currents.
- Cons: 2 shunts/faz + 3 SOIC-8 add board area on the drive board (Ø62 shell-frame has
  room); zero-drift bandwidth adequate (350 kHz ≫ FOC 15 kHz sampled loop).

## Cost Estimate (lakhs)
≈ US$1.4–1.8 each → 3× ≈ ₹400 @1k; shunts 3× ≈ ₹90. New A6 rows (CSA set + shunt set).

## Recommendation
**Select 3× INA240A2D + 3× WSL2512 2 mΩ.** Runner-up: ADI AD8410A (cheaper, 20 V/V —
but no enhanced PWM-rejection architecture; rejected for the 15 kHz in-line placement).

## Links to Code/CAD
- cleansheet/06_ELECTRONICS_ARCHITECTURE.md §4 (sense chain), §7 BOM
- flight_sw/board/board_config.h (drive-side current scale constants documented for the link)
