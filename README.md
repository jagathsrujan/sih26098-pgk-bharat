# SIH26098 — Low-Cost PGK + Smart Fuze for 155mm

**PS:** `SIH26098` | **Org:** Yantra India / MoD | **Guns:** ATAGS/Dhanush/K9/M777 (39/45/52 cal) | **Deadline:** 20 Sep 2026 | **Target:** CEP ≤30m, ₹8–11L/kit

> Screw-in guidance kit replacing the standard fuze. 3-frame architecture: shell spins (250 rev/s), rotor is de-spun & roll-aimed, fin pair steers. Inert exhibition design — flight performance is simulation only.

---

## TL;DR for Teammates & Agents

| What | Where | Status |
|------|-------|--------|
| **Design of record** — CAD + docs + sim | `cleansheet/` | **Rev 1.3** (Aug 31) — Assembly + GNC sim done |
| **Bench demonstrator** — inert, low-speed | `cad_models/` | Separate exhibition artifact, not the design |
| **Research board** — 108 ideas, 7 entries | `research/` + `SIH26098_LIVEBOARD.md` | Push → auto-updates |

**Read first:** `SIH26098_TEAM_BRIEFING.md` (PS + artillery 101 + roles) → `cleansheet/03_DESIGN_REPORT.md` (design) → `cleansheet/PGK_CleanSheet.FCStd` (CAD).

**Team = 6 (3 Mech + 1 EEE + 2 ECE → 2 teams):** `research/01_mech-CAA/` … `03_mech-system/` (MECH) and `research/04_electronics-GNC/` … `06_electronics-embedded-power/` (ELECTRONICS). Branch name tells the AI your PS task.

**Universal prompt to share:** `research/templates/UNIVERSAL_ONBOARDING_PROMPT.md:1` — paste as first message to any AI, tell it your `git branch --show-current`, it assigns your PS deliverable and co-works.

---

## Repo Map

```
.
├── cleansheet/                  # ★ Design of record (Rev 1.3)
│   ├── PGK_CleanSheet.FCStd     # FreeCAD 1.1.3 — 24 links, 23 joints, 122-frame Simulation
│   ├── 03_DESIGN_REPORT.md      # Master report (§2.4 Assembly, §4 subsystems, §10 sim)
│   ├── 02_BOM_MANUFACTURING_ASSEMBLY.md  # BOM + fits + costing
│   ├── 00_REQUIREMENTS.md       # PS-derived requirements (M/L/P/F/S)
│   ├── HANDOFF.md               # Build provenance + how to play simulation
│   ├── out_sim/                 # Sim results + plots (RESULTS.md, RESULTS_GNC.md)
│   └── scripts/                 # FreecadCmd + trajectory sims (gated, headless)
├── research/                    # 2 teams × 3 roles = 6 PS-driven folders
│   ├── 01_mech-CAA/ ... 03_mech-system/      # TEAM MECH (3 mech)
│   ├── 04_electronics-GNC/ ... 06_electronics-embedded-power/  # TEAM ELECTRONICS (1 EEE + 2 ECE)
│   ├── A_system/ ... I_test/    # Legacy A-J (kept for history, use 01-06 for new work)
│   ├── templates/entry_template.md
│   ├── templates/agent_prompt.md
│   ├── templates/UNIVERSAL_ONBOARDING_PROMPT.md  # ← Share this with teammates
│   └── merge.py                 # → SIH26098_LIVEBOARD.md (run on push)
├── cad_models/                  # Bench demonstrator (not design of record)
│   ├── generate_pgk_155.py
│   ├── PGK_DEMO_ASSEMBLY.md
│   └── simulate_trajectory_155.py
├── legacy/old_two_motor_design/ # Superseded — keep for history
├── .github/workflows/research-sync.yml
├── SIH2026_Hardware_PS.*        # Official PS (csv/json/md)
├── SIH26098_Excalidraw.excalidraw  # 6-panel board (problem→team)
├── SIH26098_Exhaustive_Ideas_Catalog.md  # 108 ideas, A–J
├── SIH26098_Ideas_Database.json # 110 ideas (JSON)
└── docs/archive/                # PS dumps & HTML viewers (not for daily use)
```

---

## Quick Start — Humans

```bash
git clone https://github.com/jagathsrujan/sih26098-pgk-bharat.git
cd sih26098-pgk-bharat
# 1. Read briefing + design
cat SIH26098_TEAM_BRIEFING.md
cat cleansheet/03_DESIGN_REPORT.md | head -100
# 2. Open CAD
open cleansheet/PGK_CleanSheet.FCStd  # FreeCAD 1.1.3 → Assembly → double-click Simulation → Play
# 3. Run sim
python3 cleansheet/scripts/sim_guidance_check.py   # 250-run MC → out_sim/RESULTS.md
python3 cleansheet/scripts/sim_gnc_check.py        # estimator-in-loop → out_sim/RESULTS_GNC.md
```

**Your team → Your PS deliverables (branch tells the agent your role):**

**TEAM MECH — 3 members (Mechanical)**
| # | Role | Folder | PS Deliverable | Focus |
|---|------|--------|----------------|-------|
| 1 | MECH-CAA | `research/01_mech-CAA/` | Canard Actuation Assembly + CAD of CAA | 4-fin mechanism, deployment, aero, bearing joint |
| 2 | MECH-Structure | `research/02_mech-structure/` | Environmental + SWaP-C + Manufacturability | 15,000g, STANAG fit, mass ≤1.5kg, YIL forging, cost |
| 3 | MECH-System | `research/03_mech-system/` | System Architecture + Prototype + Validation | Assembly (24 links), 6DOF/Monte Carlo, CEP ≤30m |

**TEAM ELECTRONICS — 3 members (1 EEE + 2 ECE)**
| # | Role | Folder | PS Deliverable | Focus |
|---|------|--------|----------------|-------|
| 4 | ELECTRONICS-GNC | `research/04_electronics-GNC/` | GNC + Sensors + Sim | Guidance methodology, IMU/GNSS/baro, flight control, trajectory sim |
| 5 | ELECTRONICS-Fuze | `research/05_electronics-fuze/` | Multi-mode Fuze | Proximity/Time/Impact, FMCW, S&A, safety |
| 6 | ELECTRONICS-Embedded | `research/06_electronics-embedded-power/` | Embedded + Power + Comms | Real-time HW/SW, power high-g, programming interface, block diagram |

```bash
# Your branch decides your role — create it:
git checkout -b research/01_mech-CAA-<github-username>   # or mech/CAA-<username> / electronics/GNC-<username>
cp research/templates/entry_template.md research/01_mech-CAA/entry_20260831_<topic>.md
# fill URL (mandatory), TRL, Cost, Indian Path (YIL/BEL/ARDE/ISRO)
python3 research/merge.py   # preview
git add . && git commit -m "feat(01-CAA): fin hinge trade" && git push  # → LIVEBOARD auto
```

## Quick Start — AI Agents (2-Team, Branch-Based)

**Share this ONE prompt with teammates — branch tells the agent the PS task:**

**Copy-paste this as your first message:**

```
You are my SIH26098 Onboarding Agent. Repo: https://github.com/jagathsrujan/sih26098-pgk-bharat
Run: git branch --show-current → tell me your branch. If on main, tell me which of 6 roles you want (01_mech-CAA ... 06_electronics-embedded-power).
Read: README.md → SIH26098_TEAM_BRIEFING.md → research/<your-role>/README.md (your PS tasks) → cleansheet/03_DESIGN_REPORT.md (Rev 1.3) → SIH26098_LIVEBOARD.md
Ask 7 questions (name/github/branch/skills/interest/hours/ownership/prior), then assign ONE of 6 PS roles based on branch + skills, create branch if on main, and make welcome entry.
Rules: URL mandatory, TRL justified, Indian Path (YIL/BEL/ARDE) required, never invent URLs.
```

**Universal prompt (full 4-phase, branch-based, PS-driven):** `research/templates/UNIVERSAL_ONBOARDING_PROMPT.md:1` — just paste the whole file.

**How it works:** Teammate clones → `git checkout -b research/01_mech-CAA-john` (or tells agent "I'm on 04_GNC") → agent reads `research/<role>/README.md` with 3 PS questions → co-works on that deliverable (CAD/GNC/fuze/power etc.) → pushes to that folder.

**Agent rules:**
- Quote paths with spaces: `"/home/.../smart india hackathon"`
- One `entry_YYYYMMDD_topic.md` per finding, with real URL + accessed date
- Run `research/merge.py` before push, check `SIH26098_LIVEBOARD.md`
- Keep `cleansheet/` as source of truth — don't edit CAD via GUI booleans (use `freecadcmd` gated scripts, see `HANDOFF.md:43`)

---

## Design of Record — Rev 1.3 (2026-08-31)

**CAD:** `cleansheet/PGK_CleanSheet.FCStd` — FreeCAD 1.1.3 Assembly (24 `App::Link`, 21 Fixed + 2 Revolute `J_MotorRotor`/`J_RollDecouple` + Ground) + 122-frame Simulation (30 fps, `3.1416*time` / `-1.0472*time` rad/s). Solver rc=0.

**Three frames:**

| Frame | Rotation | Members |
|-------|----------|---------|
| S — Shell | 250–267 rev/s | body, outer ring (2-12UN full-depth well), cartridge, stator, battery |
| R — Rotor | ψ-aimed | bell + magnet ring, 1-pc canard (4 fins tip Ø138, pair ±3° mirrored), radome + GNC + GNSS + prox |
| Balls Ø3×160 | de-spin joint | between S and R |

**Steering:** roll-aimed fin-pair lift (mirrored ±3° → pure radial, zero side force). Motor = de-spin (15 s @ ≤40 A boost) + steer + harvest.

**Current specs (post-GNC sim):** Mass 1.84 kg → 1.56 kg optimized (≤2.0 kg hard, ≤1.5 kg stretch) | Power 1×26500 NMC 16.7 Wh (≥18× margin, ≤0.9 Wh worst) | Cost ₹0.7–0.9 L @1k (8–12% of ceiling) | Sim CEP 6.9 m guided vs 207 m unguided (250 MC, lock 45 s → 8.5 m) — see `out_sim/RESULTS.md:1` + `RESULTS_GNC.md:1`.

**Docs:** `00_REQUIREMENTS.md:1` (M/L/P/F/S) · `02_BOM...md:1` (§G Rev 1.2 deltas) · `03_DESIGN_REPORT.md:1` (Rev 1.3 §4.5 drag-vector roll, q-scaled authority) · `HANDOFF.md:1` (how to play sim + crash lessons).

**Run sim:**
```bash
python3 cleansheet/scripts/sim_guidance_check.py   # 3DOF, 250 MC
python3 cleansheet/scripts/sim_gnc_check.py        # 12-state EKF + phasor-duty, see RESULTS_GNC.md:1
```

---

## Deliverables (from PS)

**PS Expected Outcome → Our files:**

| PS Deliverable | Owner (Team) | File | Status |
|---|---|---|---|
| System architecture | MECH-System (03) | `cleansheet/03_DESIGN_REPORT.md:1` + `cleansheet/HANDOFF.md:1` | [x] Rev 1.3 |
| CAD of CAA | MECH-CAA (01) | `cleansheet/PGK_CleanSheet.FCStd` + `cad_models/PGK_DEMO_ASSEMBLY.md:1` | [x] Assembly+Sim |
| Electronics block diagram | ELECTRONICS-Embedded (06) | `cleansheet/02_BOM...md:A4-A10` + `04_electronics` docs | [ ] Next: integrate GNC+fuze+power |
| GNC algorithm | ELECTRONICS-GNC (04) | `cleansheet/scripts/sim_gnc_check.py:1` | [x] Rev D (295k frames) |
| Trajectory-correction sim | ELECTRONICS-GNC (04) + MECH-System (03) | `sim_guidance_check.py:1` → `out_sim/RESULTS.md:1` | [x] 250 MC, 6.9m CEP |
| Prototype / PoC | MECH-CAA+Structure (01+02) | `cad_models/` + `cleansheet/` bench (guarded) | [x] Inert + sim frames |
| Performance CEP ≤30m | ELECTRONICS-GNC (04) + MECH-System (03) | `out_sim/RESULTS*.md` + Monte Carlo ≥1000 | [ ] 6DOF next (roadmap §10) |
| Fuze (Prox/Time/Impact) | ELECTRONICS-Fuze (05) | `cleansheet/03_DESIGN_REPORT.md:4.6` | [x] FMCW + S&A design |
| Power + Comms + Embedded | ELECTRONICS-Embedded (06) | `03_DESIGN_REPORT.md:5` + `02_BOM:A` | [x] 16.7 Wh, inductive setter |
| Manufacturability & Cost | MECH-Structure (02) | `02_BOM:1` §D–G | [x] ₹0.7–0.9L @1k, NRE ₹4.2Cr |

---

## Key Docs

| Doc | Purpose |
|-----|---------|
| `TEAM_STRUCTURE.md:1` | 2 teams × 6 roles — branch → PS deliverable mapping |
| `UNIVERSAL_PROMPT.md:1` | Shareable 1-prompt onboarding (also `research/templates/UNIVERSAL_...md:1`) |
| `SIH26098_TEAM_BRIEFING.md:1` | PS breakdown, glossary, 3-week plan |
| `SIH26098_Exhaustive_Ideas_Catalog.md:1` | 108 ideas, 30+ sources (A–J) |
| `cleansheet/03_DESIGN_REPORT.md:1` | Master design (315 lines) |
| `cleansheet/02_BOM...md:1` | BOM, fits, costing, §G deltas |
| `research/templates/entry_template.md:1` | Research entry format |
| `SIH26098_LIVEBOARD.md:1` | Auto-generated board |
| `research/01_mech-CAA/README.md:1` … `06_electronics-.../README.md:1` | Per-role PS tasks + 3 starter questions |

---

## References

- PS: `SIH2026_Hardware_PS.json:349`, `SIH2026_Hardware_PS.md:647`
- Bench: `cad_models/PGK_DEMO_ASSEMBLY.md:1`, `legacy/old_two_motor_design/README.md:1` (superseded)
- Archive: `docs/archive/` (PS dumps, HTML viewers)

> **Boundary:** Inert exhibition design only — no energetics, no live S&A. Flight performance via simulation.
