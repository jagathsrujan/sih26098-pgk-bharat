# SIH26098 — PGK Kit Deep-Dive Design (Exhibition Demonstrator)

> **2026-08-29 update:** the mechanical baseline has advanced past this study's v1 sketches — see `PGK_155mm.FCStd` + `cad_models/PGK_155MM_ASSEMBLY.md` (single 61811 de-spin bearing, 12-pole ring motor for torque AND regen, detent launch lock, 4 strakes on a de-spun Ø106 stator, 6× 14430 bay, NEO-M9N + patch). The research, math and trade reasoning below remain valid; component-level specifics were refined in `SIH26098_FLIGHT_KIT_BOM.md` v2.

**Version:** 1.0 | **Date:** 2026-08-28 | **Owner:** jagathsrujan (A_system)
**Scope:** The inert, low-speed PGK nose module for the SIH26098 demo — the active
baseline (now advanced) in `cad_models/PGK_155MM_ASSEMBLY.md` + `PGK_155mm.FCStd`,
powered by the reference track in `cad_models/simulate_trajectory_155.py`.

> **Boundary (unchanged):** This is a non-launchable, inert exhibition kit.
> No energetics, no live fuze electronics, no launch-compatible interface.
> All flight performance (CEP, 15k g survivability, guidance) is simulation or
> public reference only. This doc designs the *demo*, not a weapon.

---

## 1. What the demo must prove (in one page)

The PS (`SIH2026_Hardware_PS.md:647`) asks for a kit that turns a dumb 155mm shell
(CEP ~267 m at 30 km) into a ≤30 m CEP shell at ₹8–11 L. Our single demonstrator
answers every PS bullet through one story:

> *"A screw-in nose module that harvests its own power from shell spin, keeps a
> four-strake steering frame de-spun against 250 rev/s of body roll, and points the
> combined lift vector at the miss distance — we show the moving parts, the
> power path, and the angle feedback live; the flight math runs in simulation."*

| PS bullet | Demo evidence | Where |
|---|---|---|
| Canard Actuation Assembly | 4 fixed canards on ONE common carrier, bearing-isolated, one torque element | CAD + bench rig |
| GNC for terminal accuracy | Live relative-angle readout mirrored against ZEM sim steering | `simulate_trajectory_155.py` |
| Multi-mode fuze | Mock SAFE/SET/ARMED slider + labelled state-machine graphic only | `04_Inert_Status_Slider` |
| Embedded electronics | Low-voltage (<5 V) display stack: harvester → supercap → MCU → OLED/LEDs | §6 |
| High-g power management | Shell-spin alternator (rotor = shell side, stator = carrier side) | §6.2 |
| Pre-fire programming | Mock BLE "setter" app screen; no live interface | E_fuze |
| CEP ≤ 30 m | Monte Carlo histogram, 1000 runs | `out_sim/` |
| Fits existing 155mm | Nonfunctional slip-fit adapter onto printed shell | §4 |
| Survive extreme conditions | Explicitly NOT claimed; guarded low-speed envelope only | §9 |

---

## 2. Architecture — two frames, one torque element

The whole kit is a study in **relative rotation between exactly two frames**:

```
        FRAME A — SPIN SIDE (shell + outer housing)          ~250 rev/s in flight
        FRAME B — CARRIER SIDE (4 fixed canards, de-spun)    ~0 rev/s, roll-positioned
                        ▲
   ┌────────────────────┴─────────────────────────────┐
   │ 60_NoseCap_InertRadome        (A)                 │
   │ 51_GNSS_PatchAntenna          (B, top)            │
   │ 50_TopPlate                   (interface A-B)     │
   │ 33_GNSS PCB / 32_AngleSensor PCB / 35_Index+Hall  │
   │ 31_Controller+IMU PCB / 30_Power PCB              │
   │ 41_AlternatorStator           (B)                 │
   │ 40_AlternatorRotor            (A)  ← power bridge │
   │ 22_Torque_Emulator            (A→B) ← steer bridge│
   │ 20_FixedCanard_01..04         (B)                 │
   │ 14_CommonCanardCarrier        (B)                 │
   │ 13_RearBearing / 12_FrontBearing (A-B) ← roll iso │
   │ 10_OuterHousing_SpinSide      (A)                 │
   │ 03/02_Power conditioning + supercap (B)           │
   │ 01_DemoShankAdapter → printed shell (slip-fit)    │
   └───────────────────────────────────────────────────┘
```

**Why one carrier, not four servos (A1 vs A2, frozen):** each servo would need to
survive ~15,000 g setback in a flight article; one bearing-isolated carrier with
fixed canards needs only *relative rotation*, which a small brake/torque element
can produce. Fewer motors, fewer failure points, one moving assembly to guard.
The legacy two-motor CAD stays in `legacy/old_two_motor_design/` for contrast.

**Steering principle (B_aero, one paragraph):** the four fixed strakes are set at
incidence, so at any stator roll angle they produce one net side-force vector in
the shell's frame. Hold the de-spun frame at roll angle ψ and the shell bends toward
that direction (quasi-steady side force, averaged by the still-spinning body).
ψ is commanded from predicted impact point — that's the entire control law.

---

## 3. Envelope & mass budget (from the actual CAD, not invented)

v1 display dims (from legacy `legacy/old_common_carrier_demo/generate_pgk_155.py`, mm) — superseded by `PGK_155mm.FCStd`:

| Parameter | Value | Note |
|---|---|---|
| Module length (adapter→radome tip) | ~228 mm | Fuze-class length |
| Body diameter (housing) | 56 mm | Matches printed shell shank Ø49.6 slip-fit |
| Canard span | 151 mm (Ø tip 2×75.5) | Deliberately inside the 155 mm bore envelope |
| Carrier OD / ID | 44.4 / 35.0 mm | PCB stack rides inside Ø35 bore |
| Bearing section | Ø49.6/45.2 × 5 mm, balls Ø2.9 | Front z=128, rear z=187 (59 mm spread) |
| Alternator | rotor Ø48×3 mm (8 magnets), stator Ø37.6×3 mm (6 coils), gap z=166–176 | |
| Printed mass (PLA/PA12 est.) | ~300 g | Housing 80, adapter 45, carrier 30, canards 4×6, nose 25, rings 20 |
| Display electronics | ~60 g | PCBs 4×8, supercap 15, magnets 10, wiring |
| **Bench module total** | **~360 g** | Flight-article reference remains ~770 g (briefing §1) |

Design implication: the Ø35 mm inner bore is the SWaP constraint for the
electronics stack — four 1.6 mm PCBs + standoffs fit only with components
kept ≤15 mm tall near the alternator section.

---

## 4. Interface control (the three external interfaces)

**I1 — Module ↔ shell (display only).** Slip-fit Ø49.6 shank, 88 mm long, printed
taper stop at z=88–92. No thread, no torque path. If we later want a threaded
look for the exhibition, print a decorative 2-12UN *simulated* thread ring on the
nose lip and label it "represents STANAG 2916 well — nonfunctional".

**I2 — Module ↔ bench stand.** Adapter tail face (z=0, Ø5 recess) accepts a soft
chuck/spindle cup. Stand drives FRAME A only. Guarded envelope: ≤600 rpm, see §9.

**I3 — Module ↔ laptop.** BLE/WiFi from the display controller streams
relative angle, harvested voltage, supercap state to the demo dashboard, which
runs `simulate_trajectory_155.py` alongside. No connection to anything live.

---

## 5. Mechanical deep-dive (part by part)

### 5.1 Bearings — the part to upgrade for the bench
The printed ball race (Ø2.9 balls in a 2.2 mm section) is illustrative; at demo
speeds it will be noisy and wear. **Bench recommendation:** replace with two
real thin-section sealed ball bearings (e.g., 45×52×5 class, or custom races
with Ø2 mm steel balls + lithium grease). Front bearing = axial location +
radial; rear = radial. Preload via front bearing seat shim, ≤0.05 mm interference
on the housing. At ≤600 rpm with ~3 N radial load, friction torque is <5 mN·m.

### 5.2 Carrier
One ring Ø44.4/35.0 × 56 mm long with four integral canard roots. Keep it a
single print (or print + 4 glued canards). Canard incidence is illustrative;
do not tune it — aero numbers come from the sim's `CLS_CAN = 0.005 m²`.

### 5.3 Canards
Root chord 26 mm, tip chord 19 mm, span 51 mm each, 2.8 mm thick, tips at
R=75.5 mm. Print 0.8–1.0 mm trailing edges or the tips will blob. Add 0.5 mm
root fillets or they snap at the root in handling.

### 5.4 Torque emulator (the A→B steer bridge)
Function on the bench: rotate/hold the carrier against bearing friction +
alternator cogging. **Torque budget:** bearing friction ~5 mN·m + magnet cogging
~10 mN·m (8 magnets, small gap) + margin → **≤50 mN·m**. A 5 V N20 gearmotor
(100:1, ~0.1–0.4 N·m stall) with a printed pinion engaging a carrier gear ring
covers it with margin — same motor family as the legacy design, now one unit.
Drive it open-loop from the MCU for the demo; hold-position by short-braking.

### 5.5 Alternator
Rotor: 8 N42/N52 block magnets (2.8×2.8×2 mm) on the shell-side ring at Ø43;
stator: 6 hand-wound coils on the carrier-side ring at Ø34.6. Air gap target
≤0.8 mm (printed parts will need a facing pass or shim washers). Electrical
frequency = 4 × shell rev/s (8 poles = 4 pole pairs). EMF budget (stated
assumptions: N=600 turns/coil, B=0.5 T, coil area 1e-5 m², 3-phase series):

| Shell speed | f_elec | E_peak/coil | After rectifier (into supercap) |
|---|---|---|---|
| 60 rpm (hand) | 4 Hz | ~16 mV | µW — not viable |
| 300 rpm | 20 Hz | ~78 mV | still too low without a boost transformer stage |
| **600 rpm (demo max)** | 40 Hz | ~0.75 V | **viable** → rectifier → 2.7 V supercap in ~1–2 min |

**Demo design decision:** run the stand at 600 rpm for the power act (guarded,
§9), use an ultra-low-voltage boost (LTC3108-class or discrete flyback) between
rectifier and supercap, and *also* wire one bare LED to flash on each magnet pass
as a visible "power is being made" cue at any speed. Supercap: 2.7 V, 10–25 F
radial, matches the existing `02_Supercapacitor_Display` slot.

### 5.6 Top plate / radome
Ø50.6 top plate with antenna pass-through; radome is a hollow cone Ø56→14 ×
136 mm, 2 walls. Keep GNSS patch (Ø25) on the carrier top plate (FRAME B) — in
the real kit the antenna is on the despun side so it doesn't spin at 250 Hz;
on the bench this is also why the antenna PCB sits at the top of the stack.

### 5.7 Status slider (fuze story, inert)
Three-position manual slider SAFE/SET/ARMED tied to nothing but the display
state machine (§7.3). Engrave "INERT — DISPLAY ONLY" on it.

---

## 6. Electronics deep-dive (all ≤5 V, all display-grade)

### 6.1 Stack (top → bottom, inside Ø35 bore)
| PCB | Content | Frame |
|---|---|---|
| 33 GNSS | Ø25 patch + u-blox/NavIC-module footprint (unpopulated or receiver-only) | B |
| 32 Angle sensor | AS5600 magnetic rotary encoder + Hall index | B→A sense |
| 31 Controller | ESP32-S3 (or RP2040) + IMU footprint (display only) + BLE | B |
| 30 Power | 3-phase rectifier → boost harvester → supercap management → 3V3 LDO | B |
| 35 Angle magnet+index | encoder magnet on housing-side stub, index flag | A→B sense |

**Upgrade over the index marker:** the single Hall index gives one pulse/rev.
Add the AS5600 (magnet on FRAME A stub, chip on FRAME B board) → continuous
12-bit relative angle, ₹150, I²C. This single change makes the demo read like a
real control loop instead of a blink.

### 6.2 Power tree
```
shell spin (A) → rotor magnets → stator coils (B) → 3φ rectifier
   → ultra-low-V boost → 2.7 V supercap (10–25 F) → 3.3 V LDO
   → MCU + AS5600 + OLED (burst duty) + torque emulator (only while steering demo)
```
Budget: MCU+encoder+BLE ≈ 100 mW duty-cycled → a 25 F/2.7 V cap from 2.0→2.7 V
stores ~7.4 J ≈ 70 s of demo operation per charge cycle. Fine for a stand demo;
if it's tight, OLED only on demand.

### 6.3 Firmware (display-only, ~200 lines)
1. Read AS5600 angle → OLED: "REL ANGLE 213.4° | V Harvest 0.62 V | CAP 78%".
2. Torque emulator micro-moves carrier to a commanded angle ( potentiometer or
   BLE slider) → shows "steering" live.
3. BLE advertises the same values to the laptop dashboard.
No navigation, no fuze logic, nothing connected to anything dangerous.

### 6.4 Mock setter app (E_fuze, Krupa)
Phone screen mock: target grid → mode (PD/MT/VT) → "SET" → shows the same
SAFE/SET/ARMED slider state. Rendered on a phone/tablet next to the rig; the
slider on the model moves by hand in sync. Label: "concept UI — no live fuze".

---

## 7. GNC story (simulation side, C_gnc — how the angle readout ties in)

From `simulate_trajectory_155.py`: 3-DOF ISA + M107 Cd(Mach), ZEM (zero-effort-
miss) steering, `TGUIDE = 0.1 s`, `DGUIDE = 2 m` dead-zone, canard authority
`CLS_CAN = 0.005 m²`, capped at `A_MAX = 3 g`. At 3 g held for the last ~20 s
the authority is ~5.9 km vs a ~267 m miss — **20× margin** is the number to say
out loud at the demo.

Dashboard during the demo:
- Left: ballistic vs guided trajectories (two runs of the sim, pre-computed +
  one live run with slider-changed wind to show re-convergence).
- Right: live bench telemetry — carrier angle θ(t) from AS5600, harvest voltage,
  supercap. The narrated link: *"the sim commands a roll angle ψ to point the
  lift vector at the miss; the bench shows exactly that angle being held."*

Monte Carlo CEP histogram (1000 runs, randomised v₀/wind/sensor errors) prints
CEP ≤30 m — presented strictly as **simulation result**, per briefing §1.

---

## 8. Build & integration plan (maps to W2, Sep 8–14)

| Step | Task | Owner | Est. |
|---|---|---|---|
| 1 | Regenerate CAD with bearing + alternator upgrades (§5) | Naman | 2 d |
| 2 | Print housing/carrier/canards/nose (PLA, 0.2 mm, 25% infill; canards 0.12 mm) | Naman | 3 d print |
| 3 | Wind 6 stator coils (600 T, 0.1 mm Cu), bond magnets, set 0.8 mm gap | Naman+Anvita | 1 d |
| 4 | Power PCB v1: rectifier + boost + supercap; verify 2.7 V charge at 600 rpm | Anvita | 2 d |
| 5 | Controller PCB v1: ESP32-S3 + AS5600 + OLED; firmware §6.3 | Anvita | 2 d |
| 6 | Bench stand: guarded acrylic tube, 775 motor + belt 1:2, e-stop, tach | Member 5 | 2 d |
| 7 | Integrate on stand → telemetry → dashboard → rehearse script | All | 2 d |

---

## 9. Safe operating envelope (the guardrails of the demo)

1. **Speed cap: 600 rpm.** Tach verified, e-stop, polycarbonate guard around the
   full rotating envelope (Ø151 canard span × 228 mm). No spectators reach-in.
2. **Drive only FRAME A** via the stand spindle; never free-run the module.
3. **Retention:** stand spindle cup positively retains the adapter; a printed
   delrin-style keeper ring prevents axial walk at speed.
4. **Balance check** before every run: spin to 100 rpm, watch for wobble >2 mm
   TIR, add tape weights to canard roots. Unbalanced Ø151 span at 600 rpm is the
   one real hazard — treat it as such.
5. **Electrical:** everything ≤5 V, supercap discharged via resistor before
   handling. No LiPo on the demo table.
6. **Claims discipline:** signage — "INERT EXHIBITION MODEL · NON-LAUNCHABLE ·
   PERFORMANCE FIGURES ARE SIMULATION". Rehearse the boundary sentence (§1).

---

## 10. Bench test plan (I_test — evidence we show, not claims we make)

| # | Test | Pass criterion | Evidence |
|---|---|---|---|
| T1 | Spin + power harvest, 600 rpm | Supercap ≥2.5 V in ≤3 min | Video + log |
| T2 | Angle accuracy | AS5600 vs protractor ≤2° over 360° | Photo series |
| T3 | Torque emulator hold | Holds carrier within ±3° against cogging at 600 rpm shell spin | Video |
| T4 | Endurance | 10 × 3-min runs, no bearing temps >45 °C, no debris | Log |
| T5 | Drop (inert integrity) | 1 m onto plywood, housing only, no crack, re-runs | Video |
| T6 | Sim verification | Monte Carlo rerun reproduces CEP ≤30 m ±5 m | `out_sim/` + notebook |

---

## 11. Cost — demo build (not the ₹8–11 L production estimate)

| Item | ₹ |
|---|---|
| Printed parts (filament + 2 spares of canards/nose) | 1,500 |
| 2× thin-section bearings, steel balls, grease | 1,200 |
| Magnets (N52, 8+spares) + 0.1 mm Cu wire | 900 |
| ESP32-S3, AS5600, OLED, PCBs, passives | 2,500 |
| Supercap + boost harvester + rectifier | 800 |
| N20 torque emulator + pinion/ring gears | 400 |
| Stand (motor, belt, guard, e-stop, tach) | 3,500 |
| Signage, tools, consumables | 1,200 |
| **Demo total** | **≈ ₹12,000** |

---

## 12. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| EMF too low at allowed speed | Power demo flops | §5.6 design margin (N=600, B=0.5 T, gap ≤0.8 mm); fallback LED-per-magnet-pass cue |
| Canard wobble at 600 rpm | Safety | TIR balance check before every run; hard speed cap |
| Carrier seizes (printed bearing) | Demo stops | Real thin-section bearings in v1, not printed races |
| Judges ask "is this flight hardware?" | Credibility | Boundary script + signage; sim is the performance evidence, and it's honest |
| AS5600 cross-axis error from magnet misalignment | Bad readout | 3D-printed magnet jig; 1° magnet truing pass |

---

## 13. Open decisions (needed before Sep 6 freeze review)

1. Bearing spec final: catalogue thin-section (45×52×5) vs custom race — pick by Sep 2.
2. Boost harvester: discrete flyback (parts on hand) vs LTC3108 module (₹600, faster) — Anvita.
3. Dashboard: reuse `out_sim` charts live vs pre-rendered video fallback — Member 5.
4. Does the module keep the inspection window at demo speed, or fit a clear
   polycarbonate housing sleeve instead? — Naman, after T4.

*Cross-refs: `cad_models/PGK_155MM_ASSEMBLY.md` (active baseline) ·
`PGK_155mm.FCStd` (dims) · `cad_models/simulate_trajectory_155.py`
(GNC numbers in §7) · `SIH26098_TEAM_BRIEFING.md` (physics + boundary) ·
`SIH26098_Exhaustive_Ideas_Catalog.md` (A1/B1 selection rationale).*
