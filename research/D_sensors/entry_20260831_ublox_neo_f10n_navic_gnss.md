---
id: D2-20260831-ublox-neo-f10n-navic
category: D_sensors
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
GNSS selection: u-blox NEO-F10N (NavIC L5 + GPS/GAL/BDS, dual-band L1/L5) — BOM D4 baseline

## Summary (2-3 lines)
NEO-F10N is u-blox's standard-precision dual-band module with **NavIC SPS-L5** support
(F10 platform, FW SPG 6.00, mass production since R04/R05 2025). Datasheet: **1 m CEP**
position, **0.05 m/s** velocity accuracy, hot-start TTFF **2 s**, UART to 921600 baud,
−40…+85 °C, 3.0 V class, 12.2×16×2.4 mm LCC. Meets every GNC flow-down with margin
(config GPS_POS_SIG 5 m / GPS_VEL_SIG 0.3 m/s are ≥5× conservative).

## Source (MANDATORY - no URL = reject)
- URL: https://content.u-blox.com/sites/default/files/documents/NEO-F10N_DataSheet_UBX-23002117.pdf (UBX-23002117 R05, 09-Oct-2025)
- Also: https://www.u-blox.com/en/product/neo-f10n-module
- Accessed: 2026-08-31
- Quote: "Position accuracy (CEP) … GPS+NavIC 1 m"; "Velocity accuracy 0.05 m/s";
  "Operational limits: Altitude 80,000 m, Velocity 500 m/s, Dynamics ≤ 4 g";
  "NavIC SPS-L5 (1176.450 MHz)"; "TTFF Hot start 2 s (GPS+NavIC 27 s cold)".

## Evidence
- Datasheet Table 1/2/4 (performance + supported constellations), Table 12/13 (abs max /
  operating: −40…+85 °C, 2.7–3.6 V), Table 15 (26 mA acquisition @3.0 V).
- **Verification of plan item "M9/F9 NavIC status":** NEO-M9N datasheet (UBX-19014285)
  lists GPS/GLONASS/BeiDou/Galileo only — **no NavIC on the M9 platform**. ZED-F9P
  materials reviewed list no NavIC either (US$127.50 list — also 38× over budget). The
  F10 platform is u-blox's NavIC-capable standard-precision line.
- **Flight-procurement gaps (honest):** (a) 500 m/s velocity limit < 827 m/s muzzle
  velocity — standard COTS receiver cannot track during boost; requires u-blox
  unlimited-dynamics order variant (professional track) or sovereign ASIC; (b) NavIC is
  **L5-only** (no NavIC L1) — acceptable: L5 is the ranging-grade signal; (c) 4 g
  dynamics limit is a tracking-loop spec under "Airborne 4 g platform" — our lateral
  command profile is ≤0.14 g; setback is powered-off.

## Indian Path
MeitY sovereign NavIC ASIC (D5 catalog) = upgrade path only (user-set constraint);
F10N module + Ø25 ceramic patch sourced via global distributors; GAGAN SBAS supported.

## Pros / Cons
- Pros: only COTS standard-precision module with datasheet-backed NavIC + GPS dual-band;
  1 m CEP / 0.05 m/s blows past the 5 m / 0.3 m/s EKF assumptions; hot-start 2 s meets
  the ≤5 s post-despin fix spec; 80 km altitude OK; professional grade, AEC-Q104 subset.
- Cons: 500 m/s ITAR limit (order variant needed for flight); NavIC L5-only; UART-only
  interface; ~US$20–25 module (≈₹2.4k) — within BOM D4 envelope.

## Cost Estimate (lakhs)
Module ≈ ₹2.4k + patch ≈ ₹0.8k → D4 line ≈ ₹5.2k proto / ₹2.6k @1k (unchanged envelope).

## Recommendation
**Select** as GNSS baseline. Runner-up: Quectel LC29H(AI) (see D2-20260831-quectel-lc29h).

## Links to Code/CAD
- flight_sw/fsw/config.py (GPS_POS_SIG/GPS_VEL_SIG/GNSS_LAT)
- cleansheet/05_SENSOR_SELECTION.md §1/§3 (this selection)
