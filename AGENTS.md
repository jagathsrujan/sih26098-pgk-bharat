# AGENTS.md — Read This First (applies to every agent, every session)

## Main design of record (the ONLY thing you design against)

| Artifact | Path | Status |
|---|---|---|
| **System spec sheet** | `cad_models/PGK_SPEC_SHEET.md` | **THE main document** — mission timeline, motor, energy ledger, sensor stack, loads, standing process |
| **Canonical CAD assembly** | `cad_models/PGK_Motor_Assembly.FCStd` | Single time-share machine in the 155mm envelope (FreeCAD 1.1.3) |
| **CAD conventions + file inventory** | `cad_models/README.md` | One Body per part file, global coords, datum z=125, Ø30 through-bore reserved |
| **Part files** | `cad_models/parts/` | S-series = current; M01/M04/M09/M10 = current & shared; M02/M03/M05–M08 = dual-rotor reference only |
| **Design envelope** | `cad_models/PGK_155mm_Envelope.FCStd` | Zones + datum (z=125) every part must fit |

**The design in one line:** single 12s10p ring PMSM inside a 2"-12 UNEF fuze kit for 155mm;
ascent = windmill generator charging an annular supercap (875 J); apogee = regen brake + mode
switch; descent = the same machine servo-holds 4 mirror-pitched fins (reverse + parallel pairs,
±12°) for terminal course correction. No battery. No cold gas. Through-bore keeps the shell's
explosive train untouched.

## Hierarchy — treat accordingly

1. **`cad_models/PGK_SPEC_SHEET.md` + `cad_models/PGK_Motor_Assembly.FCStd`** — main design.
   All new work extends these and updates the spec sheet (its §11 is the standing process).
2. **Reference (read, cite, don't treat as current):**
   - `cleansheet/` — prior design lineage (Rev 1.7, de-spin motor + slip ring + NMC battery).
     **Superseded by the single-machine design.** Its GNC methodology, sensor-selection
     error-budget work, flight-software structure and KiCad skeleton remain useful references,
     but its architecture (battery, slip ring, Ø138 canard, dual-domain electronics) is NOT
     the current design.
   - `electronics/` — KiCad skeleton from that lineage (reference for schematic style).
   - `research/` — team research folders + evidence (living, but not design authority).
   - `cad_models/PGK_Motor_Assembly_DUAL_reference.FCStd` — dual-rotor trade-study CAD.
   - `cad_models/PGK_155MM_ASSEMBLY.md`, `out_pgk/`, `render_pgk_155mm.py`,
     `simulate_trajectory_155.py` — earlier 155mm exhibition model, reference only.
   - Root BOMs (`SIH26098_COTS_BOM.*`, `SIH26098_FLIGHT_KIT_BOM.*`) — date from the prior
     design; resync before reusing any line item.
   - `SIH26098_TERMINAL_KICKER_EVAL.md`, `SIH26098_Exhaustive_Ideas_Catalog.md` — trade
     studies / ideation references.
3. **Legacy — never add work here:** `legacy/` (see `legacy/README.md`). Cold-gas concept
   docs were archived here after being rejected by calculation.

## Rules for any agent

1. **Before designing anything:** read `cad_models/PGK_SPEC_SHEET.md` end-to-end, then
   `cad_models/README.md`. If your change touches a section, update that section.
2. **Standing process** (spec sheet §11): every new part/subsystem/analysis gets
   (a) CAD under `cad_models/parts/` per conventions, (b) a dimension table from CAD in the
   spec sheet, (c) functional spec (mass, loads, power, timing, failure modes),
   (d) energy-ledger update if it produces/consumes energy, (e) timeline update if the
   sequence changes, (f) open items recorded — never silent assumptions.
3. **Never modify:** `legacy/`, `PGK_Motor_Assembly_DUAL_reference.FCStd`, or the envelope
   zones — references are read-only history.
4. **Never reintroduce:** cold-gas thrusters (rejected by calculation), onboard batteries in
   the baseline (supercap-only; optional Li-SOCl2 footprint reserved), or a second motor.
5. **FreeCAD scripting gotchas that cost us time:** `App::Link` — set `LinkPlacement` (it
   mirrors `Placement`; never compose both, the transform double-applies); PolarPattern via
   scripting is unreliable — use explicit rotated revolutions; `doc.removeObject` takes a
   NAME string, not an object; `Vector.multiply` mutates in place; verify every part's bbox
   and volume after each build step.
6. **Team/research process** (liveboard, entry files, branches) is unchanged — see root
   `README.md` Quick Start; but design answers must align with the main design above, and
   conflicts resolve in favor of `PGK_SPEC_SHEET.md`.
