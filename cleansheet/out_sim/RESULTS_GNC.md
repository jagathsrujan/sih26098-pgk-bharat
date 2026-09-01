# GNC methodology verification — PGK clean-sheet (Rev E)

Runs: 250 primary + 80x5 secondary MC (seed 20260901), paired dispersions.
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
| nominal | — | 12.5 | guide | 5.33 |
| mount bias 5deg | — | 18.1 | guide | 10.98 |
| crosswind 6 | — | 9.4 | guide | 1.39 |
| headwind 6 | — | 13.7 | guide | 1.05 |
| Cd +5% | — | 104.5 | guide | 0.57 |
| BLIND (no roll ref) | — | 91.4 | degraded | nan |

## Monte Carlo (disp V0 s0.15% aim 0.6 mrad wind s3 m/axis Cd s0.8% mass s0.6%)

| Config | CEP50 | mean | p90 | max | dutyPk med | psiErr med (deg) |
|---|---|---|---|---|---|---|
| Unguided | 212.3 | 239.0 | 450.5 | 735.5 | 0.00 | nan |
| Legacy windowed (lock45, idealized actuator) | 8.9 | 12.1 | 23.5 | 68.8 | 1.00 | nan |
| Rev E EKF+dragref L0 | 21.5 | 22.1 | 33.1 | 149.5 | 0.71 | 5.74 |
| Rev E ZEM 6dp/tgo2 | 21.5 | 24.1 | 41.6 | 73.8 | 0.93 | 1.64 |
| Rev E APN clean N=3 | 148.6 | 194.8 | 356.9 | 712.6 | 0.36 | 1.43 |
| Rev E L0 outage 60-70s | 17.6 | 19.2 | 32.1 | 52.3 | 0.71 | 5.55 |
| Rev E BLIND (no roll ref) | 115.2 | 114.2 | 165.1 | 206.7 | 0.87 | nan |
| Rev E L0 wind_fit=False | 20.8 | 21.3 | 38.6 | 67.3 | 0.72 | 4.41 |
| Rev E never-lock (fail-safe) | 209.7 | 240.7 | 456.0 | 728.5 | 0.00 | nan |

**Improvement vs unguided: revE L0 9.9x (legacy idealized-actuator reference: 0.41x).**
- end-modes revE_l0: {'guide': 233, 'degraded': 17}
- end-modes revE_neverlock: {'ballistic': 250}
- end-modes revE_outage: {'guide': 78, 'degraded': 2}
- ba-block max offdiag corr median: 0.013 (E5 conditioning check)

## Findings
- **Requirement gate: revE L0 CEP50 21.5 m vs 30 m (PS M2) under honest assumptions — 9.9x vs unguided.** End-modes revE_l0 {'guide': 233, 'degraded': 17} — the Rev D deny-cascade (172/250 denied) is eliminated.
- **The dominant fix was a units bug, not new machinery:** Rev D computed anchor R as (radians(0.8 deg) + 57.3*res_ratio)^2 — radians and degrees mixed —
  inflating the anchor measurement variance ~3283x and silently disabling drag-referenced roll anchoring (gain ~0). Every Rev D anchor result is invalid
  for this reason; the 'roll-anchor robustness' next-rung item was in fact an inert-sensor bug plus slew-poisoned windows.
- **Settled-window discipline makes the anchor real:** windows closed on 32 settled samples (servo quiescent >= 0.55 s), flushed at every pattern change;
  anchor sigma 20-3000 deg (slew-poisoned) -> ~1-2 deg. Deterministic mount-bias 5 deg: 205.4 -> 18.1 m; crosswind 6: 27.3 (denied) -> 9.4 m.
- **Adaptive-R + mode ladder (E2):** accepting fixes with R inflated by NIS/gate (reject only >10x) plus degraded-guidance (sigma>12.5 m still steers
  open-loop) converts the deny cascade into continued steering; outage 60-70 s CEP50 17.6 m.
- **Wind fit neutral in MC (revE_l0 21.5 vs wind_fit=False 20.8 m, within noise) and kept:** it removes the
  epsilon-rotated-feedforward -> phantom-wind -> anchor-reference feedback loop (ungated: headwind 6 fitted wy=6.1 phantom) and closes
  deterministic crosswind to 9.4 m.
- **Law trade:** ZEM 21.5 ties L0; APN remains rejected (148.6) under 1-Hz nav + q-scaled authority.
  BLIND (no roll ref) 115.2 m — the roll channel is worth ~5x, confirming roll anchoring as THE architecture problem.
- **Limiting error budget now:** terminal q-scaled authority (Cd+5% stress 104.5 m is authority-limited, duty >=0.9 from lock), phasor wobble phase
  at impact, and the anchor noise floor (psiErr med 5.74 deg vs 0.8 deg design floor). Next rung: 6DOF truth (Magnus, spin decay), MC >=1000.

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
