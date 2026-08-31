# 03 — MECH: System Architecture + Integration + Validation (Mech)

**Team:** MECH (3/3) | **PS Bullet:** Complete system architecture, CAD assembly, prototype

## Your PS Deliverables
- **System architecture document** (mech integration view) → contributes to `cleansheet/03_DESIGN_REPORT.md`
- **CAD assembly** — full kit in `cleansheet/PGK_CleanSheet.FCStd` (Assembly: 24 links, 23 joints, 122-frame Simulation)
- **Prototype or proof-of-concept** (mech) — 3D print + bench de-spin rig
- **Simulation and validation methodology** (mech side) — 6DOF, Monte Carlo, MIL-STD-331 plan

## What You Do
- Architecture: three-frame topology S (shell) / R (rotor) / balls (de-spin), operation timeline t=0→90s
- CAD: maintain Assembly `J_MotorRotor` / `J_RollDecouple`, Simulation drives `3.1416*time` / `-1.0472*time`
- Integration: ensure GNC/fuze/power boards fit rotor frame, slip ring only 1.5W crosses
- Validation: mass ≤2.0 kg, length 260mm, balance <0.5 g·cm

## Key Files
- `cleansheet/03_DESIGN_REPORT.md:2` (architecture), `2.4` (Assembly), `10` (roadmap)
- `cleansheet/HANDOFF.md` (how to play sim, crash lessons)
- `SIH26098_TEAM_BRIEFING.md:5` (dependencies)

## Initial 3 Research Questions
1. How to model retention lip + shear pins (REQ-1/2) without breaking Assembly solver?
2. What bench de-spin rig proves 250→0 rev/s in 15s with ≤40A?
3. Which 6DOF Monte Carlo (≥1000 runs) proves CEP ≤30m?

## Branch
`research/03_mech-system-<username>` or `mech/system-<username>`
