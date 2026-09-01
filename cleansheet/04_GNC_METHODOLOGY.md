# 04 — Guidance & Navigation Methodology (GNC) for Terminal Accuracy

**SIH26098 clean-sheet PGK · Rev E (2026-08-31)**
Companion to `03_DESIGN_REPORT.md` (§8 decisions 12–19) and `scripts/sim_gnc_check.py`
(`out_sim/RESULTS_GNC.md` carries the machine-generated evidence). This document states
the methodology itself: what is computed on board, in what order, with what models, and
why each choice was made over its rejected alternative.

---

## 1. Problem statement (GNC-relevant slice)

Screw-in guidance kit for a 155 mm M795-class shell (muzzle 827 m/s, 46° quadrant elevation,
nominal 30.0 km / TOF 89.6 s / apogee 9.9 km). Requirement: **CEP50 ≤ 30 m** (PS M2) against
launch dispersions (V0 σ0.15%, aim σ0.6 mrad, wind σ3 m/s/axis, Cd σ0.8%, mass σ0.6%).
Unguided CEP50 under the same dispersions: ~192–240 m.

Hard constraints that shape the whole methodology:

| Constraint | Consequence |
|---|---|
| Canards are machined at fixed trim (±3°) — **nothing moves except the nose roll** | Control is **direction-only**: force magnitude is set by dynamic pressure, not commanded |
| Nose co-rotates at 250 rev/s until de-spin (t = 25–40 s) | Gyro saturates (ICM-45686, ±4,000 °/s FS — selected to match the sim clip; Rev 1.3 methodology wrote ICM-42688, whose FS is ±2,000), accelerometer is centripetal-pinned, angle sensor is collar↔bell **relative** — no absolute roll reference exists before de-spin + first GNSS fix |
| COTS GNSS (NavIC L1/L5, 1 Hz, σ5 m pos / σ0.3 m/s vel, 100 ms latency), jamming expected | Navigation must survive outages; guidance must degrade gracefully |
| STM32G474 (170 MHz M4F, 128 K RAM) shares the die with 15 kHz motor FOC | GNC budget: <0.5 ms worst 1 Hz tick, <5 KB RAM |
| 90 s flight, correction window ≈ 45–90 s | Total lateral impulse is limited by q(t); early authority is ~10% of terminal |

## 2. Mission phasing and frames

Three-frame topology (report §2.1): shell (S) spins; rotor bell (R) de-spins; the canard
shell is rolled by the motor to aim the fixed trim force. Frames used by GNC:

- **Inertial frame (I):** ECEF-local, z up; all navigation states live here.
- **Nose/body frame (B):** accelerometer strapdown frame; differs from the canard-shell
  frame by the unknown mount bias `m` (estimated).
- **Controller frame:** the commanded azimuth schedule; the servo executes *relative*
  rotations (precise collar↔bell encoder), so an absolute aim error equals the absolute
  roll-estimate error — aim quality = estimate quality.

| Phase | t (s) | Navigation | Guidance |
|---|---|---|---|
| Boost/co-rotate | 0–25 | none (sensors unusable) | none |
| De-spin | 25–40 | none (accel pinned by ~2500 g/mm) | none |
| Coast, pre-fix | 40–45 | roll EKF idle, translational EKF not initialized | neutral park |
| Acquire | 45–~47 | hard init from first accepted fix; R ×2 | commands held until an absolute roll estimate exists |
| Guide | ~47–90 | 12-state EKF + drag-referenced roll anchor @ settled windows | IPP + law @ 1 Hz |
| Fail-safe ladder | any | see §7 | degraded / denied / ballistic |

## 3. Navigation methodology

### 3.1 Translational EKF (12-state, model-based predict)

State: `x = [pos³, vel³, ba³, cd_scale, wx, wy]`, discrete predict at 40 Hz (DT_TRUTH step,
IMU-decimated), update at 1 Hz (GNSS pos+vel, 6-vector, latency-propagated).

- **Model-based predict** (not raw-IMU integration): `a = −k(v−w) + ff − ba + g`,
  `k = ½ρ(z)·cd·A·|v−w|/m`, with `ff` = commanded mean force feedforward.
  *Why:* raw-f_meas prediction leaves cd/wind unobservable and lets the trim force trip
  the innovation gate (Rev C evidence); model-based predict makes innovations unbiased.
- **Joseph-form update** with **adaptive R inflation** (E2): a fix is *accepted* with
  `R ← R · clip(NIS/χ², 1, 8)`; only NIS > 10×χ² is rejected outright. A rejected fix
  inflates P (pos ×1.3, vel ×1.6) instead of triggering mode demotion.
  *Why:* Rev D's hard χ² gate caused a reject cascade (3 rejects → denied) in 172/250 MC
  runs — the single largest accuracy killer. Variance inflation keeps the information
  flowing while honestly widening the state uncertainty.
- **Two-time-scale environment estimation** (D9 + E4): `cd`/`wind` are *frozen at
  priors* inside the KF (Q = 0) — they are weakly observable per-fix and their estimate
  noise maps 1:1 into IPP error. A slow outer fit over a 15 s baseline re-fits:
  - `cd_scale`: along-track speed-drop residual vs an incremental model twin that
    integrates the live `a_mean` command history (Euler, 40 Hz);
  - `wy` (cross-wind): cross-track velocity residual / ∫k dt, blended 0.3, clamped ±12 m/s,
    **gated on roll-estimate health** (P small AND anchor innovation sane).
    *Why the gate:* the model applies feedforward at the believed azimuth; the true force
    lands at `pattern − ε`. A roll error ε leaks `|a_mean|·sin(ε)` into the cross residual
    and would otherwise be laundered into a phantom wind that then rotates the anchor's
    drag reference — a destabilizing loop (observed: headwind 6 m/s case fitted wy = 6.1).
  - The fitted `wy` feeds **three** consumers: the IPP, the EKF predict model, and the
    anchor's drag-azimuth reference.

### 3.2 Roll channel — the architecture problem

Absolute nose roll does not exist on board until post-despin (the collar↔bell angle sensor
is relative-only; the gyro is saturated 22× during spin; the magnetometer is swamped by the
motor magnet ring — report §4.5 / §8 decision 12). The methodology:

1. **Drag-vector anchoring.** The body-frame horizontal specific force is dominated by drag,
   whose inertial azimuth is known from the GNSS-tracked velocity and the aero model.
   Each **settled** accel sample is un-rotated into the inertial frame by the commanded
   pattern azimuth, accumulated, and solved against the modeled force vector by a Newton
   rotation solve: `psi_meas = az(ū) − Δ`, with `Δ = az(c̄) − az(m̄)`.
2. **3-state roll EKF** `[ψ, gyro_bias_z, mount_bias]`. The mount bias is a *slow state*
   (E1) — Rev D injected it as a known constant, which is a sim artifact. Innovation-gated
   updates (|y| > 3√S → inflate P, reject); initialization rejected from any window with
   σ > 10°.
3. **Settled-window discipline** (E1 — the core fix). Servo slews (180° park transitions,
   ~0.48 s transit) swing the fin vector through tens of degrees inside a measurement
   window; the averaged vectors lose their azimuth meaning and the solve returns garbage
   (observed: σ 20–3000° windows). Therefore:
   - accumulate only samples where the commanded pattern has been constant ≥ 0.55 s;
   - flush the window at any pattern change (no bimodal ū mixtures);
   - close the window on a fixed count (32) of settled samples — cadence adapts to duty,
     ~1–2 s typical — and continue anchoring through GNSS outages and rejected fixes.
4. **Azimuth-only measurement variance.** `R_psi = (0.8° + |res_⊥|/|c̄|)²` with `res_⊥`
   the perpendicular residual component. Drag-*magnitude* error (cd scale) must not
   inflate the azimuth variance — it does not rotate the vector.
   **Unit-bug note:** Rev D computed `(rad(0.8°) + 57.3·res)` — mixing radians and degrees —
   inflating R ≈ 3283× and silently disabling the anchor (gain ~0). Every Rev D anchor
   result is suspect for this reason; Rev E fixes the units.
5. **Decoupled reference.** Un-rotation reference and modeled fin azimuth both use the
   commanded pattern (not the estimate), removing one estimator feedback path; the
   residual estimate-error feedback enters only via the fin fraction (gain ≈ 0.37 < 1,
   stable).

### 3.3 Impact-point prediction (IPP)

Numerical propagation (RK2, dt 0.15 s) from the **mean-trajectory state** to ground with
the same dynamics as truth (exp atmosphere, drag(cd_hat, w_hat), g). The known commanded
wobble (position + velocity, cycle-referenced) is subtracted from the state before the IPP
(F10) — guidance controls the mean trajectory, the ±90° park excursions are not steered.

## 4. Guidance methodology

- **Laws (trade, same IPP miss):**
  - **L0 (fielded baseline):** `a = 2·miss/t_go²`
  - **ZEM (min-energy, free final velocity):** `a = 6·miss/t_go²`
  - **APN (N=3, clean):** retained for the trade record; consistently worst under 1 Hz nav
    + q-scaled authority (drag biases Vc/λ̇; GNSS noise makes LOS rate noisy at long range).
  Clamped to q-scaled authority `a_auth(t) = F₆₀·q(t)/q(70 s)/m`; deadband 8 m; freeze t_go < 2 s.
- **Command shaping:** vector low-pass (blend 0.55/tick, τ ≈ 1.4 s) so the loop does not
  chase per-cycle estimator ringing; commanded pattern (θ, d) refreshes **every** guidance
  tick (E3) — Rev D refreshed only at 3 s cycle boundaries, adding ~2 s of effective lag.
- **Actuation interface (phasor duty, F2/F13):** fixed-magnitude trim force at azimuth θ(t)
  for a dwell `d·T`, neutral split `(1−d)·T` at θ±90° (zero mean). `d = |a_cmd|/a_auth`.
  The within-cycle wobble (±1.3 m/s velocity at T = 3 s) is commanded and therefore known;
  it is cycle-referenced and subtracted, not fought.

## 5. Fail-safe mode ladder (E2)

```
pre ──fix──▶ acq (R×2, commands neutral until absolute roll exists)
        ──engage──▶ guide ◀──────────┐
        σ>12.5 m ──▶ degraded (R×4, guidance CONTINUES open-loop)  ──σ<12.5──▶ guide
        σ>25 m ────▶ denied (neutral coast, position-only R×16 re-acq) ──σ<8──▶ guide
        never locked / t>50 s ──▶ ballistic (neutral park, timed fuze)
```

*Why "degraded" steers instead of coasting:* the coasting EKF state is still good enough to
halve an IPP miss; Rev D's neutral-coast denied mode was statistically indistinguishable
from unguided (172/250 runs).

## 6. Verification methodology & results

Paired Monte Carlo (identical dispersion draws per variant), 3DOF RK4 truth, exp atmosphere,
Cd calibrated to 0.2115 (nominal 30.0 km). Deterministic stress cases (Rev E, L0):

| Case | Unguided | Rev E | Mode |
|---|---|---|---|
| nominal | 0 | 12.5 m | guide |
| mount bias 5° | 0 | 18.1 m | guide |
| crosswind 6 m/s | 224.6 | 9.4 m | guide |
| headwind 6 m/s | 346.4 | 13.7 m | guide |
| Cd +5% (6σ stress) | 908.9 | 104.5 m | guide |
| BLIND (no roll ref) | 0 | 91.4 m | degraded |

Cd +5% is **authority-limited**, not algorithm-limited: duty saturates ≥0.9 from lock; the
required early correction (a = 2·miss/t_go² ≈ 0.96 m/s² at t_go 42 s) exceeds the q-scaled
early authority (~0.55 m/s²). Rev A/B's "Cd +5% → 10.5 m" assumed constant 60 N from lock
(the F8 dishonesty). At the MC dispersion (Cd σ0.8%) the contribution closes well inside
requirement.

**Full Monte Carlo** (250 primary + 80×5 secondary paired runs, seed 20260901):

| Config | CEP50 | mean | p90 | max | dutyPk med | psiErr med |
|---|---|---|---|---|---|---|
| Unguided | 212.3 m | 239.0 | 450.5 | 735.5 | — | — |
| Legacy windowed (idealized actuator) | 8.9 m | 12.1 | 23.5 | 68.8 | 1.00 | — |
| **Rev E L0** | **21.5 m** | 22.1 | 33.1 | 149.5 | 0.71 | 5.74° |
| Rev E ZEM | 21.5 m | 24.1 | 41.6 | 73.8 | 0.93 | 1.64° |
| Rev E APN (N=3, clean) | 148.6 m | 194.8 | 356.9 | 712.6 | 0.36 | 1.43° |
| Rev E L0, GNSS outage 60–70 s | 17.6 m | 19.2 | 32.1 | 52.3 | 0.71 | 5.55° |
| Rev E BLIND (no roll ref) | 115.2 m | 114.2 | 165.1 | 206.7 | 0.87 | — |
| Rev E L0, wind fit off | 20.8 m | 21.3 | 38.6 | 67.3 | 0.72 | 4.41° |
| Rev E never-lock (fail-safe) | 209.7 m | 240.7 | 456.0 | 728.5 | — | — |

**Gate verdict: CEP50 21.5 m ≤ 30 m (PS M2) under honest assumptions — 9.9× vs unguided;
250/250 runs end in guidance (233 guide + 17 degraded, 0 denied).** The gap to the
idealized-actuator legacy (8.9 m) is the honest price of the real actuator (direction-only,
q-scaled, phasor wobble) and 1 Hz nav — a 0.41× ratio, documented, not hidden.

Full machine-generated evidence: `out_sim/RESULTS_GNC.md` (Rev E, Findings section filled),
plot `out_sim/steering_gnc_revE.png`, run log `out_sim/revE_full_run.log`.

## 7. On-board implementation budget (STM32G474, 170 MHz M4F)

| Block | Rate | Cost |
|---|---|---|
| EKF predict (12×12 F/P) | 100 Hz | ~2 kFLOPs/tick → 0.2 MFLOPs/s |
| GNSS update (Joseph, 6×12) | 1 Hz | ~3 kFLOPs |
| Roll EKF (3×3) + anchor solve | 40 Hz / ~1 Hz | < 0.1 kFLOPs/tick |
| Slow (cd, wy) fit twin | 40 Hz | < 0.1 kFLOPs/tick |
| IPP (300 RK2 × 6-state) | 1 Hz | ~9 kFLOPs (~0.1 ms) |
| **Total GNC** | | **< 0.5 ms worst 1 Hz tick** vs FOC 15 kHz ISR ~10 µs |

RAM < 5 KB (state 96 B, P 1.15 KB, roll states, buffers), flash < 20 KB. Scheduling:
FOC/HRTIM highest priority, GNC on the 100 Hz SysTick, GNSS UART DMA background — all
non-blocking, double-buffered (report §4.5).

## 8. Limitations and next rungs

1. **6DOF truth** (report §10.1 rung 2): Magnus, spin decay, roll-pitch coupling, duty
   wobble in truth; MC ≥ 1000 for the formal CEP claim. Expected to move the CEP budget
   little (aero moments are higher-order for a point-mass translation problem) but must be
   shown, not argued.
2. Roll-anchor validation over extreme dispersions (drag-dominance assumption breaks in
   high-crosswind transient right after de-spin).
3. FOC/motor slew co-simulation remains first-order (rate/alpha caps).
4. GNSS-denied terminal phase: methodology is outage-tested (60–70 s) but not full
   terminal-denied; a late baro/radar-altimeter update is the candidate mitigations.

## 9. Revision trail (evidence)

| Rev | Methodology state | CEP50 (MC) | Why |
|---|---|---|---|
| A/B (`sim_guidance_check.py`) | windowed LS fit, idealized actuator (constant 60 N, no roll channel, no wobble/latency) | 6.9 m | upper bound with dishonest assumptions |
| C (`sim_gnc_check.py revC`) | 12-state EKF, 3 laws — still earth-referenced angle sensor, constant 60 N | ~6.4 m | physically impossible sensor |
| D (`main_revD`) | honest actuator + relative-only sensor; anchor crippled by the rad/deg unit bug + slew-poisoned windows + hard gating | 80 m (172/250 denied) | regression diagnosed in Rev E |
| **E (`main_revE`)** | this document | see RESULTS_GNC.md | unit fix, settled-window anchoring, mount state, adaptive R + mode ladder, wind fit, command-chain latency |
