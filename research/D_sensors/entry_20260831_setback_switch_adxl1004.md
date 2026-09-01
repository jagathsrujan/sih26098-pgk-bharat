---
id: D11-20260831-setback-switch-adxl1004
category: D_sensors
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 8
---

## Idea Title
Setback sensor (S&A signature 1): mechanical setback armer (flight) + ADXL1004 electronic
signature — fills the missing BOM line

## Summary (2-3 lines)
S&A signature 1 (setback ≥ threshold) had no part and no spec. Two-element design:
(a) **flight S&A = mechanical setback armer** (mass-spring, artillery-fuze class —
Precision Arming Solutions "setback, inertia & high-G switches" group; threshold placed
between manhandling (<100 g) and the kinematic mean (~5,000 g), design peak 15,000 g);
(b) **electronic launch signature = ADXL1004** ±500 g MEMS (dc–24 kHz, 45 kHz resonance,
"immune to external shocks up to 10,000 g") — threshold detect, soft-mounted/potted so
setback is a saturating event, not a measurement.

## Source (MANDATORY - no URL = reject)
- URL (setback switches class): https://www.select-controls.com/category/95/setback-inertial-high-g-switches.html
- URL (ADXL1004): https://www.analog.com/en/products/ADXL1004.html ;
  datasheet https://www.analog.com/media/en/technical-documentation/data-sheets/adxl1004.pdf
- Accessed: 2026-08-31
- Quote (ADXL1004): "Full-scale range: ±500 g"; "dc to 24 kHz typical"; "noise density
  of 125 μg/√Hz"; "immune to external shocks up to 10,000 g".
- Quote (PAS): "setback, inertia, and high-G switch solutions engineered for artillery
  and mortar systems … controlled munition arming sequence requirements".

## Evidence
- Environment: setback design peak 15,000 g, kinematic mean ~5,000 g (report §3/§7
  audit row 1). Electronics boot at muzzle exit (t≈2 s) → powered-off through setback;
  the electronic signature is for S&A logic state + launch detect, not for the arming
  force path (STANAG 4187 practice; live S&A stays with partner ESAF — project boundary).
- **Honest gap:** ADXL1004 immunity spec is 10,000 g < 15,000 g design peak →
  soft-mount (potting isolation) attenuation required; documented as QA item on D3c.

## Indian Path
Setback armer = partner ESAF domain (BEL/ECIL class, STANAG 4187); ADXL1004 via
Analog/Arrow India (≈US$12 → ≈₹1.1k); threshold electronics on the power board (A6).

## Pros / Cons
- Pros: mechanical armer is the proven, power-free, qualifiable S&A device; ADXL1004
  gives a fast electronic signature + launch detect with huge bandwidth margin.
- Cons: armer is a partner/qual item (outside inert exhibition scope — architecture
  only); ADXL1004 over-range needs mount design; neither measures the 15k g peak
  quantitatively (telemetry rounds use Endevco 7280A-class instrumentation, not BOM).

## Cost Estimate (lakhs)
D3c line ≈₹2.5k proto (armer dummy/inert + ADXL1004 + threshold circuit) / ₹800 @1k.

## Recommendation
**Select** two-element architecture (new BOM line D3c). Catalog D11 (setback threshold
launch detect) and D7 (ADXL1004) consolidated here.

## Links to Code/CAD
- cleansheet/05_SENSOR_SELECTION.md §3; BOM D3c (new); report §4.6 S&A signatures
