# Team Structure — SIH26098 (6 members: 3 Mech + 1 EEE + 2 ECE → 2 Teams)

**PS:** Design & Development of Precision Guidance Kit with Canard Actuation + Multi-Mode Fuze for 155mm (CEP ≤30m, YIL, 20 Sep 2026)

This repo is organized so that **your branch tells your AI agent what PS deliverable to work on**.

## 2 Teams, 6 Roles

### TEAM MECH (3 — Mechanical)
| Role | Branch Example | Folder | PS Deliverable | Key Output |
|------|----------------|--------|----------------|------------|
| 01_mech-CAA | `research/01_mech-CAA-john` | `research/01_mech-CAA/` | Canard Actuation Assembly + CAD of CAA | 4-fin mechanism, aero, `PGK_CleanSheet.FCStd` canard shell |
| 02_mech-structure | `research/02_mech-structure-priya` | `research/02_mech-structure/` | Structure + Environmental + SWaP-C + Manufacturability | 15,000g survival, STANAG fit, YIL costing, `02_BOM` |
| 03_mech-system | `research/03_mech-system-alex` | `research/03_mech-system/` | System Architecture + Prototype + Validation | Architecture doc `03_DESIGN_REPORT.md`, Assembly, 6DOF/MC |

### TEAM ELECTRONICS (3 — 1 EEE + 2 ECE)
| Role | Branch Example | Folder | PS Deliverable | Key Output |
|------|----------------|--------|----------------|------------|
| 04_electronics-GNC | `research/04_electronics-GNC-anvita` | `research/04_electronics-GNC/` | GNC + Sensors + Flight Control + Sim | Guidance methodology, IMU/GNSS, `sim_*.py` → `out_sim/`, CEP |
| 05_electronics-fuze | `research/05_electronics-fuze-krupa` | `research/05_electronics-fuze/` | Multi-mode Fuze (Prox/Time/Impact) | FMCW 24GHz HOB, S&A logic, fuze design |
| 06_electronics-embedded-power | `research/06_electronics-embedded-power-rahul` | `research/06_electronics-embedded-power/` | Embedded + Power + Comms | HW/SW block diagram, 16.7Wh power, inductive setter |

## Branch → Agent Mapping

When you clone and run:
```bash
git branch --show-current
# e.g., research/01_mech-CAA-jagathsrujan
```
Paste `research/templates/UNIVERSAL_ONBOARDING_PROMPT.md` as first message to your AI. It will:
1. Detect your branch prefix (`01`, `CAA`, `GNC`, `fuze`, `embedded`, etc.)
2. Read `research/<your-role>/README.md` (your 3 PS questions)
3. Ask 7 onboarding questions, then assign + create welcome entry `research/<role>/entry_20260825_welcome_<user>.md`
4. Co-work: searches 3 new ideas in your PS category, drafts entries with real URLs, helps with CAD/sim/block-diagram

If on `main`, tell agent which of the 6 you want — it will create the branch.

## Legacy Mapping (for history)

Old A-J folders → New 01-06:
- A_system → 03_mech-system
- B_aero → 01_mech-CAA
- C_gnc + D_sensors → 04_electronics-GNC
- E_fuze → 05_electronics-fuze
- F_power + J_integration → 06_electronics-embedded-power
- G_structure + H_mfg → 02_mech-structure
- I_test → shared (03 + 04)

New work uses `01_`–`06_` folders. `research/merge.py` auto-merges both old and new into `SIH26098_LIVEBOARD.md`.

## How Teams Integrate

- **MECH** integrates CAD/structure at `cleansheet/` (FCStd Assembly, BOM mass/cost)
- **ELECTRONICS** integrates GNC/fuze/power at `cleansheet/02_BOM` + block diagrams
- **Both** meet at `03_mech-system` for final system architecture (`03_DESIGN_REPORT.md`) and at `out_sim/` for CEP proof

See `SIH26098_TEAM_BRIEFING.md` for PS breakdown + artillery 101, and `research/templates/UNIVERSAL_ONBOARDING_PROMPT.md` for the shareable AI prompt.
