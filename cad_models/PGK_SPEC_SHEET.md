# PGK 155mm — MAIN SPECIFICATION SHEET
### Single time-share motor (alternator ⇄ actuator) · canonical design
**Doc status: living document — design of record for the whole workspace** (supersedes the
`cleansheet/` Rev 1.7 lineage, which remains as methods reference only). Every future design
item in this workspace MUST add/update its section here (standing process, §11).
Last synced with CAD: this rev — S-series build + bias ring (S04), nose RF section (S07),
control ring (S08) **+ interior electronics detail (2 PCBs + GNSS/MCU/FRAM/PwrMux inside shield can, this rev)**, fuze-well stack (S10); fwd bearing z166; assembly gate 0 clashes
(4 rotor phases), bore clear, Ø108.0 × z0–220, PGK ~1.20 kg (was ~1.18 kg; +18 g S08 interior).

---

## 1. Mission & ballistic assumptions (155mm, M795-class)

| Parameter | Value | Basis |
|---|---|---|
| Projectile all-up mass | ~48.0 kg (shell 46.84 H01 `PGK_SPEC_SHEET.md:581` + PGK ~1.20 kg `PGK_SPEC_SHEET.md:80`: motor+shell 719 + nose 99 + fuze 269 + control 35 + caps 67 + harness/fastener/potting reserve 15 g pending) | M795 + this kit — **reconciled this rev; was 47.9/1.18 with 17 g control-ring prior, now 35.4 g** |
| Muzzle velocity | 800 m/s (charge-dependent 650–900) | nominal charge |
| Rifling twist | 1 turn / 20 cal → spin at muzzle **15,480 rpm** | 155mm standard |
| Spin at target | ~14,000 rpm (~10% decay) | standard decay models |
| Flight regime | spin-stabilized, correction in terminal (descent) phase only | PGK doctrine |

**Time-of-flight / apogee table (45° quadrant elevation, ISA, no wind):**

| Range | v₀ (m/s) | TOF — analytic table (§1) | Apogee — analytic | TOF — point-mass sim `sim/sim_single_machine.py:1` | Apogee — sim | Use for design |
|---|---|---|---|---|---|---|
| 20 km | ~650 | 63 s | ~31 s / ~8 km | 58.4 s | 28.5 s / 7.1 km | sim for energy; table for mission planning |
| **30 km (nominal)** | **800** | **92 s** | **~46 s / ~11.5 km** | **87.6 s** | **~40.6 s / ~9.5 km** | **sim is authoritative for ledger (conservative exp-atmosphere); 46 s is legacy doctrine window kept for setter tables** |
| 40 km | ~900 (BB/RAP) | 118 s | ~60 s / ~13 km | 112 s | ~56 s / ~11.2 km | sim |

> **Reconciliation `PGK_SPEC_SHEET.md:594` item 1:** the analytic table uses sea-level ρ and constant Cd 0.30 with no wind; the sim uses exponential atmosphere + Cd 0.203 + 6-state drag. Difference ΔTOF ≈ -4 to -6 s, Δapogee ≈ -2 km is expected conservatism, not an error. Both close the energy ledger (sim margin 35% vs analytic 28%). **Before PDR: 6DOF** must add Magnus, yaw-of-repose, precession steering chain and subsonic Cd rise. Sim impact speed 413 m/s vs `PGK_SPEC_SHEET.md:266` 300-350 m/s is the subsonic-Cd omission — treat 413 m/s as upper bound, 350 m/s as lower bound until 6DOF.

Dynamic pressure during correction (descent, 2–8 km alt): **q ≈ 15–50 kPa** (nominal 35 kPa) — measured at fin mid-span; q at apogee ≈ 13 kPa `PGK_SPEC_SHEET.md:262`.

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

  **Mass rollup (CAD volumes, assembled — density × tip volume, no fasteners/potting):**

| Part | cm³ | g | Basis |
|---|---|---|---|
| Shaft tube M01 (incl. fwd ext) | 28.3 | 78.8 | 7075 2.81 g/cm³ |
| Stator core (lam.) | 22.8 | 174.2 | M250-35A 7.65 |
| Coils (potted Cu) | 8.3 | 69.4 | Cu 8.96 + potting |
| PCB M04 | 0.9 | 1.7 | FR4 1.85 |
| Rotor (ring+magnets+bias ring) | 25.5 | 199.1 | steel 7.85 + N42SH 7.5 |
| **Canard shell S11 (incl. LIT cavities)** | 31.0 | 82.9 | AlSi10Mg 2.68 SLS |
| Fins ×4 (7075) | 3.2 | 9.0 | 7075 2.81 |
| Bearings ×2 | 10.3 | 80.9 | 100Cr6 7.85 simplified |
| Endbell (aft only) | 8.2 | 22.9 | 7075 |
| **Motor module subtotal (CAD)** | | **718.9 → reported 719** | **was 723 — 4.1 g was legacy fastener allowance double-counted; corrected this rev** |
| Fastener/potting reserve (8×M4 shell→iron, 8×M5 fin roots, potting) | — | **4.1** | not in CAD, carried as reserve to keep 723 headline for backward compat |
| **Motor module with reserve** | | **723** | headline kept for `PGK_SPEC_SHEET.md:79` rollup stability |
| Supercap stack S09 | 37.5 | 67.4 | EDLC + bus discs |
| **Total power/train section** | | **790** | 723 + 67 |
| Nose RF section S07 (radome+antenna+coupler) | 41.1 | ~99 | GFRP 1.9 + ferrite + Al |
| Control ring S08 (PCB+shield can + 2 inner PCBs + 4 modules) | 14.0 | **35.4** | FR4+Al, was 17 g pre-interior |
| Fuze-well stack S10 | 58.4 | ~269 | steel+7075+LCP |
| **PGK modeled total** | | **~1.20 kg** | was 1.18 kg pre-S08 interior (+18.4 g); harness/energetics/fasteners **pending 12-18 g** carries separate reserve line below |
| Harness + coax + flex tails + potting (estimate) | — | **~12 g** | AWG26 PTFE + coax, not in CAD |

> **Honest gate `cad_models/README.md:52`:** `PGK_Motor_Assembly.FCStd:18` parametric + `PGK_Full_Assembly.FCStd:19` flattened + `PGK_Shell_Mated_Assembly.FCStd:37` mated all check: **bore Ø30 clear z0-173 (S10 train exception), envelope Ø108.0 `PGK_SPEC_SHEET.md:59` (fins tip) < Ø110, z0-220, clashes = 0 *after* excluding intentional overlaps S01∩S02/S01∩M04/S02∩M04 (winding wrap) and tangent S07 flange↔S08 PCB `PGK_SPEC_SHEET.md:7`; true solver clashes = 0.**

### 2.2 Electrical spec

| Parameter | Value | Condition |
|---|---|---|
| Torque constant Kt | ~0.095 N·m/A (25 mm active) | sizing scaling `PGK_SPEC_SHEET.md:600` item 2, to be verified FEMM |
| Phase resistance | ~0.15 Ω | 12×150T 0.35mm litz-equiv `PGK_SPEC_SHEET.md:51` |
| Line EMF (open-circuit) | 7.5–10 mV/rpm → **150–200 V @20,000 rpm rel.** buck-charged to 54V bus | early flight max; throttled at altitude |
| Continuous torque (thermal) | 0.5 N·m | 2× margin over 0.22 N·m aero hold `PGK_SPEC_SHEET.md:374` |
| Peak torque (100 ms, firmware-limited 16A) | 1.5 N·m | 2× margin over 0.7 N·m slew `PGK_SPEC_SHEET.md:376` |
| **Generator output, ascent** | **10–15 W regulated (up to 20 W early, throttled)** | CPU sets P_e to set equilibrium ω `PGK_SPEC_SHEET.md:194` |
| Actuator hold current | ~2.1 A → ~2 W copper | `PGK_SPEC_SHEET.md:202` |
| Peak slew current | ~16 A (100 ms bursts) | `PGK_SPEC_SHEET.md:202` |

> **Speed definitions reconciled this rev `PGK_SPEC_SHEET.md:623` item 14 — three distinct speeds, not one:** (a) **Windmill equilibrium early flight ~18–20k rpm rel.** `PGK_SPEC_SHEET.md:88` = aero torque vs generator load crossing at q≈200-392kPa `PGK_SPEC_SHEET.md:242`; (b) **Rotor speed at apogee switch ~10.7k rpm** from `sim/sim_single_machine.py:1` `PGK_SPEC_SHEET.md:596` - the value that sets regen energy; (c) **Held/slewing speed ≈0 inertial** `PGK_SPEC_SHEET.md:199` descent. The legacy `PGK_SPEC_SHEET.md:363` “4,500 rpm inertial stop” is retired — it was a pre-sim placeholder. Line EMF 150-200V applies to (a); regen energy applies to (b).

### 2.3 Power architecture (one power stage, two software roles) — parts defined this rev

The rectifier and the motor inverter are the **same three half-bridges** — the "mode change"
at apogee is a software role switch, not a hardware change. All three control loops (FOC
current control, charge regulation, mode state machine) run on the single MCU (C2000 dual-core: core0 FOC, core1 nav — see `PGK_SPEC_SHEET.md:483`).

```
GENERATOR MODE (ascent):                    ACTUATOR MODE (descent):
windmill rotor spins (0→46 s)               rotor servo-held / slewed (46→92 s)
   ↓ 3-phase AC, 150–200 V @ 20k rpm           ↑ FOC phase currents, ≤16 A
   ↓                                           ↑
same inverter bridges ──► ACTIVE RECTIFIER  same inverter bridges ◄── 54 V bus (S09 0.6F)
   ↓ synchronous buck charger (85% eff., LT8616/LT8645S-class)  ↓
SUPERCAP STACK 0.6 F @ 54 V (875 J) ══════► SUPERCAP STACK (sole source after apogee)
   ↓ wide-Vin bucks + holdup caps (see below)
3.3 / 5 V rails ──► GPS · IMU · MCU · FRAM · fuze electronics
```

**Recommended power-stage PNs this rev (54 V bus → wide-Vin, not the `electronics/` 5 V reference `cleansheet/06_ELECTRONICS_ARCHITECTURE.md:47`):**

| Block | PN (recommended) | Key spec | Placement | Notes |
|---|---|---|---|---|
| 3ph bridge (×3 half-bridges) | **DRV8323RS** smart gate driver + **6× BSC040N10NS5 100V/4.0mΩ** (2∥ per switch = 2.0mΩ) | 65V max VM, 3.3V logic, bootstrap + trickle pump, HW OCP; FET 100V survives 54V+EMF clamp + TVS | **M04 PCB** `PGK_SPEC_SHEET.md:51` Ø52/58.5 z138-139.5 | 16A/100ms → I_rms≈11A → cond 3×121×2.0mΩ≈0.73W over 42s hold, slews 16A only ms; adiabatic on 2oz Cu + S01 core spreader |
| Active-rectifier → buck charger | **LT8645S / LT8616 65V sync buck** (42V-65V in, 54V→32V charge profile) | 65V Vin, 8A, 95% peak, spread-spectrum, EN tied to charge-regulation loop | M04, inductor 10µH 10A saturated rated >15.5kg, TVS SMAJ58A on bus | CPU throttles P_e to hold cap 54→20V window; inductor/cap sized for 20W early q388kPa |
| Wide-Vin logic bucks (logic rail) | **TPS62933 3.8-30V → used with pre-regulator LTC3639 60V→12V intermediate** or **LT8645S 65V direct 54→3.3V (preferred, one stage)** | 65V direct eliminates intermediate; 3A, 2.2MHz spread-spectrum isolates GNSS | S08 Upper PCB `PGK_SPEC_SHEET.md:531` | dome load `PGK_SPEC_SHEET.md:329` 0.25W 3.3V + K-LD7 0.20W/12V via separate 12V tap; slip-ring heritage budget not applicable — all on same frame |
| RF LDO | **TLV75733P 3.3→3.0V / TLV70733** | 1A, 25µVrms, PSRR >60dB @1MHz | S08 Inner PCB | isolates NEO-F10N/NavASIC RF from buck ripple |
| Bus protection | **SMAJ58A 58V TVS + 10µF 100V + 470µF bulk** | clamp so buck Vin stays <65V through 200V EMF dump | M04 bus entry | ride-through on contact bounce ≥5ms is now cap-bus ride-through, not slip-ring |
| Current sense | **3× INA240A2 + 3× 5mΩ 2512 shunts** | −4→80V CM, PWM-rejection 93dB | M04 inline | 16A →80mV → ADC1 15kHz scan triggered by TIM1 |

CPU control authority (single MCU, three nested jobs):
1. **FOC current/torque loops** (~20 kHz, core0): commanded hold/slew torque → phase currents (T = Kt·I); rotor roll position `PGK_SPEC_SHEET.md:140` measured per cycle. Current hard-limited to 16 A in firmware — the 1.5 N·m spec cannot be exceeded even by software fault. Loop isolated from nav core1 (`PGK_SPEC_SHEET.md:483` dual-core) so nav hiccup never stalls FOC.
2. **Charge regulation** (core0, 1kHz): rectifier load throttled to hold the cap inside its 54→20 V window — buck enable/Ilmit set by PI on Vcap.
3. **Mode state machine** (core1, 100Hz): Phase 0 session `PGK_SPEC_SHEET.md:293`, generator/actuator switch at apogee `PGK_SPEC_SHEET.md:304` (IMU vertical-velocity flip OR time-table, dual-redundant `PGK_SPEC_SHEET.md:317`), regen braking, self-destruct supervision.

Sequencing note: during ascent the electronics run **live off the rectified generator** (cap charging in parallel); the cap becomes the sole source at the apogee mode switch. Actuator bursts begin only after GPS solution is stored — the noisy phase never overlaps receiver acquisition (`PGK_SPEC_SHEET.md:124` §8).

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

## 6. Actuator consumption — "return to position + steer" (reconciled `PGK_SPEC_SHEET.md:623` item 14)

| Action | Electrical energy | Basis |
|---|---|---|
| Regenerative brake at apogee — **sim value ~10.7k rpm → ~35–55 J (sim reports 155 J gross at 10.7k rpm with ideal inverter, derated to 35-55 J after 85% rectifier + bearing drag)** | **−35 to −55 J (recovers)** | `sim/sim_single_machine.py:1` inertia 4.5e-4 kg·m² × ω²/2; **legacy 4,500 rpm /15-25J placeholder retired** - keep 35-55J as PDR planning value, 15-25J retained as conservative ledger entry until measured |
| Hold hover, 42 s descent | 84 J (2.1 A continuous, ~2 W) | quasi-static copper |
| Phase slews, 8 × 90° in 0.15 s | 40 J (~5 J each: 0.8 J mech + I²R) | |
| **Net actuator budget** | **~70–90 J (if 35-55J regen) ~100–120 J (if legacy regen ignored)** | **~15% of 875J** — ledger `PGK_SPEC_SHEET.md:338` stays conservative with 15-25J regen |

> **Ledger `PGK_SPEC_SHEET.md:338` stays at 344 J consumed / 412-450 J generated / 28-35% margin — regen upside is not credited to margin until spin-tunnel validates equilibrium speed `PGK_SPEC_SHEET.md:605` item 3.**

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

| Parameter | Spec / Reference part — **closed this rev `PGK_SPEC_SHEET.md:623` item13** |
|---|---|
| Selection | analog sin/cos Hall/MR array (ams/iC-Haus **TMAG5170** or **AS5600 bare-die** class) reading a **2-pole diametral bias ring on rotor S04** — Ø41/Ø51.6 × 3 mm at z163–166 (S04 CAD, done), bonded to bearing-B outer-race face with **3M DP420 epoxy 282mm² 9.4MPa shear** `PGK_SPEC_SHEET.md:385` |
| Readout | annular board FR4 0.8mm on M01 OD40 at z163–166, r18 — reads ring ID across **1.5 mm gap via 1.0mm FR4 shim+0.5mm die height**; gap set by 2× M1.6 standoffs to tune field to **40 mT at die (linear range 30-50mT)** — 0.5mm nominal would give >70mT saturation, now avoided |
| Spec | ≤0.1° interpolation after 12-bit ADC, 2 dies 90° → sin/cos, 3× TLE4906L digital Hall fallback 60° segments, bare-die potted with Nusil CV-2500 g-hard |
| Connection | `PGK_SPEC_SHEET.md:504` 4× AWG30 shielded → M04 ADC/comparator `PGK_SPEC_SHEET.md:104` DRV8323RS sense chain; <5 mW (inside `PGK_SPEC_SHEET.md:338` electronics budget) |

### 9.5 Compute & non-volatile memory — **electronics divergence clarified this rev**

| Function | Reference part — **current single-machine baseline (this spec)** | Legacy reference `electronics/` `cleansheet/06_ELECTRONICS_ARCHITECTURE.md:17` | Why |
|---|---|---|---|
| FOC + guidance MCU | **TI C2000 F2837xD-class dual-core** (core0 20kHz FOC, core1 nav/GNSS fusion/EKF `PGK_SPEC_SHEET.md:122`) | STM32G474RET6 + G431CBT6 dual-die dual-board `electronics/gnc_mcu.kicad_sch:13` - **superseded as architecture per `AGENTS.md:2`**, kept as methods/schematic-style reference only | dual-core single-die isolation: FOC never stalls if nav hiccups; ~300MHz FPU/TMU 16b PWM; die-level military variants obtainable; single MCU owns `PGK_SPEC_SHEET.md:104` three loops |
| State retention | **Infineon FM25V05 FRAM** (5 Mbit SPI, 10¹³ endurance) + **W25Q128JVSIQ flash shadow** on S08 Inner PCB | W25Q128JVSIQ only `electronics/gnc_board.net:1830` `electronics/gnc_sensors.kicad_sch:398` | FRAM for Phase0 instant writes powered-off survival; flash for VNS reference imagery ≤8MB `PGK_SPEC_SHEET.md:585` + BIT log overflow |
| Power stage | **DRV8323RS + 6× BSC040N10NS5** `PGK_SPEC_SHEET.md:104` 100V FETs on M04 annular | DRV8329 + NVMFS5C460NL 40V 6× on A6 boost 5V bus `cleansheet/06_ELECTRONICS_ARCHITECTURE.md:17` - 40V insufficient for 54V cap bus | 100V FETs survive 54V+clamp; same 3 half-bridges per `PGK_SPEC_SHEET.md:104` serve rectifier AND inverter |
| Mounting | MCU+FRAM+gate driver **proto on M04** `PGK_SPEC_SHEET.md:51`; production splits: M04=power/FOC front-end, **S08 control ring (z175–184.8, `PGK_SPEC_SHEET.md:535`)** = nav compute — connected via M01 slot `PGK_SPEC_SHEET.md:504` wiring channel | `electronics/gnc_board.kicad_pro:1` GNC board D3 Ø62 4-layer on rotor frame - topology changed to body-fixed single frame `PGK_SPEC_SHEET.md:550` | Proto consolidation simplifies `PGK_SPEC_SHEET.md:340` ledger; production separation isolates `PGK_SPEC_SHEET.md:149` 15kHz PWM EMI from GNSS |

> **BOM note `SIH26098_COTS_BOM.md:1` vs `SIH26098_FLIGHT_KIT_BOM.*`:** those BOMs date from `cleansheet/` Rev1.7 dual-rotor + battery heritage `README.md:46` - resync required before reuse per `AGENTS.md:2`. Current kit flight BOM delta is `S09:67g + S08:35g + S07:99g + harness12g - battery410g (removed) - second rotor~210g` = net -380g and -₹22k vs Rev1.7 1.88kg `cleansheet/03_DESIGN_REPORT.md:326`.

### 9.6 Stack wiring (physical connection map) — defined this rev (harness PN, gauge, potting, grounding)

```
S07 radome:  GNSS antenna (z196–200) ──RF coax RG178 50Ω──► S08 control ring (z175–184.8): GNSS Rx + nav MCU + FRAM
        ▲ inductive coupler z185.5–191.5 (see `PGK_SPEC_SHEET.md:426` link budget)      │ 3-wire power+data flex (flange bore → endbell Ø5 hole @45° → M01 slots 2× 2.5×30)
stator:  M04 PCB: DRV8323RS + BSC040N10 + MCU-core0 (FOC) · tube board z163–166: sin/cos array (→S04 bias ring) FR4 0.8mm
              ↑ 3-phase 3× 0.75mm² PTFE 19/0.22 (tube slots, twisted)   ↑ sin/cos 4× AWG30 twisted-shield + GND
         S04 rotor (magnets + bias ring)     M01 tube: sensor board (SiIMU02-class IMU) SPI 4× AWG30
                                                  │ 54V bus 2× AWG26 PTFE (S09↔M04↔S08)  │ mag ring board (RM3100/raw MR) z≈115 SPI 100kHz
         S09 caps (z70–100) ──54 V via M01 slots (fused 20A SMD, TVS SMAJ58A @M04)──┘   ▼
                                                      EKF on S08 control ring (Al shield can = star GND)
```

**Harness & grounding defined this rev:**

| Run | Route | Cable | Current/loss | Protection | Notes |
|---|---|---|---|---|---|
| 54V bus S09↔M04↔S08 | S09 bus discs z68.5-101.5 → M01 slots 2×2.5×30 to z138 → M04 ring → up slots to z175 → S08 ring PCB `PGK_SPEC_SHEET.md:526` flange bore (no notch) → endbell hole Ø5 `PGK_SPEC_SHEET.md:550` | **2× AWG26 PTFE 19/0.22, 3A cont, >0.5mm creepage to Ø30 bore** (red/black twisted) | 2.1A hold, 16A 100ms slew — I²R AWG26 0.13Ω/m ×0.08m≈10mΩ → 0.04V hold, 2.6V peak→local 470µF 63V bulk @M04+S08 | 20A fast SMD fuse + SMAJ58A + 10µF 100V ceramic + 100n decoupling per IC | slots potted with **Nusil CV-2500 / Araldite CW1312** after harness lay, strain-relieved at slot ends with Kapton tie + epoxy fillet; harness mass counted 12g `PGK_SPEC_SHEET.md:81` |
| 3ph motor M04↔S01 coils | M04 annular → 3× slots → S02 tooth coils 150T | **3× 0.75mm² PTFE 105×0.09 litz-equiv, twisted trio, 8A cont /16A peak** | Rph 0.15Ω `PGK_SPEC_SHEET.md:95` dominates | INA240 5mΩ sense `PGK_SPEC_SHEET.md:104` inline | litz potted with S02 coils, entry via M04 edge cutouts |
| Sin/cos array z163-166 → M04 | annular board on M01 OD40 `PGK_SPEC_SHEET.md:491` → along slot → M04 ADC | **4× AWG30 twisted shielded (S+ / S- analog), shield = AGND at M04 only** | <5mW `PGK_SPEC_SHEET.md:491` | RC 1k/10n + TVS PRTR5V0U2X | board spacer 1.5mm FR4 shim sets gap `PGK_SPEC_SHEET.md:623` item13; 1.5mm = 40mT at dies, linear range |
| IMU SPI z125-135 → S08 | M01 mount r≤20 `PGK_SPEC_SHEET.md:503` → slot → S08 SPI | **4× AWG30 twisted (SCLK/SDI/SDO) + S-gnd, 10MHz** | — | 33Ω series + 100pF + PRTR5V0U2X | magnetometer  ≥25mm from rotor `PGK_SPEC_SHEET.md:465` |
| GNSS coax | patch Ø30 z199 `PGK_SPEC_SHEET.md:527` → support tube Ø18/Ø10 z184.8-196 coax channel → S08 feedthrough Ø3.2 `PGK_SPEC_SHEET.md:540` | **RG178 50Ω, SMA→U.FL, loss <0.5dB** | — | gas-discharge + ESD PRTR5V0U2X @ S08 | tube channel potted except coax; radome wall 2.5mm GFRP `PGK_SPEC_SHEET.md:526` RF ≥85% @ L1/L5 |
| S10 connector flex | S10 housing `PGK_SPEC_SHEET.md:566` top-web slot @45° flex tail 25mm → S09/S08 bus | **7-pin 1.27mm flex: 54V/fire/self-destruct/prox/spare/GND, 0.5mm polyimide** | fire bus 5A cap-discharge pulse | TVS SMAJ5.0A per line + 10n feedthrough | LCP connector `PGK_SPEC_SHEET.md:566` mated at assembly, flex tail soldered then potted |

**Grounding & ESD star:** S08 shield can Al 0.5w `PGK_SPEC_SHEET.md:540` is single-point chassis GND — bonded to M01 tube via 4× M2.5 through-bolts `PGK_SPEC_SHEET.md:538` + internal 6mm wide Cu strap to M04 GND plane at slot exit; M04/S08 GND planes tied only at that strap (no loop through caps). RF feedthrough Ø3.2 `PGK_SPEC_SHEET.md:540` uses 10n feedthrough cap + PRTR5V0U2X 5V TVS array. Bulk caps 470µF 63V @M04 & @S08 provide `PGK_SPEC_SHEET.md:149` 5ms ride-through for FOC bursts (16A ×100µs → 1.6mC → ΔV 3.4V on 470µF, held by cap bus 54→20V window). All boards 2oz Cu `cleansheet/06_ELECTRONICS_ARCHITECTURE.md:284` heritage, potted for 15.5kg `PGK_SPEC_SHEET.md:611` item9.

### 9.7 Nose RF section — S07 radome (CAD: `parts/S07_radome.FCStd`, 3 bodies)

**Nose contour (design of record, this rev):** tangent ogive from **Ø76 at z=172.5** (the S11
canard-shell drum) to tip z=220; ρ = (R²+L²)/2R = **48.63 mm** (R=38, L=47.5); blunt tip r=2.
The contour is continuous with the fin drum — the former Ø70 cylinder + Ø87.8 flange step is
gone. Radome occupies z=173→220; 0.5 mm axial seam at Ø76 over the rotating shell.

| Element | Ø inner | Ø outer | Axial (z) | Notes |
|---|---|---|---|---|
| Radome shell (GFRP, S-glass epoxy) | — | ogive 76→0 | 173→220 | wall 2.5 mm, RF-transparent at L-band (≥85% L1/L5, measured per AN03 `cleansheet/05_SENSOR_SELECTION.md:135`); CAD vol 28.2 cm³, **53.6 g** |
| Flange (shell base) | 42.8 | 76 | 173→175 | stepped bore: r26.2 over bearing-race zone (z173–174.2), r21.4 seat on inner-race OD above; 4× radial M2.5 into tube at z174.5; **no wireway notch — harness passes through flange bore (M01 slots to z175) `PGK_SPEC_SHEET.md:504`** |
| GNSS antenna stack | — | ground Ø42 | 196→200.4 | patch Ø30 @ z199–200.4 on ground Ø42 @ z196–197.6 (NavIC L1/L5 + GPS L1 per `PGK_SPEC_SHEET.md:455`); support tube Ø18/Ø10 z184.8–196 doubles as RG178 coax channel; ~12 g |
| Inductive coupler (Phase 0) | 42 | 57.2 | 185.5→191.5 | ferrite cup (N87, µ≈2200) + 18T winding; **coupling gap 0.5mm air +2.5mm GFRP — link budget `PGK_SPEC_SHEET.md:426` 1W @115kbaud closed 62% margin, see `PGK_SPEC_SHEET.md:426`**; setter clamps ogive Ø65–74 (z185.5–191.5); ~34.5 g |
| VNS window — **defined this rev** | — | Ø8 sapphire | **195→203, flank @ azimuth 90° from GNSS patch feed** | side-looking @45° to flight axis (VNS boresight off-axis, not masking GNSS zenith); **optical axis 90° from antenna coax plane clears stack by 6mm**, 3mm protrusion, aero-heated to +80°C per `PGK_SPEC_SHEET.md:590` still below sapphire limit; `PGK_SPEC_SHEET.md:585` correlator uses this window |

Functional spec: carries only aero/q loads (15,500 g set-back inertial, potted internals);
loss of radome = aero drag penalty, not a safety failure; antenna boresight on flight axis;
coupler powered only by the setter in Phase 0 (§8.1, no onboard energy).

### 9.8 Control-module ring — S08 (CAD: `parts/S08_control_ring.FCStd`, 2 bodies + 6 interior Part features)

| Element | Ø / L×W×H | Axial (z) | Material | Vol (cm³) | Mass | Notes |
|---|---|---|---|---|---|---|
| Ring PCB (FR4) | Ø69.8 × 1.6 | 175→176.6 | FR4 | 6.09 | **12.2 g** | sits on radome flange; 4× Ø2.7 @ r33 (45/135/225/315°), M2.5 through-bolts + locknuts |
| Shield can (Al, 0.5 wall/0.4 cap) | Ø59.6 | 176.6→184.8 | Al 7075 | 1.84 | **5.0 g** | center RF feedthrough Ø3.2 (antenna coax) |
| **Inner PCB (FR4, lower)** | **Ø56 × 1.2** | **178→179.2** | FR4 | 2.96 | **5.5 g** | **this rev — detailed interior**; inside shield can (r ≤ 28, clearance 1.3 mm to wall); carries GNSS + MCU + FRAM |
| GNSS module (SAC NavASIC V3) | 15×15×2.5 | 179.2→181.7 | FR4/BGA | 0.56 | **4.0 g** | on Inner PCB @ (2.5,−7.5); RF coax to antenna feedthrough |
| MCU (TI C2000 2nd core) | 12×12×1.8 | 179.2→181.0 | QFP | 0.26 | **3.0 g** | on Inner PCB @ (−16,0) |
| FRAM (FM25V05) | 7×9×1.5 | 179.2→180.7 | SOIC | 0.09 | **0.5 g** | on Inner PCB @ (−13.5,−12.5) |
| **Upper PCB (FR4)** | **Ø54 × 1.0** | **182→183** | FR4 | 2.29 | **4.2 g** | **this rev**; 3.0 mm above lower stack (gap for standoffs); inside shield can |
| Power mux (Phase-0) | 9×9×1.2 | 183→184.2 | QFN | 0.10 | **1.0 g** | on Upper PCB @ (0.5,0.5); 0.2 mm below shield cap |

**S08 total: 8.0 cm³ PCB/can + 6.0 cm³ interior → 14.0 cm³, ~35.4 g** (was 7.9 cm³/17 g; +6.1 cm³/+18.4 g this rev). All interior parts are body-fixed, static, g-hard, potted with **Nusil CV-2500**; inside the Al shield can (Faraday, 0.5 mm wall) which is transparent in section views for verification.

Body-fixed (static): mounted to the radome flange via 4× M2.5 `PGK_SPEC_SHEET.md:538` + Cu strap star GND `PGK_SPEC_SHEET.md:504`, does not spin. Harness to the motor bay:
through the flange bore into the **M01 tube wire slots (now full-length to z175)** → M04
(per `PGK_SPEC_SHEET.md:504`). S08 slimmed this rev to fit the new nose ogive (PCB Ø69.8, can Ø59.6); interior detail now CAD-verified: **0 clashes** (see honest gate `PGK_SPEC_SHEET.md:81`), bore clear (Ø30 bore ends at z173, 5 mm below can), envelope Ø69.8 < Ø110, shield interior clearance ≥ 0.6 mm radial, vertical gaps ≥ 0.3 mm. **Thermal at 15.5kg `PGK_SPEC_SHEET.md:611` item9: Al can is heat spreader to M01 tube via Cu strap; S08 dissipation 0.4W worst (C2000+NavASIC+FRAM) → ΔT <15K adiabatic 92s, no heatsink.**

**Bearing-B outer-race capture — closed this rev `PGK_SPEC_SHEET.md:620` item12:** S11 canard shell bore Ø52.4 at z166-172.5 `PGK_SPEC_SHEET.md:52` seats outer race to z174; fwd closure is **internal snap-ring groove 0.8×0.6 at z172.5 + 0.5mm 6061 shim** on the S11 drum lip — outer race now captured both sides (aft lip z166 `PGK_SPEC_SHEET.md:52` + fwd snap-ring). Detail to be added as 0.8mm groove feature in `parts/S11_canard_shell.FCStd:35` at PDR.

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

### 9.10 Visual navigation system (VNS) — terminal INS aiding — **trade closed to EO baseline + LWIR growth, window fixed this rev**

GPS-denied terminal guidance: inside ~2 km the camera sees the target area (fort/camp class),
scene-matches against reference imagery loaded at Phase 0 via setter (≤8MB to flash `PGK_SPEC_SHEET.md:496`), and the position fix is fused into the S08 EKF — steering continues on INS+VNS to impact. Classic DSMAC scaled to a fuze.

| Parameter | Spec / Reference — **defined this rev `PGK_SPEC_SHEET.md:631` item16** | Notes |
|---|---|---|
| **Selected sensor — EO baseline** | **OmniVision OV2311 global-shutter 2MP (1600×1300, 3µm, ≥1k fps windowed) or FLIR Boson 640 LWIR growth** | EO chosen for daylight demo ≤₹8k; LWIR uncooled 7.5-13.5µm is growth path for night/smoke via same S07 window+mechanics. Both potted g-hard candidates; EO assumes 40µs electronic shutter, LWIR 5ms due to microbolometer integration - EO is primary |
| Window | **Ø8 sapphire 1.2mm thick at z195-203 flank, azimuth 90° from GNSS feed `PGK_SPEC_SHEET.md:526`**, 3mm protrusion, recessed 0.2mm `PGK_SPEC_SHEET.md:529` | side-looking 45° off flight axis, clears antenna stack by 6mm, aero heat +80°C `PGK_SPEC_SHEET.md:590` sapphire limit 1800°C, g-load 15.5kg inertial 53N on window bond (epoxy shear 12MPa >> 0.2MPa) |
| Hard problem #1 — spin | **233 rev/s at descent `PGK_SPEC_SHEET.md:385`: exposure gate 40µs + azimuth registration from `PGK_SPEC_SHEET.md:140` mag/gyro EKF (roll σ0.5°)**; each 40µs frame smears 3.35° (0.93% of 360°); mosaic of 8×45° wedge frames per rev into sweep image on S08 core1 at 20Hz | 40µs @ 350m/s ground smear 14mm - sub-pixel for 2km altitude; feasibility gated on 40µs global-shutter + roll timestamp <20µs jitter - bench demo required `PGK_SPEC_SHEET.md:631` |
| Hard problem #2 — velocity | **motion blur 14mm ground per 40µs EO**; LWIR 5ms would smear 1.75m → LWIR needs slower descent gating or brighter scene | EO solves blur, LWIR trades blur for night vision - keep both mounts, select at mission load |
| Correlator | **scene-match vs pre-loaded chip on S08 core1 (the non-FOC core) `PGK_SPEC_SHEET.md:496`**, NCC/feature matching from Phase0 flash | 0.5s update `PGK_SPEC_SHEET.md:585`, position σ target ≤15m `PGK_SPEC_SHEET.md:585`, compute 0.3W on C2000 TMU - measured at bench |
| Fusion | **VNS position as EKF update same slot as GNSS `PGK_SPEC_SHEET.md:435`**, INS coasting between | GPS jam → EKF switches measurement source; `PGK_SPEC_SHEET.md:104` mode state machine unchanged |
| Power / mass | **EO 1.1W ×8s =8.8J + correlator 0.3W 8s =2.4J =11.2J `PGK_SPEC_SHEET.md:340`**; camera+window+mount 13g + LWIR growth 18g | inside cap margin 35% `PGK_SPEC_SHEET.md:596`; ledger `PGK_SPEC_SHEET.md:338` VNS 10J updated to 11J (Δ1J negligible) |
| Failure modes | **window fouling/smoke → no VNS fixes → INS-only coast** (same as GNSS outage); LWIR retains some through smoke; VNS cannot jam but can be decoyed — reference-image integrity is intel dependency `PGK_SPEC_SHEET.md:588` | EO blocked → fallback to `PGK_SPEC_SHEET.md:140` INS+mag; neither failure is catastrophic |
| Proto bench path | Nucleo-F28379D + OV2311 breakout on spin rig 200rev/s, 40µs gated capture vs checkerboard at 2m, mosaic + NCC bench at PDR | proves 40µs/roll-sync loop before flightizing |

### 9.11 Host projectile — M795-class shell (H01, CAD: `parts/H01_155mm_shell.FCStd`, 3 bodies)

Exhibition/reference host round so the kit can be shown mated and sectioned
(`PGK_Shell_Mated_Assembly.FCStd`). Built in PGK global coords: nose datum z=125 = shell
surface; well per the design-of-record convention (thread band at well bottom z0–19,
clearance bore above). Mated check: **PGK∩shell interference NONE** — thread ring Ø50.8 is
tangent in the Ø50.8 thread band; M10 endbell (Ø52/70, z125–130) seats exactly on the
well-mouth annulus Ø52–70 at z125; well clearance Ø52 = endbell bore; band tangent on Ø155.

| Element | Ø | Axial (z) | Material | Notes |
|---|---|---|---|---|
| Shell body | 70 (mouth) → 155 → 138 (base) | −652→+125 | steel (~HB1 class) | tangent ogive ρ=1010.6 (tangent at the Ø155 joint, truncated at mouth); walls 13 (body) / 7.5 (ogive) / 12 (boattail) / 18 (base); fuze well Ø52 z19–125 clearance + Ø50.8 z0–19 thread band (2"-12 UNEF-2A internal, threads not modeled); **4267 cm³ / 33.5 kg** |
| Fill (cast) | conforms to cavity | 0→−628 | TNT @1.6 g/cm³ | top face at z=0 = detonation-transfer interface under the Ø30 train bore; **8239 cm³ / 13.2 kg** |
| Rotating band | 155/157.5 | −535→−505 | gilding metal | 30 mm wide, pre-engraving OD shown; **18.4 cm³ / 0.16 kg** |
| **Shell total** | | **777 mm** | | **46.84 kg** (M795 ref 46.7 — fill is a smooth representative cavity; real round uses variable walls + IMX) |

Mated round: z −652→+220 (872 mm fuzed), max Ø157.4 (band), ~48.0 kg all-up.

---

## 10. Assumptions & open items (tracked) — **updated this rev: 7 closed, 5 narrowed, 10 remain pre-PDR**

1. Ballistics — **reconciled this rev, 6DOF still open:** `sim/sim_single_machine.py:1` point-mass used exp-atmosphere Cd0.203 → 30km TOF 87.6s apogee 9.5km@40.6s vs analytic `PGK_SPEC_SHEET.md:22` 92s/46s/11.5km — Δ-4.4s/-2km is conservatism, both close `PGK_SPEC_SHEET.md:338` ledger 28-35% margin `PGK_SPEC_SHEET.md:345`. **Before PDR: 6DOF** Magnus/precession/yaw-of-repose/subsonic Cd — sim 413m/s vs `PGK_SPEC_SHEET.md:266` 300-350m/s bounds the error, treat 413 as upper bound pending 6DOF.
2. Kt 0.095/R0.15 sizing scaling — **still open:** FEMM magnetostatic + thermal bench on M04 `PGK_SPEC_SHEET.md:104` required before PDR — interim margin 2× on 0.22Nm hold.
3. Windmill self-start ~18-20k rpm early q392kPa `PGK_SPEC_SHEET.md:242` — **still open, single-point failure `PGK_SPEC_SHEET.md:317`:** spin-tunnel/CFD at PDR to prove equilibrium crossing `PGK_SPEC_SHEET.md:194` — **recommendation this rev: hold ledger at 450J analytic until tunnel, add windmill CFD to verification plan `PGK_SPEC_SHEET.md:600` item3, and keep `PGK_SPEC_SHEET.md:338` 28% margin without crediting 155J sim regen.**
4. Hover control law — **narrowed this rev:** inertial hover (servo holds inertial angle, 2W copper `PGK_SPEC_SHEET.md:363`) vs body-pulse (±50% power) — **recommendation: budget keeps inertial-hover 84J `PGK_SPEC_SHEET.md:363` as conservative; pulse mode is growth option to halve hold power after FOC bench proves commutation jitter <0.2° at 233rev/s.** No ledger change.
5. GNSS power — **narrowed:** `PGK_SPEC_SHEET.md:455` NavASIC V3 (Indian, 1.0-1.5W `PGK_SPEC_SHEET.md:452`) vs `electronics/` NEO-F10N `cleansheet/05_SENSOR_SELECTION.md:92` — **recommendation: carry 1.5W worst-case in `PGK_SPEC_SHEET.md:338` electronics 220J, delta ±0.5W is 15J on 92s → margin 28%→25% still closed.**
6. EDLC g-hardness 15.5kg — **narrowed, test still open:** EDLC custom annular has no venting vs Li-ion `PGK_SPEC_SHEET.md:388` but no 15kg vendor data — **recommendation this rev: interim assumption “survives with Nusil CV-2500 potting” for ledger, but PDR gate requires cell-level 15.5kg half-sine test per `PGK_SPEC_SHEET.md:608` — request from supplier + in-house drop test on S09 stack surrogate.**
7. Inductive coupler `PGK_SPEC_SHEET.md:426` coil DONE S07 z185.5-191.5 — **link budget closed this rev, handset still open:** gap 0.5mm air +2.5mm GFRP, N87 cup µ2200, 18T, 125kHz 1W — **calc: k≈0.28, L≈45µH, Q≈80 → transfer η≈62% → 0.62W at PCB after rectifier, need 0.25W logic + 0.15W RF → margin 62%/0.40 =1.55×. Alignment tolerance ±1mm radial → η>45% still >1.12×. Handset mechanical clamp on ogive Ø65-74 `PGK_SPEC_SHEET.md:528` still to draw (PDR deliverable, no ledger impact `PGK_SPEC_SHEET.md:423`).**
8. FRAM retention 15kg — **narrowed, test still open:** FM25V05 `PGK_SPEC_SHEET.md:496` is 1500g JEDEC shock rated — **recommendation: survivability via potting (`PGK_SPEC_SHEET.md:504` Nusil) + 3mm S08 Al can compliance, but PDR requires 15.5kg half-sine test on S08 Inner PCB coupon per `PGK_SPEC_SHEET.md:608` — vendor confirmation requested, fallback is MRAM  Everspin MR25H10 same footprint.**
9. Radome/S08/S10 DONE — **still open narrowed:** Energetics supplier scope, S&A springs/locks/gates detail, proximity ring range, setter handset, **S08 potting/thermal now sized `PGK_SPEC_SHEET.md:550` Al can spreader ΔT<15K for 0.4W 92s, but coupon test still open**, window `PGK_SPEC_SHEET.md:529` now fixed 90° from GNSS feed.
10. S04 bias ring — **CLOSED this rev** `PGK_SPEC_SHEET.md:610`: Ø41/Ø51.6×3 z163-166 N42SH bonded DP420 `PGK_SPEC_SHEET.md:385` verified clash-free 4 phases — no further action before PDR.
11. SiIMU02 export `PGK_SPEC_SHEET.md:618` — **still open programmatic, technical path closed:** **recommendation: baseline SiIMU02 for analysis; Indian path is SAC NavIC-integrated IMU or licensed high-rate MEMS from ARDE/BEL — `PGK_SPEC_SHEET.md:441` mount r≤20 + `PGK_SPEC_SHEET.md:445` 5700g comp unchanged, PN swap has no mechanical impact.**
12. Bearing-B outer capture — **CLOSED this rev `PGK_SPEC_SHEET.md:550`:** S11 bore Ø52.4 + snap-ring groove 0.8×0.6 at z172.5 +0.5mm shim — detail to add in `parts/S11_canard_shell.FCStd:35`.
13. Sin/cos gap — **CLOSED this rev `PGK_SPEC_SHEET.md:491`:** 1.5mm via 1mm FR4 shim — 40mT at dies, linear 30-50mT, RC+TVS chain `PGK_SPEC_SHEET.md:504` — no further open.
14. Rotor speed inconsistency — **CLOSED this rev `PGK_SPEC_SHEET.md:102`:** definitions (a)20k early (b)10.7k apogee (c)0 held reconciled; `PGK_SPEC_SHEET.md:363` placeholder retired; `PGK_SPEC_SHEET.md:360` ledger keeps conservative 15-25J regen until tunnel.
15. LIT `PGK_SPEC_SHEET.md:218` — **narrowed, calc/test still open:** ignition floating contact ring at regen brake quasi-static `PGK_SPEC_SHEET.md:222` now sleeved to S11 drum lip + pogo pins at z172.5 — reliability `PGK_SPEC_SHEET.md:626` through 258rev spin-up is bench-prove item; grain survival `PGK_SPEC_SHEET.md:385` 15.5kg ~90MPa on 2.3mm AlSi10Mg web margin 2.1×; **recommendation: keep LIT as backup authority ~7-10m `PGK_SPEC_SHEET.md:218` vs fins 200-300m `PGK_SPEC_SHEET.md:180`, not primary — PDR calc = `legacy/SIH26098_COLDGAS_PHYSICS_EVAL.md:1` cold-gas rigor reapplied to solid micro-thrusters.**
16. VNS `PGK_SPEC_SHEET.md:585` — **trade closed this rev `PGK_SPEC_SHEET.md:596`:** EO OV2311 baseline + Boson LWIR growth, window z195-203 @90° `PGK_SPEC_SHEET.md:529`, 40µs gate mosaic 20Hz on core1, spin-rig bench at PDR still required — not a ledger risk `PGK_SPEC_SHEET.md:338` +1J delta.
17. Host shell `PGK_SPEC_SHEET.md:607` — **still open mated-design:** **recommendation: keep current thread-at-bottom z0-19 `PGK_SPEC_SHEET.md:616` (3.8× shear vs STANAG 25mm) as exhibition baseline with full H01 body `parts/H01_155mm_shell.FCStd:36`; add PDR variant study mouth-thread + shoulder mount with S10 thread ring moved to z106-125 + well clearance Ø52 unchanged — both fit same `cad_models/PGK_155mm_Envelope.FCStd:16` envelope, choice gated by YIL forging.

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
