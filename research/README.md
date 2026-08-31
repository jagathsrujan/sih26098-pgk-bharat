# research/ — 2 Teams, 6 PS-Driven Roles

**Use your branch to know your PS deliverable.** See `../TEAM_STRUCTURE.md:1` and `../UNIVERSAL_PROMPT.md:1`.

## New Structure (use these for new work)

| Folder | Team | PS Deliverable | Legacy |
|--------|------|----------------|--------|
| `01_mech-CAA/` | MECH (1/3) | Canard Actuation Assembly + CAD of CAA | B_aero |
| `02_mech-structure/` | MECH (2/3) | Structure/Environmental/SWaP-C/Manufacturability | G_structure + H_mfg |
| `03_mech-system/` | MECH (3/3) | System Architecture + Prototype + Validation | A_system + I_test |
| `04_electronics-GNC/` | ELECTRONICS (1/3) | GNC + Sensors + Sim (CEP) | C_gnc + D_sensors |
| `05_electronics-fuze/` | ELECTRONICS (2/3) | Multi-mode Fuze (Prox/Time/Impact) | E_fuze |
| `06_electronics-embedded-power/` | ELECTRONICS (3/3) | Embedded + Power + Comms | F_power + J_integration |

**Branch naming:** `research/<role>-<github-username>` e.g., `research/01_mech-CAA-john`, `research/04_electronics-GNC-anvita`

## Legacy (kept for history)

`A_system/`, `B_aero/`, `C_gnc/`, `D_sensors/`, `E_fuze/`, `G_structure/`, `I_test/` — 7 entries from Aug 25-26. New entries go to `01_`–`06_` folders. `merge.py` scans both.

## Quick Add

```bash
cp templates/entry_template.md 01_mech-CAA/entry_20260831_my_topic.md
# fill URL, TRL, Cost, Indian Path
python3 ../research/merge.py  # from repo root: python3 research/merge.py
git add . && git commit -m "feat(01-CAA): ..." && git push
```

See `templates/UNIVERSAL_ONBOARDING_PROMPT.md:1` for branch-based auto-assign and `templates/agent_prompt.md:1` for AI researcher prompt.
