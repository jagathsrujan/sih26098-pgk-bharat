# SIH26098 — Low-Cost PGK + Smart Fuze for 155mm

**PS:** `SIH26098` | **Org:** Yantra India / MoD | **Guns:** ATAGS/Dhanush/K9/M777 (39/45/52 cal) | **Deadline:** 20 Sep 2026 | **Target:** CEP ≤30m, ₹8–11L/kit

> Screw-in guidance kit replacing the standard fuze. **Single time-share machine:** one ring
> PMSM acts as spin-windmill alternator during ascent, then as the fin-actuator servo during
> terminal correction. Supercapacitor energy, no battery, no cold gas. Inert exhibition design —
> flight performance is simulation only.

---

## ⭐ Read This First — Design of Record (2026-09-01)

| What | Where | Status |
|------|-------|--------|
| **MAIN SPEC** — mission, motor, energy, sensors, loads, standing process | **`cad_models/PGK_SPEC_SHEET.md`** | Living main document — every design item extends it |
| **MAIN CAD** — canonical assembly (single time-share machine) | **`cad_models/PGK_Motor_Assembly.FCStd`** | FreeCAD 1.1.3, verified: 0 clashes, bore clear, Ø108 in envelope |
| **CAD conventions + file inventory** | `cad_models/README.md` | One Body per part, global coords, datum z=125, Ø30 through-bore reserved |
| **Part files** | `cad_models/parts/` | S-series = current; M01/M04/M09/M10 shared; M02/M03/M05–M08 = dual-rotor reference |

**Agents:** read `AGENTS.md` first — it declares the main design, the reference hierarchy, the
standing process, and the FreeCAD scripting gotchas we already paid for.

**Humans:** read `cad_models/PGK_SPEC_SHEET.md` → `cad_models/README.md` → `AGENTS.md`.

**Design in one line:** the shell spins (15,480 rpm) — a windmill pair spins the machine's
rotor, which generates and charges an annular supercap (875 J) during ascent; at apogee the
machine regen-brakes, mode-switches, and becomes a torque servo that roll-phases four
mirror-pitched fins (±12°, reverse + parallel pairs) for terminal course correction. No battery.
No thrusters. The Ø30 through-bore leaves the shell's explosive train untouched.

---

## Design hierarchy (what is current vs reference vs legacy)

1. **Main design — `cad_models/`**: `PGK_SPEC_SHEET.md` (living spec) + `PGK_Motor_Assembly.FCStd`
   (canonical single-machine assembly) + `parts/` + `PGK_155mm_Envelope.FCStd` (zones).
   `PGK_Motor_Assembly_DUAL_reference.FCStd` = dual-rotor trade-study reference.
2. **Superseded reference — `cleansheet/` (Rev 1.7) + `electronics/`**: prior architecture
   (de-spin motor + slip ring + NMC battery + Ø138 one-piece canard). **Superseded as design of
   record** by the single-machine design — but its GNC methodology (CEP50 21.5 m sims),
   sensor-selection error budgets, flight-software structure, KiCad skeleton and costing work
   remain valuable engineering references. Do not extend its architecture.
3. **Living research — `research/` + `SIH26098_LIVEBOARD.md`**: 6 team folders, evidence entries.
4. **Archive — `legacy/`**: superseded designs and dead concepts (incl. cold-gas, rejected by
   calculation — see `legacy/README.md`). New work never goes here.

---

## Latest Progress — 2026-09-01

### Current design (cad_models — single time-share machine)

| Area | Status | Evidence |
|------|--------|----------|
| Motor CAD | Dual→single variant modeled, assembled in envelope, verified: 0 clashes at all rotor phases, Ø30 bore clear z0→173, Ø108.1 max external | `cad_models/PGK_Motor_Assembly.FCStd` · `out/single_motor_*.png` |
| Main spec sheet | Mission timeline (Phase 0 pre-fire + flight), motor/electrical spec, energy ledger, canard loads, sensor stack, standing process | `cad_models/PGK_SPEC_SHEET.md` |
| Actuation concept | Cold gas rejected by calculation; fin actuation via magnetic ring motor adopted; fin scheme corrected to reference (reverse-differential + parallel pairs, ±12°) | `legacy/SIH26098_COLDGAS_PHYSICS_EVAL.md` · `research/SIH26098_leadingpgk_site_articles_extract.md` |
| Sensors | Military-grade stack selected: SiIMU02-class gun-hard IMU, SAC NavASIC V3 (NavIC+GPS), RM3100-class roll sensing, C2000-class dual-core, FRAM | spec sheet §9 |

### Prior lineage (cleansheet Rev 1.7 — superseded as architecture, methods remain reference)

| Area | Achievement | Evidence |
|------|-------------|----------|
| **GNC** | Rev E terminal-accuracy gate closed at the 3DOF rung: **CEP50 21.5 m** vs ≤30 m PS M2, **9.9×** vs unguided, 250/250 runs | `cleansheet/out_sim/RESULTS_GNC.md` |
| **Flight software** | Deterministic Python reference FSW; paired co-sim parity; 33/33 tests green | `cleansheet/flight_sw/` · `out_sim/RESULTS_FSW.md` |
| **Sensors (error budget)** | Five sensors datasheet-flowed; baseline/selected/worst-case all pass (21.5/21.7/21.1 m) | `cleansheet/05_SENSOR_SELECTION.md` |
| **Electronics** | Dual-domain split locked; KiCad skeleton ERC-clean (34 comps/170 nodes) | `cleansheet/06_ELECTRONICS_ARCHITECTURE.md` · `electronics/` |
| **System & cost** | Rev 1.7 BOM: ~1.88 kg, ₹30,800 @1k | `cleansheet/03_DESIGN_REPORT.md` · `02_BOM...md` |

> **Note:** the lineage above was built around a de-spin motor, slip ring and NMC battery.
> Those architectural elements are superseded; the analysis methods, sims and error budgets
> carry over as references and should be re-run against the single-machine design.

---

## Repo Map

```
.
├── AGENTS.md                      # ★ Start here for any agent — main-design declaration
├── cad_models/                    # ★ MAIN DESIGN
│   ├── PGK_SPEC_SHEET.md          #   living system spec (standing process = §11)
│   ├── README.md                  #   CAD conventions + file inventory
│   ├── PGK_Motor_Assembly.FCStd   #   canonical single-machine assembly (FreeCAD 1.1.3)
│   ├── PGK_155mm_Envelope.FCStd   #   design envelope zones + datum z=125
│   ├── parts/                     #   S-series (current) + M-series (current/shared/reference)
│   ├── PGK_Motor_Assembly_DUAL_reference.FCStd   # dual-rotor trade study (reference)
│   ├── PGK_155MM_ASSEMBLY.md · out_pgk/ · render_pgk_155mm.py · simulate_trajectory_155.py
│   │                              #   earlier 155mm exhibition model (reference only)
│   └── out/                       #   renders + verification shots
├── cleansheet/                    # Superseded reference lineage (Rev 1.7) — sims, methods, BOM
│   ├── PGK_CleanSheet.FCStd · 03_DESIGN_REPORT.md · 05_SENSOR_SELECTION.md
│   ├── 04_GNC_METHODOLOGY.md · 06_ELECTRONICS_ARCHITECTURE.md · 00_REQUIREMENTS.md
│   ├── flight_sw/ · out_sim/ · scripts/ · HANDOFF.md
├── electronics/                   # KiCad GNC-board skeleton from the lineage (ERC clean)
├── research/                      # 6 team folders + D_sensors + templates + merge.py → LIVEBOARD
├── legacy/                        # Archive (cold gas, old CAD lineages) — never add work here
├── .github/workflows/research-sync.yml
├── SIH2026_Hardware_PS.*          # Official PS (csv/json/md)
├── SIH26098_COTS_BOM.* · SIH26098_FLIGHT_KIT_BOM.*   # BOMs from the prior design — resync before reuse
├── SIH26098_Exhaustive_Ideas_Catalog.md · SIH26098_Ideas_Database.json (+csv)
├── SIH26098_LIVEBOARD.md          # Auto-generated research board
├── SIH26098_TEAM_BRIEFING.md · TEAM_STRUCTURE.md · UNIVERSAL_PROMPT.md
├── SIH26098_TERMINAL_KICKER_EVAL.md            # trade study (reference)
├── GuidanceKit_Thesis_Explainer.html · pgk_3d_viewer.html · SIH26098_PS_Infographic.html
└── briefing-*.png · thesis_images/ · 10463953.pdf
```

---

## Quick Start — Humans

```bash
git clone https://github.com/jagathsrujan/sih26098-pgk-bharat.git
cd sih26098-pgk-bharat
# 1. Main design
cat cad_models/PGK_SPEC_SHEET.md
open cad_models/PGK_Motor_Assembly.FCStd      # FreeCAD 1.1.3
# 2. Team briefing + research process
cat SIH26098_TEAM_BRIEFING.md
# 3. Reference lineage sims/tests (methods — architecture superseded)
python3 cleansheet/scripts/sim_guidance_check.py
python3 -m pytest cleansheet/flight_sw/tests/ -q
```

**Your team → Your PS deliverables (branch tells the agent your role):**

**TEAM MECH — 3 members (Mechanical)**
| # | Role | Folder | PS Deliverable | Focus |
|---|------|--------|----------------|-------|
| 1 | MECH-CAA | `research/01_mech-CAA/` | Canard Actuation Assembly + CAD of CAA | 4-fin mechanism, deployment, aero, bearing joint |
| 2 | MECH-Structure | `research/02_mech-structure/` | Environmental + SWaP-C + Manufacturability | 15,000g, STANAG fit, mass, YIL forging, cost |
| 3 | MECH-System | `research/03_mech-system/` | System Architecture + Prototype + Validation | Assembly, 6DOF/Monte Carlo, CEP ≤30m |

**TEAM ELECTRONICS — 3 members (1 EEE + 2 ECE)**
| # | Role | Folder | PS Deliverable | Focus |
|---|------|--------|----------------|-------|
| 4 | ELECTRONICS-GNC | `research/04_electronics-GNC/` | GNC + Sensors + Sim | Guidance methodology, IMU/GNSS/baro, flight control, trajectory sim |
| 5 | ELECTRONICS-Fuze | `research/05_electronics-fuze/` | Multi-mode Fuze | Proximity/Time/Impact, FMCW, S&A, safety |
| 6 | ELECTRONICS-Embedded | `research/06_electronics-embedded-power/` | Embedded + Power + Comms | Real-time HW/SW, power high-g, programming interface, block diagram |

```bash
git checkout -b research/01_mech-CAA-<github-username>
cp research/templates/entry_template.md research/01_mech-CAA/entry_20260831_<topic>.md
python3 research/merge.py
git add . && git commit -m "feat(01-CAA): fin hinge trade" && git push  # → LIVEBOARD auto
```

## Quick Start — AI Agents

**Share this ONE prompt with teammates — branch tells the agent the PS task:**

```
You are my SIH26098 Onboarding Agent. Repo: https://github.com/jagathsrujan/sih26098-pgk-bharat
Run: git branch --show-current → tell me your branch. If on main, tell me which of 6 roles you want (01_mech-CAA ... 06_electronics-embedded-power).
Read: AGENTS.md (main-design declaration) → cad_models/PGK_SPEC_SHEET.md (main spec) → cad_models/README.md (CAD conventions) → research/<your-role>/README.md (your PS tasks) → SIH26098_LIVEBOARD.md
Ask 7 questions (name/github/branch/skills/interest/hours/ownership/prior), then assign ONE of 6 PS roles based on branch + skills, create branch if on main, and make welcome entry.
Rules: URL mandatory, TRL justified, Indian Path (YIL/BEL/ARDE) required, never invent URLs. Design answers must follow the main design in AGENTS.md.
```

**Agent rules:**
- Quote paths with spaces: `"/home/.../smart india hackathon"`
- Main design first: `AGENTS.md` → `cad_models/PGK_SPEC_SHEET.md` → `cad_models/README.md`
- One `entry_YYYYMMDD_topic.md` per finding, with real URL + accessed date
- Run `research/merge.py` before push, check `SIH26098_LIVEBOARD.md`
- `cleansheet/` + `electronics/` are superseded references — cite methods, don't extend architecture
- FreeCAD: see the gotchas in `AGENTS.md` (LinkPlacement, rotated revolutions, remove-by-name…)

---

## Design of Record — Single Time-Share Machine (2026-09-01)

**CAD:** `cad_models/PGK_Motor_Assembly.FCStd` — FreeCAD 1.1.3; parts: S01 stator (12s/10p,
Ø58.5, 25 mm zone), S02 coils, S04 rotor (Ø70 ring, 10 N42SH arcs), S05/S06 fins (±12°,
Ø76–108), M01 shaft tube (Ø40/Ø30), M04 PCB, M09 bearings ×2, M10 endbells, S09 supercap
stack (annular, 0.6 F @ 54 V, 875 J, fuze-well zone). Verified: 0 clashes at all rotor phases,
Ø30 through-bore clear, Ø108.1 max external, ~725 g motor module + 67 g caps.

**Mission:** Phase 0 pre-fire programming (inductive setter: BIT, IMU bias, NavIC/GPS
ephemeris → FRAM) → launch → windmill generation 10–15 W charging the stack → apogee mode
switch (regen brake) → FOC roll-phase hover of the fin pairs → terminal correction → impact.

**Specs:** `cad_models/PGK_SPEC_SHEET.md` — Kt ≈ 0.095 N·m/A, hold 0.2–0.25 N·m, peak 1.5 N·m,
canard loads 4–6 N nominal / 13 N peak / 1.3 kN centrifugal per fin, energy ledger 450 J
generated vs 344 J consumed (28% margin), sensors per §9 (SiIMU02-class IMU, SAC NavASIC V3,
RM3100-class roll sensor, C2000-class dual-core).

**Prior architecture (reference):** cleansheet Rev 1.7 — de-spin motor + slip ring + NMC
battery + one-piece Ø138 canard; GNC CEP50 21.5 m; 1.88 kg; ₹30.8k @1k. Superseded; methods
reused, architecture retired.

---

## Deliverables (from PS)

| PS Deliverable | Owner (Team) | Main file | Reference inputs |
|---|---|---|---|
| System architecture | MECH-System (03) | `cad_models/PGK_SPEC_SHEET.md` | `cleansheet/03_DESIGN_REPORT.md` (methods) |
| CAD of CAA | MECH-CAA (01) | `cad_models/PGK_Motor_Assembly.FCStd` + `parts/` | `cleansheet/PGK_CleanSheet.FCStd` (joint patterns) |
| Electronics block diagram | ELECTRONICS-Embedded (06) | spec sheet §2.3/§9 | `cleansheet/06_ELECTRONICS_ARCHITECTURE.md` + `electronics/` |
| GNC algorithm | ELECTRONICS-GNC (04) | spec sheet §3 + `cleansheet/scripts/sim_gnc_check.py` | `cleansheet/04_GNC_METHODOLOGY.md` |
| Trajectory-correction sim | ELECTRONICS-GNC (04) + MECH-System (03) | re-run against single-machine model | `cleansheet/out_sim/RESULTS_GNC.md` |
| Prototype / PoC | MECH-CAA+Structure (01+02) | `cad_models/` | bench demonstrator lineage |
| Performance CEP ≤30m | ELECTRONICS-GNC (04) + MECH-System (03) | Monte Carlo ≥1000 on new model | `cleansheet/out_sim/RESULTS*.md` |
| Fuze (Prox/Time/Impact) | ELECTRONICS-Fuze (05) | spec sheet §9 (to extend) | `cleansheet/03_DESIGN_REPORT.md:4.6` |
| Power + Comms + Embedded | ELECTRONICS-Embedded (06) | spec sheet §2.3/§5 | `cleansheet/06_ELECTRONICS_ARCHITECTURE.md` |
| Manufacturability & Cost | MECH-Structure (02) | BOM resync pending vs S-series | `cleansheet/02_BOM...md` (costing method) |

---

## Key Docs

| Doc | Purpose |
|-----|---------|
| `AGENTS.md` | Main-design declaration + rules for any agent |
| `cad_models/PGK_SPEC_SHEET.md` | **Main living spec** (mission, motor, energy, sensors, process) |
| `cad_models/README.md` | CAD conventions + file inventory |
| `TEAM_STRUCTURE.md` / `UNIVERSAL_PROMPT.md` / `SIH26098_TEAM_BRIEFING.md` | Team + PS onboarding |
| `research/templates/entry_template.md` | Research entry format |
| `SIH26098_LIVEBOARD.md` | Auto-generated research board |
| `cleansheet/03_DESIGN_REPORT.md` · `04_GNC_METHODOLOGY.md` · `05_SENSOR_SELECTION.md` · `06_ELECTRONICS_ARCHITECTURE.md` | Superseded-architecture references (methods still cited) |
| `SIH26098_Exhaustive_Ideas_Catalog.md` | 108 ideas, 30+ sources |

---

## References

- PS: `SIH2026_Hardware_PS.json`, `SIH2026_Hardware_PS.md`
- Archive: `legacy/` (see `legacy/README.md` — cold gas, old CAD lineages, docs dumps)

> **Boundary:** Inert exhibition design only — no energetics, no live S&A. Flight performance via simulation.
