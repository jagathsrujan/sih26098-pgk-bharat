# 02 — MECH: Structure, Environmental Protection & Manufacturability

**Team:** MECH (2/3) | **PS Bullet:** Compatible with 155mm, survive high-g, SWaP-C, modular

## Your PS Deliverables
- **Environmental protection strategy** — survive 15,000g setback, 267 rev/s spin, vibration, −40…+60°C, rain
- **Manufacturability and cost optimization** — YIL forging, CNC, ex-works ₹0.7–0.9L @1k
- **Power supply and environmental protection** (structural side)
- Supports **System architecture** (fit checks)

## What You Do
- Structure: shell interface STANAG 2916 2-12UN-1A full-depth thread, module mass ≤1.5 kg target (current 1.84 kg → 1.56 kg via thin-wall)
- Environmental: bore pressure, setback load path (retention lip + shear pins REQ-1/2, 220 kN), sealing, potting (Araldite CT200)
- Manufacturability: A1 outer ring (100Cr6, grind after HT), A3 cartridge (turn-mill), C1 canard (5-axis), D1 radome (GFRP)
- Fit classes: journal Ø31.6 g6 in bore Ø32 H7/g6, thread 2A/2B

## Key Files
- `cleansheet/00_REQUIREMENTS.md:M/L/P` (launch, envelope)
- `cleansheet/02_BOM_MANUFACTURING_ASSEMBLY.md:C` (fit classes), `D` (costing, NRE ₹4.2Cr), `F` (mass rollup)
- `cleansheet/03_DESIGN_REPORT.md:3` (interface), `5` (power/thermal), `6` (mass)

## Initial 3 Research Questions
1. Which 100Cr6 heat-treat + grind sequence holds race Ra0.4 after 15kg?
2. What potting survives 15,000g + −40°C without cracking around windings?
3. How to cut module mass 280g (A1 thin-wall + Al bell with steel sleeve)?

## Branch
`research/02_mech-structure-<username>` or `mech/structure-<username>`
