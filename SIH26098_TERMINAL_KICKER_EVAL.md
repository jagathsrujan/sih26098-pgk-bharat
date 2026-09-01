# SIH26098 — Terminal-Kicker Physics Evaluation
## Solid-propellant RCS integrated into the printed canard structure

> **Date:** 2026-09-01 | **Refines:** `legacy/SIH26098_COLDGAS_PGK.md` + `legacy/SIH26098_COLDGAS_PHYSICS_EVAL.md`
> **Verdict:** ✅ **GNC value proven by simulation; hardware feasibility plausible with one gating risk (propellant volume).**
> The concept works as a *last-resort terminal impulse*, not a replacement for the
> guidance canards — exactly the role proposed. Evidence: `cleansheet/out_sim/RESULTS_KICKER.md`.

---

## 1. The concept (formalized)

Metal-LPBF print the **canard shell + canards as one integral structure** with the
maximum cavity fraction the structure allows. Fill the cavities with solid grain.
Put nozzle rows on the two faces of each canard. In the last seconds of flight,
**when the guidance canards are saturated and the predicted miss still exceeds the
requirement**, open (ignite) the face whose thrust vector points the way the shell
needs to go and burn to a planned impulse.

Three design commitments (all kept in the evaluation):

1. **Terminal-only** — the continuous guidance loop stays exactly as built (Rev E
   ring-motor/canard phasor). The kicker is a one-shot reserve, not a steering
   actuator.
2. **Expendable** — the kit is destroyed at impact anyway; only
   *function-before-impact* matters. Chamber walls, throats and electronics may be
   degraded by the burn as long as the correction completes first.
3. **Structure = tank** — the grain acts as a compression core for the printed
   thin walls (same logic as foam-filled/case-bonded structures).

**Key architectural insight discovered in evaluation:** mounting the thruster bank
on the **de-spun canard frame** (which the ring motor already controls) removes the
whole roll-phase-locking problem of the original cold-gas concept. The frame *is*
the pointer; no metering disk is needed at all — **chamber selection IS the valve**
(one igniter per face). The only moving parts are the ones already on the kit.

---

## 2. The scenario it addresses (from the project's own sim)

`cleansheet/scripts/sim_gnc_check.py` (Rev E, verified, seed 20260901):

| Quantity | Value | Meaning |
|---|---|---|
| Nominal CEP50 | 21.5 m | requirement 30 m — median is fine |
| Cd +5% stress case | **104.5 m** | fin force saturated (duty ≥ 0.9 from lock) |
| Guidance window | ~45 s (lock → impact) | continuous loop has authority limits |
| Fin authority | 60 N · q(t)/q(70 s) ≈ 1.3–1.5 m/s² | 0.13 g on the 46 kg shell |

The kicker exists **for the tail, not the median**: runs where the continuous
loop saturates and the impact-point prediction still breaches ~25–30 m inside the
terminal window. In the nominal case it never fires (dead mass, priced below).

---

## 3. Physics sizing

### 3.1 Impulse budget (the number that killed cold gas — now revisited)

Terminal correction is an impulse problem: a lateral Δv applied τ before impact
shifts the impact point by ≈ Δv·(t_go − τ).

- Required closure: the sim's stress tail (104.5 m) at t_go = 12 s needs
  **~9–12 m/s** of lateral Δv (leverage-corrected, see §4).
- Solid grain (AP/HTPB-class, ρ = 1.7 g/cm³) at the **conservative Isp = 170 s**
  (small printed chambers lose heat; literature band for this scale is 120–200 s):

| Isp (s) | Propellant for 12.8 m/s | Volume @ 1.7 g/cm³ |
|---|---|---|
| 130 | 461 g | 271 cm³ |
| 150 | 400 g | 235 cm³ |
| **170 (design)** | **353 g** | **208 cm³** |
| 200 | 300 g | 176 cm³ |

- Δv budget (design point): Δv = Isp·g·ln(m₀/(m₀−m_p)) = 170·9.81·ln(46/45.65)
  = **12.84 m/s** → leverage-corrected closure ≈ **108 m at t_go = 12 s** — matches
  the deterministic sim (104.6 → 11.2 m).

**Compare with the rejected cold-gas concept:** cold gas needed 1.18 kg of N₂
(3.3 L @ 300 bar — 22× the bore) for the same job. Solid grain needs 0.35 kg in
0.21 L. That is the entire reason this variant lives and cold gas dies.

### 3.2 Chamber / nozzle sizing (per face, one face burning at a time)

| Quantity | Value | Basis |
|---|---|---|
| Thrust, one face | ~150 N | sized to burn the budget inside the arm window |
| Mass flow | 69 g/s (115 N continuous-equivalent) | derated ~20 % for inter-face slew dead time |
| Chamber pressure | 5 MPa | conventional SRM |
| Total throat/face | 20.7 mm² → 3 × Ø2.96 mm | ṁ·C*/p_c, C* = 1500 m/s — LPBF-printable |
| Grain per face | 44 g / 26 cm³ | 353 g over 8 faces |
| Effective L* | grows 0 → ~1.3 m as the port opens | needs an internal free port (~40 % of cavity) — see §3.4 |
| Burn time (full budget) | 5.1 s | fits the 12 s arm window with margin |

### 3.3 Structural checks

| Load | Value | Margin |
|---|---|---|
| Setback 15,000 g: case-bond shear (60 mm grain) | **15.0 MPa** | marginal — needs bond-strength design (classic case-bonded SRM problem; solvable with stress-relief boots/geometry, flagged) |
| Chamber hoop (5 MPa, Ø10 mm, 1.5 mm wall) | 16.7 MPa | ~60× vs 17-4PH H900 (~1100 MPa yield) — trivial |
| Grain as compression core | viscoelastic, E ≈ 10–100 MPa | supports local wall buckling + damps vibration (foam-core logic), NOT global bending |
| Gas-pressure stiffening | — | real (Atlas balloon tanks) but needs heavy walls; not the chosen path |

### 3.4 The gating risk: propellant volume (be honest here)

The grain needs free volume to burn into (internal port ≈ 40 % of cavity), so the
**cavity** requirement is ~1.6–1.8× the grain volume:

| Closure claim | Grain | Cavity needed | Fits? |
|---|---|---|---|
| ≤ 60 m tails (Δv ≈ 6 m/s) | 130 g / 76 cm³ | ~130 cm³ | ✅ likely — canard-shell annulus + canard internals alone |
| Full 12.8 m/s (≤ 108 m tails) | 353 g / 208 cm³ | ~330–370 cm³ | ⚠️ marginal — needs the annulus measured, high-density/high-Isp grain (Isp 200 → 176 cm³ grain), and possibly sharing battery-bay voids |

**Next-rung action:** measure the actual cavity volume of `Canard_Shell_Machined` +
fins + bore surplus in `PGK_CleanSheet.FCStd`, then set the flight claim to the
largest rung that fits. The GNC machinery is identical either way (one constant).

### 3.5 Other real-life factors

- **Jet interaction bonus:** at supersonic speed a side jet injects into the
  crossflow — documented amplification (jet-flap / side-jet interaction, BMD
  kill-vehicle literature) means the delivered lateral force exceeds the vacuum
  thrust. We conservatively did NOT count this in the sim.
- **Roll torque:** symmetric nozzle pairs about the spin axis → net roll torque ≈ 0;
  the ring motor holds the frame regardless (it already fights far larger slews).
- **Thermal:** 5 s burn soaks the printed walls; expendable philosophy covers it.
- **Failure symmetry:** chambers are designed to vent axially on crack (a lateral
  canard failure inside the terminal window is the one bad failure mode).
- **Energetics boundary:** this is a paper + simulation concept for SIH. The bench
  demonstrator remains the inert compressed-air rig through the same printed
  nozzle geometry. Ignition/S&A hardware stays with the partner (ESAF boundary).

---

## 4. Control methodology (as implemented and simulated)

Injected into `sim_gnc_revE` as a guarded variant (`kicker=True`; default path
bit-identical — 33/33 FSW tests still pass):

1. **Trigger (1 Hz nav tick, one-shot, irreversible):** commit iff
   - mode ∈ {guide, degraded} (healthy nav; never in denied/acq/ballistic),
   - roll reference valid (never fires BLIND — verified in sim),
   - **fin duty ≥ 0.9** (the saturation co-condition — fires only when the
     continuous loop *cannot* close it; kills false-positive fires on transient
     nav noise, e.g. the headwind det case correctly stays silent),
   - t_go ≤ 12 s and IPP predicted miss > 25 m.

2. **Allocation (burn-leverage corrected):** a Δv applied τ before impact moves
   the impact ~Δv·(t_go−τ), so the plan solves
   `dv·(t_go − settle − burn/2)·cos(22.5°) = miss` (2-pass fixed point), capped at
   the 12.84 m/s prop budget. Partial correction when the tail exceeds budget —
   still monotone gain.

3. **Pointing:** the fin phasor freezes **full-duty on the required azimuth at
   commit**; the frame slews there during a 0.35 s settle (≤180° @ 6.28 rad/s +
   ignition delay); thrust rides the nearest of the 8 face spokes. Worst-case
   22.5° quantization error is held for the whole burn (conservative envelope —
   real face sequencing would halve it).

4. **Burn:** bang-bang full throttle integrated at truth rate (rocket-equation
   mass depletion included); stops exactly at the committed Δv plan or prop
   exhaustion. Fin phasor refresh resumes at burnout — the continuous loop
   finishes the job.

5. **Filter consistency:** the commanded thrust is fed into the EKF predict model
   AND the drag-anchor reference model (D7 discipline — no unmodeled force hits
   the filter mid-burn).

---

## 5. Mechanism (hardware bill of the delta vs the current kit)

| Element | Choice | Note |
|---|---|---|
| Storage | grain case-bonded in printed cavities | replaces the metering-disk manifold entirely |
| Valve | **none** — one electric igniter (hot-bridge) per face | chamber selection = ignition; 8 ESD-protected channels |
| Pointing | the existing ring motor + de-spun frame | zero new moving parts |
| Nozzles | 3 × Ø3 mm throats per face, LPBF-printed in situ | the original printed-nozzle idea survives verbatim |
| Arming | same S&A ladder as the concept: apogee + nav-healthy + trigger | hardware with partner |
| Demo | compressed air through the printed nozzle rig | inert boundary unchanged |

Mass cost: **+353 g** (grain) carried always — ~19 % of the 1.88 kg kit budget.
That is the honest price of insurance; the fallback rung (6 m/s) costs 130 g.

---

## 6. Simulation evidence

All numbers generated by `python3 cleansheet/scripts/sim_gnc_check.py kicker`
(paired per-run re-seeded streams: baseline and kicker see *identical* dispersions
and sensor noise — every delta below is purely the kicker). Full tables:
`cleansheet/out_sim/RESULTS_KICKER.md`, plot `steering_kicker.png`, log
`kicker_full_run.log`.

**Deterministic (paired seeds):**

| Case | Baseline | + kicker | fired |
|---|---|---|---|
| nominal | 12.5 | 12.5 | no |
| mount bias 5° | 24.6 | 24.6 | no |
| crosswind 6 | 60.2 | 60.2 | no |
| headwind 6 | 9.7 | 9.7 | no |
| **Cd +5% (stress)** | **104.6** | **11.2** | **yes — full 12.74 m/s burn, 5.08 s** |
| outage 60–70 s | 28.0 | 28.0 | no |
| BLIND (no roll ref) | 97.6 | 97.6 | **never fires (fail-safe verified)** |

**Monte Carlo (three paired populations):**

| Population | Metric | Baseline | + kicker |
|---|---|---|---|
| primary (250) | CEP50 / p90 / max, breaches | 19.9 / 35.6 / 86.9 — 42/250 | **identical — kicker never fires (fins close everything; correct dormancy)** |
| outage 60–70 s (80) | breaches | 12/80 | identical — never fires, silent delta 0.000 m |
| **stressed Cd +3.5% (100)** | CEP50 | 16.0 | 14.8 |
| | mean | 52.7 | **30.0** |
| | p90 | 148.9 | **46.4 (3.2× better tail)** |
| | breaches >30 m | 28/100 | **15/100 (46% erased)** |
| | paired Δ on fired runs (34/100) | — | **median −98.0 m**, best −110.1, worst +39.5 |

Reading: in nominal dispersions the continuous loop never saturates, so the
kicker correctly stays silent and changes nothing (paired delta exactly 0). Under
a systematic drag shift — the off-nominal scenario the concept targets — the fin
loop saturates, the kicker commits in a third of the runs, the median miss on
those runs drops by ~98 m, and nearly half the requirement breaches are erased.
One fired run got *worse* by +39.5 m (fired on a bad nav estimate) — the honest
false-positive cost, visible because the population is paired.

---

## 7. Verdict and open items

**Does it work in real life?** The physics closes where cold gas did not: solid
grain delivers the terminal impulse within a plausibly printable structure, the
de-spun-frame architecture removes the phase-locking complexity, and the GNC
simulation shows the tail compression the concept promises. The one item that
decides the flight claim is **cavity volume vs grain + port** (§3.4) — measure it
in CAD before committing the submission numbers.

Open items:
- [ ] CAD cavity measurement (shell annulus + canards + bore surplus) → set the closure claim (6 vs 12.8 m/s)
- [ ] Case-bond shear design for 15,000 g setback (stress boot / grain geometry)
- [ ] Igniter channel count vs face-count trade (8 faces × 1 igniter)
- [ ] Jet-interaction CFD rung (bonus authority, currently uncounted)
- [ ] Sensitivity: Isp 130–200 sweep re-run of the MC (one-constant change)
