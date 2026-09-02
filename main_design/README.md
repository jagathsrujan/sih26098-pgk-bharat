# Main Design — PPT Prep Bundle

**Purpose:** one folder with everything belonging to the CURRENT main design (single
time-share machine, no battery, no cold gas) so presentation content can be generated
without hunting the repo. Assembled 2026-09-02.

**Status of these copies:** SNAPSHOT for reference only. The canonical originals stay in
place — `cad_models/PGK_SPEC_SHEET.md` is the design of record; edit there, then re-copy.
(CAD files were copied, not moved: the parametric assembly uses relative `App::Link`s into
`cad_models/parts/`, so moving them would break the source assembly.)

---

## 1. What is in here

| Item | File | Canonical original |
|---|---|---|
| **Master spec (design of record)** | `PGK_SPEC_SHEET.md` | `cad_models/PGK_SPEC_SHEET.md` |
| CAD conventions + file inventory | `CAD_README.md` | `cad_models/README.md` |
| Mated round (shell + PGK, self-contained, section groups) | `design_CAD/PGK_Shell_Mated_Assembly.FCStd` | same |
| Flattened PGK assembly (25 bodies) | `design_CAD/PGK_Full_Assembly.FCStd` | same |
| Parametric source assembly | `design_CAD/PGK_Motor_Assembly.FCStd` | same |
| Design envelope (zones, datum z=125) | `design_CAD/PGK_155mm_Envelope.FCStd` | same |
| Part files ×15 (current design only) | `design_CAD/parts/` (S01–S11, M01/M04/M09/M10, H01 shell) | `cad_models/parts/` |
| Trajectory + energy sim (results) | `simulation/RESULTS_SINGLE_MACHINE.md` | `sim/` |
| Trajectory + energy sim (script) | `simulation/sim_single_machine.py` | `sim/` |
| Renders for slides | `renders/complete_iso.png`, `renders/sec_half_front.png`, `renders/sec_quarter_iso.png` | generated from the mated assembly |
| KiCad GNC skeleton (prior lineage) | `electronics_kicad_reference/` (gnc_board + power/mcu/sensors/comms sheets, ERC report, netlist) | `electronics/` |

**Excluded on purpose (not current design):** `M02/M03/M05–M08` parts (dual-rotor trade
study — superseded), `cleansheet/` (Rev 1.7 battery+slip-ring architecture — reference
only), `legacy/` (cold gas — rejected by calculation), root BOMs (dated from the prior
design — resync before reusing any line item), `PGK_155MM_ASSEMBLY.md`/`out_pgk/`
(earlier exhibition model).

**Electronics caveat:** the KiCad skeleton is the prior lineage's board architecture —
keep it for schematic style / part library only. The CURRENT electronics design of record
is spec sheet §9 (sensor & electronics stack): NavIC/GNSS + IMU classes (§9.2–9.5),
stator PCB M04 + control ring S08, sin/cos angle array, magnetometer roll module (§9.5),
stack wiring map (§9.6), fuze electronics (§9.9).

## 2. Design in one line

Single 12s10p annular PMSM inside a 2"-12 UNEF fuze kit for 155mm: ascent = windmill
generator charging an annular supercap (875 J); apogee = regen brake + software mode
switch; descent = the same machine servo-holds 4 mirror-pitched fins (±12°) for terminal
course correction. No battery. No cold gas. Ø30 through-bore keeps the explosive train
untouched.

## 3. PPT content map (spec sheet section → slide)

| # | Slide | Content source | Key numbers to quote |
|---|---|---|---|
| 1 | Problem & solution | AGENTS.md one-liner; §1 | 47.9 kg round, 30 km, CEP need |
| 2 | Mission profile | §1, §2.6 | 800 m/s muzzle, 15,480 rpm spin, TOF 92 s, apogee ~46 s |
| 3 | Architecture — one machine, two roles | §2 + §2.3 diagram | ascent generator ⇄ descent actuator, software mode switch |
| 4 | Motor design | §2.1, §2.2 | 12 slots/10 poles, Ø40–70 ring, 25 mm active zone, Kt 0.095 N·m/A, EMF 150–200 V |
| 5 | Power architecture | §2.3 | same 3 half-bridges: active rectifier ⇄ FOC inverter; 54 V bus |
| 6 | Energy ledger | §4 | stored 875 J, consumed ~344 J, ~28% margin; sim: 412 J generated |
| 7 | Storage | §5 | annular EDLC 0.6 F @ 54 V, Ø49/31 × 30 mm, 67 g, charged in flight |
| 8 | Control effectors | §2.5, §7 | 4 fins ±12°, lateral force 15–25 N, authority 200–300 m, hold torque 0.2–0.25 N·m |
| 9 | LIT thruster add-on (optional slide) | §2.7 | 8 stations, ~8.4 N·s set, ~7–10 m trim |
| 10 | GNC & sensors | §9.1–9.5, §9.6 | NavIC L1/L5 + GPS, ±25,000°/s roll gyro, RM3100-class mag @ ≥2 kHz, EKF fusion |
| 11 | Electronics stack | §9.6, §9.8, M04/S08 | control ring PCB Ø69.8 z175–184.8, shield can, stack wiring map |
| 12 | Safety & fuze | §9.9, §2.6 | S&A slider (out-of-line SAFE), inertia switches, Ø30 train bore reserved |
| 13 | Gun-launch survival | §2.6, §10 | 13,400–15,500 g set-back, 100 kN·m spin-up, no battery = no chemistry |
| 14 | CAD — mated round | `renders/*.png`, `PGK_Shell_Mated_Assembly.FCStd` | 0 clashes, Ø108 max PGK in Ø155, ~1.18 kg kit on 46.84 kg shell |
| 15 | Simulation results | `simulation/RESULTS_SINGLE_MACHINE.md` | 30 km closed, Cd 0.203, guided CEP 28.5 m vs 196 m unguided (7×) |
| 16 | Validation status & honesty | §10 | open: 6DOF, FEMM Kt check, windmill self-start test, EDLC g-hard data |
| 17 | Roadmap / team | root `README.md`, `TEAM_STRUCTURE.md`, liveboard | — |

## 4. Slide-image checklist (export from CAD before the deck)

- [ ] `renders/complete_iso.png` — full mated round (have)
- [ ] `renders/sec_half_front.png` — half section (have)
- [ ] `renders/sec_quarter_iso.png` — quarter section iso (have)
- [ ] Exploded stack view (export later from `PGK_Full_Assembly.FCStd`)
- [ ] Rotor close-up with magnets + bias ring (from `PGK_Full_Assembly.FCStd`, rotor phase 0/90/180/270)
- [ ] Fin cant geometry (S05/S06 pairs) for the steering slide
