---
id: B14-20260825-lshang-cfd-aero-database
category: B_aero
author: @jagathsrujan
date: 2026-08-25
source_type: video
trl: 6
---

## Idea Title
L Shang ICEM/Fluent Aero Database Method — 14mm Static Margin at 30m/s + Pressure Streamlines for Canard Sizing

## Summary (2-3 lines)
Teardown shows full CFD pipeline: ICEM unstructured mesh (cylindrical farfield) -> Fluent 1000 iter on Xeon 8275CL (93.9GB, 100% CPU) -> pressure contours (-1400 to 400Pa) -> Excel database (lift/drag/pitch moment/CoP) at 30m/s yielding CoG 439.6mm / CoP 473.7mm / margin 14.06mm. Same pipeline needed for SIH155mm at Mach 0.8-3.0 to size canards per B14 topology optimization.

## Source (MANDATORY - no URL = reject)
- URL: file:///Users/jagathsrujan/Downloads/Canard%20control%20vertical%20recovery%20guidance%20technology%20experimental%20rocket%20development%20-%20L%20Shang%20%28720p,%20h264%29.mp4
- Accessed: 2026-08-25
- Quote: "ICEM非结构化网格划分 | 高性能计算机求解 Intel Xeon Platinum 8275CL CPU @3.00GHz 100% 16.0/93.9GB | 气动仿真数据处理 | 中心距弹头距离 419.3881836 压心位置 473.7284392 重心位置 439.6 重心偏移 14.0618164 | 速度 30m/s 升力 阻力 俯仰力矩 压心位置 升阻比"
- Patent/BIB: ANSYS ICEM R19.2 + Fluent (continuity/x-velocity residuals visible)

## Evidence
- thumb_0175.jpg: ICEM GUI "Geometry->Points/Curves/Surfaces/Bodies + Mesh" tree, cylindrical domain, ANSYS R19.2, Surface Mesh Setup panel
- thumb_0185.jpg: Task Manager Xeon 8275CL 100% 3.00GHz 16/93.9GB, Fluent "Data Sampling for Steady Statistics / Number of Iterations 1000 / Calculate"
- thumb_0195.jpg: Streamlines colored by pressure -1400 (blue) to 400 (red), canard-tail vortex interaction, AoA ~5deg, stagnation at nose tip red
- thumb_0205.jpg: Excel rows 2177-2190 columns 1.93-1.96 / 0.47 / -0.10 + title "气动仿真数据处理"
- thumb_0215.jpg: Table headers "升力 阻力 俯仰力矩 压心位置 升阻比" at 30m/s, rows 0.52377582 drag / 686.57 CoP, graph y=0.4267x (Cm_alpha linearization)
- Derived margin: CoP 473.72 - CoG 439.6 = 34.12? but second row shows 14.06 for other Mach — shows aero moving with AoA/Mach, needs gain scheduling.

## Indian Path
ARDE bourrelet design + nubless stability (TOI Nagpur) + DRDO 8 guided-artillery tasks (aero). Replicate pipeline on YIL bore: Missile DATCOM for quick 0.8-3.0M sweeps -> ICEM/Fluent for canard deflection 0/5/10deg -> Python table same columns as L Shang (replace 30m/s with Mach). Use 10,000-ton press extrusion data for housing thermal.

## Pros / Cons
- Pros: Proves low-cost team can do HPC CFD (not just DATCOM), gives exact Excel template for SIH, validates static margin 0.4D (34mm nose -> 14mm margin), streamlines show canard authority; directly reusable for PGK split-canard B16
- Cons: Only low subsonic 30m/s shown; artillery needs supersonic 684m/s (Mach 2.0) where CoP shifts 1-2D; 34mm model not 155mm; no Magnus/roll coupling; Xeon cloud cost (~$50/solve) not budgeted

## Cost Estimate (lakhs)
CFD: ₹0.05L per solve (cloud Xeon), 20 solves ₹1L. Wind tunnel validation I3 (LIS 1N.m dyno 25rpm 450V Liu IOP 1507/102008) ₹0.3L. Total aero DB ₹1.5L.

## Recommendation
**Use.** Copy L Shang's Excel header structure for SIH deliverable "CAD model + aero". Immediate: run ICEM on `cad_models/out_pgk/pgk_assembly.step` cylindrical domain, sweep Mach 0.8/1.0/1.5/2.0/2.5, AoA 0/4/8deg, Delta 0/5/10deg, populate same table. Add Magnus term per ARDE.

## Links to Code/CAD
- cad_models/generate_pgk_155.py:144 (fin polygon 28.5->FIN_TIP 75.5, hub r5.5) + simulate_trajectory_155.py:40 Cd(Mach) table (needs canard delta columns)
- research/B_aero/ (topology-optimized canard B14)
- SIH26098_Exhaustive_Ideas_Catalog.md:52 (B1-B16)
