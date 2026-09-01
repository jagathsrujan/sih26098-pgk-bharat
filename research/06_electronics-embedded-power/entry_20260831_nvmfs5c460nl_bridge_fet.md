---
id: E06-20260831-nvmfs5c460nl-bridge-fet
category: 06_electronics-embedded-power
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
Bridge FETs: 6× onsemi NVMFS5C460NL (40 V / 78 A / 4.5 mΩ, DFN5×6 wettable flank)

## Summary (2-3 lines)
The 3-phase bridge must carry the ≤40 A / 15 s braking pulse (de-spin, report §4.3) at a
5 V gate-drive-friendly Vds class. NVMFS5C460NL: 40 V, 78 A, 4.5 mΩ class N-channel in a
5×6 mm flat-lead DFN with wettable flank (AOI-friendly — matches the BOM's AOI QA gate)
and AEC-Q101 qual. Deployed 2 in parallel per switch (6 FETs): ~2.25 mΩ per switch.

## Source (MANDATORY - no URL = reject)
- URL: https://www.onsemi.com/pdf/datasheet/nvmfs5c460nl-d.pdf (NVMFS5C460N/L datasheet)
- Family: https://www.onsemi.com/products/discrete-power-modules/mosfets/low-medium-voltage-mosfets/ntmfs5c460nl
  ("Single N-Channel Power MOSFET 40V, 78A, 4.5mΩ")
- Accessed: 2026-08-31

## Evidence
- Conduction estimate (worst-case de-spin): phase-current amplitude 40 A sinusoidal →
  I_rms ≈ 28.3 A/phase; bridge conduction ≈ 3 × I_rms² × R_switch ≈ 3 × 800 × 2.25 mΩ
  ≈ 5.4 W over 15 s ≈ **81 J** across 6 devices (≈13.5 J each) — adiabatic on 2 oz
  4-layer copper + collar heatsink; QA thermal survey added on the A6 line (same class
  as the A7b 720 J winding survey). Regeneration/brake energy is absorbed by the A7b
  dump path, not the FETs.
- 40 V class gives transient headroom above the 5 V bus (phase-leg spikes, leakage-L
  events; bus TVS-clamped). 30 V parts (e.g., BSC0906NS) are cheaper but leave less
  margin in a gun-hard EMI environment.
- Rds(on) is specified by the family at the 4.5 V gate class — consistent with a 5 V bus
  gate drive through the DRV8329 (smart gate drive; verify the exact 4.5 V vs 10 V Rds
  table value at schematic capture and re-run the conduction estimate with that number —
  recorded as a 06 §6 design rule).

## Indian Path
onsemi via Arrow/Avnet/Mouser India (automotive AEC-Q101 line, active).

## Pros / Cons
- Pros: 78 A rating = ~2× the 40 A pulse per device even before paralleling; wettable
  flank = optical inspection on the A6 AOI line; AEC-Q101; 5×6 flat-lead package has
  low parasitic inductance for the 15 kHz switching.
- Cons: 4.5 mΩ is mid-field for 2026 (lower-Rds 30 V parts exist); DFN thermal pad needs
  via-farm under the tab (layout rule).

## Cost Estimate (lakhs)
≈ US$1.1–1.4 each → 6× ≈ ₹650 @1k; proto ≈ ₹900 (6 devices). New A6 row (bridge set).

## Recommendation
**Select 6× NVMFS5C460NL** (2∥ per switch). Runner-up: Infineon BSC0906NS (30 V / 63 A /
4.5 mΩ SuperSO8 — 30 V class accepted only with a TVS clamp audit; kept as second source).

## Links to Code/CAD
- cleansheet/06_ELECTRONICS_ARCHITECTURE.md §4 (bridge sizing + thermal note), §7 BOM
- cleansheet/03_DESIGN_REPORT.md §4.3 (0.095 N·m @ ≤40 A/15 s spec), §5 (boost stage)
