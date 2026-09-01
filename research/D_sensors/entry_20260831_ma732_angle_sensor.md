---
id: D12-20260831-ma732-magnetic-angle
category: D_sensors
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
Collar↔bell angle sensor: MPS MagAlpha MA732 (14-bit, 60,000 rpm) — fills the missing BOM line

## Summary (2-3 lines)
The FOC/de-spin/S&A-spin-signature angle sensor (report §4.3/§4.5) had **no BOM line
item**. MA732 is a contactless on-axis magnetic rotary sensor: **14-bit** absolute angle,
tracking **0–60,000 rpm**, 25 MHz SPI (no minimum clock), 3.3 V. Requirement: resolve
the 3 kHz electrical frequency (12 pole pairs × 250 rev/s = 15,000 rpm relative) with
12-bit resolution → MA732 clears speed with 4× margin and resolution with 1 bit.

## Source (MANDATORY - no URL = reject)
- URL: https://www.monolithicpower.com/en/ma732.html (product page)
- Datasheet: https://www.mouser.com/datasheet/2/277/MA732-1855903.pdf
- Accessed: 2026-08-31
- Quote: "accurate angle measurements at speeds from 0 to 60,000 rpm"; "The maximum
  clock rate supported on SPI is 25MHz"; "14-Bit, Digital, Contactless Angle Sensor
  with ABZ Incremental & PWM Outputs".

## Evidence
- Speed gate: relative collar↔bell rate peaks at 250 rev/s (15,000 rpm) during the
  braking transient (report §4.3: electrical frequency ≤3 kHz = 250 rev/s × 12 pairs).
  MA732 60,000 rpm = 4.0×; runner-up ams AS5047P "up to 28krpm" = 1.9× (datasheet
  DS000324: https://www.mouser.com/datasheet/2/588/AS5047P_DS000324_3_00-1843440.pdf,
  accessed 2026-08-31). RLS AksIM-2 = precision off-axis module, ₹10k+ — over budget
  (≤₹1.5k gate, user-set) for a commutation-grade role.
- Angle constant: config ANGLE_BITS = 12 (0.088° quantization). MA732 14-bit (0.022°)
  exceeds the requirement → sim's 12-bit quantization assumption is conservative.

## Indian Path
MPS via Mouser/Digi-Key India (≈US$3–4 @1k, ≈₹300–400); diametral magnet (Ø6 NdFeB)
bonded to bell ID / sensor potted on collar face — no precision bearing of its own.

## Pros / Cons
- Pros: 4× speed margin over the de-spin transient; 14-bit > 12-bit gate; 25 MHz SPI
  serves the ≥10 kHz commutation read; no bearings (survives 15,000 g potted); tiny
  cost; also delivers ABZ/PWM redundancy outputs.
- Cons: on-axis magnet needed (magnet + potting stack-up on the bell ID — mechanical
  note for D3b); 14-bit angle accuracy depends on magnet alignment (fine for FOC).

## Cost Estimate (lakhs)
IC ≈₹400 + magnet ≈₹200 → D3b line ≈₹600 proto / ₹350 @1k (inside ₹1.5k gate).

## Recommendation
**Select MA732** (new BOM line D3b). Runner-up AS5047P (28 kRpm — passes but 1.9× margin).

## Links to Code/CAD
- flight_sw/fsw/config.py (ANGLE_BITS)
- cleansheet/05_SENSOR_SELECTION.md §3; BOM D3b (new)
