---
id: WELCOME-G-naman-20260826
category: G_structure
author: @naman
date: 2026-08-26
source_type: assignment
trl: N/A
---

## Idea Title
Welcome — Naman (Mechanical) — G_structure Primary + F_power Backup

## Summary
Assigned primary: **G_structure (Structure/Materials/High-G Survivability G1-G10)** — best fit for Mechanical core. Owns 155mm body forging, fuze housing, bearing shield, potting/thermal, radome, and 15,000g survivability. Backup: **F_power** — Body Builder synergy (alternator + super-cap housing shares same structure). Mech owns the entire "Body Builder" #5 deliverable in README.md.

## Why This Fit (Decision Logic)
- Skills: Mechanical Engineering → G_structure needs forging/machining (YIL), FEA (ANSYS), materials (Inconel 718 vs 316L anisotropy), bearing 630 inertial shield, potting RTV 3140 → pure Mech.
- Catalog gap: research/G_structure/ had 0 entries before this → you own the critical path (without structure surviving 15kG, no other subsystem works).
- Indian Path lever: YIL Ambajhari forging + 10,000-ton extrusion press (19 June 2026) + BEL/ECIL potting + ARDE bourrelet nubless design → all Mech manufacturing.
- Backup F_power shares housing/power integration → you deliver the full 3D printed body + power test for SIH demo.

## Assignment
- **Primary: G_structure (Structure, Materials & Survivability)** — Owns G1-G10, CAD, FEA, material choice, high-G potting
- **Backup/Secondary: F_power (Power Systems)** — Support super-cap/alternator housing & thermal
- Branch: `research/G_structure-naman` (rename to `research/G_structure-<your-github-username>` after you share username)

## First 3 Research Questions (gaps in catalog)
1. **G3 vs G4 material trade:** Inconel 718 LPBF vs 316L vs Ti64 for fuze housing — which survives 15kG + thermal -46 to +71°C best? Find Indian supplier (YIL/Bharat Forge) cost/kg, HIP + solution anneal data, anisotropy scatter (CrucibleInsight: 148-227GPa). [Source: CrucibleInsight AM-structural, HDIAC 3D printed ammo]
2. **G5 + G9 potting & thermal:** Dow Corning RTV 3140 vs indigenized RTV (YIL DRISHTI Challenge 60) for PCB potting — does CTE mismatch crack solder over Ladakh day-night cycling? Test Invar vs Al housing for thermal stress compensation. [Source: YIL DRISHTI Challenge 60, MIL-STD-331 thermal shock]
3. **G6 + G8 bearing & radome:** Bearing 630 inertial shield (Pat 10295320) isolation of 25kG + quartz/polycarbonate radome RF transparency at NavIC L5 (1176MHz) & GPS L1 — what wall thickness keeps loss <1dB while surviving aero heating 830m/s? [Source: Pat 10295320, G8 radome spec]

## Next 3 Concrete Tasks
1. Read `SIH26098_Exhaustive_Ideas_Catalog.md` §7 Category G (G1-G10) and `SIH26098_Ideas_Database.json` G1-G10 entries — pick G3 or G6 to deep-dive first.
2. Run `research/templates/agent_prompt.md` with `{CATEGORY}=G_structure` via your AI agent — create `research/G_structure/entry_20260827_<topic>.md` for question 1 above (with URL + TRL + cost ₹L + Indian Path YIL/BEL/ARDE).
3. Checkout branch and push (after updating username): `git checkout research/G_structure-naman && git add research/G_structure/entry_20260826_welcome_naman.md && git commit -m "feat(G): welcome naman — Mech -> G_structure primary + F_power backup" && git push -u origin research/G_structure-naman` then `python3 research/merge.py`.

## Links to Code/CAD
- `research/G_structure/` (your folder - currently 0 entries, you are first!)
- `cad_models/generate_pgk_155.py` (run to get 155mm housing CAD)
- `cad_models/generate_shell_155.py` (inert mockup)
- `research/templates/agent_prompt.md` (paste with G_structure)
- `research/templates/entry_template.md`
- `SIH26098_Exhaustive_Ideas_Catalog.md:152-166` Category G

## Source
- Invite: https://github.com/jagathsrujan/sih26098-pgk-bharat/invitations (accept)
- Onboarding: `ONBOARDING_PROMPT.md:1`
- Team Map: `README.md:58-65` #5 The Body Builder

## GitHub Permissions
- Repo role: **Write** (can push to research/* branches) — already granted via invite. Do NOT need Admin.
- Branch protection: push to your `research/G_structure-naman` branch, open PR to `main` for review.
