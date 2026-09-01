# SIH26098 — TEAM BRIEFING (Read This First)
### Low-Cost Precision Guidance Kit + Smart Electronic Fuze for 155mm Artillery Shell
**For:** all 6 teammates | **By:** jagathsrujan | **Deadline:** 20 Sep 2026 | **Org:** Ministry of Defence / Yantra India Limited (YIL), Ambajhari, Nagpur

> **One-line version:** The army's normal 155mm shells miss the target by ~267m at long range. We design a **screw-on smart nose** (guidance kit + electronic fuze) that makes the same old shell land within **30m** — at ₹8–11 lakh per kit instead of ₹60L+ for imported rounds. YIL (the factory that makes India's 155mm shells) wants this.

> **Active build boundary:** The physical artifact in this workspace is an inert, low-speed exhibition demonstrator. Its active mechanical baseline is detailed CAD: `PGK_155mm.FCStd` — shell-spin rotor hub, ONE 61811 thin-section de-spin bearing, Ø106 dome-nosed de-spun stator carrying 4 fixed strakes, a 12-pole ring motor (steering torque + regen power), detent pawl + solenoid launch lock, Ø87 GNC PCB (2× STM32F405, ICM-42688, MMC-5983, dual Hall index), 6× 14430 battery bay, NEO-M9N + Ø25 patch. It is not launch hardware and must not be presented as an exact production teardown.

> **Clean-sheet design of record (Rev 1.1, 2026-08-30):** `cleansheet/PGK_CleanSheet.FCStd` — threaded-race bearing-in-well, pancake outrunner, roll-decoupled canard shell. Native Assembly + 122-frame kinematic Simulation. Docs: `cleansheet/03_DESIGN_REPORT.md` (Rev 1.1), `cleansheet/HANDOFF.md` (Rev B). The bench demonstrator above is the exhibition artifact; the clean-sheet track is the analysis/design of record.

---

## SECTION 1 — Problem Statement, Decoded

Official PS: `SIH2026_Hardware_PS.md:647` | S.No 98 | Category: **Hardware** | Theme: Miscellaneous | Submissions so far: 0/500 (wide open!)

### What the PS literally asks for (every bullet = a thing we must build)

| PS says (official text) | What it means in plain English | Our answer (from ideas catalog) |
|---|---|---|
| "Canard Actuation Assembly (CAA) for in-flight trajectory correction" | Small steering surfaces near the nose that steer the shell mid-flight | 4 fixed strakes on ONE de-spun stator frame; isolation shown with a real 61811 thin-section bearing; steering = ring-motor roll torque (torque AND regen in one machine) |
| "GNC system capable of improving terminal accuracy" | A brain that would guide the flight article; the exhibit only shows the electronics story | Display controller + relative-angle sensor + LEDs; flight GNC remains simulation/reference work (C1/C10/C11) |
| "Multi-mode Electronic Fuze: Proximity / Time / Impact" | A project requirement to explain, not hardware to reproduce in the exhibit | Clearly labelled mock state machine/UI only; no radar, initiator, arming, fuze, or firing hardware |
| "Embedded electronics and software for real-time flight control" | A future flight-article requirement; the exhibit only shows the electronics story | Low-voltage display controller, relative-angle sensor, and LEDs; flight electronics remain reference/simulation work |
| "Power management suitable for high-g launch" | The exhibit demonstrates the energy path at low speed | Ring-motor regen (drag mode) → rectifier/boost → 6× 14430 bay → FOC/BlackPill rails |
| "Communication and programming interface for fuze configuration prior to firing" | A project requirement to explain, not hardware to reproduce in the exhibit | Optional mock phone UI only; no live fuze, setter, initiator, or firing interface |
| "CEP of 30 meters or better" | A future flight-performance target | Any trajectory/CEP result is simulation or public reference only—not a result from the printed bench model |
| "Compatibility with existing 155mm shell design" | A future interface requirement | CAD shows a Ø56 STANAG 2916-class thread insert (simulated, printed for the demo); no live-compatible interface |
| "Survive extreme mechanical and environmental conditions" | A future flight-article requirement, not a claim made by the printed exhibit | Lightweight printed housing, guarded low-speed operation, and explicit no-launch boundary (G1–G10 reference only) |
| "Low SWaP-C, high reliability, modular" | Small, light, cheap, upgradeable | ~770g nose module, ₹8–11L, bay for future seekers |

### What we must SUBMIT (PS "Desired Deliverables" → our files)

1. **System architecture document** → we have 108 ideas cataloged; baseline frozen in CAD (`PGK_155mm.FCStd`) + documented in `cad_models/PGK_155MM_ASSEMBLY.md`
2. **CAD model of the steering assembly** → `PGK_155mm.FCStd` + `cad_models/PGK_155MM_ASSEMBLY.md` (de-spun stator + strakes + ring motor + 61811 bearing; exports/renders in `cad_models/out_pgk/`)
3. **Electronics block diagram** → D/E/F/J categories combined block diagram
4. **Guidance and control algorithm** → PID + impact-prediction (MPC-style), documented
5. **Simulation demonstrating trajectory correction** → `cad_models/simulate_trajectory_155.py` (3DOF → 6DOF, Monte Carlo CEP)
6. **Prototype or proof-of-concept (preferred)** → CAD-detailed inert nose (print from `cad_models/out_pgk/stl/`) + bench de-spin rig + drop test plan
7. **Performance estimation showing CEP ≤30m** → Monte Carlo histogram + report

### Why judges will care (our pitch spine)
- **Pain:** Unguided shell at 30km has CEP ~267m → "danger close" fire missions impossible, huge ammo waste.
- **Logistics win:** Killing one target needs ~301 dumb shells (18.2 tonnes, 959 propellant charges) vs **77 with our kit** (4.5t) → **74% fewer shells, 75% less weight** (idea H8).
- **Atmanirbhar:** NavIC (India's GPS) primary, YIL forging, BEL/ECIL electronics — fully Indian supply chain.
- **Price:** ₹8–11L/kit vs ₹60L–2Cr imported rounds (Excalibur ~$100k).

---

## SECTION 2 — Artillery Gun 101 (What it is, how it works)

### What is an artillery gun (howitzer)?
A big cannon that fires shells **indirectly** — the shell flies in a high arc (like a basketball shot) over hills and lands tens of km away. The gun crew never sees the target. Unlike a tank gun (flat, direct fire), a howitzer lobs shells at 45°+ elevation.

### How a firing mission works (the kill chain)
```
Forward Observer (sees target)
      │  radio: grid coordinates + "fire for effect"
      ▼
Fire Direction Centre (ballistic computer: range, wind, charge, angle)
      │  firing data: elevation 42.3°, charge M3A1, fuze setting
      ▼
Gun crew: sets fuze → loads SHELL → loads PROPELLANT CHARGE → closes breech → FIRE
      │
      ▼
Shell arcs 20–30km for ~60–90 seconds → fuze triggers → detonation at/above target
```

### Inside the gun — what happens at firing (0 to 800 m/s in 17 milliseconds)
1. **Propellant ignition:** Primer ignites the charge (bags of nitrocellulose). Pressure spikes to ~300–400 MPa (≈3,000–4,000 atmospheres).
2. **Shot start:** Pressure pushes the shell; its soft copper **rotating band** is engraved by the barrel's **rifling** (spiral grooves).
3. **Spin-up:** Rifling (≈1 turn in 20 calibers) spins the shell to ~250 revolutions/second — this gyroscopic spin is what keeps the shell stable in flight (like a thrown American football).
4. **Muzzle exit:** A real flight article would see roughly this launch environment. The printed exhibition model is not tested for it and must stay outside any launch path.
5. **Recoil:** The gun jumps back ~1m; hydro-pneumatic recoil cylinders absorb it and return the barrel to battery.

### The 4 guns our kit must fit (PS requirement — STANAG 2916 fuze thread is common to all)

| Gun | Caliber length | Range | Made by | Note |
|---|---|---|---|
| **ATAGS** | 52 cal (~8.06m barrel) | ~40–48 km | DRDO + Bharat Forge / Tata | India's newest, 307 ordered (₹6,900 Cr) |
| **Dhanush** | 45 cal | ~38 km | YIL/AWEIL | "Desi Bofors" |
| **K9 Vajra-T** | 52 cal | ~40+ km | L&T + Hanwha (Korea) | Self-propelled tracked |
| **M777** | 39 cal (~6.05m) | ~24–30 km | BAE (USA) | Ultra-light 4.2t, Chinook-liftable |

*"Caliber length" = barrel length expressed in multiples of bore diameter. 52 cal × 155mm ≈ 8.06m.*

---

## SECTION 3 — Artillery Shell 101 (Anatomy + every term you need)

### Anatomy of a 155mm high-explosive shell (e.g., M107/M795, ~43–47kg)
```
        NOSE
   ┌─────────────┐
   │    FUZE     │ ← screws into fuze well (STANAG 2916, 2-12UN-1A thread)
   │ (our PGK    │    THIS IS THE PART WE REPLACE — everything else stays stock
   │  goes here) │
   ├─────────────┤
    \   OGIVE   /   ← curved aerodynamic nose cone
     ├─────────┤
     │BOURRELET│     ← machined bearing surface, rides the barrel (front)
     │         │
     │  BODY   │     ← forged steel case filled with ~10kg TNT/Comp-B
     │ (HE fill)│
     │         │
     ├─────────┤
     │ROTATING │     ← soft copper band: seals gas + engages rifling = spin
     │  BAND   │
     ├─────────┤
      \BOAT TAIL/    ← tapered tail, cuts base drag
       └──────┘
         BASE        ← flat (or base-bleed / rocket-assist in special shells)
```

### Complete glossary (memorize these — you'll hear them in reviews)

**Ballistics terms**
- **CEP (Circular Error Probable):** Radius of circle around the target inside which 50% of shells land. *Smaller = better.* Unguided ≈267m at 30km → our goal ≤30m.
- **Muzzle velocity (v₀):** Speed leaving the barrel. 684 m/s (charge M3A1) to ~827 m/s (max charge).
- **Ballistic trajectory:** Unpowered arc under gravity + drag. Once it leaves the barrel, a dumb shell cannot change anything.
- **Apogee:** Highest point of the arc (~10–12km at max range).
- **Quadrant Elevation (QE):** Gun barrel angle, typically 45° for max range.
- **Drag:** Air resistance. Costs ~half the ideal range. `F = ½ρv²CdA`.
- **Spin stabilization:** Rifling spins shell ~250 rev/s; gyroscopic stiffness keeps nose forward.
- **Magnus effect / Coriolis:** Small aerodynamic & Earth-rotation forces that push the shell sideways ~50–150m at long range — part of why dumb shells miss.
- **Probable Error (PEr/PEd):** Army way of saying scatter in range / deflection.

**Fuze terms**
- **Fuze:** The "nose computer" that decides WHEN the shell detonates. (Not "fuse" — fuze = munition device.)
- **PD (Point Detonating):** Explodes on contact. *Superquick* <250µs; *Delay* 0–60ms (digs into bunkers first).
- **Proximity (VT) mode:** Radar measures height, explodes in air 6/12/18m above ground (HOB = Height Of Burst) — lethal against troops in trenches.
- **Time mode:** Explodes at set time (3.0–199.9s) — used for cargo/smoke/illumination shells.
- **S&A (Safe & Arm):** Mechanical/electronic lock that keeps the fuze SAFE in storage/transport and ARMS only after real launch signatures (setback ≥850g + spin ≥2900rpm + distance ≥100m — STANAG 4187).
- **Setback:** The massive backward acceleration at firing (what we feel as "g-force") — used by the fuze as "proof we were actually fired".
- **EPIAFS / inductive setter:** Wireless (no pins) coil that programs the fuze inside the breech — target coords, mode, GPS keys.
- **MOFA:** Multi-Option Fuze for Artillery (existing Indian fuze family, ECIL/BEL).

**Our project terms**
- **PGK (Precision Guidance Kit):** A fuze-shaped module with GPS + steering surfaces that replaces the standard fuze and steers the shell. Our whole project.
- **Strakes / canards:** Small fins near the nose. Ours are FIXED to the de-spun frame; holding that frame at an orientation aims their net lift.
- **Despun nose / stator:** The steering frame is bearing-isolated from the spinning shell by ONE 61811 thin-section bearing; a 12-pole ring motor controls its relative orientation (and doubles as the spin-power harvester).
- **GNC:** Guidance (where should I go), Navigation (where am I), Control (hold the de-spun frame at the steering orientation).
- **IMU:** Inertial Measurement Unit — accelerometers + gyroscopes.
- **GNSS / NavIC / GPS:** Satellite navigation. NavIC = India's own constellation (L5 band) — sovereign, can't be switched off by the US.
- **FMCW radar:** Frequency-Modulated Continuous Wave — tiny radar that measures distance precisely (for proximity fuze).
- **SWaP-C:** Size, Weight, Power and Cost — the 4 things we must keep LOW.
- **TRL:** Technology Readiness Level (1=paper idea, 9=flown in service). Real PGK = TRL9.
- **STANAG 2916:** NATO standard for fuze threads/wells — screw our kit in, it fits every 155mm shell & gun.
- **6DOF:** Six Degrees Of Freedom simulation (3 position + 3 rotation) — how we prove CEP without firing.
- **Monte Carlo:** Run the sim 1000× with random wind/sensor errors → get the CEP histogram.

---

## SECTION 4 — The Physics of a Shell (formulas + one full worked example)

You don't need to derive these — you need to *quote* them in reviews. All numbers below use our sim's parameters (`cad_models/simulate_trajectory_155.py:21-31`): M107 shell, **m = 43.2 kg, d = 0.155 m, v₀ = 684 m/s, QE = 45°**.

### 4.1 Inside the barrel — how hard is the launch?
```
Average acceleration:   a = v² / (2L)     (v² = u² + 2as with u=0)
  a = 684² / (2 × 6.045) = 467,856 / 12.09 ≈ 38,700 m/s² ≈ 3,950 g (average)
  Peak (pressure spike ≈ 2.5–4× average) → 10,000–15,000 g  ← future flight-article reference

Time inside barrel:     t = 2L / v = 12.09 / 684 ≈ 17.7 ms

Spin from rifling:      n = v / (twist × d) = 684 / (20 × 0.155) ≈ 220 rev/s ≈ 13,000 rpm

Kinetic energy:         KE = ½mv² = ½ × 43.2 × 684² ≈ 10.1 MJ
  (≈ a 1.5-tonne car at 420 km/h — in something the size of a fire extinguisher)
```
**Scope boundary:** 15,000g survivability is a future flight-article requirement, not a claim about our printed model. For the exhibition, choose low-voltage parts, retain moving components, guard the rotating assembly, and document the safe operating envelope.

### 4.2 In flight — how far does it go?
```
Ideal (vacuum) range:   R = v₀² · sin(2θ) / g
  R = 684² × sin(90°) / 9.81 = 467,856 / 9.81 ≈ 47.7 km   ← physics-class answer

Real range with drag:   ≈ 24 km (drag eats ~half!)
Drag force:             F = ½ ρ v² Cd A
  at muzzle: ½ × 1.225 × 684² × 0.15 × 0.0189 ≈ 810 N → ~1.9g of deceleration
  (Cd spikes to ~0.31 near Mach 1 — transonic region is the worst)

Apogee:                 h = v₀² sin²θ / 2g ≈ 11.9 km
Time of flight:         t = 2 v₀ sinθ / g ≈ 99 s (vacuum) / ~70–80 s real
```

### 4.3 Why do dumb shells MISS? (the whole reason we exist)
The gun is aimed by calculation, but reality adds errors:
- Muzzle velocity varies shot-to-shot (±1–2 m/s from propellant temperature)
- Wind aloft is unknown (shell flies 12km high through jet stream)
- Coriolis (Earth rotation) & Magnus (spin×airflow) forces
- Manufacturing tolerances (mass, asymmetry)

Each error grows with time of flight (~80s) → **CEP ≈ 267m at 30km**. To reliably kill a target you must fire hundreds of shells: **~301 shells = 18.2 tonnes + 959 charges for ONE target** (idea H8).

### 4.4 How 4 small strakes fix 267m of error
```
Strake lift:            L = ½ ρ v² · (CL·S)
  our strake lift-area: CL·S ≈ 0.005 m² (from sim, canard-equivalent class)
  at q ≈ 287 kPa near muzzle → L ≈ 1.4 kN available → we cap at 3g

Lateral correction:     Δx = ½ a t²
  with a = 3g = 29.4 m/s² held for just 20 s of guided flight:
  Δx = ½ × 29.4 × 20² ≈ 5.9 km of correction authority
```
**We have ~6km of steering authority against a 267m problem — 20× margin.** That's the mathematical reason PGK works with just 4 fixed strakes on one de-spun frame and one torque machine.

### 4.5 How the de-spun steering frame is represented in our model
- All four strakes are fixed to one de-spun stator (`PGK_Stator_Body`, Ø106, dome-nosed); there are no individual fin hinges or gear motors.
- The shell + rotor hub are the spin-side frame (FRAME A). The stator rides on ONE 61811 thin-section bearing (55×72×9).
- The 12-pole ring motor both steers FRAME B (torque mode) and harvests spin power (regen mode) — one machine, two acts.
- A detent pawl + solenoid (D12×20) is the launch lock: engaged through setback/spin, release = "armed" (display-only).
- On the bench, FRAME B is held nearly stationary while FRAME A rotates slowly. This demonstrates relative phase only; it does not validate flight guidance or launch survivability.

### 4.6 CEP math (what we report to judges)
```
Fire N=1000 sims with randomized errors (Monte Carlo).
rᵢ = distance of impact i from target.
Sort rᵢ, take median → CEP = r₅₀₀ (radius containing 50%).
Target: CEP ≤ 30m. Stretch: 10m (real PGK achieved 10m median in 2015 tests).
```

---

## SECTION 5 — Our Solution, Subsystem by Subsystem

Active demonstrator architecture = detailed CAD in `PGK_155mm.FCStd` (public-architecture analogue): a fuze-shaped nose module with a simulated STANAG 2916-class thread insert, shell-spin rotor hub, ONE 61811 de-spin bearing, Ø106 dome-nosed de-spun stator with 4 fixed strakes, 12-pole ring motor (torque + regen), detent pawl + solenoid, Ø87 GNC PCB (2× STM32F405, ICM-42688, MMC-5983, dual Hall), 6× 14430 bay, NEO-M9N + patch. Kit envelope Ø148 × 168 mm. Dimensions and cost are display/project estimates, not production claims.

```
 ┌──────────────────── ACTIVE INERT PGK DEMONSTRATOR ──────────────────────────┐
 │                                                                             │
 │  [Dome + Ø25 GNSS patch   [Ø87 PCB: 2× STM32F405, ICM-42688,          │
 │   under apex (NEO-M9N      MMC-5983, FOC driver, dual Hall index]      │
 │   below the shelf]                                  ▲                  │
 │                           [12-pole RING MOTOR: torque ⇄ regen]           │
 │  [6× 14430 battery bay in hexagon @ r36.5]            │                  │
 │  [Detent pawl + solenoid — launch lock (display-only)]│                  │
 │  [ONE 61811 thin-section bearing] ◄───────────────────┘                  │
 │  [Rotor hub + Ø56 simulated STANAG 2916 thread insert]                    │
 └─────────────────────────────────────────────────────────────────────────────┘
                         │ nonfunctional slip-fit display adapter
              ┌──────────▼──────────┐
              │  PRINTED SHELL      │  lightweight, guarded, low-speed bench use
              └─────────────────────┘
```

| # | Subsystem | Owner | What it does | Key design choice | What you SUBMIT |
|---|---|---|---|---|
| 1 | **A_system + H_mfg** (Planner) | jagathsrujan | Overall architecture, requirements, cost model, interfaces between all subsystems | Active inert common-carrier demonstrator; separate simulation/reference track for future performance work | Architecture doc, cost sheet, master CAD, final PPT |
| 2 | **B_aero** (Steering) | **OPEN — hiring** | Strake geometry, relative-rotation physics, lift/moment database | 4 fixed strakes on the de-spun stator (per `PGK_155mm.FCStd`); guarded bench validation | Strake CAD + CFD/simulation notes + safe rotation diagram |
| 3 | **D_sensors + C_gnc** (Brain) | Anvita Pranjal | Demonstrates relative-angle sensing and display control | Low-voltage controller + angle sensor + LEDs; flight GNC is simulation/reference only | Display PCB + live angle/power readout |
| 4 | **E_fuze + J_integration** (Display Electronics) | Krupa Nalige | Explains public fuze concepts without reproducing them | Mock state machine/UI only; no radar, initiator, arming, fuze, or firing hardware | Clearly labelled display block diagram + mock-programming demo |
| 5 | **G_structure + F_power** (Body) | Naman | Provides a clear, safe exhibition structure and demonstrates power harvesting | Stator + strake print set, ONE 61811 bearing, ring motor (torque⇄regen) → rectifier → 14430 bay | 3D-printed nose model + guarded low-speed power/angle demo |
| 6 | **I_test** (Tester) | Member 5 (TBD) | Proves it works without firing a real gun | 6DOF + Monte Carlo CEP, MIL-STD-331 test plan, drop/despin rigs | Sim report (CEP histogram) + test plan + final demo video |

**Dependencies (talk to each other!):** Body(5) must give power before Brain(3) works • Steering(2) tells Brain(3) which way is up • Brain(3) tells Fuze(4) when/where to burst • Tester(6) checks everyone's numbers → Planner(1) puts it in the deck.

---

## SECTION 6 — Already-Built PGKs (study these) + Video Watchlist

### Products that already exist (= proof our idea works + what to beat on cost)

| Kit | Country | How it steers | CEP | Cost | Lesson for us |
|---|---|---|---|---|---|
| **M1156 PGK** | USA (ATK→Northrop) | Public reference for fixed canards + controlled relative rotation | Public benchmark only; not our demo result | Public reference only | Study the architecture; do not claim an exact teardown |
| **M982 Excalibur** | USA/Sweden | Full new shell, glide + fins, GPS/INS | <4–6m | ~$100k (₹85L+) | The "gold standard" we undercut 8× on price; India already bought some |
| **Elbit Silver Bullet** | Israel | Fuze-replacement kit, GPS | <20m class | ~$20k class | Direct competitor concept |
| **Junghans/KNDS FOX, DM84** | Germany | Course-correcting fuze | ~10–20m | — | FMCW proximity heritage (our E1) |
| **Aselsan ASAF / MOFA** | Turkey | Multi-mode fuze | — | — | Multi-mode fuze reference (E-cat) |
| **ECIL M85P13 / BEL M180** | **India** | Proximity fuze (no guidance) | — | fielded 2.2M+ | Indian electronics path (BEL/ECIL supply chain) |
| **IIT Madras + MIL kit** | **India** | Research kit | 10m CEP claimed | research | Proof India can do GNC; DRDO guided-artillery program backs this |
| **L Shang student rocket** | China (student!) | 4 servos + canards, ADRC + EKF | recovered vertically | <$200 BOM | A student did CAD→CFD→PCB→GNC→7 flights in 30 days. 70% of his toolchain transfers to us. Full teardown in `legacy/SIH26098_LShang_Video_Teardown_Gap_Analysis.md` |

### Watch these BEFORE our first meeting (45 min total)
1. **PGK Overview (ATK)** — public reference for canards + controlled relative rotation: https://www.youtube.com/watch?v=Ebzh12PR0-U *(use it to understand the architecture; our physical model is inert and not an exact teardown)*
2. **Precision Guidance Kit (Northrop Grumman)**: https://www.youtube.com/watch?v=nppX02X_vVQ
3. **M1156 PGK**: https://www.youtube.com/watch?v=JNgslxFyOv0
4. **How Accurate Can a 155mm Shell Get — PGK test**: https://www.youtube.com/watch?v=tlDhdhbIN7g
5. **M982 Excalibur — precision hit at 70km**: https://www.youtube.com/watch?v=0VPrQNUC25A
6. **Excalibur first combat use (Afghanistan)**: https://www.youtube.com/watch?v=nfESvQIpdz8
7. **L Shang canard rocket (23 min)** — see repo teardown doc §1 for the frame-by-frame guide: what a student team can build in 30 days

---

## SECTION 7 — Planning Process: How We Go From Today → 20 Sep

### The daily loop (everyone, every day, ~1–2h)
```
1. git pull                      → see what teammates did (check SIH26098_LIVEBOARD.md)
2. Research your category        → real sources only (datasheets, patents, papers)
3. Write entry                   → research/<your_category>/entry_YYYYMMDD_<topic>.md
                                   (use research/templates/entry_template.md)
4. Fill the 4 mandatory fields   → Source URL + TRL + Cost (₹) + Indian Path (YIL/BEL/ARDE/ISRO/MIL)
5. git add . && commit && push   → GitHub Action auto-updates the LIVEBOARD
```
**Hard rules:** No URL = entry rejected. Never invent sources. Pull before you push. Conflicts → GitHub Issues or team chat.

### 3-week battle plan (deadline 20 Sep 2026)

| Week | Dates | Theme | Milestones (what exists by end of week) |
|---|---|---|---|
| **W0 — Onboard** | Aug 26–31 | Learn | Everyone: read this doc + README, watch the 7 videos, clone repo, accept GitHub invite, first welcome entry pushed. 6th member hired (target: aero/CFD or controls). |
| **W1 — Research & Freeze** | Sep 1–7 | Decide | Each category has 3+ researched entries with real sources. **Architecture freeze review (Sep 6):** inert common-carrier baseline confirmed, display electronics mapped, CAD v1, safe test plan. |
| **W2 — Build** | Sep 8–14 | Show | Simulation and electronics block diagram; inert 3D-printed nose + guarded low-speed de-spin rig; relative-angle/power LED demo; steering concept notes. |
| **W3 — Integrate & Pitch** | Sep 15–19 | Prove | All 7 PS deliverables assembled; performance report (CEP ≤30m evidence); 5-min pitch deck + demo video rehearsed twice. Buffer day Sep 19. |
| **SUBMIT** | **Sep 20** | 🎯 | Upload. Celebrate. |

### Roles at a glance (Research → Work → Submit)
- **jagathsrujan (Planner/A+H):** research old kits & cost methods → integrate everything, own architecture & cost → submit: architecture doc + cost sheet + PPT
- **OPEN SLOT (Steering/B):** research canards, despin, CFD → canard geometry + lift database → submit: CFD results + steering-authority graph
- **Anvita (Brain/D+C):** research relative-angle sensing and low-voltage display control → display PCB + sensor demo → submit: live angle/power readout
- **Krupa (Display Electronics/E+J):** research public fuze concepts and safety communication → mock state machine + optional phone UI → submit: clearly labelled display block diagram
- **Naman (Body/G+F):** research printed housing, bearings, alternator display → CAD + 3D print + guarded power bench → submit: inert model + relative-angle/power demo
- **Member 5 (Tester/I):** research safe bench methods → rotation/LED test plan and observations → submit: exhibition test report + final demo video

---

## SECTION 8 — New-Member FAQ

**Q: I know nothing about defence. Can I still contribute?**
Yes. This is an engineering project: wings, sensors, code, structures. Everything military you need is in Sections 2–4 of this doc. Watch the 7 videos and you'll know enough.

**Q: Are we building an actual weapon?**
No. We build *inert* demonstrators: CAD, simulation, 3D prints, bench electronics. No energetics, no explosives, ever. The PS is published by the Government of India for exactly this kind of student engineering.

**Q: What's the single hardest technical risk?**
For the active exhibit, the hardest risk is safe low-speed operation: retain every moving part, guard the rotating shell, and keep the adapter nonfunctional. Flight survivability and fuze logic remain reference/simulation topics, not claims about this model.

**Q: What if NavIC/GPS is jammed?**
Stretch goal: LSTM AI that predicts impact point from IMU data alone (<5m error in published research, idea C7). Great "innovation" slide.

**Q: How much time do I need?**
~10h/week for 3.5 weeks. Daily 1–2h research entries + one weekend build session per week.

**Q: Where is everything?**
- This doc: `SIH26098_TEAM_BRIEFING.md` (start here)
- Team map & roles: `README.md`
- 108 researched ideas: `SIH26098_Exhaustive_Ideas_Catalog.md`
- Your onboarding prompt (paste into any AI): `ONBOARDING_PROMPT.md`
- **Design of record:** `cleansheet/03_DESIGN_REPORT.md` (Rev 1.1) + `cleansheet/HANDOFF.md` (Rev B) + `cleansheet/PGK_CleanSheet.FCStd`
- Bench demonstrator CAD + sim: `cad_models/` | Research entries: `research/<category>/`
- Live board: `SIH26098_LIVEBOARD.md`

---
*Generated 2026-08-26. Edit names/roles as the 6th member joins. Keep this doc honest — it is what new teammates read first. | Updated 2026-08-30: added clean-sheet design-of-record pointers.*
