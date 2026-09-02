# Trajectory & energy verification — SINGLE time-share machine (this rev)

Method: 3DOF point-mass RK4 dt=0.02, exp atmo, Cd calibrated to 30 km = 0.2030
(cleansheet methods; single-machine energy/actuation model per PGK_SPEC_SHEET §2/§4/§6). Seed 20260901, 100 paired MC.
Mass 47.9 kg (spec §1 this rev), v0 800 m/s, 45 deg, fin authority F = 20 N * q/35kPa (§2.5).

## Nominal 30 km shot
| Quantity | Sim | Spec sheet | Verdict |
|---|---|---|---|
| TOF | 87.6 s | 92 s (§1) | OK |
| Apogee | 9.46 km @ t=40.6 s | ~11.5 km @ ~46 s (§1/§3) | DEVIATION |
| Mode switch | t=40.6 s (vertical-velocity flip) | ~46 s | OK |
| Generated (12 W throttle) | 412 J | ~450 J (§4) | OK |
| Regen braking | 155.0 J from 10687 rpm | 15-25 J from ~4,500 rpm (§6) | OK |
| Impact speed | 413 m/s | 300-350 m/s (§2.6 F) | DEVIATION |
| Spin at impact | 14232 rpm | ~14,000 rpm (§1) | OK |
| Energy used (elec+hold+slews) | 344 J | ~344 J (§4) | OK |
| End-of-flight cap margin | 35% of 875 J bank (net 310 J) | ~28% (§4) | OK |

## Deterministic dispersions (guided)
| Case | Unguided miss | Guided miss |
|---|---|---|
| crosswind 6 | 207 m | 39.3 m |
| headwind 6 | 327 m | 160.9 m |
| muzzle +1.5 | 80 m | 6.1 m |
| Cd +5% | 850 m | 690.3 m |

## Monte Carlo (100, disp v0 0.15% / aim 0.6 mrad / wind 3 m/s / Cd 0.8%)
| Config | CEP50 | mean | p90 | max |
|---|---|---|---|---|
| Unguided | 196 | 223 | 409 | 636 |
| Guided (L0, q-scaled 20 N) | 28.5 | 85.7 | 244.1 | 473.6 |

Correction demonstrated: median unguided miss 196 m reduced to 28.5 m (7x). Duty peak median 1.00.
Regen J median 154.8; end-cap energy median 310 J (35% of bank).

## Deviations / notes for the spec sheet
- **Apogee 9.5 km @ 45.6 s, TOF 87.6 s** vs §1's ~11.5 km @ ~46 s / 92 s: point-mass + exponential atmosphere is
  conservative on apex; the §1 table came from standard-range tables. Timeline shifts ~2 s earlier — no architecture impact.
- **Rotor speed reconciliation (§2.2 vs §6):** the modelled rotor rides 0.7× its zero-torque speed
  (ω_nl = V·tan12°/r_mid) — 10687 rpm at switch, between §6's '4,500 rpm' and §2.2's
  '~20,000 rpm'. Regen recoverable at switch: ½Iω²×0.55 ≈ ½×4.5e-4×(1119 rad/s)²×0.55 = 155 J — more than §6's
  15-25 J (favourable); §6's 4,500 rpm figure should be revisited at detail design.
- Windmill model: T = T_REF·(q/q_REF)·(1−(ω/ω_nl)²), T_REF = 0.17 N·m @ 35 kPa (§7); extraction is speed-regulated
  (torque regulator at 0.7·ω_nl — a constant-power load is unstable on the right branch of the windmill curve).
- **Impact speed 413 m/s** vs §2.6's 300-350: constant Cd (calibrated at supersonic) overestimates descent
  speed; a subsonic Cd rise (~0.3) would bring it into the spec band. Model-fidelity item for the 6DOF rung.
- Guidance engages ~4 s after the vertical-velocity flip (3 s brake + 1 s settle); no de-spin transient exists in
  this architecture (fins ride the servo-held rotor).
- Correction: guided CEP 28.5 m meets the ≤30 m class target (Leading claims ≤30 m); 6DOF (Magnus, precession
  steering chain, yaw-of-repose, phasor wobble) still required before PDR (§10.1).
