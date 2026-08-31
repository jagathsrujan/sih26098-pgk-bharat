# SIH26098 — Clean-Sheet Precision Guidance Kit: Detailed Design Report
**Project:** Low-Cost PGK + Smart Electronic Fuze, 155 mm Artillery Shell ("PGK Bharat" clean-sheet track)
**Doc:** `cleansheet/03_DESIGN_REPORT.md` | **Rev:** 1.3 | **CAD of record:** `cleansheet/PGK_CleanSheet.FCStd`
**Rev 1.1 change:** CAD of record now contains a **native FreeCAD Assembly** (24 links, 23 joints + ground) and a **kinematic Simulation** (122 frames @ 30 fps) implementing the §2.1 three-frame topology — see §2.4.
**Rev 1.2 change:** steering-effectiveness sim added (§10.1 precursor — `scripts/sim_guidance_check.py`, `out_sim/RESULTS.md`: guided CEP 6.9 m vs unguided 207 m); de-spin re-specced **15 s @ ≤40 A** with boost stage (was 10 s/60 A regen-dominant, zero torque margin); GNSS lock 35→45 s; energy ledger restated. Spec deltas: BOM §G.
**Rev 1.3 change:** GNC methodology pass (`scripts/sim_gnc_check.py`, `out_sim/RESULTS_GNC.md` Rev D). §4.5 roll-reference story corrected — the collar↔bell angle sensor is **relative-only**; absolute nose roll is acquired post-despin by drag-vector referencing against GNSS velocity (accelerometer). Fin authority restated as **q-scaled** (60 N reference = q at 70 s; ~0.5 N at lock). §4.3 electrical frequency corrected 1.25→3 kHz at hold. §8 decisions 12–15 added.
**Companion docs:** `00_REQUIREMENTS.md`, `02_BOM_MANUFACTURING_ASSEMBLY.md`, `01_POWER_MOTOR_SPEC.md`
**Coordinate system:** origin at shell base center, +Z toward nose. Fuze seat plane z = 696.0. All dimensions mm.

---

## 1. Scope & boundary

This report documents the **inert exhibition / analysis design** of a screw-in precision guidance kit (PGK) replacing the standard fuze on a 155 mm shell. It is **not launch hardware**: no energetics, no live S&A, no initiator. Flight performance (CEP, survivability) is simulation/analysis only. Flight-artifact energetics are partner-supplied (qualified ESAF, STANAG 4187).

**Design drivers (from PS SIH26098):** CEP ≤ 30 m · retrofit to standard 155 mm (ATAGS/Dhanush/K9/M777) · survives launch (15,000 g design peak, ~267 rev/s spin) · multi-mode fuze (proximity/time/impact) · pre-fire setter · SWaP-C low · target kit cost ≤ ₹8–11 L.

---

## 2. System architecture

### 2.1 Three-frame topology

The kit is organized around **exactly three rotating frames**:

| Frame | Rotation | Members |
|---|---|---|
| **S — Shell** | ~250–267 rev/s (rifling-imposed) | shell body, bearing outer ring (threaded into well, torque anchor via shear pins), core cartridge (pinned S1→S), stator, battery, ignitor interface |
| **R — Rotor/Canard** | motor-positioned at roll angle ψ (~0 absolute) | outrunner bell + magnet ring, one-piece canard shell (4 fins), pilot bearing, radome + full electronics stack |
| *(balls between S and R = the de-spin joint)* | | |

**Steering principle:** the rotor frame is roll-aimed so its fin-pair lift vector points at the miss vector; the 0°/180° fin pair deflects together (mirrored ±3° at trim) to command correction magnitude; the 90°/270° pair rides neutral. Mirror-symmetric pair deflection ⇒ pure radial force, zero side force, zero roll coupling.

### 2.2 Assembly tree
See `02_BOM_MANUFACTURING_ASSEMBLY.md` §A (assembly tree, 30+ items in 3 frame groups).

### 2.3 Operation timeline

```
t=0        bore ride: setback 15 kg·g design peak; module co-rotates (S frame)
t≈2 s      muzzle exit; battery-backed electronics boot; GNSS receiver ON (not acquiring)
t≈2–25 s   ballistic coast, co-rotating at shell rate; MEMS gyros saturated by roll —
           roll estimate carried by the absolute magnetic angle sensor (spin-proof)
t≈25 s     motor spin-up → DE-SPIN TRANSIENT: rotor braked 250→0 rev/s over ~15 s
           (≤40 A boost-sourced braking — Rev 1.2; was 10 s/60 A regen-dominant, zero torque margin)
t≈40 s     de-spin complete
t≈45 s     GNSS/NavIC acquisition (scheduled post-despin; antenna now steady)
t≈45 s+    guidance active: impact-point prediction, ψ updates each nav cycle,
           0/180 pair deflection commands correction (start EARLY — see §8.2)
t≈80 s     proximity head armed (HOB 6/12/18 m) or time/impact per setting
t≈90 s     fuze action
```

### 2.4 Kinematic assembly & simulation in CAD (Rev 1.1)

The three-frame topology is now **implemented as a native Assembly inside the CAD of record** (`PGK_CleanSheet.FCStd`), not just paper. Objects created (2026-08-30):

| Object | Content |
|---|---|
| `Assembly` | container with 24 `App::Link` members (one per part, shell → nose) |
| `Assembly > Joints` (`Assembly::JointGroup`) | 1 `GroundedJoint` (shell body = S frame, simulation reference) · 21 `Fixed` joints (band + bearing outer ring + balls + battery + cartridge + initiator interface + stator + windings A/B/C + Hall sensors + pilot bearing → S; stub shaft + magnet ring → rotor; fins + radome + dome ring + GNC + GNSS + prox head + bearing inner ring → R) · **2 `Revolute` joints**: `J_MotorRotor` (S↔rotor bell) and `J_RollDecouple` (S↔canard shell R frame) |
| `Assembly > Simulations > Simulation` | 0→4 s, 30 fps, 122 frames; `Motion_Rotor_Spin` = `3.1416*time` rad/s (180 °/s ≈ de-spin/steer motor motion, exaggerated for visibility) on `J_MotorRotor`; `Motion_Nose_RollDecouple` = `-1.0472*time` rad/s (−60 °/s, opposite sense — roll decoupling) on `J_RollDecouple` |

**What it demonstrates:** playing the Simulation (Assembly WB → double-click `Simulation` → Play) shows the rotor bell + magnet ring spinning one way inside the shell while the canard shell + fins + radome + electronics stack roll the opposite way — the bearing de-spin joint and the motor-positioned rotor frame of §2.1, kinematically closed. Solver return 0 (no conflicts, nothing over-constrained); joint coordinate systems are identity at the shell axis (global Z through origin), parts verified unmoved by the solve.

**Modeling simplifications (on record):** joints use whole-part references with detached identity JCS (faces referenced only for solver part-mapping); bearing balls are Fixed to S (visual duty only — flight duty is rolling contact); drives are kinematic position histories, not dynamic torque simulation; integration shows ≈6° drift over 4 s (nominal for the frame-based kinematic solver, irrelevant at this fidelity).

---

## 3. Interface with host shell

| Item | Value | Note |
|---|---|---|
| Shell reference | M795-class envelope | 696 mm long, Ø154.9 body, 4.07-cal tangent ogive, modeled in CAD as host |
| Well thread | **2-12UN-1A RH, FULL cavity depth** | crest Ø48.0 / root Ø50.8, pitch 2.1167, ~42 turns over z 606–696 |
| Well mouth | countersink 45° × 2.5 (Ø50.9→Ø55.9) | lead-in |
| Install torque | 50 N·m + anti-seize | standard fuze practice |
| **Design divergence (on record):** | full-depth thread | STANAG wells thread only ~25 mm; full-depth gives 3.8× shear area for setback/torque. Mating shank must match. |

**Launch environment (design cases):** setback 15,000 g peak (kinematic mean ~5,000 g, peak/mean ≈ 3); spin 267 rev/s at 827 m/s muzzle; temperature −40…+60 °C; 60–90 s flight; apogee 10–12 km at 30 km range.

---

## 4. Subsystem design

### 4.1 De-spin bearing (the rotation joint)

A full-face angular-contact-style ball bearing occupying the entire fuze well — the mechanical heart of the kit.

| Parameter | Value |
|---|---|
| Outer ring | male 2-12UN-2A thread (crest Ø50.7 / root Ø48.2) × 90 long; race bore Ø43.0 H6; torus race grooves R2.0; 100Cr6, 60 HRC, Ra 0.4 |
| Inner ring | race OD Ø37.0 (grooved), bore Ø32.0 H6; **retention lip ID Ø29.6 × 2 at bore bottom [REQ]**; 100Cr6 |
| Balls | Ø3.0, 10 rows (z = 612+9k) × 16/row, on Ø40 circle; G10 chrome steel (flight option: Si₃N₄ hybrid for skid resistance); snap-in cage (2-piece) |
| Differential speed | 250 rev/s continuous (shell vs carrier) — normal bearing duty |
| Race groove depth | 0.5 mm ball pockets (torus major R20 / minor R2) |

**Physics check:** flight loads on balls ≤ ~10 N (setback is taken by retention lip + shear pins, NOT the balls — see §8.1). Ball speed class ~9,000 rpm — standard greased-bearing duty.

**Open:** cage design, lubricant spec (space-grade grease), spin-bench survival test at 15,000 g spike.

### 4.2 Core cartridge (power + ignition interface)

One-piece 7075-T6 turn-mill part, the "spine" inside the bearing bore:

| Feature | Value |
|---|---|
| Journal OD | Ø31.6 g6 in Ø32 bore (running fit) |
| Length | z 606–712 (floor, ignitor bay, partition, battery bay, collar flange Ø40 × 16) |
| Ignitor bay | z 610–632: inert pad Ø25 × 3 + Ø6 boss toward booster seat; **flight: qualified initiator interface, fires axially into booster** (frame crossing is axial-only — rotation-invariant) |
| Battery bay | z 634–692, Ø25.6: one 26500 high-drain Li-ion + BeCu spring contacts (self-connecting into collar) |
| Firing channel | Ø2.4 in cartridge wall at x = +14.3 (bridged 0.3 mm inside OD/ID — no journal breach), routes ignitor → S&A/power board |
| Axial retention | **[REQ]** cartridge floor seats on inner-ring retention lip (takes 220 kN setback; bypasses balls) |
| Torque anchor | **[REQ]** 4× Ø3 shear pins (4–6 kN each) cartridge collar ↔ outer ring top face |

**Battery decision (§ power):** one 26500 high-drain Li-ion (NMC), 4.5 Ah / 16.7 Wh / 45 A class. Rationale in §7.2.

### 4.3 Pancake outrunner actuator (de-spin + steering + generation)

Mounted on the collar (cartridge frame, **shear-pinned to shell ⇒ shell-locked stator**); rotor bell drives the canard shell.

| Parameter | Value | Basis |
|---|---|---|
| Topology | outer-rotor pancake BLDC, 24 slots / 12 pole-pairs (flight EM; CAD shows 24 magnet segments — pole change on record) | torque density vs drive feasibility |
| Stator | yoke Ø45–72, teeth to Ø73.4, stack 16, M350-50A laminations; 24 Cu coils (AWG22), star | CAD |
| Rotor bell | Ø76.4–83 × 22 wall + cap Ø83; magnet ring Ø74.7–76.4 × 15, N42SH, potted | CAD |
| Air gap | 0.5 mm radial | CAD |
| **K_T (decided)** | **0.0024 N·m/A** (single-turn-class winding) | voltage-wall: EMF = K_T·ω ≤ 3.7 V bus at ω_rel = 1,571 rad/s |
| Peak | 0.095 N·m @ ≤40 A for 15 s (de-spin; boost-sourced braking — Rev 1.2) | L = 1.43 kg·m²/s (J from BOM masses, sim-verified) ÷ 15 s; 1.39× current margin |
| Continuous | 0.05 N·m @ 5 A | roll hold (aero disturbance ~mN·m) + corrections |
| Electrical frequency | ≤ 3 kHz at max relative rate (250 rev/s × 12 pairs; Rev 1.3 — 1.25 kHz was an arithmetic slip) | FOC current loop ≥ 15 kHz |
| Feedback | absolute magnetic angle sensor (collar↔bell), 12-bit = 0.09° | also spin-signature source for S&A |
| Support | pilot: Ø20.4 stub shaft + thin-section bearing Ø20.8/24.7 (carries bell only) | CAD |

**EM budget:** B ≈ 0.6 T, active length 16 mm, r = 37 mm ⇒ F ≈ 0.1 N/conductor·A ⇒ >1 N·m available at 10 A ⇒ ≥7× torque margin over de-spin/hold requirement. Thermal: ≤720 J copper loss over the 15 s pulse (40 A) → adiabatic ΔT ≤50 K, class H — no heatsink needed.

### 4.4 One-piece machined canard shell

7075-T6 billet, 5-axis, 2 setups: cap Ø89 × 4 (pilot bore Ø21.2; 6× M3 on Ø72 BC to bell) + stepped drum (Ø84–89 upper, step shoulder, Ø81–85 lower band) + **four integral delta fins**:

| Parameter | Value |
|---|---|
| Planform | root chord 24 (z 697.5–721.5, on lower drum), tip chord 18, span 24.5, tip Ø138 (< Ø153 bore ✓) |
| Sweep | LE swept 6 mm aft; TE vertical |
| Section | 3 mm plate, 1 mm edge bevels (hexagonal section, 3-section loft) |
| Incidence/trim | **0°/180° pair +3°/−3° mirrored about own quarter-chord hinges** (net radial force, no side force); 90/270 neutral |
| Root blend | 3 mm machined fairings, both faces, full chord |
| Camber | (earlier revs) 2% bent-plate — flight option: flat machined plate at neutral, deflection-only control |

### 4.5 Radome + electronics stack (rotor frame)

| Part | Detail |
|---|---|
| Radome | tangent-ogive shell Ø84 base × 49.6 tall, tip R2, wall 2 mm, GFRP E-glass (RF ≥85% transmission); z 726.5–776.1 |
| Base ring | Al 6061 Ø76–84 adapter |
| GNC board | Ø62 4-layer: STM32G474 (FOC + guidance), ICM-42688 IMU, flash; z 728.2 |
| GNSS/NavIC | Ø25 ceramic patch + L1/L5 multi-constellation module; z 734.6 (zenith-facing) |
| Prox head | FMCW 24 GHz Ø30 + patch, HOB 6/12/18 m; z 738.3–746.3 |
| Slip ring | 3-contact axial Ø12 (dome power ~1.5 W crosses rotor↔shell frame) |

**Sensor/processor logic (Rev 1.3):** the collar↔bell angle sensor is a **relative** device — during co-rotation it reads a constant and carries **no** inertial roll information; the nose gyro is saturated 22× (250 rev/s = 90,000 °/s vs 4,000 °/s clip). Absolute nose roll therefore does not exist on board until the nose is de-spun; it is then **acquired by drag-vector referencing**: the accelerometer's horizontal specific force (drag-dominated, ~2 m/s²) is compared in azimuth against the GNSS-velocity drag direction, giving absolute roll to ~0.3–2° per second, continuously, with the gyro propagating between fixes. The angle sensor's real roles: FOC commutation, de-spin progress monitor, S&A spin signature. Its 0.09° resolution is commutation-relevant, not a roll-reference budget item. Residual slow aim biases (mount, trim-model) self-correct through the closed guidance loop. GNSS acquisition is scheduled after de-spin settles. See `out_sim/RESULTS_GNC.md` (Rev D) for the estimator/guidance methodology and §8 decisions 12–15.

### 4.6 Multi-mode fuze (functional architecture)

- **Impact:** axial accelerometer logic (nose-mounted in dome), threshold + duration signature.
- **Time:** software timer from muzzle-exit epoch, set by setter, crystal-disciplined.
- **Proximity:** FMCW head, HOB 6/12/18 m selectable; steady (de-spun) beam is the enabling feature of the bearing architecture.
- **S&A:** electrical safe-and-arm logic — firing line default-shorted, interrupted until three independent signatures: setback ≥ threshold (g-switch), spin ≥ threshold (angle sensor rate), bore-exit timer. Fail-any → safe. Energetics by partner.

### 4.7 Pre-fire configuration

Inductive setter (EPIAFS-class, ground unit): loads target grid, fuze mode, HOB/time, crypto keys; runs initiator continuity checks; inductively couples through the shell wall — no pins.

---

## 5. Power system (decided)

| Item | Decision | Basis |
|---|---|---|
| Battery | **1× 26500 high-drain Li-ion (NMC), 4.5 Ah, 16.7 Wh, 45 A class**, in core bay (bay bored Ø26.2) | rechargeable; de-spin re-specced **≤40 A/15 s** — within the cell's continuous rating (Rev 1.2); boost stage (A6) guarantees cold-start voltage headroom; fits bay |
| Chemistry rejects | Li-SOCl₂ (primary — cannot take regen/high pulse); thermal battery (one-shot, no regen, cost) | §7.2 |
| Bus | 3.7 V single-cell + **de-spin boost to 5 V** (Rev 1.2); motor winding matched (K_T 0.0024); logic rails via buck/LDO | fits bay geometry |
| Energy ledger | consumption ≤ **0.9 Wh worst** (de-spin 0.83 boost-sourced + electronics 0.025 + roll-hold 0.05); regen return **opportunistic 0–0.2 Wh** | Rev 1.2 — was 0.10 Wh with 0.2–0.3 Wh regen reliance |
| Margin | 16.7 Wh vs ≤0.9 Wh worst ⇒ **≥18×** (≥8× after −40 °C/50% derate) | |
| Residual risk | Li-ion cold soak at −40 °C: ogive stagnation + setback heating give a few °C; qualify cell at cold | risk register R7 |
| Regen crossing | stator + battery both shell-frame (post shear-pins) ⇒ motor power needs **no slip ring**; only dome ~1.5 W crosses (C3 slip ring) | §4.3 |

---

## 6. Mass & SWaP rollup

| Group | Mass |
|---|---|
| Core + battery + power (shell frame) | ≈ 414 g (Rev 1.2: +chopper/boost/fitting) |
| Bearing (rings, balls, cage) | ≈ 515 g |
| Actuator (stator, windings, magnets, shaft, pilot bearing) | ≈ 470 g |
| Canard shell + radome + electronics | ≈ 445 g |
| **Total** | **≈ 1.84 kg as-built** → optimization path (thin-wall A1 ring, Al bell yoke w/ steel sleeve): **≈ 1.56 kg** (hard limit 2.0 kg; ≤1.5 kg now a stretch — see BOM §G) |

Module: ~260 mm total (90 in-well + ~170 protrusion). SWaP-C fit: P3 pass after mass optimization; cost pass (§ BOM: ex-works ~₹0.7–0.9 L @1k units, 8–12% of PS ceiling).

---

## 7. Physics verification audit (first-principles)

| # | Mechanism | Requirement | Delivered | Margin | Verdict |
|---|---|---|---|---|---|
| 1 | Setback design level | survive shot | 15,000 g design (kinematic mean ~5,000 g, peak/mean ≈ 3) | — | ✓ case |
| 2 | Steering force (30 km, correct from ~45 s-to-go) | 2×300/45² × 46 kg ≈ **14 N** | 30–100 N (fin pair + body lift amplification 2–3×) at 3–5° of ±8° authority | 2–7× | ✓ |
| 3 | De-spin torque | L/t = 1.43/15 = **0.095 N·m** | 0.095 @ ≤40 A for 15 s, boost-sourced (Rev 1.2); EM ≥1 N·m @10 A | 1.39× current margin; ≥10× EM | ✓ |
| 4 | Voltage wall | braking current sustainable at ω_rel 1,571 rad/s | boost stage 3.7→5 V ⇒ terminal headroom ~3× at −40 °C/50 % SoC (Rev 1.2; was exact-fit regen) | 1.39× | ✓ |
| 5 | Energy | ≤ 0.9 Wh worst | 16.7 Wh (+ opportunistic regen 0–0.2 Wh) | ≥18× | ✓ (Rev 1.2) |
| 6 | Fin structure | — | root bending 33 MPa vs 500 MPa (7075) | 15× | ✓ |
| 7 | Pointing/roll | ψ error → miss | drag-ref roll anchor σ ~0.3–2°/fix (Rev 1.3); angle sensor is relative-only (commutation role); gyro drift bounded by 1-Hz re-anchoring | inside 30 m budget, **analysis pending anchor robustness pass** | ✓ w/ condition |
| 8 | Roll hold | vs aero disturbance (mN·m) | 0.05 N·m continuous | 10×+ | ✓ |
| 9 | Radome heating | M ≈ 0.8 descent | +38 °C stagnation | negligible | ✓ |
| 10 | Setback axial path | 220 kN | **[REQ] retention lip** — designed, not yet in CAD | — | ✗→REQ |
| 11 | Torque anchor | steering reaction | **[REQ] shear pins** — designed, not yet in CAD | — | ✗→REQ |
| 12 | Control timing | start correcting post-despin | control-law requirement (late-only correction is 3× short) | — | ✓ w/ condition |

**Verdict:** every physical mechanism closes with margin **once REQ items 10–11 are modeled** — both are simple geometry, no physics barrier. Condition: guidance begins correcting immediately after de-spin.

## 8. Key design decisions & rationale (decision log)

| # | Decision | Alternatives rejected | Rationale |
|---|---|---|---|
| 1 | Roll-aimed carrier + pair deflection | (B) phase-synchronous actuation at 250 Hz — needs 250 Hz servo bandwidth, infeasible; (D) drag brakes — 3× too weak; (E) moving mass — 50× weak | only family where control = "hold angle" at 10 Hz-class mechanism |
| 2 | Fixed-span fins on machined shell | flip-out hinges | integral joints beat hinged joints on fatigue/flutter; bore-span cap accepted (Ø138 < 153) |
| 3 | Full-depth well thread | STANAG 25 mm practice | 3.8× engagement for setback/torque; documented divergence |
| 4 | Bearing-in-well as de-spin joint | spin-decoupling obturator band (shell spins, carrier free) | bearing shows the differential rotation explicitly; demo-friendly; carrying structure doubles as joint |
| 5 | Pancake motor = de-spin + steer + harvest | separate de-spin mechanism + steering servos + thermal battery | one machine, three functions; removes thermal battery (cost/logistics) |
| 6 | K_T 0.0024 low-KT winding | high-KT drone winding (390 V EMF wall) | voltage-wall arithmetic (§8.4 audit) |
| 7 | Single 26500 Li-ion | Li-SOCl₂ primary; thermal battery; 3S pack | rechargeable for regen; fits bay; 45 A class; 30× energy margin |
| 8 | Mirrored pair trim ±3°, own-side hinges | same-sign pair (buggy first rev) | mirror symmetry ⇒ pure radial force, no side force/roll coupling |
| 9 | One-piece machined canard shell | printed fins + fasteners | no root joints (flutter/fatigue), YIL machining story, fin clocks + balance in one setup |
| 10 | Electronics stack on rotor frame | shell-frame electronics + slip-ring everything | IMU measures commanded frame directly; antennas steady; only 1.5 W crosses via slip ring |
| 11 | All-COTS electronics | rad-hard/custom | 90 s mission, error-corrected; cost |
| 12 | Roll reference = drag-vector anchoring (accel × GNSS velocity), post-despin only | earth-referenced angle sensor (physically impossible — sensor is relative); magnetometer (motor magnet ring swamps Earth field) | no new hardware; σ ~0.3–2°/fix; angle sensor stays on commutation/S&A |
| 13 | Phasor-duty actuation model (dwell at aim, ±90° neutral split, T = 3 s) | continuous proportional-force model (not realizable — trim is machined in) | honest actuator: force magnitude is fixed by aero, direction-only control |
| 14 | Two-time-scale drag estimation (KF cd frozen at prior; slow 15-s along-track scalar fit) | per-fix cd/wind states in KF (weakly observable, estimate noise maps 1:1 into IPP error, gate churn) | along-track IPP bias needs cd; bandwidth separation stabilizes it |
| 15 | Guidance controls the MEAN trajectory (cycle-referenced wobble subtraction + command low-pass) | chasing 1-Hz IPP miss incl. wobble (servo churns, no quiescent windows, anchor starvation) | neutral-park wobble is ±1.3 m/s — first-order, must be modeled |

## 9. Open items (REQ register)

| ID | Item | Type | Status |
|---|---|---|---|
| REQ-1 | Retention lip (inner ring bore bottom, ID Ø29.6 × 2) | axial load path | designed, not modeled |
| REQ-2 | Shear pins 4× Ø3 (collar ↔ outer ring) | torque anchor | designed, not modeled |
| REQ-3 | Magnet ring pole change 24 → 12 pairs | EM drive feasibility | spec'd, CAD pending |
| REQ-4 | Rotor bell yoke ring (steel back-iron behind magnets) | EM | spec'd, CAD pending |
| REQ-5 | Ball cage (2-piece snap) | bearing | spec'd, CAD pending |
| REQ-6 | Slip ring 3-contact axial at pilot shaft | dome power | spec'd, CAD pending |
| REQ-7 | ESAF + initiator partner interface | fuze | architecture only |
| REQ-8 | A1 thin-wall + C4 Al-yoke mass optimization (−280 g) | SWaP | analysis only |

## 10. Verification & qualification roadmap

0. **Kinematic assembly demo (DONE, Rev 1.1):** native Assembly + Simulation in CAD of record — three-frame topology closes kinematically (§2.4). Shell/nose transparency set in GUI for exhibition viewing.
1. **Sim:** 3DOF steering check **DONE (Rev 1.2)** — `scripts/sim_guidance_check.py`, `out_sim/RESULTS.md`: guided CEP 6.9 m vs unguided 207 m (250 paired runs); lock-45 s variant 8.5 m. GNC methodology pass **DONE (Rev 1.3)** — `scripts/sim_gnc_check.py`, `out_sim/RESULTS_GNC.md` (Rev D): estimator-in-loop (12-state EKF + drag-ref roll anchoring + phasor-duty actuator + fail-safe modes) under honest q-scaled authority. **Open (next rung): roll-anchor robustness under wind/mount bias**, then 6DOF (spin, Magnus, roll channel), **Monte Carlo ≥1,000 runs** → CEP histogram vs 30 m. *Deliverable: out_sim/ report.*
2. **Bench de-spin rig:** spin cartridge+canard assembly to 250 rev/s equivalent; demonstrate regen harvest, roll-hold at ψ (live angle readout), braking time constant.
3. **Bearing spin-survival:** 15,000 g spike fixture + spin test; post-test drag torque.
4. **Structural:** fin root static 3× UL, modal (flutter margin), shock 15k g half-sine on fixture.
5. **Env:** MIL-STD-331 subset (temp/shock/vibration), rain, humidity.
6. **Gun qualification:** 12–18 instrumented rounds, ATAGS/Dhanush, CEP measurement vs target.
7. **Docs/tests gate to TRL 5–6.**

## 11. Risk register (top)

| ID | Risk | L×C | Mitigation |
|---|---|---|---|
| R1 | Bearing ball damage at setback | M×H | retention lip REQ-1; load-path analysis; spin test |
| R2 | Motor transient torque shortfall at −40 °C | M×M | magnet grade N42SH; supercap pre-heat; pulse budget |
| R3 | GNSS denial/jamming | M×H | NavIC primary + INS coast + prox/time fallback modes |
| R4 | FOC instability across de-spin band | M×H | HIL test; low-KT margin; angle-sensor commutation |
| R5 | Cartridge runaway (no pins) | L×H | REQ-2 pins (trivial fix) |
| R6 | Qualification schedule (3 yr) | M×M | phased TRL plan, partner MoUs early |
| R7 | Li-ion cold soak | M×M | bay thermal design; cell qual; primary+supercap fallback option |

## 12. Competitive position (summary)

vs **M1156 PGK (TRL9, ~25k fielded, ₹9–10 L):** same accuracy class target, sovereign NavIC-first navigation, motor-integrated de-spin/steer/harvest (3 functions, 1 machine), no thermal battery, projected ex-works 8–12% of ceiling — separated honestly by TRL and firing history. vs **Excalibur-class (₹60 L–2 Cr):** classic PGK retrofit value at 5–10× lower cost. vs **Krasnopol-class (laser):** different targeting paradigm (fire-and-forget vs designated).

---

## Appendix A — Master parameter table (as-built)

| Parameter | Value |
|---|---|
| Shell host length / body Ø / ogive | 696 / Ø154.9 / 4.07 cal tangent |
| Well thread | 2-12UN-1A RH, pitch 2.1167, z 606–696 full depth |
| Bearing balls | Ø3, Ø40 circle, 10 rows × 16 |
| Outer ring thread | crest Ø50.7 / root Ø48.2 male |
| Core journal | Ø31.6 g6 in Ø32 H6 |
| Battery bay | Ø25.6 × 54 (cell Ø26.2 × 50) |
| Firing channel | Ø2.4 @ x = +14.3 |
| Collar | Ø40 × 16 (z 696–712) |
| Stator | Ø45–73.4 × 16, 24 teeth, M350-50A |
| Air gap | 0.5 |
| Bell | Ø76.4–83 × 22 + cap Ø83 × 3 |
| Magnet ring | Ø74.7–76.4 × 15, N42SH |
| Pilot bearing | Ø20.8/24.7 × 2.6, 12 balls Ø1.7 |
| Canard shell | cap Ø89; drum steps Ø84–89 / Ø81–85; 7075-T6 |
| Fins | root 24 / tip 18 chord, span 24.5, tip Ø138, 3 mm, bevel 1 mm, blend 3 mm, trim ±3° |
| Radome | Ø84 × 49.6 tangent ogive, wall 2, tip R2 |
| Kinematic sim (Rev 1.1) | Assembly: 24 links · Joints: 21 Fixed + 2 Revolute + Ground · Simulation: 0–4 s, 30 fps, 122 frames, drives 180 °/s rotor / −60 °/s nose |
| Steering sim (Rev 1.2) | 3DOF MC, 250 paired runs: guided CEP 6.9 m vs unguided 207 m (lock 35 s); 8.5 m (lock 45 s); authority duty ≤27 % mean; `out_sim/RESULTS.md` |
| GNC sim (Rev 1.3) | estimator-in-loop 3DOF: 12-state EKF + drag-ref roll anchor + phasor-duty actuator (T=3 s) + fail-safe; q-scaled authority; `out_sim/RESULTS_GNC.md` Rev D |
| Module mass (as-built) | ≈ 1.84 kg (→1.56 kg optimized; Rev 1.2 +70 g power stage) |
| Module station span | z 606–776.1 |

## Appendix B — Glossary
See `attachments/SIH26098_TEAM_BRIEFING.md` §3 (CEP, S&A, FMCW, SWaP-C, TRL, STANAG 2916/4187, 6DOF, Monte Carlo, K_T, FOC).

---
*End of design report. CAD of record: `cleansheet/PGK_CleanSheet.FCStd` (Rev 1.1 — native Assembly, joints and playable kinematic Simulation). Rev 1.2: steering sim + de-spin re-spec (BOM §G). Rev 1.3: GNC methodology pass — §4.5 roll-reference correction, q-scaled authority, §8 decisions 12–15, `out_sim/RESULTS_GNC.md` Rev D. BOM: `02_BOM_MANUFACTURING_ASSEMBLY.md`. Requirements: `00_REQUIREMENTS.md`.*
