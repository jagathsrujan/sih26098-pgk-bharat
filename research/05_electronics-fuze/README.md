# 05 — ELECTRONICS: Multi-Mode Electronic Fuze

**Team:** ELECTRONICS (2/3, ECE/EEE) | **PS Bullet:** Multi-mode Electronic Fuze — Proximity / Time / Impact

## Your PS Deliverables
- **Multi-mode electronic fuze design** (Proximity + Time + Impact)
- **Proximity sensor** selection + HOB logic (6/12/18 m)
- **Embedded hardware architecture** (fuze part) + block diagram
- Safety: S&A logic, reliability, fail-safe

## What You Do
- Fuze modes: Impact (axial accel threshold), Time (crystal timer 3–199.9s), Proximity (FMCW 24 GHz, HOB 6/12/18m, de-spun beam enabled)
- S&A: firing line shorted until 3 signatures — setback ≥850g (g-switch) + spin ≥2900rpm (angle sensor rate) + bore-exit timer (STANAG 4187), fail-any → safe
- Hardware: prox head Ø30 FMCW + patch (z 738), GNC board STM32G474 + ICM-42688, dome base ring
- Setter: inductive EPIAFS-class, loads target grid/mode/HOB/crypto, checks continuity

## Key Files
- `cleansheet/03_DESIGN_REPORT.md:4.6` (fuze), `4.7` (setter), `5` (S&A)
- `SIH26098_Exhaustive_Ideas_Catalog.md:E` (E1-E10), `J` (J1-J6)
- `02_BOM:D5` (prox head), `A3.3` (initiator interface)

## Initial 3 Research Questions
1. Which FMCW 24 GHz module gives HOB ±1m at 15,000g with <100mW?
2. What S&A logic guarantees <1 ppm premature with 3 independent signatures?
3. How to program fuze inductively through shell wall with EPIAFS?

## Branch
`research/05_electronics-fuze-<username>` or `electronics/fuze-<username>`
