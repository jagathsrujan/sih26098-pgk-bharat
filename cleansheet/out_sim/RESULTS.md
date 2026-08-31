# Steering-effectiveness verification — clean-sheet PGK canard mechanism

Runs: 250 paired Monte Carlo runs (identical dispersion draws per variant), seed 20260830.
Truth model: 3DOF point mass, RK4 dt=0.025 s, exponential atmosphere, drag-only,
Cd calibrated to 0.2115 so the nominal shot (46 deg, 827 m/s) lands at 30.0 km
(TOF 90 s, apogee 9.9 km — matches report §3 design case).

## Mechanism modeled
- Fixed-trim canard pair -> constant-force roll-aimed actuator; magnitude via duty cycling
  (as-built CAD: fins are machined at ±3°/0°, nothing moves except the nose roll)
- Lateral authority: 60 N total (fin pair + body lift amplification; audit range 30–100 N)
- De-spin t=25 s; GNSS lock t=35 s (late-lock variant t=60 s); 1 Hz nav updates
- IPP from 1 Hz GPS fixes (pos σ 5 m, vel σ 0.3 m/s) with in-flight drag-scale + crosswind estimation
- Guidance law: a_cmd = 2·miss/t_go², clamped to authority

## Deterministic cases

| Case | Unguided miss (m) | Guided miss (m) |
|---|---|---|
| no error | 0.0 | 3.5 |
| crosswind 6 m/s | 224.6 | 14.8 |
| headwind 6 m/s | 346.4 | 12.5 |
| muzzle +1.5 m/s | 76.0 | 5.6 |
| Cd +5% | 908.9 | 10.5 |

## Monte Carlo (dispersions: V0 σ0.15%, aim σ0.6 mrad, wind σ3 m/axis, Cd σ0.8%, mass σ0.6%)

| Config | CEP50 (m) | mean (m) | p90 (m) | max (m) |
|---|---|---|---|---|
| Unguided | 206.7 | 231.9 | 405.0 | 769.6 |
| Guided (lock 35 s) | 6.9 | 7.6 | 12.0 | 64.9 |
| Guided (lock 60 s) | 10.6 | 45.3 | 129.2 | 482.9 |

**CEP improvement guided/unguided: 29.9×**

- Duty fraction |a_cmd|/a_max: median of per-run peak = 1.00, median of per-run mean = 0.21
- Authority floor (30 N fins): 6 m/s crosswind case guided miss = 19.1 m

## Actuator feasibility (first principles, from BOM masses)
- Rotor-frame J ≈ 0.91e-3 kg·m² → L = 1.43 kg·m²/s at 250 rev/s (matches report §7)
- Rev 1.1 de-spin (10 s): 0.143 N·m → 60 A == peak spec, zero margin — RE-SPECCED
- Rev 1.2 de-spin (15 s): 0.095 N·m → ≤40 A, within cell 45 A continuous (1.39× margin);
  boost stage 3.7→5 V guarantees terminal headroom at −40 °C/50 % SoC (BOM §G)
- Steering roll slews are cheap: 90° in 1 s needs ~5.6 mN·m vs 50 mN·m continuous rating
  → the nose can re-aim essentially instantly compared to the 1 Hz nav cycle

## Known model limitations (next rungs per report §10.1)
- No spin / Magnus / roll channel yet (6DOF rung); drag-only aero with calibrated Cd,
  not tabulated M795 Mach-dependent drag
- Point-mass lateral force: no trim-drag penalty during coast whirl; no actuator lag
  (roll slew ≪ nav cycle — verified above)
- Estimator is a windowed ratio fit, not a Kalman filter — conservative vs a flight implementation
- GPS-denied final-seconds behavior and jamming not modeled
