# SIH26098 Clean-Sheet Design Track — R1 Requirements (derived from PS)

> **Purpose:** Independent re-derivation of the design problem, before any architecture is chosen.
> Every requirement is tagged: `[PS]` = from the official problem statement (`SIH2026_Hardware_PS.md:647`),
> `[D]` = derived by us from physics/public sources, `[A]` = assumption to verify.
> Rule: no requirement may smuggle in a solution. Steering mechanisms, bearing choices, etc. are Phase 2.

## M — Mission

| ID | Requirement | Source |
|----|-------------|--------|
| M1 | Retrofit module replaces the standard fuze in the standard 155mm fuze well; shell otherwise stays stock | [PS] "compatibility with the existing 155 mm shell design" |
| M2 | Terminal accuracy CEP ≤ 30 m (target better) at long range vs ~267 m unguided baseline | [PS] |
| M3 | Multi-mode electronic fuze: Proximity / Time / Impact | [PS] |
| M4 | Configuration interface before firing (fuze settings, coordinates, mode) | [PS] |
| M5 | Works across 155mm gun family (39–52 cal: M777, Dhanush, K9, ATAGS) | [A→verify with PS org; consistent with YIL context] |
| M6 | Modular/upgradable architecture (future seeker, nav updates) | [PS] |
| M7 | Cost-effective at scale; team cost target ₹8–11 L/kit | [PS "low cost"] + [A: team target] |

## L — Launch environment (drives everything downstream)

| ID | Requirement | Source |
|----|-------------|--------|
| L1 | Survive setback acceleration: design for 15,000 g peak | [D: public PGK-class qualification level; simple kinematics (827 m/s over ~8 m barrel travel) gives ~4.4 k g average — peak/average ratio in gun launch is high. Verify vs MIL-STD-331] |
| L2 | Survive spin-up to ~250–270 rev/s (1-in-20-cal rifling at 827 m/s muzzle → ~267 rev/s; decay in flight) | [D from rifling + muzzle velocity] |
| L3 | Muzzle velocity band: ~684–827 m/s (charge-dependent) | [D: public charge tables] |
| L4 | Flight duration ~60–90 s at 30 km; apogee ~10–12 km | [D: ballistic estimate] |
| L5 | Environmental: −40…+60 °C storage/ops, rain, humidity, EMI | [A: MIL-STD-810/331 class; verify] |
| L6 | All electronics/mechanisms must function immediately after launch environment (no performance degradation from the gun ride) | [PS] |

## P — Physical envelope

| ID | Requirement | Source |
|----|-------------|--------|
| P1 | Interface: STANAG 2916-class fuze well thread (2-12UN-1A), screw-in | [D: standard; verify exact class] |
| P2 | Body must fit 155 mm bore: any pre-launch external span ≤ bore (deployables may extend only after muzzle exit) | [D: physical] |
| P3 | Module mass: fuze-class, target ≤ 1.5 kg, hard limit 2.0 kg (excess nose mass shifts CG and trajectory) | [A: fuze-class mass; sizing in Phase 3] |
| P4 | Length above ogive: minimize; fit existing fuze-length logistics handling | [A: verify max permissible nose length] |

## F — Function

| ID | Requirement | Source |
|----|-------------|--------|
| F1 | In-flight trajectory correction after a ballistic launch — no mid-course updates required (fire-and-forget; target coords loaded pre-fire) | [PS implied] |
| F2 | Navigation: absolute position/velocity in flight; NavIC primary (sovereign), GPS/GLONASS fallback; inertial aiding for outages | [A: team sovereignty stance; PS lists GNSS/IMU/baro candidates] |
| F3 | Fuze modes: proximity (HOB ~6–18 m), time (3–199.9 s), impact (PD) | [PS + public fuze practice] |
| F4 | Pre-fire setting: mode, HOB, time, target grid, GPS crypto keys — via setter at the gun (inductive or wireless) | [PS] |
| F5 | Safe & arm: fuze must be SAFE through storage/transport/loading; arming only after confirmed launch signatures (setback + spin + bore-exit distance) | [D: STANAG 4187 practice; public] |
| F6 | Fail-safe: loss of nav or gross deviation must not increase collateral risk (GPS-loss behavior must be defined) | [D: public PGK practice] |
| F7 | Real-time onboard control loop, autonomous, no operator in flight | [PS] |

## S — Sizing & energy (to be derived in Phase 3 from chosen architecture)

| ID | Requirement | Source |
|----|-------------|--------|
| S1 | Power: total electrical energy for full flight + reserves; activation on launch (no battery shelf drain) | [D from F7/L4] |
| S2 | Actuation: authority to correct dispersion + muzzle velocity error + met error at 30 km; response bandwidth adequate for spin environment | [D: F1/L2] |
| S3 | Structure: housings/bearings/actuators sized for L1/L2 with margin | [D from L1/L2] |

## Verification intent (Phase 5)

- 6DOF trajectory sim (3DOF → 6DOF), Monte Carlo (≥1000 runs: wind, muzzle velocity, nav noise, actuator lag) → CEP histogram vs 30 m
- Structural screening of the concept against L1/L2 (analysis-level for hackathon)
- Bench demo: inert, low-speed (per existing team boundary — no energetics, no launch hardware)

---

**Open items to verify with PS org / public standards:** exact setback & spin qualification levels (MIL-STD-331), max nose length/mass for STANAG 2916 wells, required gun list confirmation, cost definition (per kit at what production volume).
