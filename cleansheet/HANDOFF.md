# SIH26098 Clean-Sheet PGK — Session Handoff (2026-08-30, Rev B)

## Project
- Clean-sheet redesign track of team PGK Bharat's SIH26098 entry (low-cost guidance kit + smart electronic fuze, 155mm, CEP ≤30 m, ₹8–11 L).
- Existing/frozen team baseline lives in `attachments/` (de-spun strake concept — do NOT confuse with this track). **`cleansheet/PGK_CleanSheet.FCStd` is the current design of record** (supersedes `attachments/PGK_155mm.FCStd`).
- This track: `cleansheet/` — requirements in `cleansheet/00_REQUIREMENTS.md`, design report `cleansheet/03_DESIGN_REPORT.md` (**now Rev 1.1**), BOM `cleansheet/02_BOM_MANUFACTURING_ASSEMBLY.md`, build scripts in `cleansheet/scripts/`.
- Role split: the USER drives design ideas; the AI does math, stress-testing, and CAD execution.

## CAD state (PGK_CleanSheet.FCStd — current, saved 2026-08-30)
Built bottom-up; axis = shell centerline, z=0 at base, +Z toward nose, seat plane z=696.
1. `Shell_Body_155` — 696 mm M795-class envelope (Ø154.9 body, 4.07-cal tangent ogive, boattail). Hidden solid.
2. `Rotating_Band` — copper Ø157 ring, z=100–124. Hidden.
3. Fuze well in shell: STANAG 2916-class **2-12UN-1A RH internal thread, FULL cavity depth** (z=606→696), countersunk mouth. User's deliberate divergence from standard (std ~25 mm).
4. **Threaded-race ball bearing** in the cavity (v2 in CAD): `Bearing_OuterRing_Threaded` (male 2-12UN, race bore Ø43, vol ≈ 41k), `Bearing_InnerRing_Smooth` (OD Ø37/bore Ø32), `Bearing_Balls` (Ø3, 10 rows × 16, Ø40 circle).
5. Persistent parametric sections: `Section_Shell`, `Section_Band`, `Section_Bearing_*`, `Section_*` for motor/GNC/radome/canards (Part::Cut via `Section_Cutter` box, y>0 removed). Currently HIDDEN — the Assembly view (below) replaced them as the display state.
6. Full module stack (all built): `Core_Cartridge`, `Battery_Stack`, `Initiator_Interface_INERT`, `Outrunner_Stator` + `Windings_PhaseA/B/C` + `Hall_Sensors`, `Outrunner_Rotor_Bell` + `Magnet_Ring_Segmented` + `Motor_StubShaft` + `Motor_PilotBearing`, `Canard_Shell_Machined` + `_fins`, `Dome_Base_Ring`, `GNC_Board`, `GNSS_Patch`, `Prox_Head`, `Radome`.
7. **NEW (Rev 1.1): native Assembly** —
   - `Assembly` (Assembly::AssemblyObject) with 24 `App::Link` members (one per part above).
   - `Assembly > Joints` (Assembly::JointGroup): `GroundedJoint` on shell link; 21 Fixed joints (statics + rotor group + nose group); **2 Revolute**: `J_MotorRotor` (shell↔rotor bell) and `J_RollDecouple` (shell↔canard shell). Solver rc=0; JCS = identity on global Z; `Detach1/2=True` everywhere.
   - `Assembly > Simulations > Simulation` (FeaturePython, proxy from `Mod/Assembly/CommandCreateSimulation.py`): t 0→4 s, 30 fps, **122 frames**; motions: `Motion_Rotor_Spin` = `3.1416*time` rad/s on J_MotorRotor, `Motion_Nose_RollDecouple` = `-1.0472*time` rad/s on J_RollDecouple. Generated via `asm.generateSimulation(sim)`; playback via `asm.updateForFrame(i)`.
   - Verified kinematically: rotor spins +180°/s, nose rolls −60°/s opposite (frames 0/30/60/90 screenshotted). Kinematic integration drift ≈6° over 4 s (normal).
   - Display state: all links visible, shell/canard/radome translucent (55–62%) via link `OverrideColorList`, sections hidden. To restore section views: unhide `Section_*`, hide `Assembly`.
- Full kinematic/assembly detail: `03_DESIGN_REPORT.md` §2.4 (Rev 1.1).
- **Rev 1.2 (2026-08-30): steering-effectiveness sim + spec deltas** — `scripts/sim_guidance_check.py` + `out_sim/RESULTS.md` (3DOF MC, 250 paired runs: guided CEP 6.9 m vs unguided 207 m; lock-45 s variant 8.5 m median/worst 145 m). De-spin re-specced **15 s @ ≤40 A** with boost stage + brake chopper (was 10 s/60 A regen-dominant — zero torque margin, L/t = 0.143 vs 0.14 spec); GNSS lock 35→45 s; energy ledger restated (≤0.9 Wh worst, regen now opportunistic); mass 1.77→1.84 kg. Deltas in BOM §G, report Rev 1.2. Materials unchanged.

## How to play the simulation (for demo/exhibition)
Assembly workbench → tree → double-click `Assembly > Simulations > Simulation` → Play (or drag the frame slider). 122 frames = 4 s at 30 fps. Rotor does 2 turns CW while nose does 2/3 turn CCW.

## NEXT RUNGS (user drives ideas, AI executes)
1. REQ-1/REQ-2 modeling: inner-ring retention lip + 4× Ø3 shear pins (still "designed, not modeled" — see report §9).
2. 6DOF Python sim, Monte Carlo ≥1000 runs → CEP ≤30 m evidence (report §10.1).
3. Mass optimization → 1.56 kg path (report §6, Rev 1.2) if SWaP becomes gating.
4. Optional: second Simulation object for the de-spin transient (250→0 rev/s over 10 s) using a decaying formula (e.g. smooth/exponential form — `CommandCreateSimulation.py` documents supported formula shapes: linear/quadratic/harmonic/exponential/smooth-step).
5. Update `00_REQUIREMENTS.md` open items when PS org answers arrive.

## CRITICAL PROCESS KNOWLEDGE (learned the hard way)
- Heavy booleans/helical sweeps CRASH FreeCAD when run in-GUI. Do heavy geometry headless: `freecadcmd script.py` (AppImage extracted at `~/Downloads/squashfs-root/usr/bin/freecadcmd`). Run with `nohup ... &`, poll log, gate before `doc.save()`.
- After headless edits: MCP `freecad_reload_document`. GUI MCP calls time out on heavy recomputes (e.g., Part::Cut on 160-ball compound — do NOT do that in GUI).
- **MCP execute_code pattern for long/fragile ops:** write progress to `/tmp/opencode/<log>.log` via file appends and print the log at the end — stdout is DISCARDED when the call raises; file writes survive. Keep calls small; a timed-out call leaves NO partial state (rolled back).
- Thread construction that works: 48-steps/turn ruled loft of trapezoid profile along helix; gate with ring-band common volume + crest-bore common ≈ 0 check.
- GUI camera control is flaky — for close-ups, `freecad_get_view` with `focus_object` fits that object; view_name "Back" shows y=0 section faces.
- **Assembly scripting API (FreeCAD 1.1.3, discovered this session):**
  - Joint/simulation objects are `App::FeaturePython` with proxies from `App.getHomePath() + "Mod/Assembly"`: `JointObject.Joint(j, idx)` (idx: 0=Fixed, 1=Revolute…), `JointObject.GroundedJoint(g, obj)`, `CommandCreateSimulation.Simulation(sim)` / `.Motion(m, "Angular", joint=..., formula=...)` + matching ViewProviders. `Assembly::JointObject` does NOT exist as a doc type.
  - Joints MUST live inside an `Assembly::JointGroup` named "Joints" (`asm.newObject("Assembly::JointGroup", "Joints")`) — only then do `asm.Joints`, `isPartGrounded`, solver, and simulations see them. Simulations go in `Assembly::SimulationGroup` "Simulations".
  - `Reference1/2` (PropertyXLinkSub) assignment format: `(obj, ["Face1"])` — a single TUPLE, not a list of tuples (list form raises "Expect input sequence of size 2").
  - Set `Detach1/2 = True` + explicit identity `Placement1/2` to pin joint coordinate systems (avoids findPlacement picking arbitrary face origins that would shift parts on solve).
  - Drive formulas for Angular motions are in **radians/second** ("3.1416*time" = 180°/s). Supported formula families documented in `CommandCreateSimulation.py` (linear/quadratic/harmonic/exp/smooth-step).
  - After `generateSimulation(sim)`: `asm.numberOfFrames()`, `asm.updateForFrame(i)`; `asm.updateForFrame(0)` restores initial state.
  - `asm.Type` must be `"Assembly"` (was empty when created via script — set it explicitly or joint GUI behaviors misfire).
- App::Link colors: link VPs have no ShapeColor; use `vp.OverrideColorList = [(r,g,b,a)]` (+ vp.Transparency). Link DisplayMode "Link" mirrors source otherwise.

## Environment
- Working dir: `/home/jagath-srujan/Documents/smart india hackathon` (spaces in path — quote everything).
- FreeCAD 1.1.3 AppImage + freecad-mcp (execute_code, reload_document, get_view, etc.).
- Team repo: github.com/jagathsrujan/sih26098-pgk-bharat (private). Deadline 20 Sep 2026.
