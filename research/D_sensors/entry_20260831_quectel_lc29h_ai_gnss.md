---
id: D2-20260831-quectel-lc29h-ai
category: D_sensors
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
GNSS runner-up: Quectel LC29H(AI) — NavIC L5 dual-band module (fails apogee ceiling)

## Summary (2-3 lines)
LC29H(AI) is the only LC29H variant with NavIC (L5). Datasheet: 1.8 m CEP autonomous,
0.1 m/s velocity, hot start 1 s, AGNSS cold 5 s, 3.3 V/16 mA, −40…+85 °C, UART/SPI/I2C.
**Killer: maximum altitude 10,000 m (ITAR)** vs apogee 9.9–12 km — at or below the
mission ceiling. Velocity 500 m/s limit as on the u-blox part.

## Source (MANDATORY - no URL = reject)
- URL: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/7133/Quectel_LC29H_Series_GNSS_Specification_V1.8.pdf
- Also: https://www.quectel.com/product/gnss-lc29h/
- Accessed: 2026-08-31
- Quote: "NavIC: L5 (only supported by LC29H (AI))"; "Maximum Altitude: 10000 m,
  Maximum Velocity: 500 m/s, Maximum Acceleration: 4g"; "Velocity Accuracy 0.1 m/s";
  "Autonomous 1.8 m"; "Hot Start: 1 s".

## Evidence
- Spec sheet LC29H(AI) column (bands, TTFF, dynamics, price class ≈US$8–10 → ≈₹0.8–1k).
- Altitude 10 km < 12 km apogee case (30 km range, 46° elev — cleansheet §3): **fails
  the L4 envelope with zero margin**.

## Indian Path
Cheapest NavIC L5 COTS; widely stocked with Indian distributors; good for bench/HIL
demos where the trajectory is simulated.

## Pros / Cons
- Pros: lowest cost NavIC dual-band; SPI available; AGNSS cold-start 5 s.
- Cons: 10 km ceiling (apogee 9.9–12 km — fails); 1.8 m CEP / 0.1 m/s (still ≥2.7×
  better than the EKF assumptions, but 2–3× worse than F10N); NavIC L5-only.

## Cost Estimate (lakhs)
≈₹0.9k module — would cut D4 by ~₹1.7k if the ceiling were acceptable (it is not).

## Recommendation
**Reject as flight GNSS (altitude limit); keep as bench/runner-up.**

## Links to Code/CAD
- research/D_sensors/entry_20260831_ublox_neo_f10n_navic_gnss.md (winner)
