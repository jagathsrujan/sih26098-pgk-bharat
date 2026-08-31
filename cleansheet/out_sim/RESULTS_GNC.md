# GNC methodology verification — PGK clean-sheet (Rev D)

Runs: 8 primary + 4x4 secondary MC (seed 20260831), paired dispersions.
Truth: 3DOF RK4 dt=0.025, exp atmo, Cd=0.2115 -> nom 30000 km-range TOF90s apo9.9km.
Authority: F(t) = 60 N * q(t)/q(70s) (q70=41392 Pa) — honest q-scaled fin force (F8).
Sensor: NavIC pos 5 m / vel 0.3 m/s 1 Hz, latency 100 ms time-tagged (F6);
  gyro sat 4000 deg/s; accel body-frame averaged (sigma 0.0057 m/s2/sqrt(s)); angle sensor = relative only (F1).

## Rev D architecture (decisions)
- **F1 roll anchor:** nose roll is NOT observable pre-despin (angle sensor is collar-bell RELATIVE; gyro saturated 22x). Post-despin it is anchored by the
  accelerometer drag vector: rotation-invariant azimuth solve - each accel sample is un-rotated by the gyro-propagated reference roll before averaging,
  so slews do not poison windows; 1-Hz updates keep the gyro-bias state observable. Angle sensor keeps commutation + de-spin monitor + S&A roles.
- **F2 actuator:** fixed-magnitude trim force, direction-only; magnitude = phasor duty (dwell d*T at aim, (1-d)*T split +/-90 deg neutral), T=3 s,
  servo rate 360 deg/s / alpha 55 rad/s2, discretization-safe time-optimal slew (no near-target limit cycle).
- **F3:** no translational nav pre-lock (accel centripetal-pinned by spin); hard init from first accepted fix; lock deadline 50 s -> ballistic mode.
- **D7:** 12-state EKF, MODEL-based predict (drag(cd,wind) + g + commanded feedforward - ba), chi2-gated GNSS pos+vel updates, Joseph form.
- **D9 two-time-scale drag:** cd/wind frozen at calibration priors inside the KF (weakly observable; their estimate noise maps 1:1 into IPP error);
  a slow scalar re-fits the along-track velocity drop over a 15-s baseline every 5 s (legacy drop-fit) and feeds the IPP.
- **F10 wobble:** the phasor-duty scheme applies FULL-magnitude sideways force during neutral phases (q at 'apogee' ~21 kPa since horizontal velocity
  ~320 m/s persists) -> +/-1.3 m/s trajectory wobble at the modulation period. Guidance controls the MEAN trajectory: the known commanded wobble is
  cycle-referenced (reset each T_MOD) and subtracted from the state before the IPP; commands are vector low-passed (tau ~ 2 s).
- **F5 laws:** L0 2*miss/t_go^2 (fielded baseline), L2 ZEM 6*miss/t_go^2 (min-energy free-vf), L1 clean APN N=3 (no blend/floor).
- **Fail-safe:** chi2 gate 22.46 (6dof); 3 consecutive rejects or sigma_pos>25 m -> denied (neutral aim, coast); resume <12.5 m; never-lock -> ballistic.

## Deterministic (Rev D)
| Case | Unguided | Rev D L0 | mode | psi err (deg) |
|---|---|---|---|---|
| nominal | — | 33.7 | guide | 0.98 |
| mount bias 5deg | — | 205.4 | denied | 82.31 |
| crosswind 6 | — | 27.3 | denied | 53.80 |
| Cd +5% | — | 176.4 | guide | 0.64 |
| BLIND (no roll ref) | — | 83.1 | guide | nan |

## Monte Carlo (disp V0 s0.15% aim 0.6 mrad wind s3 m/axis Cd s0.8% mass s0.6%)

| Config | CEP50 | mean | p90 | max | dutyPk med | psiErr med (deg) |
|---|---|---|---|---|---|---|
| Unguided | 179.8 | 199.1 | 275.3 | 363.2 | 0.00 | nan |
| Legacy windowed (lock45, Rev C method) | 6.3 | 6.7 | 11.2 | 13.7 | 1.00 | nan |
| Rev D EKF+dragref L0 | 142.6 | 218.5 | 361.5 | 534.8 | 0.69 | 88.96 |
| Rev D ZEM 6dp/tgo2 | 49.8 | 115.5 | 55.2 | 342.2 | 0.93 | 36.03 |
| Rev D APN clean N=3 | 185.9 | 189.1 | 236.1 | 383.3 | 0.40 | 29.57 |
| Rev D L0 outage 60-70s | 77.8 | 89.1 | 90.4 | 179.8 | 0.87 | 59.56 |
| Rev D never-lock (fail-safe) | 178.0 | 194.3 | 271.5 | 357.3 | 0.00 | nan |
| Rev D BLIND (no roll ref) | 95.5 | 93.8 | 104.3 | 139.3 | 0.92 | nan |

**Improvement vs unguided: revD L0 1.3x.**
- end-modes revD_l0: {'denied': 6, 'guide': 2}
- end-modes revD_neverlock: {'ballistic': 8}
- end-modes revD_outage: {'denied': 4}
- ba-cd max|corr| median: 1.445 (conditioning check, Q4)

## Findings
- Rev C's 6.4 m is NOT reproducible under honest assumptions: it relied on an earth-referenced absolute angle sensor (the collar-bell sensor is RELATIVE),
  constant 60 N authority from lock (true authority is q-scaled: ~0.5 N at lock, 60 N mid-descent), no wobble, no latency, no innovation gating.
- The roll channel is THE architecture problem: absolute nose roll does not exist on board until post-despin drag-vector anchoring begins (F1).
- Anchor robustness under wind/mount-bias bias is the top next-rung item: residual quality-gating of anchor windows and the servo/anchor
  interaction need one more hardening pass; deterministic benign cases reach psiErr < 1 deg, biased cases drift (see deterministic table).
- The phasor-duty mechanism's neutral-park wobble is a first-order flight-mechanics effect (not a second-order nicety) and must be carried into the 6DOF rung.

## Implementation budget (STM32G474 170 MHz M4F, 128 K RAM)
- EKF predict 100 Hz model-based: ~2 k FLOPs/tick -> 0.2 M FLOPs/s (~0.15 ms/s).
- Drag-vector roll solve: ~40 FLOPs/fix at 1 Hz — negligible.
- IPP 1 Hz: ~300 RK2 steps x 6-state (~30 FLOPs) ~ 9 kFLOPs (~0.1 ms).
- Total GNC <0.5 ms worst 1 Hz tick vs FOC 15 kHz ISR ~10 us. RAM <5 KB, flash <20 KB.
- FOC electrical freq at hold: 250 rev/s x 12 pairs = 3 kHz (report 4.3 '1.25 kHz' is an arithmetic slip — flag Rev 1.3).

## Known limitations (next rung)
- **1. Roll-anchor robustness (top):** quality-gate the anchor windows; bound the psi_ref/servo feedback interaction; consider GNSS-residual trim-signature
  assistance during high-duty phases (no quiescent windows there). Deterministic biased cases (wind 6 m/s, mount 5 deg) still drift psiErr > 40 deg.
- Shell spin rate constant (aero decay ignored); 6DOF rung adds Magnus/roll-pitch coupling and duty wobble in truth.
- Drag-ref assumes drag dominates body horizontal specific force (true post-despin); validated over MC, not yet over extreme dispersions.
- FOC/motor slew co-simulation still first-order (rate/alpha caps only).
