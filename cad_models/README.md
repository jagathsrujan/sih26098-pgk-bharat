# PGK CAD Models — Design Status & Conventions

**This folder is the design of record for the entire workspace** (declared 2026-09-01 —
supersedes the `cleansheet/` Rev 1.7 lineage; see root `AGENTS.md`). The living system spec is
**`PGK_SPEC_SHEET.md`** in this folder.

**Canonical motor design: SINGLE time-share machine (S-series).**
One 12-slot/10-pole PMSM, one rotor carrying all four 12°-canted fins.
Ascent = windmill generator charging the supercap stack; apogee = regenerative brake + mode
switch; descent = FOC servo holds rotor roll phase for terminal course correction.
The dual-rotor design is retained only as a trade-study reference — do not build on it.

## Files

| File | Status | Contents |
|---|---|---|
| `PGK_155mm_Envelope.FCStd` | reference | Design envelope zones (datum z=125, Ø110/Ø50.8, thread band) |
| `PGK_Motor_Assembly.FCStd` | **CURRENT** | Parametric source assembly — App::Links to the part files (internal doc name: `PGK_Motor_Single_Assembly` — historical, file is canonical) |
| `PGK_Full_Assembly.FCStd` | **CURRENT** | **Single-file flattened assembly (25 PartDesign bodies + envelope refs, no external links)** — the shareable/review deliverable; edit parts via the parametric source, then re-flatten |
| `PGK_Motor_Assembly_DUAL_reference.FCStd` | reference only | Dual-rotor trade-study baseline (741 g, 2 rotors, battery) |
| `parts/M01_shaft_tube.FCStd` | CURRENT | Static tube Ø40/Ø30, wire slots (full length to z175), datum flange; fwd extension seats bearing-B inner race + radome flange |
| `parts/M02/M03`, `M05–M08` | DUAL only | Two-zone stator, dual rotors, split fin pairs |
| `parts/S01_stator_core.FCStd` | CURRENT | Single-zone 12-tooth ring, z138–163 |
| `parts/S02_stator_coils.FCStd` | CURRENT | 12 tooth-coils, one zone |
| `parts/S04_rotor_main.FCStd` | CURRENT | 25 mm rotor: ring + 10 magnets + bias ring (Ø41/Ø51.6 × 3, z163–166); spars+carrier **removed this rev** (S11 absorbs them) |
| `parts/S05_fin_main.FCStd` | CURRENT | +12° fin — placed at φ=0/90/270 (parallel control pair + reverse member) |
| `parts/S06_fin_mirror.FCStd` | CURRENT | −12° mirror fin — placed at φ=180 (completes reverse-differential pair) |
| `parts/S09_supercap_stack.FCStd` | CURRENT | Annular EDLC ~625 J, z70–100, replaces PMU battery |
| `parts/S07_radome.FCStd` | CURRENT | Nose section z173–220: ogive GFRP shell (ρ=48.63, base Ø76 @ z172.5 — continuous with the S11 drum) + GNSS antenna stack + inductive coupler (3 bodies) |
| `parts/S08_control_ring.FCStd` | CURRENT | Nav control ring: PCB Ø69.8 + Al shield can, z175–184.8 (**2 bodies + 6 interior Part features this rev: InnerPCB Ø56×1.2 @178, GNSS 15×15×2.5, MCU 12×12×1.8, FRAM 7×9×1.5, UpperPCB Ø54×1.0 @182, PwrMux 9×9×1.2 @183 — all inside shield can, CAD-verified**) |
| `parts/S10_fuze_stack.FCStd` | CURRENT | Fuze well z0–70: thread ring, housing, S&A rotor, train seat, firing PCB, connector (6 bodies; train lives in the reserved Ø30 bore by definition) |
| `parts/M04_stator_pcb.FCStd` | CURRENT | Annular driver PCB z138–139.5 |
| `parts/M09_bearing.FCStd` | CURRENT | Simplified angular-contact (×2: z130, z166) |
| `parts/M10_endbell.FCStd` | CURRENT | Aft endbell (z125–130) only — fwd endbell deleted this rev (S11 closes forward) |
| `parts/S11_canard_shell.FCStd` | CURRENT | **Canard shell (SLS AlSi10Mg): drum Ø76 z136–172.5 carrying the 4 fins + 8 LIT solid-thruster stations; sleeves back-iron, seats bearing-B race** |
| `parts/H01_155mm_shell.FCStd` | CURRENT | **M795-class host shell (3 bodies): steel body w/ fuze well + TNT fill + rotating band; z −652→+125, Ø155/Ø138, 46.84 kg — exhibition/reference host, not a PGK part** |
| `PGK_Shell_Mated_Assembly.FCStd` | CURRENT | **Flattened mated round (shell H01 + all 25 PGK bodies, no external links) with 3 view groups: COMPLETE / SECTION A-A half (view from −Y) / SECTION B-B quarter (iso); PGK∩shell interference = NONE** |

## Conventions for ALL new parts (radome, control ring, connector, S&A, PMU)

1. **Global coordinates:** origin = rear tip of fuze-well engagement; Z axis = shell axis;
   **z=125 = shell-nose datum** (`DATUM_ShellNose_Surface` in the envelope).
2. **Envelope zones:** below z=125 → Ø50.8 max (fuze well, thread z0–19);
   z125–220 → Ø110 max external, but outer contour must follow a standard fuze ogive.
3. **Through-bore Ø30** (z=0→173) is reserved for the explosive train — never intrude.
4. One PartDesign Body per file in `parts/`, parameter spreadsheet inside each file.
5. Assemblies: App::Link with identity Placement for global-coordinates parts; for rotated
   copies set **`LinkPlacement`** (it mirrors `Placement` — never compose both).
6. Envelope references in assemblies: set link `Placement` AND `LinkPlacement` to the source
   object's Placement.

## Verification gate (run before any release)

Clash check at rotor phases 0/90/180/270°, bore clearance z0→173 (explosive-train parts in
S10 are the allowed exception), envelope fit, mass rollup from Body tips only. Current
canonical: 0 clashes (stator winding-overlap pairs S01∩S02, S01∩M04, S02∩M04 excluded as
intended wrap geometry; S07 flange/S08 PCB seating interface tangent; S08 interior PCBs/modules inside shield can — clearance 0.6 mm radial/0.3 mm vertical verified), bore clear,
Ø108.0 max, z0–220, ~1.20 kg PGK total (motor+shell 723 + caps 67 + nose 99 +
control ring 35.4 + fuze stack 269).
