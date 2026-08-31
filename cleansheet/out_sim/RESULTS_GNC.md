# GNC methodology verification — PGK clean-sheet (Rev E)

Runs: 8 primary + 4x5 secondary MC (seed 20260901), paired dispersions.
Truth: 3DOF RK4 dt=0.025, exp atmo, Cd=0.2115 -> nom 30000 m-range TOF90s apo9.9km.
Authority: F(t) = 60 N * q(t)/q(70s) (q70=41392 Pa) — q-scaled fin force (F8, unchanged).
Sensor: NavIC pos 5 m / vel 0.3 m/s 1 Hz, latency 100 ms time-tagged (F6);
  gyro sat 4000 deg/s; accel body-frame averaged (sigma 0.0057 m/s2/sqrt(s)); angle sensor = relative only (F1).

## Rev E architecture (decisions on top of Rev D F1-F8/D7/D9/F10)
- **E1 anchor hardening:** mount bias is a slow STATE (3-state roll EKF psi/gyro-bias/mount; Rev D injected it as known — a sim artifact);
  anchor windows run on a fixed 1-Hz cadence (continue through outages and rejected fixes); windows straddling a T_MOD pattern boundary are
  discarded; updates are innovation-gated (|y|>3sqrt(S) -> inflate P, reject); un-rotation reference AND modeled fin force both use the
  commanded pattern (estimate-independent), removing an estimator feedback path.
- **E2 robust gating (kills the denied cascade):** adaptive R inflation — accept with R scaled by NIS/gate clamped x8; outright reject only
  above 10x gate. Mode ladder: pre -> acq (R x2) -> guide -> degraded (sigma>12.5 m: R x4, guidance CONTINUES open-loop) -> denied
  (sigma>25 m: neutral coast + position-only R x16 re-acquisition, resume sigma<8 m) -> ballistic (never locked).
- **E3 command-chain latency:** theta/d refresh every guidance tick (was 3-s cycle boundary); command low-pass 0.4 -> 0.55.
- **E4 slow (cd_scale, wy) fit:** 15-s model-propagation baseline replaces the Rev D along-track accumulators; fitted cross-wind wy feeds
  the IPP, the EKF predict model AND the anchor drag-azimuth reference. wind_fit=False fallback run for the trade.
- **E5 metric fix:** Rev D's ba-cd correlation was invalid with cd frozen (reported 1.45); replaced by live ba-block off-diagonal conditioning.

## Deterministic (Rev E)
| Case | Unguided | Rev E L0 | mode | psi err (deg) |
|---|---|---|---|---|
| nominal | — | 14.0 | guide | 7.56 |
| mount bias 5deg | — | 49.8 | degraded | 55.30 |
| crosswind 6 | — | 30.7 | guide | 23.32 |
| headwind 6 | — | 59.7 | guide | 26.53 |
| Cd +5% | — | 152.3 | guide | 0.60 |
| BLIND (no roll ref) | — | 81.6 | degraded | nan |

## Monte Carlo (disp V0 s0.15% aim 0.6 mrad wind s3 m/axis Cd s0.8% mass s0.6%)

| Config | CEP50 | mean | p90 | max | dutyPk med | psiErr med (deg) |
|---|---|---|---|---|---|---|
| Unguided | 183.4 | 220.6 | 408.8 | 427.0 | 0.00 | nan |
| Legacy windowed (lock45, idealized actuator) | 7.9 | 8.6 | 14.6 | 16.0 | 1.00 | nan |
| Rev E EKF+dragref L0 | 38.4 | 47.0 | 88.2 | 97.0 | 0.79 | 10.90 |
| Rev E ZEM 6dp/tgo2 | 23.0 | 25.9 | 23.5 | 40.3 | 0.72 | 12.15 |
| Rev E APN clean N=3 | 157.0 | 236.0 | 182.3 | 523.6 | 0.31 | 15.07 |
| Rev E L0 outage 60-70s | 16.1 | 23.2 | 18.3 | 48.3 | 0.77 | 11.63 |
| Rev E BLIND (no roll ref) | 101.3 | 103.5 | 132.0 | 156.7 | 0.86 | nan |
| Rev E L0 wind_fit=False | 21.1 | 24.6 | 21.4 | 39.9 | 0.79 | 7.21 |
| Rev E never-lock (fail-safe) | 184.2 | 216.6 | 397.5 | 415.6 | 0.00 | nan |

**Improvement vs unguided: revE L0 4.8x (legacy idealized-actuator reference: 0.21x).**
- end-modes revE_l0: {'guide': 8}
- end-modes revE_neverlock: {'ballistic': 8}
- end-modes revE_outage: {'guide': 3, 'degraded': 1}
- ba-block max offdiag corr median: 0.006 (E5 conditioning check)

## Findings
- (filled after Rev E analysis — see final section)

## Implementation budget (STM32G474 170 MHz M4F, 128 K RAM)
- EKF predict 100 Hz model-based: ~2 k FLOPs/tick -> 0.2 M FLOPs/s (~0.15 ms/s).
- Drag-vector roll solve: ~40 FLOPs/window at 1 Hz — negligible.
- Roll EKF now 3x3: ~60 FLOPs/predict tick — negligible.
- Slow fit model propagation: 100 RK2 steps per 15 s — amortized <0.05 ms/s.
- IPP 1 Hz: ~300 RK2 steps x 6-state (~30 FLOPs) ~ 9 kFLOPs (~0.1 ms).
- Total GNC <0.5 ms worst 1 Hz tick vs FOC 15 kHz ISR ~10 us. RAM <5 KB, flash <20 KB.

## Known limitations (next rung)
- Shell spin rate constant (aero decay ignored); 6DOF rung adds Magnus/roll-pitch coupling and duty wobble in truth.
- Drag-ref assumes drag dominates body horizontal specific force (true post-despin).
- FOC/motor slew co-simulation still first-order (rate/alpha caps only).
