# SIH26098 Clean-Sheet PGK — Detailed BOM, Manufacturing, Costing & Assembly
**Doc:** `cleansheet/02_BOM_MANUFACTURING_ASSEMBLY.md` | **Rev:** 1.1 | **Basis:** `PGK_CleanSheet.FCStd` (as-built dimensions) | **Currency:** INR

---

## A. Assembly tree (frames marked)

> **Rev 1.1 status:** this tree is now **implemented as a native FreeCAD Assembly** inside `PGK_CleanSheet.FCStd` — 24 links, 21 Fixed joints + 2 Revolute (`J_MotorRotor`, `J_RollDecouple`) + Ground, and a playable kinematic **Simulation** (122 frames @ 30 fps: rotor +180°/s, nose −60°/s). See `03_DESIGN_REPORT.md` §2.4.

```
PGK MODULE (screws into 155mm shell fuze well)
│
├── [SHELL FRAME — spins 250 rev/s]
│   ├── A1  Bearing Outer Ring (threaded)  ← threads into well, torque anchor
│   ├── A2  Shear Pin Set 4×               ← cartridge↔outer ring  [REQ — modeled pending]
│   ├── A3  Core Cartridge (pinned to A1)
│   │   ├── battery bay: A3.1 Li-ion cell + A3.2 contact set
│   │   └── ignitor bay: A3.3 Initiator interface (INERT; flight: partner ESAF)
│   ├── A4  Outrunner Stator (lam stack + windings + leads)
│   ├── A5  Power Board (rectifier/supercap/buck, S&A gate)
│   └── A6  Pilot Stub Shaft
│
├── [BEARING] B1 Outer ring ⇄ balls+cage ⇄ B2 Inner ring  (de-spin joint)
│
├── [ROTOR FRAME — held at roll angle ψ]
│   ├── B2  Bearing Inner Ring
│   ├── B3  Retention Lip (axial catch)    [REQ — modeled pending]
│   ├── C1  Canard Shell, one-piece 7075 (cap+skirt+4 fins, trimmed pair ±3°)
│   ├── C2  Pilot Bearing (bell support)
│   ├── C3  Slip Ring, 3-contact axial (dome power)
│   ├── D1  Radome (translucent in CAD = GFRP part)
│   ├── D2  Dome Base Ring
│   ├── D3  GNC Board (MCU+IMU+mems)
│   ├── D4  GNSS/NavIC patch + module
│   ├── D5  Proximity head (FMCW)
│   └── D6  Magnet Ring (on bell)  +  Bell/rotor yoke  +  Hall sensors ×3 (stator)
```

---

## B. Bill of Materials

### A. Core & power (shell frame)

| # | Part | Qty | Material | Key dimensions (mm) | Mass | Manufacture | Finish/QA | Cost proto | Cost @1k |
|---|------|-----|----------|---------------------|------|-------------|-----------|-----------|----------|
| A1 | Bearing outer ring, threaded | 1 | 100Cr6 (or 440C) | OD 50.7 male 2-12UN-2A × 90 long; race bore Ø43.0 H6; wall grooves 24×R2 | 320 g | CNC turn (thread + race in one setup), race grind after HT 60±2 HRC | Ra0.4 race, thread Go/No-Go, 100% MPI | ₹7,500 | ₹1,400 |
| A2 | Shear pin set | 4 | 4340 or 2024-T4 (calibrated) | Ø3 × 8 | 3 g | Centerless grind to h7, shear-load lot-tested 4–6 kN | Lot cert | ₹800 | ₹120 |
| A3 | Core cartridge | 1 | 7075-T6 | OD 31.6 g6 journal × 90; bay Ø25.6 × 54; collar Ø40 × 16 | 127 g | CNC turn-mill, one setup; y80 journal polish | Eddy-current, dim report | ₹6,500 | ₹1,200 |
| A3.1 | Li-ion cell 26500 high-drain | 1 | NMC (Molicel P45B class) | Ø26 × 50 (bay bored 26.2) | 68 g | Buy | 15k g qual cert req.; 45 A rating | ₹1,100 | ₹650 |
| A3.2 | Contact set + bus | 1 | BeCu/Au plated | — | 8 g | Stamp/form | Contact res <10 mΩ | ₹350 | ₹90 |
| A3.3 | Initiator interface (inert demo) | 1 | Al + dummy pad | Ø25 × 22 + Ø6 boss | 10 g | Turn | Label "INERT" | ₹400 | ₹120 |
| — | *(Flight: partner ESAF + qualified initiator replaces A3.3)* | 1 | — | per partner spec | ~60 g | Buy (ECIL/BEL) | STANAG 4187 cert | — | *(₹25–40k)* |
| A4 | Stator laminated core | 1 | M350-50A laminations | Ø45–73.4, stack 16, 24 teeth | 150 g | Laser/progressive die lam stack, bonded | burr <0.02 | ₹22,000 | ₹4,800 |
| A5 | Windings 3-phase (24 coils) | 1 | Cu AWG22, class H | slot fill ~45%, star | 38 g | Winding machine + insertion | surge test, R match ±3% | ₹9,000 | ₹1,800 |
| A6 | Power board | 1 | FR4-TG170, 4-layer | Ø62 round | 30 g | SMT 0402+ | AOI, ICT | ₹5,500 | ₹1,500 |
| A7 | Supercap 15 F / 10 V | 1 | — | Ø13.5 × 12 (×2 ∥) | 22 g | Buy | ESR <30 mΩ | ₹900 | ₹350 |
| A8 | Pilot stub shaft | 1 | 440C, 52 HRC | Ø20.4 g6 × 12 | 12 g | Turn/grind | Ra0.2 | ₹1,400 | ₹380 |
| A9 | Hall sensors ×3 | 3 | SS461C class | SOT-89 | 2 g | Buy | — | ₹150 | ₹45 |
| A10 | Fasteners, potting, threadlocker | — | — | — | 25 g | — | pot: Araldite CT200/HT9517 | ₹1,800 | ₹500 |

### B. Bearing & rotor frame

| # | Part | Qty | Material | Key dimensions | Mass | Manufacture | Finish/QA | Cost proto | Cost @1k |
|---|------|-----|----------|----------------|------|-------------|-----------|-----------|----------|
| B1 | *(A1 doubles as outer race side — balls ride A1 bore + B2 OD grooves)* | — | — | balls Ø3, 160 pcs, 10 rows × 16 | 9 g | Buy G10 chrome (opt. Si₃N₄ hybrid) | grade 5 | ₹1,600 | ₹420 |
| B2 | Bearing inner ring | 1 | 100Cr6 | Ø37 race OD (grooved), bore Ø32 H6 × 90, **retention lip** [REQ] | 182 g | CNC turn, grind | Ra0.4 | ₹5,800 | ₹1,100 |
| B3 | Retention lip | *(B2 integral)* | — | lip ID Ø29.6 × 2 | — | with B2 | — | — | — |
| C1 | Canard shell, one-piece | 1 | 7075-T6 billet | cap Ø89 × 4; skirt Ø84–89; fins Δ24×24.5×3, tip Ø138, pair trim ±3°; blends R3 | 155 g | 5-axis mill from billet, 2 setups | CMM on fin clocks, bal. <0.5 g·cm | ₹22,000 | ₹4,800 |
| C2 | Pilot bearing (bell) | 1 | hybrid 61804-class | Ø20.8/24.7 × 2.6 | 8 g | Buy | — | ₹2,400 | ₹850 |
| C3 | Slip ring, 3-contact axial | 1 | Au alloy | Ø12 × 4, 3 rings | 8 g | Buy micro-slip | mΩ-class | ₹2,200 | ₹700 |
| C4 | Rotor yoke/bell note | — | *(bell yoke is part of magnet carrier — see C5/flight note)* | Ø76.4–83 × 22 | ~140 g | CNC turn | — | ₹8,500 | ₹2,200 |
| D6 | Magnet ring, 24→12 poles (flight EM) | 1 | NdFeB N42SH, radial 0.85 | Ø74.7–76.4 × 15 | 23 g | Wire-EDM segments, potted | flux-map ±3% | ₹4,200 | ₹1,300 |

### D. Dome / sensor stack (rotor frame)

| # | Part | Qty | Material | Key dimensions | Mass | Manufacture | Finish/QA | Cost proto | Cost @1k |
|---|------|-----|----------|----------------|------|-------------|-----------|-----------|----------|
| D1 | Radome | 1 | Glass-epoxy (GFRP E-glass) | semi-ellipsoid Ø84 × 49.6, wall 2 | 44 g | Hand-layup/wet filament wound on mandrel, CNC trim | RF transmission ≥85%, boil test | ₹8,000 | ₹2,200 |
| D2 | Dome base ring | 1 | 6061-T6 | Ø76–84 × 1.7 | 10 g | Turn | — | ₹600 | ₹150 |
| D3 | GNC board | 1 | FR4 4-layer Ø62 | STM32G474 + ICM-42688 + flash | 35 g | SMT | ICT + functional | ₹9,500 | ₹3,200 |
| D4 | GNSS patch + module | 1 | ceramic patch + L1/L5 M9N-class | Ø25 patch | 15 g | Buy | C/N₀ test | ₹5,200 | ₹2,600 |
| D5 | Proximity head | 1 | FMCW 24 GHz module + patch | Ø30 × 8 | 25 g | Buy + integ | HOB bench 6/12/18 m | ₹4,800 | ₹1,900 |

### Ground support (non-airborne, shared)

| # | Part | Qty | Cost |
|---|------|-----|------|
| G1 | Inductive setter (EPIAFS-class, mock for demo) | 1 per gun | ₹60,000 |

**Not in BOM (flight):** energetics/boosters/explosive train — by YIL/partner, outside kit scope. **REQ items modeled pending in CAD:** A2 shear pins, B3 retention lip, C4 bell yoke ring, D6 pole-count change 24→12.

---

## C. Manufacturability highlights

| Part | Process risk | Mitigation |
|---|---|---|
| A1 outer ring | thread + thin race in one part; HT distortion | rough turn → HT → finish turn → grind race; thread after HT |
| A3 cartridge | thin 2.5 mm wall + journal concentricity | turn-mill single setup; checklist journal↔bay runout ≤0.03 |
| A4 stator | 24-slot lam stack bonding | bonded-stack fixture; deburr; slot-liner insertion |
| C1 canard shell | 5-axis fin clocks + balance | probe fin datum in-cycle; trim balance to <0.5 g·cm |
| D1 radome | wall 2 mm uniformity | wound on matched mandrel; ultrasonic thickness scan |

All parts are conventional CNC (turn, turn-mill, 5-axis mill, SMT, winding) — **no exotic processes**. YIL's existing turn/grind capacity covers A1–A3; BEL/ECIL class covers A4–D5.

## D. Costing & budgeting (INR)

**Unit cost rollup:**

| Build | Material+parts | Labor/overhead | ESAF partner | Ex-works |
|---|---|---|---|---|
| Engineering prototype (1) | ₹1,52,000 | ₹55,000 | — | **~₹2.1 L** |
| Pilot lot (25) | ₹58,000 | ₹22,000 | — | **~₹0.8 L** |
| Production (1,000) | ₹26,500 | ₹14,000 | ₹30,000 | **~₹0.7–0.9 L** |

**vs PS ceiling ₹8–11 L/kit → production ex-works lands at 8–12% of ceiling.** Headroom funds qualification, margin, and price aggression vs imports (M1156 ≈ ₹9–10 L).

**Program NRE budget (3-yr to qual):**

| Item | Cost |
|---|---|
| Simulation campaign (6DOF, Monte Carlo, aero CFD-lite) | ₹35 L |
| Bench rigs (de-spin/spin bench, HOB bench, drop/jolt) | ₹60 L |
| Env qual (MIL-STD-331 subset, temp/vibe/shock lab) | ₹80 L |
| Gun-fired qualification rounds (12–18 rounds ATAGS/Dhanush) | ₹1.6 Cr (rounds+range) |
| Flight software (FOC, GNC, S&A logic) | ₹60 L |
| Cert & docs | ₹25 L |
| **Total NRE ≈ ₹4.2 Cr** | amortized @10k units ≈ ₹4.2k/kit |

## E. Fitting & assembly

**Fit classes:**

| Interface | Fit | Spec |
|---|---|---|
| Cartridge journal ↔ inner-ring bore | running | Ø32 H7/g6 (25–50 µm) |
| Module thread ↔ well | installation | 2-12UN-2A/2B, anti-seize, **torque 50 N·m** |
| Stator bore ↔ collar | transition | Ø73.4 H7/js6 |
| Pilot bearing outer ↔ bell bore | press | H7/p6 (−2 to −19 µm) |
| Pilot shaft ↔ bearing inner | snug | js6/H7 |
| Magnet ring ↔ bell ID | bonded | 0.05 press + epoxy |
| Canard shell cap ↔ bell flange | bolted | 6× M3, 2.5 N·m + threadlocker |
| Shear pins A2 | press | Ø3 h7/H8, shear 4–6 kN each |

**Assembly sequence (with QA gates):**

1. QA well thread (Go/No-Go) → apply anti-seize
2. **Install A1** into well, torque 50 N·m, witness mark
3. Build bearing: press B2 retention lip check → load 160 balls + cage between A1 bore and B2 races → spin check (<0.5 N·m drag)
4. **Pin A3 cartridge** to A1 (4× A2 shear pins) — QA: pin shear test coupon from same lot
5. Fit battery A3.1 (contacts compress), ignitor pad A3.3 (label INERT)
6. Bolt stator A4 to collar; insert Hall sensors; connect windings → phase-resistance check
7. Fit A6 stub shaft, C2 pilot bearing, C3 slip ring
8. Bond D6 magnets into bell; fit bell over stator onto C2 → gap check 0.5 mm, spin by hand
9. Assemble dome stack (D3→D4→D5) on standoffs; bond radome D1 to base ring D2; fit to bell cap
10. **Bolt C1 canard shell** to bell flange (6× M3, 2.5 N·m); fin clock check vs datum
11. Setter G1 functional pass: continuity, S&A state machine, target upload
12. Final: mass ≤2.0 kg, length ≤276 mm, balance <0.5 g·cm

## F. Mass & SWaP rollup

| Group | Mass |
|---|---|
| Core + battery + power (shell frame) | 344 g |
| Bearing (rings + balls + cage) | 515 g |
| Actuator (stator + windings + magnets + shaft + bearing) | 470 g |
| Canard shell + dome + electronics | 445 g |
| **Module total** | **≈ 1.77 kg** (target ≤1.5 t / 2.0 hard → optimization note: A1 thin-wall + C4 Al-yoke-with-steel-sleeve saves ~280 g → **≈1.49 kg**) |
| Module length | 606→776 mm station span; protrusion above ogive ≈ 80 mm; total in-well+above ≈ 260 mm |

---

*Open/parked items carried in BOM as REQ: A2, B3, C4 flight yoke, D6 pole change, slip-ring size, ESAF partner.*
