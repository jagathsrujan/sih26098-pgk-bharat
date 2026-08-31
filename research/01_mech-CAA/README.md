# 01 — MECH: Canard Actuation Assembly (CAA)

**Team:** MECH (1/3) | **PS Bullet:** Canard Actuation Assembly for in-flight trajectory correction

## Your PS Deliverables
- **Canard deployment and actuation mechanism** — how 4 canards deploy, actuate, and steer
- **CAD model of the canard actuation assembly** → `cad_models/` + contribution to `cleansheet/PGK_CleanSheet.FCStd` (canard shell, fins, drum)
- Part of **Manufacturability & Cost optimization**

## What You Do (from PS)
- Mechanism: fixed-span vs flip-out vs retractile? Our design: one-piece machined shell with trimmed pair ±3° (see `cleansheet/03_DESIGN_REPORT.md:4.4`)
- CAD: model fins (root 24 / tip 18, span 24.5, tip Ø138), hinge at quarter-chord, ensure bore clearance
- Aero: canard lift `L = ½ρv²·CL·S`, authority vs CEP (need ~14 N for 30m correction)
- Bearings: threaded-race bearing-in-well as de-spin joint (S↔R frames)

## Key Files to Read
- `cleansheet/03_DESIGN_REPORT.md:4.1` (bearing), `4.4` (canard shell), `4.3` (outrunner)
- `cleansheet/02_BOM_MANUFACTURING_ASSEMBLY.md:A` (canard shell C1, 5-axis mill)
- `cad_models/PGK_DEMO_ASSEMBLY.md`, `SIH26098_Exhaustive_Ideas_Catalog.md:B` (B1-B16)

## Initial 3 Research Questions
1. What fin trim ±3° authority gives ≥30 N at Mach 0.8, and what is the hinge moment?
2. Which COTS bearing survives 15,000g setback with <0.5 N·m drag?
3. How does the one-piece 7075-T6 shell achieve <0.5 g·cm balance?

## Branch
`research/01_mech-CAA-<github-username>` or `mech/CAA-<username>`
