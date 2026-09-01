# PGK 155mm — MAIN SPECIFICATION SHEET
### Single time-share motor (alternator ⇄ actuator) · canonical design
**Doc status: living document — design of record for the whole workspace** (supersedes the
`cleansheet/` Rev 1.7 lineage, which remains as methods reference only). Every future design
item in this workspace MUST add/update its section here (standing process, §11).
Last synced with CAD: this rev — S-series build + bias ring (S04), nose RF section (S07),
control ring (S08), fuze-well stack (S10); fwd bearing z166; assembly gate 0 clashes
(4 rotor phases), bore clear, Ø108.0 × z0–220, PGK ~1.21–1.23 kg.

---

## 1. Mission & ballistic assumptions (155mm, M795-class)

| Parameter | Value | Basis |
|---|---|---|
| Projectile all-up mass | ~47.9 kg (shell 46.7 + PGK ~1.18 kg modeled: motor+shell 723 + nose 99 + fuze stack 269 + control ring 17 + caps 67) | M795 + this kit |
| Muzzle velocity | 800 m/s (charge-dependent 650–900) | nominal charge |
| Rifling twist | 1 turn / 20 cal → spin at muzzle **15,480 rpm** | 155mm standard |
| Spin at target | ~14,000 rpm (~10% decay) | standard decay models |
| Flight regime | spin-stabilized, correction in terminal (descent) phase only | PGK doctrine |

**Time-of-flight / apogee table (45° quadrant elevation):**

| Range | v₀ (m/s) | TOF | Apogee (mode-switch window) |
|---|---|---|---|
| 20 km | ~650 | 63 s | ~31 s |
| **30 km (nominal)** | **800** | **92 s** | **~46 s** |
| 40 km | ~900 (BB/RAP) | 118 s | ~60 s |

Dynamic pressure during correction (descent, 2–8 km alt): **q ≈ 15–50 kPa** (nominal 35 kPa).

---

## 2. Motor module — alternator/actuator (the single machine)

**Topology:** outer-rotor PMSM, 12 slots / 10 poles (5 pp), 3-phase, one 25 mm active zone.
**Dual role:** rotor free-spins (windmill-driven) in ascent = generator; rotor servo-held in
descent = actuator positioning the fin ring ("hover"). Same stator, same inverter bridges,
mode-switched at apogee.

### 2.1 Dimensions (from CAD, mm)

| Element | Ø inner | Ø outer | Axial (z) | Notes |
|---|---|---|---|---|
| Central through-bore | — | 30 | 0→173 | explosive train — reserved |
| Shaft tube (static) | 30 | 40 | 125→175 | 7075, 2 wire slots (full length); fwd extension seats bearing-B inner race + carries the radome flange |
| Stator core S01 (laminated M250-35A) | 40 | 58.5 | 138→163 | 12 teeth, root Ø40→52 |
| Stator coils S02 (Cu, potted) | 43 | 53.6 | 139.5→161.5 | 12 × ~150 turns, 0.35 mm litz-equiv |
| Stator PCB M04 | 52 | 58.5 | 138→139.5 | 3-phase gate driver + MCU front-end |
| Air gap | 58.5 | 60 | — | 0.75 mm |
| Magnet arcs (NdFeB N42SH) ×10 | 60 | 63 | 138→163 | 24° pole pitch, sleeve-retained |
| Rotor back-iron S04 | 63 | 70 | 138→163 | steel, retention lip z162 |
| Bias-magnet ring (S04) | 41 | 51.6 | 163→166 | 2-pole diametral N42SH, angle-sense; bonded to bearing-B race face |
| **Canard shell S11 (SLS AlSi10Mg)** | 70.4 | 76 | 136→172.5 | **carries the 4 fins + 8 LIT thruster stations; sleeves the back-iron (8× M4), seats bearing-B race (Ø52.4 bore, lip z166); replaces spars, carrier disc and fwd endbell** |
| Fin spars / carrier disc | — | — | — | **DELETED this rev** — functions absorbed by S11 |
| Fins ×4 (S05/S06) | 76 | **108** | ~138→163 | root chord 25, tip 15, t 2.5, cant ±12°; bolted to S11 (8× M5) |
| Bearings M09 ×2 | 40 | 52 | 130–138 / 166–174 | angular-contact, gun grease; inner race fully seated on the tube (fixed §10.12) |
| Endbell M10 (aft only) | 52 | 70 | 125–130 | fwd endbell **deleted** — S11 closes the motor forward |
| **Module envelope** | — | **Ø108.0 max** | **0→220** | continuous contour: fins → Ø76 drum → nose ogive (Ø76 @ z172.5 → tip) |

**Mass rollup (CAD volumes, assembled):**

| Part | cm³ | g |
|---|---|---|
| Shaft tube M01 (incl. fwd ext) | 28.3 | 78.8 |
| Stator core (lam.) | 22.8 | 174.2 |
| Coils (potted Cu) | 8.3 | 69.4 |
| PCB M04 | 0.9 | 1.7 |
| Rotor (ring+magnets+bias ring) | 25.5 | 199.1 |
| **Canard shell S11 (incl. LIT cavities)** | 31.0 | 82.9 |
| Fins ×4 (7075) | 3.2 | 9.0 |
| Bearings ×2 | 10.3 | 80.9 |
| Endbell (aft only) | 8.2 | 22.9 |
| **Motor module subtotal** | | **723** |
| Supercap stack S09 | 37.5 | 67.4 |
| **Total power/train section** | | **790** |
| Nose RF section S07 (radome+antenna+coupler) | 41.1 | ~99 |
| Control ring S08 (PCB+shield can) | 7.9 | 17 |
| Fuze-well stack S10 | 58.4 | ~269 |
| **PGK modeled total** | | **~1.18 kg** (wire/energetics/fasteners pending) |

### 2.2 Electrical spec

| Parameter | Value |
|---|---|
| Torque constant Kt | ~0.095 N·m/A (25 mm active length) |
| Phase resistance | ~0.15 Ω |
| Line EMF at 20,000 rpm rel. | ~150–200 V (buck-charged to cap bus) |
| Continuous torque (thermal) | 0.5 N·m |
| Peak torque (100 ms) | 1.5 N·m |
| **Generator output, ascent** | **10–15 W regulated (up to 20 W early flight, throttled)** |
| Actuator hold current | ~2.1 A → ~2 W copper loss |
| Peak slew current | ~16 A (100 ms bursts) |

### 2.3 Power architecture (one power stage, two software roles)

The rectifier and the motor inverter are the **same three half-bridges** — the "mode change"
at apogee is a software role switch, not a hardware change. All three control loops (FOC
current control, charge regulation, mode state machine) run on the single MCU.

```
GENERATOR MODE (ascent):                    ACTUATOR MODE (descent):
windmill rotor spins (0→46 s)               rotor servo-held / slewed (46→92 s)
   ↓ 3-phase AC, 150–200 V @ 20k rpm           ↑ FOC phase currents, ≤16 A
   ↓                                           ↑
same inverter bridges ──► ACTIVE RECTIFIER  same inverter bridges ◄── 54 V bus
   ↓ buck charger (85% eff.)                   ↓
SUPERCAP STACK 0.6 F @ 54 V (875 J) ══════► SUPERCAP STACK (sole source after apogee)
   ↓ wide-Vin bucks + holdup caps
3.3 / 5 V rails ──► GPS · IMU · MCU · FRAM · fuze electronics
```

CPU control authority (single MCU, three nested jobs):
1. **FOC current/torque loops** (~20 kHz): commanded hold/slew torque → phase currents
   (T = Kt·I); rotor roll position measured per cycle. Current hard-limited to 16 A in
   firmware — the 1.5 N·m torque spec cannot be exceeded even by software fault.
2. **Charge regulation**: rectifier load throttled to hold the cap inside its 54→20 V window.
3. **Mode state machine**: Phase 0 session, generator/actuator switch at apogee, regen
   braking, self-destruct supervision.

Sequencing note: during ascent the electronics run **live off the rectified generator**
(cap charging in parallel); the cap becomes the sole source at the apogee mode switch.
Actuator bursts begin only after GPS solution is stored — the noisy phase never overlaps
receiver acquisition (see §8).

### 2.4 Rotor position & roll-angle measurement (two-sensor scheme)

Inertial canard attitude = body roll + rotor angle relative to body. Two sensor groups:

| Sensor | Measures | Tech | Spec |
|---|---|---|---|
| Motor position array (stator, under rotor magnets) | rotor angle rel. body — FOC commutation + hold phase | analog sin/cos Hall or MR array + bias-magnet ring on rotor | continuous absolute angle, ≤0.1° interpolation; potted bare-die (g-hard); 3× digital Halls as redundancy fallback (60° segments) |
| Roll-angle module (body-fixed) | body roll rate/angle — inertial reference | magnetoresistive magnetometer, Earth-field | ≥1 kHz sampling (body spin 258 rev/s), ~0.5–1° accuracy; bias calibrated during Phase 0 pre-fire session |
| Fused output | inertial canard attitude @ control rate | filter (roll ± magnetometer in EKF) | hover angle error → correction direction error ≈ 1.7%/deg; target ≤0.5° |

Notes:
- Sensorless BEMF commutation is **not** viable — it fails exactly where we live (rotor
  stationary during hover hold). Physical sensors mandatory.
- Angle-array electronics add ~5–8 g; the sin/cos array rides on a small annular board on the
  static shaft tube (M01) at z163–166, reading the bias ring from inside at a 0.5 mm radial
  gap — not on M04 (the ring sits 24 mm fwd of M04; an M04-mounted array cannot see it).
- Rotor bias ring (S04 CAD, done): Ø41/Ø51.6 × 3 mm at z163–166, 2-pole diametral N42SH,
  bonded to the fwd bearing outer-race face; fwd bearing moved z165→166 to open the window.
  Ring adds 17.3 g to the rotor.
- Magnetometer disturbance modes (gun iron, debris) mitigated by Phase 0 stationary bias
  calibration; anomalous-field detection flags degraded-mode hover (body-relative pulses).

### 2.5 Canard assembly — physics, aerodynamics & actuation

**Fin set:** 4 fins, root chord 25 / tip 15 mm, span 16 mm (Ø76→108), t 2.5 mm, area 3.2 cm²
each, cant ±12° (S05 +12 @0/90/270, S06 −12 @180). Mirror-pitched opposite fins, 90° apart.
**Mounting (this rev):** fins bolt to the **S11 canard shell** (8× M5 through the Ø76 drum into
the fin roots); the shell sleeves the rotor back-iron (8× M4) — fin loads close
fin → shell → back-iron → rotor, same closure as the old integral spars but through a
replaceable printed interface. Lateral impulse thrusters (LIT) are embedded in the same shell
(§2.7).

**Flow environment (what the fin actually feels):** relative wind is axial (flight velocity V)
**plus** a tangential component from body spin, v_t = ω_b·r ≈ 1,676×0.045 ≈ **75 m/s** at fin
mid-span. That makes the local flow angle ~**atan(75/300) ≈ 14°** — the same order as the fin
twist. Every fin's effective angle of attack is therefore **angle-of-azimuth dependent** and
oscillates once per fin per revolution; the servo and the windmill both live with this.

**Force generation (two orthogonal mechanisms):**
1. **Span-twist → tangential force → roll torque.** A fin twisted θ about its span axis sees
   AoA θ; supersonic lift Cl_α ≈ 4/√(M²−1) ≈ **1.75/rad** at M 2.5 (matches our 1.8 assumption).
   Lift normal to the fin plane resolves into a tangential component → torque about the shell
   axis. The **mirror pairs (+,− and −,+)** make all four torques add — this is the windmill:
   free-spinning rotor extracts power; net lateral force zero (opposite fins' forces cancel).
2. **Roll-phase ("hover") → net lateral force.** With the rotor servo-held at an inertial roll
   angle, the mirror-pair forces add *laterally* (both fins of a pair push the same direction —
   that is the point of mirror mounting) while their torques cancel. The held ring then
   produces a steady lateral force in whatever direction the servo points it.

**Magnitudes (nominal descent, q = 35 kPa, M ≈ 1.0–1.3):**

| Quantity | Value | Derivation |
|---|---|---|
| Normal force per fin (12°) | 4–6 N | q·S·Cl = 35e3·3.2e-4·0.38 |
| **Net lateral correction force** | **15–25 N** | mirror pairs sum |
| Lateral acceleration | 0.3–0.5 m/s² | F/47.5 kg |
| Correction authority (35 s descent) | **~200–300 m** | ½·a·t² — matches M1156 class |
| Axial drag of fin set | ~8 N | ~1–2% range penalty |
| Windmill torque, held rotor | 0.14–0.2 N·m | what the servo must fight |
| Torque ripple frequency | ~1 kHz | 4 fins × 258 rev/s — filtered by rotor inertia (I≈4.5e-4 kg·m²) |

**Supersonic notes:** muzzle exit M ≈ 2.4–2.7 — fin lift uses linear supersonic theory (above);
canards sit ahead of the body bow shock, add 1.2–1.4× body carryover (isolated-fin approx is
conservative); wave drag on fins is the axial penalty counted above.

**Actuation physics (torque balance on the rotor):**

```
FREE (ascent, generator):     I·dω/dt = T_aero(ω) − T_gen(ω) − T_bearing
                              equilibrium ω where the aero torque curve crosses the
                              generator load line; T_gen = P_e/(ω·η) — the CPU sets P_e,
              so it sets the equilibrium speed AND the charge rate simultaneously.

HELD (descent, actuator):     0 = T_motor + T_aero_held + T_friction → T_motor ≈ 0.15–0.2 N·m
SLEW:                         T_peak = I·α + T_aero ≈ 0.06 + 0.2 → ~0.3 N·m; spec 1.5 N·m (5×)
```

**Force flow path:** canard → **S11 canard shell** (8× M5 fin-root bolts) → back-iron (8× M4
shell screws) → rotor ring → 2 bearings (M09) → shaft tube (M01) → connector → shell fuze
threads → shell. The 1.3 kN/fin centrifugal load (spin) closes through this same path — it
sizes the shell drum section, the fin-root bolts and bearing pre-load, not the servo.

### 2.7 Lateral impulse thrusters (LIT) — embedded in the canard shell

8 solid-propellant micro-thruster stations machined into the S11 shell wall (SLS-printed
internal cavities), flanking each fin (azimuths 22.5°+45k). Firing a mirror pair on one side
(e.g. top+bottom right) produces a net lateral impulse — the roll-phased thruster analogue of
the fin "hover", usable for terminal precision trim and as correction authority if the
servo/windmill path fails (§3 single-point failure).

| Parameter | Value | Notes |
|---|---|---|
| Stations | 8 (2 per fin, one each side) | Ø8.5 × 6.5 mm axial grain pockets @ r33 (drilled from the aft face) + radial Ø3 nozzle + Ø6 exit flare at z169.5 + Ø2.5 igniter bore from the fwd face |
| Grain per station | ~0.56 cm³ ≈ 0.9 g (placeholder) | energetics = OFB/DRDO allocation (no design content here) |
| Impulse per station / pair | ~1.0 / ~2.1 N·s (Isp ≈ 190 s) | full set 8.4 N·s → Δv ≈ 0.18 m/s → **~7–10 m terminal trim** — a precision add-on, NOT a replacement for the 200–300 m fin authority |
| Thrust (pair, 50 ms burn) | ~85 N peak | lateral load closes shell → 8× M4 → back-iron → bearings → body; bearing radial capacity ≫ |
| Ignition bus | mates at mode switch | rotor is quasi-static after the regen brake — floating contact ring engages; reliability through the 258 rev/s spin-up is open (§10.15) |
| Structure | SLS AlSi10Mg, wall webs 2.3–2.6 mm | grain retained fwd by 2.3 mm web; survival at 15,500 g setback + spin = open item (§10.15) |

**Honest trade note:** the workspace previously rejected cold-gas reaction control by
calculation (`legacy/`). LIT is a different implementation (solid micro-thrusters, terminal
trim/backup role, ~5 g of propellant vs a gas bottle) but it reintroduces reaction-control
mass, ignition safety and OFB logistics — it must pass the same calculation rigor before PDR
(§10.15).

### 2.6 The shell through firing and flight — phases and forces

**Phase A — in-bore (t = 0→~11 ms).** Propellant burns at ~330 MPa peak; base pressure on
Bore area (0.0189 m²) accelerates the 47.5 kg all-up round:

| Effect | Value | Physics |
|---|---|---|
| **Set-back acceleration** | peak **~13,400–15,500 g** | a = P·A/m; sizes every potting joint, magnet retention, bearing preload |
| **Spin-up** | 0 → 15,480 rpm | driving band engraves into 1/20-cal rifling; torque ≈ F·r·tan(twist+friction) ≈ 100 kN·m peak; I_z ≈ 0.158 kg·m² |
| Balloting | bore-clearance bounce | lateral ding at obturation — disturbance input, no design action |
| PGK state | electronics dead (FRAM retains), fins already deployed (Ø108 < 155 bore — no deployment mechanism needed) | |

**Phase B — muzzle exit transition (~1 ms).** Base pressure release → **set-forward 1–2 k g**;
muzzle blast asymmetry (disturbance impulse); first real dynamic pressure q = ½·1.225·800² ≈
**392 kPa** → windmill torque spike ~1.5 N·m spins the free rotor to ~20,000 rpm in <1 s
(α ≈ T/I ≈ 3,400 rad/s²); S&A arms on set-back + set-forward + spin gates.

**Phase C — ascent (0→46 s).** v falls 800→270 m/s, altitude climbs to ~11.5 km, q falls
392→13 kPa. Forces on the shell:

| Force | Model | Notes |
|---|---|---|
| Gravity | m·g, always | the trajectory maker |
| Drag | ½ρV²·S·C_D(M) | S=0.0189 m², C_D ~0.15–0.3 supersonic |
| Lift (from yaw) | ½ρV²·S·C_Lα·α | yaw is small but nonzero |
| **Overturning moment** | M_α = q·S·d·C_Mα·α | CP sits ~1.5–2.5 cal ahead of CG — destabilizing |
| **Gyroscopic stiffness** | spin ω_z resists M_α | the *reason for rifling*: fast precession instead of tumble |
| Yaw of repose | δ_R ∝ ρ·S·d·C_Mα·g·cosθ /(2·I_z·ω_z·v)·k² | small constant nose offset → lift → **spin drift** (hundreds of m at 30 km — one of the errors the canards correct) |
| Magnus force/moment | ω·α coupling | second-order, absorbed by filter |
| Windmill reaction | T_wind on rotor ↔ stator | tiny (~0.1 N·m), slightly increases spin decay (~10%/flight) |

**Phase D — apogee & mode switch (~46 s).** v ≈ 270 m/s, q ≈ 13 kPa (windmill still delivers
60–80 W — comfortable above the 15 W draw). IMU flag + time table trigger regen braking.

**Phase E — descent & correction (46→92 s).** q recovers 15→50 kPa; correction window ~40 s.
The **gyroscopic precession chain** is the physics of steering: canard lateral force 20 N at
~0.65 m ahead of CG → moment ≈ 13 N·m → precession rate Ω = M/(I_z·ω_z) ≈ **0.05 rad/s
(~2.8°/s)**. The shell doesn't "pitch over" — it *precesses* its nose toward the correction,
and because the canards precess with it, the servo continuously re-phases the fin ring so the
averaged force stays on the target line. Integrated Δv ≈ 13–17 m/s → impact shift ≈ 200–300 m.

**Phase F — terminal/impact (~92 s).** v ≈ 300–350 m/s, steep impact angle; fuze function
(proximity/impact) then S&A-covered detonation; self-destruct timer as fallback.

**Force timeline summary (per-phase dominant loads):**

```
A in-bore   : 13,400–15,500 g set-back | ~100 kN·m spin-up torque | balloting
B muzzle    : 1–2 k g set-forward | blast impulse | first q (392 kPa) on fins
C ascent    : drag 8–15 kN | lift/yaw small | overturning moment vs gyro | windmill drag +Δ10% spin decay
D apogee    : min q (13 kPa) | min dynamic loads | mode switch + regen brake
E descent   : q 15–50 kPa | canard forces 15–25 N lateral | hold torque 0.2 N·m | precession steering
F impact    : 300–350 m/s | fuze function | (self-destruct reserve)
```

---

## 3. Mission timeline — when it generates, when it switches

### Phase 0 — pre-fire programming (round not yet fired, no onboard energy used)
Electronics powered **by the inductive setter** (handheld programmer at the nose, cf. Leading
video / M1156 EPIAFS) for 60–90 s while the crew performs laying data:
- BIT of receiver/IMU/motor; status read back on setter (failed rounds not fired)
- IMU turn-on bias sampling + coarse alignment to gun azimuth/quadrant elevation → stored in FRAM
- Mission load: target coordinates, GPS time + ephemeris → stored in FRAM
- Sensor temperature logged for in-flight bias coefficients
- **Power latched OFF before firing** — nothing powered during setback (FRAM retains all state)

```
t=0        Launch. Setback ~15,000 g (electronics dead, state in FRAM); S&A arms;
           windmill rotor spins up <1 s after muzzle exit → generator live immediately
           (bus powers reboot at ~2-3 s; filter initializes from FRAM, not from zero).
t=3–10 s   GPS REACQUISITION (fast — ephemeris/time preloaded), trajectory solution.
t=3→46 s   GENERATOR MODE. Cap charges at 10–15 W. Electronics draw from bus.
t≈46 s     APOGEE (30 km shot): IMU vertical-velocity sign flip or time-table trigger
           → MODE SWITCH: stop generation → regenerative brake 2–4 s (recovers
           ~15–25 J from rotor inertia) → FOC servo mode.
t=50→55 s  Impact-point solution; first fin-phase slews.
t=55→92 s  CORRECTION: rotor roll-phased ("hover"), hold ~2 W + slews.
t≈84–92 s  TERMINAL: VNS window opens inside 2 km (GPS-denied fallback): camera frames
           roll-gated against the 233 rev/s spin, scene-matched vs Phase-0 reference
           imagery, position updates fused into the EKF every ~0.5 s; LIT pairs
           available on command for terminal precision trim / servo-failure backup.
t≈92 s     Impact (or self-destruct timer fallback).
```

Mode change is triggered **twice-redundant**: IMU apogee detection OR time-from-launch table;
if windmill start fails, no generation AND no actuation — the one single-point failure of this
architecture (mitigation: windmill self-start demonstrated ≥0.999, see §10).

---

## 4. Energy ledger (nominal 30 km shot)

| Flow | Energy | Notes |
|---|---|---|
| **Generated** (ascent, 12 W avg × 44 s, 85% charger eff.) | **~450 J** into cap | +15–25 J regen braking at apogee |
| **Stored** | **~465–480 J** in cap | see §5 capacity |
| Electronics consumption (2.4 W bus × 92 s) | 220 J | GPS 1.2 W, IMU 0.4, MCU 0.3, fuze 0.2, losses incl. |
| VNS terminal segment (camera+correlator ~1.2 W × 8 s) | +10 J | §9.10 — GPS-denied fallback |
| Actuator hold (2 W × 42 s) | 84 J | quasi-static hover = copper loss only |
| Actuator slews (8 × 5 J) | 40 J | 90° phase changes |
| **Total consumed** | **~344 J** | |
| **End-of-flight margin** | **~28%** | cap never fully discharged (50→20 V window) |

Range sensitivity: 20 km shot → gen ~360 J vs demand ~270 J (margin 25%);
40 km → gen ~590 J vs demand ~470 J (margin 20%). Closes across the board.

---

## 5. Supercapacitor stack (S09) — storage

| Parameter | Value |
|---|---|
| Type | **Annular-wound EDLC** (custom), no chemistry → g-hard |
| Dimensions (CAD) | OD 49 / ID 31 × 30 mm + two Ø49/Ø30 bus discs (z68.5–101.5) |
| Placement | fuze-well zone z70–100, annulus around Ø30 bore (replaces PMU battery) |
| Bank | **0.6 F @ 54 V** (20 × 2.7 V cell equivalents) |
| Stored energy | ½CV² = **875 J** |
| Usable window (54→20 V, 85% conv. eff.) | **~535 J** |
| Mass | ~67 g |
| Self-discharge note | EDLC leaks %/day — irrelevant here because the stack is charged **in flight**, never stored charged |

---

## 6. Actuator consumption — "return to position + steer"

| Action | Electrical energy |
|---|---|
| Regenerative brake at apogee (4,500 rpm inertial stop) | **−15 to −25 J (recovers)** |
| Hold hover, 42 s descent | 84 J (2.1 A continuous, ~2 W) |
| Phase slews, 8 × 90° in 0.15 s | 40 J (~5 J each: 0.8 J mech + I²R) |
| **Net actuator budget** | **~100–120 J** (~25% of stored energy) |

---

## 7. Canard aerodynamic loads & actuator torque demand

Fin geometry: 3.2 cm² each (root 25 / tip 15 / span 16 mm), 4 fins, cant ±12°.

| Load case | Value | Derivation |
|---|---|---|
| Nominal correction force per fin | **4–6 N** | q=35 kPa, Cl≈0.38 @12° |
| Total lateral correction force | **15–25 N** | mirror-pair sum (opposite fins add, reverse pair cancels laterally) |
| Peak fin load (max q, fin + spin-induced AoA ~26°) | **13 N/fin, ~50 N total** | q=50 kPa, Cl≈0.8 |
| **Centrifugal load per fin** | **≈1.3 kN** | m≈10 g at r=45 mm, 15,480 rpm — dominates fin-root/spar design |
| Bias-ring retention (S04) | bond shear ~9.4 MPa @ 15,500 g set-back; hoop ~10.6 MPa @ 15,480 rpm | epoxy joint on bearing-B race face, ~282 mm² bond; NdFeB hoop margin >7× |
| Fin root design load | 100 N total (≈2× peak) | structural margin |
| Aero windmill torque on held rotor | 0.14–0.2 N·m | 4 fins @ descent q |
| Bearing drag torque (body spinning under held rotor) | ~0.005 N·m | @16,000 rpm relative |
| **Actuator hold torque** | **0.2–0.25 N·m continuous** | spec 0.5 N·m (2× margin) |
| **Actuator peak (slew) torque** | **0.6–0.8 N·m** (inertia 3.6e-4 kg·m², 180°/0.15 s ≈ 0.06 N·m + aero) | spec 1.5 N·m (2× margin) |

---

## 8. Battery vs capacitor for the electronics — trade answer

**Recommendation: supercap-only, no battery in the baseline.** The question is one of
reliability, not energy — any Ø15×30 Li-SOCl2 cell (~5–7 kJ) holds 15+ flights' worth of
electronics energy. The decision drivers:

Pro cap-only (baseline):
- The stack charges **in flight** from muzzle exit — EDLC self-discharge (its usual weakness)
  is irrelevant because it is never stored charged.
- No chemistry = best-case gun-launch survivability (15,000 g setback, −40/+70 °C depot life,
  no venting safety case, >15 y shelf life).
- **Power-quality risk is scheduled away:** GPS acquisition + trajectory solution happen during
  ascent, while the actuator is completely quiescent. FOC bursts (16 A on the 54 V bus) begin
  only at apogee, when the receiver is in tracking mode with the solution already stored.
  ESR dip on the cap bus during bursts ≈ 0.2–0.5 V — ride-through handled by local holdup
  caps on the regulated 3.3/5 V rail.
- Fielded precedent: M1156 PGK — alternator + capacitor, explicitly no battery.

Pro battery (fallback configuration):
- Insures the single-point "windmill fails to start" failure (§10 item 3): electronics would
  boot and fuze functions remain, though actuation authority is still lost with the machine.
- Provides full guidance/actuator power independence if a review board demands it.

**Design provisions adopted (cost nothing now):**
1. Dedicated regulated electronics rail with local holdup capacitance (ms-scale ride-through).
2. Acquisition-before-actuation scheduling (already inherent in the mission timeline, §3).
3. Reserved battery footprint in the PMU section (Ø15×30 cell space) — the optional Li-SOCl2
   cell (~40 g, 7 kJ) can be inserted as a configuration option without redesign.
4. Thermal battery rejected: 100+ g, one-shot, energy role already filled by the alternator.

### 8.1 Pre-fire power & data interface (Phase 0 hardware)

| Item | Spec | Notes |
|---|---|---|
| Inductive coupler | ~1 W transfer, 60–90 s sessions, data ≥ 115 kbaud | **as-built: S07 coupler, ferrite cup Ø42/Ø58.4 at z185.5–191.5**, couples through 0.5 mm gap + 2.5 mm GFRP ogive wall; setter handset clamps the Ø65–74 nose section (handset design still open, §10.7) |
| Non-volatile state store | FRAM, ≥ 8 kB (bias set, ephemeris, mission, BIT log) | g-hard, instant writes, 10^12 endurance |
| Power-path mux | setter power ⇄ generator bus, auto-select, latch-off on fire command | zero onboard pre-fire energy — battery-free architecture preserved |
| Pre-fire session budget | setter supplies ~15–25 J/session | no impact on cap energy ledger |

---

## 9. Sensor & electronics stack — military-grade selection

**Guiding constraint discovered in selection:** the shell spins at **232,000°/s (15,480 rpm)**
about the roll axis — 100× beyond standard tactical IMU gyro range. Every sensor here must be
specified for gun-launched munitions (high-g set-back AND high roll rate), not generic tactical.

### 9.1 IMU — inertial navigation (body-fixed)

| Parameter | Spec / Reference part |
|---|---|
| Baseline selection | **Collins Aerospace SiIMU02** (ex-Atlantic/BAE) — MEMS, all-digital, **gun-hard to 20,000 g** set-back, designed for spinning gun-launched munitions (Excalibur/PGK-class) |
| Critical config | roll-axis gyro ordered in **high-rate variant (≥±25,000°/s)**; lateral axes ±2,000°/s class |
| Gyro performance class | bias repeatability ~1–10 °/h, ARW ~0.1–0.4 °/√h (datasheet per model), accel range **±30,000 g set-back / ±30 g in-flight** class |
| Alt candidates | Honeywell HG1930 (tactical MEMS, munitions-rated; needs high-rate roll variant), ADI ADIS16507 (industrial baseline for bench prototyping only — NOT gun-hard) |
| Power / mass / size | ~2 W class, ~50–100 g, ~Ø50×60 mm class |
| **Mounting (PGK part connection)** | **body-fixed**: small sensor board bolted to shaft tube **M01** near the datum (z≈125–135), r ≤ 20 mm off-axis; mount radius recorded and **centripetal acceleration compensated in the EKF** (a=ω²·r ≈ 5,700 g artifact at our spin — deterministic, subtracted in software) |
| Connection | SPI to control PCB; powered from 3.3 V regulated rail (§2.3) |

### 9.2 GNSS receiver — NavIC + GPS (India context)

| Parameter | Spec / Reference part |
|---|---|
| Baseline selection | **ISRO SAC NavASIC V3** baseband — NavIC SPS + multi-GNSS, low power, small form factor (indigenous, export-clean for SIH) |
| Signals | NavIC L5-SPS + L1-SPS, GPS L1 C/A (L5 dual-band option via URSC NavIC-1 12-ch reference design) |
| Military-grade reference (non-indigenous) | BAESystems G-hardened SAASM receiver w/ integrated 5-channel anti-jam (precision artillery precedent); L3Harris N202 munitions-CRPA shows the miniaturized AJ antenna state of the art |
| Anti-jam posture | full CRPA aperture too large for a fuze → **software AJ**: beam/null steering off single antenna + IMU coupling (deep integration), ephemeris preloaded at Phase 0 reduces acquisition vulnerability window |
| Performance class | 10-channel tracking, C/N₀ down to ~25 dB-Hz, cold-start from Phase 0 ephemeris <10 s |
| Power / mass | ~1.0–1.5 W incl. RF front-end, <20 g |
| **Mounting (PGK part connection)** | receiver/baseband on the **S08 control-module ring (z175–184.8, §9.8, body-fixed)**; **antenna in the S07 radome (z196–200.4, on axis, §9.7)** — antenna boresight along flight axis; RF feed via support-tube coax channel → S08 can feedthrough; the radome's dielectric (S-glass GFRP, 2.5 mm) is RF-transparent |
| Connection | UART/SPI to MCU; 3.3 V rail; 1-PPS time sync to EKF |

### 9.3 Magnetometer — body roll reference (spin sensing)

| Parameter | Spec / Reference part |
|---|---|
| Baseline selection | **PNI RM3100** tri-axis MR magnetometer — highest-resolution low-SWaP, MagI2C ASIC, proven in spin-sensing applications |
| Critical config | body spin 258 Hz → sample **≥2 kHz** (RM3100 continuous mode w/ reduced resolution, or raw MR bridge e.g. Honeywell HMC10xx-class sampled by MCU ADC at ≥5 kHz — analog bridge preferred at high rate) |
| Performance | ~13 nT/√Hz noise (RM3100), Earth field ~25–65 µT → roll resolution well under 0.5° at our spin rate |
| Disturbance handling | rotor PM ring (z138–163) is the near-field threat: mount **≥25 mm aft of z=138**; Phase 0 stationary calibration captures body ferrous signature |
| Power / mass | <10 mW, <2 g |
| **Mounting (PGK part connection)** | small ring board on **shaft tube M01 at z≈115–120** (fuze-well top, inside Ø50.8, body-fixed, >25 mm from rotor magnets); wired along M01 slot to control board |

### 9.4 Rotor-angle array (stator-side, per §2.4)

| Parameter | Spec / Reference part |
|---|---|
| Selection | analog sin/cos Hall/MR array (ams/iC-Haus angle-die class) reading a **2-pole diametral bias ring on rotor S04** — Ø41/Ø51.6 × 3 mm at z163–166 (S04 CAD, done), bonded to the fwd bearing outer-race face |
| Readout | array on a small annular board on the static shaft tube (M01) at z163–166, r ≤ 20 — reads the ring ID across a 0.5 mm radial gap (final gap 1–2 mm via board spacer — open item §10.13) |
| Spec | ≤0.1° interpolation, 2 dies at 90° → sin/cos, 3× digital Hall fallback (60° segments), bare-die potted (g-hard) |
| Connection | sensor board → wiring along M01 slot → MCU ADC/comparator inputs; <5 mW (inside §4 electronics budget — no ledger change) |

### 9.5 Compute & non-volatile memory

| Function | Reference part | Why |
|---|---|---|
| FOC + guidance MCU | **TI C2000 F2837xD-class dual-core** (one core = 20 kHz FOC, other = nav/GNSS fusion/EKF) | dual-core isolation: motor current loops never stall if nav hiccups; industrial baseline, die-level military variants obtainable; ~300 MHz, FPU/TMU, 16-bit PWM |
| State retention | **Infineon FM25V05 FRAM** (5 Mbit SPI) | instant non-volatile writes for Phase 0 (bias/ephemeris/BIT log), survives setback powered-off, 10¹³ endurance |
| Power stage | 3-phase smart gate driver + 16–20 A MOSFET bridge on **M04 PCB** | serves rectifier AND inverter per §2.3 |
| Mounting | MCU+FRAM+gate driver on **M04** (prototype consolidation); production splits: M04 = power/FOC front-end, **S08 control ring (z175–184.8, §9.8)** = nav compute — connected via the M01 slot wiring channel |

### 9.6 Stack wiring (physical connection map)

```
S07 radome:  GNSS antenna (z196–200) ──RF coax──► S08 control ring (z175–184.8): GNSS Rx + nav MCU + FRAM
        ▲ inductive coupler z185.5–191.5                     │ SPI/UART (flange wireway 45° → endbell Ø5 hole → M01 slot)
stator:  M04 PCB: gate driver + MCU-core1 (FOC)   ·   tube board z163–166: sin/cos array (→S04 bias ring)
              ↑ 3-phase power (tube slots)                ↑ sin/cos analog (short traces)
         S04 rotor (magnets + bias ring)     M01 tube: sensor board (SiIMU02-class IMU)
                                                  │ SPI          │ mag ring board (RM3100/raw MR) z≈115
         S09 caps (z70–100) ──54 V via M01 slots──┘              ▼
                                                      EKF on S08 control ring
```

### 9.7 Nose RF section — S07 radome (CAD: `parts/S07_radome.FCStd`, 3 bodies)

**Nose contour (design of record, this rev):** tangent ogive from **Ø76 at z=172.5** (the S11
canard-shell drum) to tip z=220; ρ = (R²+L²)/2R = **48.63 mm** (R=38, L=47.5); blunt tip r=2.
The contour is continuous with the fin drum — the former Ø70 cylinder + Ø87.8 flange step is
gone. Radome occupies z=173→220; 0.5 mm axial seam at Ø76 over the rotating shell.

| Element | Ø inner | Ø outer | Axial (z) | Notes |
|---|---|---|---|---|
| Radome shell (GFRP, S-glass epoxy) | — | ogive 76→0 | 173→220 | wall 2.5 mm, RF-transparent at L-band; CAD vol 28.2 cm³, **53.6 g** |
| Flange (shell base) | 42.8 | 76 | 173→175 | stepped bore: r26.2 over the bearing-race zone (z173–174.2), r21.4 seat on the inner-race OD above; 4× radial M2.5 into the tube at z174.5; **no wireway notch — the harness now passes through the flange bore (M01 slots run to z175)** |
| GNSS antenna stack | — | ground Ø42 | 196→200.4 | patch Ø30 @ z199–200.4 on ground Ø42 @ z196–197.6 (NavIC L1/L5 + GPS L1 per §9.2); support tube Ø18/Ø10 z184.8–196 doubles as coax channel; ~12 g |
| Inductive coupler (Phase 0) | 42 | 57.2 | 185.5→191.5 | ferrite cup + winding band; **coupling gap ≈0.5 mm to wall inner + 2.5 mm GFRP**; setter clamps the ogive at Ø65–74 (z185.5–191.5); ~34.5 g |
| VNS window (provisional) | — | Ø8 sapphire | ~195→205, flank | side-looking aperture for §9.10 — location/azimuth TBD, must clear the antenna stack |

Functional spec: carries only aero/q loads (15,500 g set-back inertial, potted internals);
loss of radome = aero drag penalty, not a safety failure; antenna boresight on flight axis;
coupler powered only by the setter in Phase 0 (§8.1, no onboard energy).

### 9.8 Control-module ring — S08 (CAD: `parts/S08_control_ring.FCStd`, 2 bodies)

| Element | Ø | Axial (z) | Notes |
|---|---|---|---|
| Ring PCB (FR4) | Ø69.8 × 1.6 | 175→176.6 | sits on radome flange; 4× Ø2.7 @ r33 (45/135/225/315°), M2.5 through-bolts + locknuts; **12.2 g** |
| Shield can (Al, 0.5 wall/0.4 cap) | Ø59.6 | 176.6→184.8 | center RF feedthrough Ø3.2 (antenna coax); **5.0 g** |
| Contents (not in CAD) | — | — | SAC NavASIC V3 GNSS Rx + second MCU core (nav/EKF) + FRAM + Phase-0 power mux (§8.1) — per §9.2/§9.5 |

Body-fixed (static): mounted to the radome flange, does not spin. Harness to the motor bay:
through the flange bore into the **M01 tube wire slots (now full-length to z175)** → M04
(per §9.6). S08 slimmed this rev to fit the new nose ogive (PCB Ø69.8, can Ø59.6).

### 9.9 Fuze-well stack — S10 (CAD: `parts/S10_fuze_stack.FCStd`, 6 bodies; z=0–70, Ø50.8 well)

Architecture per the Leading PGK reference (research extract §11–12: trigger module inertia
switches, ignition-control modes) adapted to our supercap-only single-machine kit.

| Element | Ø | Axial (z) | Material | Notes |
|---|---|---|---|---|
| Thread ring | Ø37/Ø50.8 | 0→19 | steel | 2"-12 UNEF-2A into the shell fuze well (threads not modeled); **142 g** |
| Fuze housing | Ø30.4/Ø50.8 | 19→68 | 7075 | bore liner (protects the Ø30 train bore) + double wall; internal cavity slot Ø34.4/Ø46.8, z21–66; webs z19–21, 66–68; **78 g** |
| Explosive train (lower) | Ø20/Ø26 | 22→34 | placeholder | booster cup + lead charge seat, **on-axis (the train itself lives in the reserved bore by definition)**; energetics = supplier detail, open item; **15 g** |
| S&A rotor | Ø28 | 34→40 | steel | slider rotor, detonator station Ø3 @ r7 (90° out-of-line = SAFE shown); arms on set-back + set-forward + spin gates (§2.6 Phases A/B); **29 g** |
| Firing/security PCB | Ø46.4/Ø18.4 ring | 46→47.6 | FR4 | inertia switches (radial + axial per Leading), firing-condenser + safe-and-arm logic, proximity FM-CW microstrip ring antenna (faces target through housing wall), delay + self-destruct (power-off via motor-cessation sense + timed); **2.4 g** |
| Connector | Ø34.4/Ø46.4 | 64→66 | LCP | 7-pin interface upward to S09/S08 bus (54 V, fire bus, self-destruct, prox, spare); flex tail through housing top-web slot @45°; **2.2 g** |

**S10 total ≈ 269 g.** Failure modes: S&A out-of-line = fail-safe (no detonation); electronics
loss leaves the inertia trigger path; connector loss = no guidance power (motor + caps
unaffected above). CAD-verified: 0 clashes, bore clear for all non-train parts, Ø50.8
well respected.

### 9.10 Visual navigation system (VNS) — terminal INS aiding (concept this rev)

GPS-denied terminal guidance: inside ~2 km the camera sees the target area (fort/camp class),
scene-matches against reference imagery loaded at Phase 0, and the position fix is fused into
the S08 EKF — steering continues on INS+VNS to impact. This is the classic DSMAC/scene-match
architecture scaled to a fuze.

| Parameter | Spec / Reference | Notes |
|---|---|---|
| Sensor | gun-hard EO camera (or LWIR microbolometer for night/smoke), ≥1 kfps global-shutter class | window: Ø8 sapphire on the S07 ogive flank (provisional z195–205 — must clear the GNSS antenna stack, azimuth TBD) |
| Hard problem #1 — spin | body spins 233 rev/s at descent: exposure must gate to 30–50 µs and register frame azimuth from the magnetometer/gyro roll solution; each frame covers a narrow azimuth wedge | frames mosaic into a sweep image; this is THE feasibility item (§10.16) |
| Hard problem #2 — velocity | ~300–350 m/s ground footprint: motion blur sets the exposure floor; LWIR relaxes it somewhat | trade EO vs LWIR open |
| Correlator | scene-match vs pre-loaded reference chip (target-area imagery, Phase 0 upload ≤ 8 MB via setter), normalized cross-correlation / feature matching on S08 core 2 | 0.5 s update rate, position σ target ≤ 15 m |
| Fusion | VNS position as an EKF update (same slot as GNSS), INS coasting between fixes | GPS jam → EKF switches measurement source; no guidance-law change |
| Power / mass | ~1.2 W × 8 s ≈ 10 J (§4); camera+window ≈ 15 g | inside the cap margin (sim: 35%) |
| Failure modes | window fouling/smoke → no VNS fixes → INS-only coast (same as GNSS outage); VNS cannot jam but can be decoyed — reference-image integrity is an intel dependency |

---

## 10. Assumptions & open items (tracked)

1. Ballistics **refined this rev** — point-mass trajectory + single-machine energy sim
   (`sim/sim_single_machine.py`, results in `sim/RESULTS_SINGLE_MACHINE.md`): 30 km closed with
   Cd 0.203; TOF 87.6 s, apogee 9.5 km @ 40.6 s (vs §1's 11.5 km/46 s — point-mass + exp-atmosphere
   conservatism); generated 412 J, used 344 J, cap margin 35% (§4 confirmed, better); guided CEP
   28.5 m vs 196 m unguided (7×, meets the ≤30 m class). **Still before PDR:** 6DOF (Magnus,
   precession steering chain, yaw-of-repose, subsonic Cd rise — sim impact speed 413 m/s vs §2.6's
   300-350).
2. Kt/R estimates from ring-motor sizing scalings — verify with FEMM magnetostatic run.
3. Windmill self-start and equilibrium speed (~20,000 rpm class) needs a spin-tunnel or CFD check — single-point failure of the architecture.
4. Hover control law (inertial hover vs body-relative pulse correction) affects hold power ±50%; budget uses the conservative inertial-hover number.
5. GPS M-code power 1.2 W assumed; Desi/NavIC receiver choice may change electronics budget ±0.5 W.
6. EDLC g-hardness data at 15,000 g setback — request cell-level test data from supplier.
7. Inductive coupler (§8.1): coil **DONE (S07, z185.5–191.5)** — setter **handset** design + coupling budget through GFRP (link budget, alignment tolerance) still open.
8. FRAM retention through 15,000 g setback shock — vendor shock-rating confirmation required.
9. Radome + control-module ring + fuze-well stack **DONE (S07/S08/S10, this rev — §9.7/§9.8/§9.9)**; still open: energetic train details (detonator/lead/booster part numbers = explosive-supplier scope), S&A mechanism detail design (springs, locks, gates), proximity-antenna detection range, setter handset.
10. S04 bias-magnet ring — **DONE (this rev)**: built as Ø41/Ø51.6 × 3 mm at z163–166,
    2-pole diametral N42SH, bonded to the fwd bearing outer-race face; fwd bearing shifted
    z165→166 (assembly link only, M09 part unchanged). The originally sketched Ø~45 × 4 at
    z163–169 was not buildable: the stator root occupies r20–26 up to z163 and the fwd
    bearing occupies r20–26 from z165 — z163–166 × Ø41–51.6 is the clash-free maximum
    (verified in assembly, all 4 rotor phases).
11. SiIMU02 (RTX/Collins, USA) is export-controlled; for the Indian program the indigenous route is a NavIC-integrated munitions IMU (SAC/partner) or a licensed high-rate MEMS set — procurement path is an open programmatic item, not a COTS buy.
12. Bearing-B inner-race seat **fixed this rev** (M01 tube extended to z175 — race fully
    seated). Still open: bearing-B **outer**-race axial capture fwd (race runs to z174, the S11
    shell ends at z172.5) — needs a snap-ring groove on the race or a capture lip at detail design.
13. Sin/cos array radial gap (0.5 mm nominal: ring ID Ø41 − tube OD Ø40) likely overdrives
    linear Hall dies — set the final 1–2 mm gap with a board spacer at detail design.
14. Rotor speed assumptions inconsistent across the sheet (§2.2 "~20,000 rpm class", §6 "4,500 rpm
    inertial stop"): trajectory sim (`sim/`, this rev) rides ~10,700 rpm at apogee switch and
    recovers ~155 J of regen (vs §6's 15–25 J — favourable). Reconcile §6 at detail design.
15. **LIT thruster set (§2.7):** ignition-bus reliability across the rotating/static interface,
    grain survival at 15,500 g setback + 258 rev/s spin, nozzle aero when unfired, and the
    trade vs the rejected cold-gas concept (`legacy/`) all need calculation + test before PDR.
    Propellant/igniters are OFB/DRDO allocations (no energetics design content).
16. **VNS (§9.10):** spin de-blur (30–50 µs gating at 233 rev/s), EO vs LWIR trade, window
    aero-heating, correlator compute load on S08 core 2, and reference-imagery tasking are
    concept-level — feasibility demo required before PDR.

---

## 11. STANDING PROCESS (applies to everything in this workspace from now on)

For **every** design item (part, subsystem, or analysis) produced in this workspace:
1. Model it in CAD under `cad_models/parts/` per `cad_models/README.md` conventions.
2. Add its **dimension table** (from CAD, not hand-typed) to this sheet.
3. Add its **functional spec**: masses, loads it must carry, power it draws or produces,
   timing of its operation within the flight profile, and failure modes.
4. Update the energy ledger (§4) if it produces or consumes energy.
5. Update the mission timeline (§3) if it changes the sequence of operations.
6. Note open items in §10 rather than leaving silent assumptions.
