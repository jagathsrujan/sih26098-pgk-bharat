# IMPROVEMENT IMPLEMENTATION PROMPT — paste as first message in a new session

```
You are my CAD/design engineer continuing the SIH26098 clean-sheet PGK design
(155mm precision guidance kit + smart fuze, "PGK Bharat", hackathon deadline 20 Sep 2026).
The full design is documented — read these FIRST, in order:
1. cleansheet/03_DESIGN_REPORT.md        (master design report — §4 subsystems, §7 physics audit, §9 REQ register)
2. cleansheet/02_BOM_MANUFACTURING_ASSEMBLY.md  (BOM, fits, costing)
3. cleansheet/01_POWER_MOTOR_SPEC.md     (motor + battery spec, if present)

CAD of record: cleansheet/PGK_CleanSheet.FCStd — currently OPEN in the running FreeCAD
GUI, which you control via the FreeCAD MCP tools (freecad_execute_code, freecad_get_view,
freecad_reload_document, freecad_get_rpc_status).

## COORDINATE SYSTEM & KEY STATIONS (all mm, origin = shell base center, +Z toward nose)
- Fuze well cavity: z 606–696 (thread crest Ø48 / root Ø50.8, full-depth 2-12UN-1A RH)
- Fuze seat plane (flat annulus of shell nose): z = 696, r 25.45–41.5
- Bearing: outer ring (threaded, shell frame) z 606–696; inner ring (rotor frame) bore Ø32;
  balls Ø3 ×160 on Ø40 circle; drum "journal": core cartridge OD Ø31.6 g6 rides the bore
- Core cartridge: z 606–712; floor 606–610; ignitor bay 610–632; battery bay 634–692
  (cell Ø25.4); collar flange Ø40, z 696–712, top face z=712; firing channel Ø2.4 @ x=+14.3
- Outrunner: stator yoke Ø45–72 z 697–713 (24 teeth to Ø73.4); bell wall Ø76.4–83
  z 697.5–719.5; bell cap Ø83 z 719.5–722.5; magnet ring Ø74.7–76.4; pilot bearing
  Ø20.8/24.7 on stub shaft Ø20.4 (z 712–724); Hall sensors ×3
- Canard shell (one-piece, part "Canard_Shell_Machined"): cap Ø89 z 722.5–726.5;
  drum1 Ø84–89 z 713.5–722.5; step z 711.5–713.5; drum2 Ø81–85 z 697.5–711.5;
  4 delta fins (root chord 24 @ r42.5→drum2, tip chord 18 @ r67, tip Ø138);
  trimmed pair: fin@0° +3°, fin@180° −3° about OWN quarter-chord hinge
  (x = 42.5·cos(az), y = 42.5·sin(az), z = 697.5+0.25·24), axis (0,1,0)
- Radome: tangent ogive Ø84 × 49.6, z 726.5–776.1, wall 2, translucent (60%)

## DISPLAY CONVENTION (keep consistent)
Section_Cutter = box removing y>0. Every design solid X gets a Section_X = X.cut(cutter).
Display state: design solids hidden; Section_* visible; EXCEPT Radome (solid shown at 65%
transparency) and Hall_Sensors (shown whole). After every change: recompute → save →
update visibility state → save again.

## WORKFLOW RULES (hard constraints — learned from two FreeCAD crashes)
1. GUI-ONLY. All geometry via MCP freecad_execute_code on the live GUI instance. NEVER headless.
2. Small increments: one boolean/fuse family per execute call. Save (doc.save()) after every
   successful gate. If an MCP call times out: poll freecad_get_rpc_status, do NOT re-fire
   blindly; then verify object state with a read-only script.
3. GATE BEFORE EVERY REPLACE: new_shape.isValid() AND new_shape.Volume > 0 AND bbox sane.
   A null shape passes isValid() — ALWAYS also check Volume > 0 (this bit us once).
4. When rotating trimmed fins/arms: hinge axis is per-fin OWN position (compute hx,hy from
   azimuth) — same-sign world rotation + own-side hinges. Never a shared hinge point.
5. Beware coincident surfaces in booleans (exact tangency corrupts shapes) — leave ≥0.2 mm
   bridges or deliberate 0.05 press fits, and verify with vertex-radius probes.
6. Quote all paths (workspace has spaces): "/home/jagath-srujan/Documents/smart india hackathon"

## WORK PACKAGES (execute in order)

### WP1 — Axial load path (retention)  [physics blocker]
Requirement: at 15,000 g the core cartridge (~1.4 kg) generates ~210 kN axial; this must be
carried shell→shell, never through the bearing balls.
Design: (a) modify Core_Cartridge: turn a pilot nose on its bottom end — z 606–612 at
Ø29.4 (step up to Ø31.6 at z=612), so the nose passes the bore and the Ø31.6 shoulder
lands per design; (b) the cartridge nose face (annulus Ø25.6–29.4) lands on the well
bottom face at z=606 (shell material, directly above booster seat = ideal load path);
(c) bearing balls then carry flight loads only (~10 N).
Verify: cartridge modified (valid, vol within ±2 cm³ of original minus removed nose stock);
inner ring axially located by design note (snap-ring sized for flight loads only).
Update: Core_Cartridge + Section_Core_Cartridge. Save. Screenshot Back view.

### WP2 — Torque anchor (shear pins)  [physics blocker]
Requirement: motor stator sits on the cartridge (frame A); without a torque anchor to the
shell, motor reaction spins the cartridge (conservation of angular momentum) and produces
zero steering. The cartridge must be shear-pinned to the bearing outer ring (= shell frame
via well thread). Interface available: radial gap between collar OD (r20) and inner-ring
bore... NO — use the outer-ring TOP annulus: it spans z=696, r 21.5–24.1, directly under
the collar flange region.
Design: (a) Torque_Coupling_Sleeve: tube r_in 20.2 / r_out 21.3, z 696–712, Al 7075,
riding in the collar-OD/race-bore annular gap (0.2–0.5 mm clearances);
(b) 4× Ø2.5 × 3 shear pins vertical at r≈22.8, azimuths 45/135/225/315, pinning sleeve↓
to outer-ring top annulus (shear 2–3 kN each — sized ~3× module friction+disturbance, NOT
setback: setback axial path is WP1's, pins see torque only);
(c) 4× M2.5 screws sleeve↑ into collar flange edge (flange locally thickened if needed).
Verify: sleeve + pins valid; clearance check vs inner-ring bore Ø32 (sleeve OD 42.6?? NO —
sleeve sits ABOVE z=696 around the collar, it must clear the bell ID Ø76.4 too — it does,
r≤21.3) and vs stator base (starts z=712 ✓ sleeve ends 712).
Update: new solids + Section_ versions. Save. Screenshot Back view.

### WP3 — Ball cage (bearing)
Design: 2-piece snap cage: for each of the 10 ball rows, one thin half-annulus ring
(r_in 38.6, r_out 40.4, 1.2 thick, y<0 half shown in section) with 16 pocket dimples
(cut R1.7 spheres at ball centers). To keep the part count sane, model ONE cage part per
row is excessive — instead model a single-row representative cage + BOM note "10 required".
Acceptance: valid, pockets align to ball positions ±0.1, does not touch races (≥0.15 gap).

### WP4 — Bearing & sensor upgrades
(a) Preload shim: thin ring Ø12.5–20.3 × 0.5 at pilot bearing top (z 722.2–722.7).
(b) Magnet pole change: rebuild Magnet_Ring_Segmented as 12 segments (12 magnets,
    3.2 mm arc width at same radii, z 699–714) — halves electrical frequency to 1.25 kHz
    at max relative rate. Keep exact curved-segment construction (annulus sliced by slot
    cuts at 15°... now 30° pitch). Update Section_Magnet_Ring_Segmented.
(c) Labyrinth seal: grooved ring at drum2 bottom rim — r 42.6–44.4, z 695.8–697.4,
    2 V-grooves, attached to shell side (0.2 mm radial clearance to drum2) — cuts grit
    path to the bearing. New part Seal_Ring_ShellSide + section.

### WP5 — Electronics board upgrades (GNC board region)
Add to GNC_Board (part "GNC_Board"): (a) barometric sensor 3×3×1 @ r≈20 azimuth 0°;
(b) lockstep second MCU 7×7×1 next to the first; (c) flash data-logger 4×3×1.
Fuse into GNC_Board, update its Section. Power-spec doc: add regen dump (brake chopper)
and cold-cell heating pulse lines to 01_POWER_MOTOR_SPEC.md.

### WP6 — Documentation sync (mandatory closeout)
1. Update 03_DESIGN_REPORT.md §9 REQ register: REQ-1/2/3/5 → MODELED (with date);
   add WP1/WP2 design notes to §4.1/4.3.
2. Update 02_BOM_MANUFACTURING_ASSEMBLY.md: add Torque sleeve, seal ring, preload shim,
   baro sensor, lockstep MCU, logger rows with costs (estimate INR, same table format).
3. Screenshots into the chat: Back view (full stack, sectioned) + one iso close-up of the
   nose showing fins +WP2 sleeve.
4. Final verification script: list all objects with isValid + Volume>0, print pass/fail.

## ORDER OF EXECUTION
Read docs (1–3) → open/verify CAD state (list objects, volumes) → WP1 → WP2 → WP3 →
WP4 → WP5 → WP6 → final screenshots + summary table of what changed.
Report progress after each work package in ≤3 lines. Ask me only if a spec is ambiguous —
everything else, decide and execute.
```
