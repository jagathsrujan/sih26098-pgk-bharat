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
├── research/                    # Team research entries (A–J categories)
│   ├── A_system/ ... I_test/    # One folder per role, 7 entries now
│   ├── templates/entry_template.md
│   ├── templates/agent_prompt.md
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

**Pick a role → add research:**

| # | Role | Folder | Focus |
|---|------|--------|-------|
| 1 | System / Cost | `research/A_system` | Architecture, SAMM, DCPP |
| 2 | Aero / Canard | `research/B_aero` | Fin trim, bearing joint |
| 3 | GNC | `research/C_gnc` | PID/MPC, 6DOF |
| 4 | Sensors | `research/D_sensors` | NavIC/IMU/baro |
| 5 | Fuze | `research/E_fuze` | FMCW, S&A |
| 6 | Power | `research/F_power` | Battery, harvest |
| 7 | Structure | `research/G_structure` | High-G, forging |
| 8 | Test | `research/I_test` | 6DOF, Monte Carlo |

```bash
cp research/templates/entry_template.md research/<category>/entry_20260831_<topic>.md
# fill URL (mandatory), TRL, Cost, Indian Path (YIL/BEL/ARDE)
python3 research/merge.py   # preview
git add . && git commit -m "feat(B): fin flutter CFD" && git push  # → LIVEBOARD auto
```

## Quick Start — AI Agents

**Copy-paste this as your first message:**

```
You are my SIH26098 agent. Repo: https://github.com/jagathsrujan/sih26098-pgk-bharat
Read in order: README.md → SIH26098_TEAM_BRIEFING.md → cleansheet/03_DESIGN_REPORT.md (Rev 1.3) → cleansheet/HANDOFF.md
Then: research/templates/entry_template.md + research/templates/agent_prompt.md + SIH26098_LIVEBOARD.md
List research/ and count entries: ls -R research
Ask me 7 onboarding questions (name/skills/interest/hours/ownership/prior/X-factor), then assign ONE category and create my welcome entry.
Rules: URL mandatory, TRL justified, Indian Path required, quote paths with spaces, never invent URLs.
```

Full onboarding prompt: `research/templates/UNIVERSAL_ONBOARDING_PROMPT.md:1`

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

## Deliverables

- [x] Architecture — `03_DESIGN_REPORT.md` Rev 1.3
- [x] CAD — `PGK_CleanSheet.FCStd` Assembly+Sim + bench in `cad_models/`
- [x] GNC sim — `sim_gnc_check.py` Rev D (295k frames) + q-scaled validation
- [ ] 6DOF + Monte Carlo ≥1000 → CEP ≤30 m (roadmap §10)
- [x] PoC — inert bench (guarded) + CAD sim frames
- [x] Cost — `02_BOM` Rev 1.2: ₹0.7–0.9 L @1k

---

## Key Docs

| Doc | Purpose |
|-----|---------|
| `SIH26098_TEAM_BRIEFING.md:1` | PS breakdown, glossary, 3-week plan |
| `SIH26098_Exhaustive_Ideas_Catalog.md:1` | 108 ideas, 30+ sources (A–J) |
| `cleansheet/03_DESIGN_REPORT.md:1` | Master design (315 lines) |
| `cleansheet/02_BOM...md:1` | BOM, fits, costing, §G deltas |
| `research/templates/entry_template.md:1` | Research entry format |
| `SIH26098_LIVEBOARD.md:1` | Auto-generated board |

---

## References

- PS: `SIH2026_Hardware_PS.json:349`, `SIH2026_Hardware_PS.md:647`
- Bench: `cad_models/PGK_DEMO_ASSEMBLY.md:1`, `legacy/old_two_motor_design/README.md:1` (superseded)
- Archive: `docs/archive/` (PS dumps, HTML viewers)

> **Boundary:** Inert exhibition design only — no energetics, no live S&A. Flight performance via simulation.
