# SIH26098 Clean-Sheet PGK — Detailed BOM, Manufacturing, Costing & Assembly
**Doc:** `cleansheet/02_BOM_MANUFACTURING_ASSEMBLY.md` | **Rev:** 1.4 | **Basis:** `PGK_CleanSheet.FCStd` (as-built dimensions) | **Currency:** INR
**Rev 1.2 change:** simulation-informed spec deltas (§G) — de-spin re-specced 15 s @ ≤40 A with boost stage, cold-rating QA added, mass/cost rollups updated.
**Rev 1.3 change:** sensor selection (§H) — GNC board IMU firmed to ICM-45686; **new line items D3b (angle sensor, MA732) and D3c (setback: armer interface + ADXL1004 signature)**; D4 firmed to NEO-F10N (NavIC L5 + GPS); D5 candidate PN K-LD7. Rollup +₹3,250 proto / +₹1,300 @1k. Evidence: `05_SENSOR_SELECTION.md` + `out_sim/RESULTS_SENSORS.md`.
**Rev 1.4 change:** electronics architecture (§I) — dual-domain split (decision 23, `06_ELECTRONICS_ARCHITECTURE.md`): **drive domain ICs added to A6** (G431 MCU, DRV8329 gate driver, 6× NVMFS5C460NL bridge set, 3× INA240A2 + 2 mΩ shunts, LDO/TVS), **D3 firmed** (STM32G474RET6 + W25Q128JVSIQ + rails TPS62933/TLV75730P/TLV7031), **D3b MA732 relocated** dome → collar-face (drive side; cost unchanged — the FOC commutation angle belongs to the drive MCU; GNC consumes the roll *estimate*, not the sensor). New-IC selections sourced in `research/06_electronics-embedded-power/entry_20260831_*.md` (8 entries); KiCad skeleton `electronics/gnc_board.kicad_pro` ERC-clean. Rollup +₹3,285 proto / +₹2,385 @1k; mass ≈ 1.88 kg.

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
│   │   ├── D3  GNC Board (MCU + IMU ICM-45686 + mems)
│   │   ├── D3b Angle sensor (MA732 + Ø6 magnet on bell)   [Rev 1.3 — new]
│   │   ├── D3c Setback sensor (armer interface + ADXL1004) [Rev 1.3 — new]
│   ├── D4  GNSS/NavIC patch + NEO-F10N module
│   ├── D5  Proximity head (FMCW, K-LD7 class)
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
| A3.1 | Li-ion cell 26500 high-drain | 1 | NMC (Molicel P45B class) | Ø26 × 50 (bay bored 26.2) | 68 g | Buy | 15k g qual cert req.; 45 A cont.; **≥55 A/15 s pulse at −40 °C, SoC ≥50 %** (de-spin duty, Rev 1.2) | ₹1,100 | ₹650 |
| A3.2 | Contact set + bus | 1 | BeCu/Au plated | — | 8 g | Stamp/form | Contact res <10 mΩ | ₹350 | ₹90 |
| A3.3 | Initiator interface (inert demo) | 1 | Al + dummy pad | Ø25 × 22 + Ø6 boss | 10 g | Turn | Label "INERT" | ₹400 | ₹120 |
| — | *(Flight: partner ESAF + qualified initiator replaces A3.3)* | 1 | — | per partner spec | ~60 g | Buy (ECIL/BEL) | STANAG 4187 cert | — | *(₹25–40k)* |
| A4 | Stator laminated core | 1 | M350-50A laminations | Ø45–73.4, stack 16, 24 teeth | 150 g | Laser/progressive die lam stack, bonded | burr <0.02 | ₹22,000 | ₹4,800 |
| A5 | Windings 3-phase (24 coils) | 1 | Cu AWG22, class H | slot fill ~45%, star | 38 g | Winding machine + insertion | surge test, R match ±3%; **adiabatic pulse ≤720 J (40 A/15 s) → ΔT ≤50 K** | ₹9,000 | ₹1,800 |
| A6 | Power board | 1 | FR4-TG170, 4-layer | Ø62 round + **de-spin boost stage 3.7→5 V / 55 A_out** | 38 g | SMT 0402+ | AOI, ICT | ₹6,300 | ₹1,700 |
| A7 | Supercap 15 F / 10 V | 1 | — | Ø13.5 × 12 (×2 ∥) | 22 g | Buy | ESR <30 mΩ; role: transient bridge + regen buffer (NOT the de-spin energy source — Rev 1.2) | ₹900 | ₹350 |
| A7b | De-spin brake chopper + dump resistor | 1 | FR4 + 15 Ω/50 W wirewound (collar-mounted) | — | 40 g | SMT + ME fit | thermal survey at 40 A/15 s | ₹1,400 | ₹400 |
| A6a | Drive MCU (Rev 1.4) | 1 | STM32G431CBT6 (LQFP48, 128K/32K) | 15 kHz FOC current loop on TIM1, MA732 SPI, chopper PWM | 1 g | Buy | — | ₹500 | ₹350 |
| A6b | 3-φ gate driver (Rev 1.4) | 1 | TI DRV8329AREER (36-WQFN) | 4.5–60 V — only mainstream smart driver regulating at the 5 V bus; bootstrap + trickle CP; HW-config | 1 g | Buy | — | ₹400 | ₹280 |
| A6c | Bridge FET set (Rev 1.4) | 6 | onsemi NVMFS5C460NL (40 V / 78 A / 4.5 mΩ, DFN5×6 wettable flank) | 2∥ per switch; conduction ≈5.4 W over the 15 s pulse (81 J) — QA thermal survey | 6 g | Buy | **thermal survey at 40 A/15 s (06 §4)** | ₹900 | ₹650 |
| A6d | Current sense (Rev 1.4) | 3+3 | TI INA240A2D + Vishay WSL2512 2 mΩ shunts | in-line per-phase, 20 V/V PWM-rejection CSA; 40 A → ~1.6 V span | 2 g | Buy | — | ₹550 | ₹490 |
| A6e | Drive logic rail + prot. (Rev 1.4) | — | LDO 5→3.3 V (TLV757P class) + SMAJ5.0A + USBLC6-2 | G431/INA240/MA732/DRV8329 logic; slip UART ESD both ends | 2 g | Buy | — | ₹150 | ₹95 |
| A8 | Pilot stub shaft | 1 | 440C, 52 HRC | Ø20.4 g6 × 12 | 12 g | Turn/grind | Ra0.2 | ₹1,400 | ₹380 |
| A9 | Hall sensors ×3 | 3 | SS461C class | SOT-89 | 2 g | Buy | — | ₹150 | ₹45 |
| A10 | Fasteners, potting, threadlocker | — | — | — | 25 g | — | pot: Araldite CT200/HT9517 | ₹1,800 | ₹500 |

### B. Bearing & rotor frame

| # | Part | Qty | Material | Key dimensions | Mass | Manufacture | Finish/QA | Cost proto | Cost @1k |
|---|------|-----|----------|----------------|------|-------------|-----------|-----------|----------|
| B1 | *(A1 doubles as outer race side — balls ride A1 bore + B2 OD grooves)* | — | — | balls Ø3, 160 pcs, 10 rows × 16 | 9 g | Buy G10 chrome (opt. Si₃N₄ hybrid) | grade 5 | ₹1,600 | ₹420 |
| B2 | Bearing inner ring | 1 | 100Cr6 | Ø37 race OD (grooved), bore Ø32 H6 × 90, **retention lip** [REQ] | 182 g | CNC turn, grind | Ra0.4 | ₹5,800 | ₹1,100 |
| B3 | Retention lip | *(B2 integral)* | — | lip ID Ø29.6 × 2 | — | with B2 | — | — | — |
| C1 | Canard shell, one-piece | 1 | 7075-T6 billet | cap Ø89 × 4; skirt Ø84–89; fins Δ24×24.5×3, tip Ø138, pair trim ±3°; blends R3 | 155 g | 5-axis mill from billet, 2 setups | CMM on fin clocks; **trim incidence ±0.2°, edge bevel ±0.1 mm** (aero-consistency, Rev 1.2); bal. <0.5 g·cm | ₹22,000 | ₹4,800 |
| C2 | Pilot bearing (bell) | 1 | hybrid 61804-class | Ø20.8/24.7 × 2.6 | 8 g | Buy | — | ₹2,400 | ₹850 |
| C3 | Slip ring, 3-contact axial | 1 | Au alloy | Ø12 × 4, 3 rings | 8 g | Buy micro-slip | mΩ-class | ₹2,200 | ₹700 |
| C4 | Rotor yoke/bell note | — | *(bell yoke is part of magnet carrier — see C5/flight note)* | Ø76.4–83 × 22 | ~140 g | CNC turn | — | ₹8,500 | ₹2,200 |
| D6 | Magnet ring, 24→12 poles (flight EM) | 1 | NdFeB N42SH, radial 0.85 | Ø74.7–76.4 × 15 | 23 g | Wire-EDM segments, potted | flux-map ±3%; **demag margin check at −40 °C @ 40 A** (risk R2, Rev 1.2) | ₹4,200 | ₹1,300 |

### D. Dome / sensor stack (rotor frame)

| # | Part | Qty | Material | Key dimensions | Mass | Manufacture | Finish/QA | Cost proto | Cost @1k |
|---|------|-----|----------|----------------|------|-------------|-----------|-----------|----------|
| D1 | Radome | 1 | Glass-epoxy (GFRP E-glass) | semi-ellipsoid Ø84 × 49.6, wall 2 | 44 g | Hand-layup/wet filament wound on mandrel, CNC trim | RF transmission ≥85%, boil test | ₹8,000 | ₹2,200 |
| D2 | Dome base ring | 1 | 6061-T6 | Ø76–84 × 1.7 | 10 g | Turn | — | ₹600 | ₹150 |
| D3 | GNC board | 1 | FR4 4-layer Ø62 | **STM32G474RET6** (GNC FSW — decision 23: dome owns EKF/IPP/ctrl only) + **ICM-45686** (±4000 dps gyro, 20k g shock) + **W25Q128JVSIQ** flash + rails (**TPS62933** buck / **TLV75730P** LDO / **TLV7031** comparator) | 35 g | SMT | ICT + functional | ₹9,500 | ₹3,200 |
| D3b | Angle sensor (Rev 1.3; **Rev 1.4 relocated to drive domain**) | 1 | MA732GQ-Z + Ø6 diametral NdFeB magnet | 14-bit absolute, 60,000 rpm, SPI 25 MHz — **IC now on the collar-face (A6 side), wired to G431 SPI1** (FOC commutation needs the angle local to the drive MCU; GNC receives angle/rate telemetry per 06 §5) | 3 g | Buy + pot to collar face | magnet-alignment fixture QA; **soft-potted (15k g)** | ₹600 | ₹350 |
| D3c | Setback sensor (Rev 1.3) | 1 | setback-armer interface (inert; flight = partner ESAF) + ADXL1004 ±500 g signature | threshold between manhandling and setback mean (~5 k g) | 12 g | Buy + threshold circuit | **soft-mount QA (ADXL1004 immunity 10k g < 15k g peak)** | ₹2,500 | ₹800 |
| D4 | GNSS patch + module | 1 | ceramic patch + **NEO-F10N-00B** (NavIC L5 + GPS L1/L5) | Ø25 patch | 15 g | Buy | C/N₀ test; **hot-start ≤ 5 s post-despin** (receiver tracks from boot, solution enabled at 45 s); flight: unlimited-dynamics factory variant | ₹5,200 | ₹2,600 |
| D5 | Proximity head | 1 | FMCW 24 GHz (**K-LD7-RFB-00H-01** candidate) + patch | Ø30 × 8 | 25 g | Buy + integ | HOB bench 6/12/18 m (K-LD7-EVAL); RFbeam AN03 radome practice | ₹4,800 | ₹1,900 |

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
| Engineering prototype (1) | ₹1,60,750 | ₹55,000 | — | **~₹2.2 L** |
| Pilot lot (25) | ₹62,300 | ₹22,000 | — | **~₹0.84 L** |
| Production (1,000) | ₹30,800 | ₹14,000 | ₹30,000 | **~₹0.7–0.9 L** |

(Rev 1.4: +₹3,285 proto / +₹2,385 @1k per §I — drive-domain ICs on A6 and dome rail/flash
fill. Rev 1.3 was +₹3,250/+₹1,300 per §H. The pilot-lot delta takes the new COTS lines at
their @1k pricing.)

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
6. Bolt stator A4 to collar; insert Hall sensors; connect windings → phase-resistance check; **fit A7b brake chopper + dump resistor to collar**
7. Fit A6 stub shaft, C2 pilot bearing, C3 slip ring
8. Bond D6 magnets into bell; fit bell over stator onto C2 → gap check 0.5 mm, spin by hand
9. Assemble dome stack (D3→D4→D5) on standoffs; bond radome D1 to base ring D2; fit to bell cap
10. **Bolt C1 canard shell** to bell flange (6× M3, 2.5 N·m); fin clock check vs datum
11. Setter G1 functional pass: continuity, S&A state machine, target upload
12. Final: mass ≤2.0 kg, length ≤276 mm, balance <0.5 g·cm

## F. Mass & SWaP rollup

| Group | Mass |
|---|---|
| Core + battery + power (shell frame) | 426 g (was 414 g; Rev 1.4: +A6a–A6e drive-domain ICs ≈ 12 g) |
| Bearing (rings + balls + cage) | 515 g |
| Actuator (stator + windings + magnets + shaft + bearing) | 470 g |
| Canard shell + dome + electronics | 464 g (Rev 1.3: +D3b angle 3 g, +D3c setback 12 g; Rev 1.4: +dome rails/protection/passives ≈ 4 g) |
| **Module total** | **≈ 1.88 kg** (hard limit 2.0 kg ✓; optimization note: A1 thin-wall + C4 Al-yoke-with-steel-sleeve saves ~280 g → **≈1.6 kg**; ≤1.5 kg target now a stretch — see §G) |
| Module length | 606→776 mm station span; protrusion above ogive ≈ 80 mm; total in-well+above ≈ 260 mm |

---

## G. Rev 1.2 — simulation-informed spec deltas (2026-08-30)

Source: `scripts/sim_guidance_check.py` + `out_sim/RESULTS.md` — 3DOF steering-effectiveness
Monte Carlo (250 paired runs) of the as-built control mechanism. Verdict: **the mechanism steers**
— guided CEP 6.9 m vs unguided 207 m (nominal lock 35 s); 8.5 m median with the Rev 1.2 lock at 45 s.

| # | Finding from sim / first-principles check | Spec change (Rev 1.2) |
|---|---|---|
| G1 | De-spin torque demand is L/t: **0.143 N·m at 10 s sits exactly on the 0.14 peak spec** (zero margin). The required 600 C braking charge cannot be absorbed by the 15 F supercap, and regen is blocked while EMF < bus terminal voltage — the old "60 A regen-dominant" path had no guaranteed braking authority, especially cold | De-spin re-specced **15 s @ ≤40 A (0.095 N·m)** — inside the cell's 45 A continuous rating with 1.39× current margin; **A6 boost stage (3.7→5 V)** guarantees terminal-voltage headroom at −40 °C/50 % SoC; **A7b brake chopper + dump resistor** gives a guaranteed energy-absorption path independent of regen |
| G2 | 15 s de-spin delays GNSS lock 35→45 s; sim-validated: CEP 8.5 m median, worst 145 m — still ~20× better than unguided median. Tail shrinks with the C4 Al-yoke J reduction (12 s / lock ~40 s) as a flight option | D4 cold-start spec added; timeline in design report §2.3 updated |
| G3 | Steering corrections use ≤27 % mean duty of the 60 N lateral authority (brief peak saturation); roll slews need ~6 mN·m vs 50 mN·m continuous rating — actuator authority comfortable | No change (margin confirmed) |
| G4 | Monte Carlo assumes Cd σ0.8 % — requires aero build consistency part-to-part | C1 QA adds **fin trim incidence ±0.2°** and **edge bevel ±0.1 mm** |
| G5 | Cold de-spin is the critical electrical event (risk R2) | Cell cold-pulse cert (A3.1); magnet demag check at −40 °C @ 40 A (D6); winding adiabatic spec ≤720 J → ΔT ≤50 K (A5) |

**Materials unchanged** (100Cr6/440C, 7075-T6, N42SH, M350-50A, GFRP E-glass, NMC cell): the sim is
flight-dynamics level — it changes electrical duty, timing and QA gates, not structural loads. Fin
root margin (33 MPa vs 500 MPa) already covers the modeled aero envelope with gust factor.

**Energy ledger restated conservatively:** de-spin now draws ≈0.83 Wh gross (boost-sourced braking);
regen return is opportunistic (0–0.2 Wh), not budget-critical. See design report §5.

---

## H. Rev 1.3 — sensor-selection deltas (2026-08-31)

Source: `05_SENSOR_SELECTION.md` + `research/D_sensors/entry_20260831_*.md` (datasheet-backed,
URLs + access dates) + `out_sim/RESULTS_SENSORS.md` (paired-MC validation of the selected
parts' sigmas). Every GNC sensor constant in `flight_sw/fsw/config.py` now maps to a cited
datasheet parameter with stated margin; the terminal-accuracy gate re-validated with the
selected parts' sigmas via runtime sensor profiles (no sim/config file edits).

| # | Finding / requirement | Spec change (Rev 1.3) |
|---|---|---|
| H1 | "M9N-class" on D4 was vague and the M9 platform has **no NavIC** (datasheet-verified); the only COTS standard-precision NavIC module meeting the apogee ceiling is u-blox NEO-F10N | D4 firmed to **NEO-F10N-00B** + Ø25 patch (cost envelope unchanged). First-fix spec reworded: **hot-start ≤ 5 s post-despin** (receiver tracks from boot; solution enabled at 45 s). Flight procurement: **unlimited-dynamics factory variant** required (500 m/s ITAR limit on standard COTS) |
| H2 | ICM-42688-P (named on D3) tops at **±2,000 dps** — the sim's 4,000 °/s saturation constant would not have mapped to it; ICM-45686 offers ±4,000 dps exactly, plus ±0.3 °/s ZRO, ±32 g accel, 20,000 g unpowered shock (≥ 15,000 g setback, 1.33×) | D3 IMU firmed to **ICM-45686** (+≈₹150) |
| H3 | The collar↔bell angle sensor (report §4.3/§4.5: FOC commutation, de-spin monitor, S&A spin signature) had **no BOM line item** | **New D3b: MA732GQ-Z + Ø6 magnet** — 14-bit (> 12-bit gate), 60,000 rpm (4× the 15,000 rpm braking transient), 25 MHz SPI, ₹600/₹350 (≤ ₹1.5k gate) |
| H4 | The setback sensor (S&A signature 1) had **no part and no spec** | **New D3c: mechanical setback-armer interface (flight = partner ESAF, STANAG 4187 path) + ADXL1004 electronic launch signature**, threshold between manhandling and the ~5,000 g kinematic mean; soft-mount QA (ADXL1004 immunity 10,000 g < 15,000 g design peak). Live S&A remains outside this project's boundary |
| H5 | D5 "FMCW 24 GHz module" had no part number | D5 candidate PN noted: **K-LD7-RFB-00H-01** (digital distance + speed + angle; AN03 radome practice; HOB gates bench-verified on K-LD7-EVAL). Cost unchanged |
| H6 | Cost/mass rollups | +₹3,250 proto / +₹1,300 @1k (§D); +15 g dome-electronics (§F) — ex-works still 8–12 % of the PS ceiling; module ≈ 1.86 kg vs 2.0 kg hard limit |

**Deliberately unchanged** (selection is analysis-level; structure/mechanism untouched):
materials (100Cr6/440C, 7075-T6, N42SH, M350-50A, GFRP E-glass, NMC cell), bearing/motor/
steering design, de-spin spec (§G), battery/power architecture. The K-LD7 adds ≈0.2 W-class
dome load — slip-ring and energy budget unchanged (0.9 Wh worst vs 16.7 Wh). Baro remains
rejected above Mach 2 (LShang teardown); magnetometer remains rejected (motor magnet ring
swamps Earth field — report §8 decision 12).

---

## I. Rev 1.4 — electronics-architecture deltas (2026-08-31)

Source: `06_ELECTRONICS_ARCHITECTURE.md` (Rev 1.0) + `research/06_electronics-embedded-power/entry_20260831_*.md`
(8 sourced entries, URLs + access dates) + `electronics/gnc_board.kicad_pro` (ERC-clean
schematic skeleton of the dome board) + `flight_sw/board/board_config.h` (the C header
contract, parity-tested against `fsw/config.py` rates).

| # | Change | Rows | Cost impact (proto / @1k) |
|---|---|---|---|
| I1 | **Dual-domain split** (decision 23): drive stage (3-φ bridge + gate driver + FOC current loop + MA732 + Hall + A7b tie-in) moves onto the shell-frame **A6 power board** under a dedicated **STM32G431CBT6**; the dome **D3** becomes GNC-only (STM32G474RET6 runs the whole `flight_sw/` stack). The 40 A braking current never crosses the frames; the existing 3-contact slip ring C3 (`+5 V \| GND \| UART`, 115.2 kBd HD) carries ≤ 0.5 W power + telemetry/commands with a 100 ms loss→safe-state rule (F6) | **new A6a–A6e** (G431 ₹500/₹350 · DRV8329 ₹400/₹280 · 6× NVMFS5C460NL ₹900/₹650 · 3× INA240A2D + 2 mΩ shunts ₹550/₹490 · LDO+TVS ₹150/₹95) | **+₹2,500 / +₹1,865** |
| I2 | **D3 firmed**: MCU variant → STM32G474RET6 (LQFP64, 512K/128K — methodology §7 RAM gate), flash → W25Q128JVSIQ, rails → TPS62933 + TLV75730P + TLV7031 | D3 note (no new row; flash/rails carried in D3 board line + passives) | **+₹785 / +₹520** |
| I3 | **D3b MA732 relocated** dome → collar-face (drive side): FOC commutation at the 3 kHz electrical frequency needs the angle local to the G431; the GNC ctrl task consumes the drag-ref roll **estimate** (report §4.5), not the sensor. Physical mount unchanged; GNC board SPI2 freed | D3b note (cost **unchanged**, ownership moves dome → shell) | ±0 / ±0 |
| I4 | Cost/mass rollups | §D, §F | **+₹3,285 proto / +₹2,385 @1k; +16 g → ≈ 1.88 kg** (still 8–12 % of ceiling; 2.0 kg hard limit ✓) |

**Deliberately unchanged:** materials, bearing/motor/steering design, de-spin spec (§G),
sensor selections (§H — all five GNC sensors keep their PNs), battery/boost architecture.
Energy ledger: dome electronics ≈ 0.49 W × 90 s ≈ 0.012 Wh — inside the existing 0.025 Wh
electronics line; **0.9 Wh worst-case unchanged** (06 §2). Slip-ring allocation: 0.49 W vs
1.5 W → 3.1× margin (≥ 2× gate ✓).

**Open/parked:** PCB layout + stackup (next rung); A6 drive-domain schematic is block-level
only (06 §4); motor FOC firmware + drive-side code (header contract defines the interface);
the A6c bridge **thermal survey QA** and the D3c soft-mount QA carry into the build QA plan.

---

*Open/parked items carried in BOM as REQ: A2, B3, C4 flight yoke, D6 pole change, slip-ring size, ESAF partner. **Rev 1.2 deltas: §G. Rev 1.3 deltas: §H (sensor selection). Rev 1.4 deltas: §I (electronics architecture — dual-domain, decision 23).***
