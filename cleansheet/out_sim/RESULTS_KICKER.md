# Terminal-kicker verification — solid RCS on the printed canard structure

Runs: 250 paired primary + 80 paired outage (60-70 s) + 100 paired
stressed (Cd systematic +3.5 %) MC; per-run re-seeded streams (base vs kicker
see IDENTICAL dispersions and sensor noise — the delta is purely the kicker).
Truth: 3DOF RK4 dt=0.025, Cd=0.2115, q70=41392 Pa; Rev E GNC (L0) unchanged.

## Kicker model (physics-sized)
| Parameter | Value | Basis |
|---|---|---|
| Thrust (continuous-equiv) | 115 N | one face ~150 N derated ~20% for inter-face slew dead time |
| Isp | 170 s | small printed chamber, conservative band 150-200 s |
| Propellant | 353 g (208 cm3) | AP/HTPB-class @ 1.7 g/cm3 in shell + canard cavities |
| dv budget | 12.79 m/s | Isp*g*ln(m0/(m0-mp)), m0 46 kg |
| Faces | 8 spokes @ 45 deg | one chamber per canard face, face = valve |
| Arm window / trigger | t_go <= 12 s, miss > 25 m, fin duty >= 0.90 | last-resort: fins saturated, nav healthy |
| Settle (slew + ignition) | 0.35 s | <=180 deg @ 6.28 rad/s + ignition delay |
| Pointing quantization | <= 22.5 deg (cos 0.924) | nearest spoke of 8; worst-case held for the whole burn |

## Control methodology (as simulated)
- **Trigger (1 Hz nav tick):** commit iff mode in (guide, degraded), roll reference valid,
  fin duty >= 0.90 (saturation co-condition: fires only when the fins cannot close it),
  t_go <= 12 s and IPP predicted miss > 25 m. One-shot, irreversible (S&A).
- **Allocation (burn-leverage corrected):** solve dv*(t_go - settle - burn/2)*cos(22.5 deg) = miss
  (2-pass fixed point, since a dv at tau before impact shifts impact ~dv*(t_go-tau)), capped at the
  prop budget; directed along the miss vector. Partial correction when the tail exceeds budget.
- **Pointing:** phasor frozen full-duty ON the required azimuth at commit (frame slews there during
  the settle window); thrust = nearest of 8 spokes; worst-case 22.5 deg error held for the whole burn.
- **Burn:** bang-bang full throttle at truth rate; stops at the committed dv plan (asymptote-checked)
  or prop exhaustion; fin phasor refresh resumes at burnout.
- **Filter consistency:** commanded thrust is fed to the EKF predict model AND the drag-anchor model
  (D7 discipline — no unmodeled force).
- **Fail-safe:** never fires without a roll reference (BLIND), nor in denied/acq/ballistic modes;
  never-lock -> ballistic preserved.

## Deterministic (paired seeds)
| Case | Rev E baseline | Rev E + kicker | fired | dv used | burn |
|---|---|---|---|---|---|
| nominal | 12.5 | 12.5 | False | 0.00 m/s | 0.00 s |
| mount bias 5deg | 24.6 | 24.6 | False | 0.00 m/s | 0.00 s |
| crosswind 6 | 60.2 | 60.2 | False | 0.00 m/s | 0.00 s |
| headwind 6 | 9.7 | 9.7 | False | 0.00 m/s | 0.00 s |
| Cd +5% (stress) | 104.6 | 11.2 | True | 12.74 m/s | 5.08 s |
| outage 60-70s | 28.0 | 28.0 | False | 0.00 m/s | 0.00 s |
| BLIND (no roll ref) | 97.6 | 97.6 | False | 0.00 m/s | 0.00 s |

## Monte Carlo
| Config | CEP50 | mean | p90 | max | fired | dv med | dv max |
|---|---|---|---|---|---|---|---|
| primary.base | 19.9 | 21.8 | 35.6 | 86.9 | 0 | nan | nan |
| primary.kick | 19.9 | 21.8 | 35.6 | 86.9 | 0 | nan | nan |
| outage.base | 17.3 | 19.2 | 31.3 | 79.0 | 0 | nan | nan |
| outage.kick | 17.3 | 19.2 | 31.3 | 79.0 | 0 | nan | nan |
| stressed.base | 16.0 | 52.7 | 148.9 | 527.6 | 0 | nan | nan |
| stressed.kick | 14.8 | 30.0 | 46.4 | 422.3 | 34 | 12.74 | 12.85 |

- **primary:** requirement breaches (>30 m) 42/250 -> 42/250 with kicker (0% of breaches erased).
  kicker never fired — silent-run paired delta max 0.000 m (integration noise only).
- **outage 60-70s:** requirement breaches (>30 m) 12/80 -> 12/80 with kicker (0% of breaches erased).
  kicker never fired — silent-run paired delta max 0.000 m (integration noise only).
- **stressed Cd+3.5%:** requirement breaches (>30 m) 28/100 -> 15/100 with kicker (46% of breaches erased).
  fired 34/100 (dv med 12.74 of 12.79 m/s budget); paired miss delta: med -98.0 m, worst +39.5, best -110.1.
- Fail-safe verified: the BLIND (no roll reference) case never fires; never-lock -> ballistic is preserved (kicker gated to guide/degraded modes).
- Authority-limited stress case (Cd+5%): 104.6 -> 11.2 m (fired=True, dv 12.74 m/s, burn 5.08 s) — the tail case the kicker exists for.
