# 06 — ELECTRONICS: Embedded + Power + Comms

**Team:** ELECTRONICS (3/3, EEE) | **PS Bullet:** Embedded electronics/software + Power + Comms interface

## Your PS Deliverables
- **Embedded electronics and software** for real-time flight control
- **Power management** suitable for high-g launch and flight
- **Communication and programming interface** for fuze config prior to firing
- **Embedded hardware architecture** + **Electronics block diagram** (integrated)
- **Power supply and environmental protection strategy** (electronics side)

## What You Do
- Embedded: STM32G474 (FOC + guidance), ICM-42688, flash, 3.7V bus + 5V boost for de-spin (55A out), FOC ≥15 kHz
- Power: 1×26500 NMC 16.7 Wh, 45A class (≥55A/15s cold pulse at −40°C, ≥18× margin, ≤0.9Wh worst), supercap 15F×2 + brake chopper + dump resistor (40g), regen opportunistic 0–0.2Wh
- Comms: inductive setter (EPIAFS), target/mode/HOB/crypto load, continuity check, crystal-disciplined timer
- Architecture: stator + battery both shell-frame (shear-pinned) → motor power needs no slip ring; only dome 1.5W crosses via 3-contact axial slip ring Ø12

## Key Files
- `cleansheet/03_DESIGN_REPORT.md:4.3` (motor), `4.5` (stack), `5` (power), `7` (physics)
- `cleansheet/02_BOM:A4-A10` (stator, windings, power board, supercap, chopper)
- `SIH26098_Exhaustive_Ideas_Catalog.md:F` (F1-F10), `J` (J1-J6), `D` (sensors power)

## Initial 3 Research Questions
1. Which 26500 cell sustains 40A/15s at −40°C with boost to 5V and <50K ΔT?
2. What 55A boost + 15Ω chopper dissipates 720J with ΔT ≤50K (class H)?
3. How to inductively couple through 2mm GFRP radome with ≥85% RF transmission?

## Branch
`research/06_electronics-embedded-power-<username>` or `electronics/embedded-<username>`
