---
id: D10-20260831-rfbeam-k-ld7-hob
category: D_sensors
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
Prox head: RFbeam K-LD7 24 GHz digital radar (FMCW-class distance + speed) — firms up BOM D5

## Summary (2-3 lines)
BOM D5 named "FMCW 24 GHz module + patch" with no part number. **K-LD7** is a fully
digital 24 GHz transceiver measuring speed, direction, distance and angle with integrated
FFT + tracking filter, serial target list, 3.2–5.5 V. Typical detection 15 m (person) /
30 m (car); the ground approaching a descending shell is a large-RCS target → HOB gates
6/12/18 m are inside the envelope. RFbeam publishes **AN03 radome design** — directly
applicable to the GFRP radome (≥85 % transmission spec).

## Source (MANDATORY - no URL = reject)
- URL: https://rfbeam.ch/product/k-ld7-radar-transceiver/
- Ordering: K-LD7-RFB-00H-01 (https://www.digikey.com/en/products/detail/rfbeam-microwave-gmbh/K-LD7-RFB-00H-01/10638820)
- Accessed: 2026-08-31
- Quote: "Measures speed, direction, distance and angle of moving objects";
  "Typical detection distance: 15m for persons / 30m for car"; "Integrated FFT signal
  processing with tracking"; "3 × 4 patch antenna with 80°/34° beam aperture";
  "AN03 - Radome design".

## Evidence
- Fuze requirement (F3/E1): HOB 6/12/18 m selectable, de-spun steady beam (report §4.6).
  K-LD7 range output + closing-rate (speed) output gives a two-condition HOB signature
  (range < gate AND closing speed consistent with terminal descent) — jamming-resistant
  vs a bare Doppler threshold (catalog E2 CW fallback noted as the alternate).
- TI IWR6843 (60 GHz) evaluated and **rejected as overkill** (3× the power/cost/
  integration burden; plan-set note). K-LC series are Doppler-only (no distance output)
  — would need external ranging; rejected for this role.
- Price class ≈US$23–30 (DigiKey) → D5 line re-costed.

## Indian Path
RFbeam via Digi-Key/Mouser India; antenna aperture already inside the Ø84 radome;
AN03 guides radome wall/attachment QA (pairs with existing boil test).

## Pros / Cons
- Pros: digital distance+speed+angle over serial (no custom signal chain); 5 V-tolerant
  supply from boost rail; published radome app note; evaluation kit for the HOB bench.
- Cons: module is motion-detection-oriented (target list) — HOB logic must gate on the
  ground return signature; range-resolution spec is coarse (~0.75 m class) — adequate
  for ±1 m HOB at 6–18 m but must be bench-verified (HOB bench already in BOM §D NRE).

## Cost Estimate (lakhs)
≈₹2.1k module → D5 ≈ ₹4.8k proto (unchanged, incl. integration) / ₹1.9k @1k.

## Recommendation
**Select K-LD7** as D5 part number baseline (bench-verify HOB gates on the K-LD7-EVAL).

## Links to Code/CAD
- cleansheet/05_SENSOR_SELECTION.md §3; BOM D5 note; report §4.6
