# 04 — ELECTRONICS: GNC + Sensors + Flight Control

**Team:** ELECTRONICS (1/3, ECE) | **PS Bullet:** Guidance, Navigation & Control for CEP ≤30m

## Your PS Deliverables
- **Guidance and navigation methodology**
- **Flight control algorithms**
- **Sensor selection** (IMU, GNSS/NavIC, baro, mag, proximity)
- **Electronics block diagram** (GNC part)
- **Simulation demonstrating trajectory correction** → `cleansheet/scripts/sim_*.py` + `out_sim/RESULTS*.md`
- **Performance estimation** showing CEP ≤30m

## What You Do
- GNC: 12-state EKF, drag-vector roll anchoring (accel vs GNSS velocity), phasor-duty actuator (T=3s)
- Sensors: ICM-42688 IMU (saturated at launch), NavIC L5 primary + GPS fallback, baro for apogee, mag (swamped by motor — not for roll)
- Control: roll-aimed fin-pair, impact-point prediction, mean-trajectory control (wobble subtraction)
- Sim: `sim_guidance_check.py` (250 MC: 6.9m CEP guided vs 207m unguided), `sim_gnc_check.py` Rev D (295k frames, q-scaled authority)

## Key Files
- `cleansheet/03_DESIGN_REPORT.md:4.5` (radome/GNC), `4.3` (motor), `8` (decisions 12-15), `10` (sim roadmap)
- `cleansheet/scripts/sim_guidance_check.py`, `sim_gnc_check.py`, `out_sim/RESULTS*.md`
- `SIH26098_Exhaustive_Ideas_Catalog.md:C` (C1-C14), `D` (D1-D16)

## Initial 3 Research Questions
1. What EKF tuning keeps drag-ref roll σ <2° with GNSS outages?
2. Which NavIC L5 module achieves cold-start ≤5s post-despin at 45s?
3. How does q-scaled fin authority (60N @ 70s → 0.5N @ lock) map to CEP?

## Branch
`research/04_electronics-GNC-<username>` or `electronics/GNC-<username>`
