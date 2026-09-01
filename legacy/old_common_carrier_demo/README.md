# Legacy: common-carrier printed demonstrator (superseded 2026-08-29)

This was the active exhibition baseline until the detailed `PGK_155mm.FCStd`
envelope model replaced it. Kept for reference and for the printed-parts story.

- `generate_pgk_155.py` — FreeCAD generator: outer housing + common canard
  carrier with 4 fixed canards, 2 display bearings, N20-style torque emulator,
  alternator rotor/stator props
- `render_pgk_155.py`, `render_mated.py` — matplotlib previews for that model
- `PGK_DEMO_ASSEMBLY.md` — its assembly/demo write-up
- `pgk_assembly_diagram.html` — its stack diagram

**Superseded by:** `PGK_155mm.FCStd` + `cad_models/render_pgk_155mm.py`
(single 61811 de-spin bearing, 12-pole ring motor, detent launch lock,
4 strakes on the de-spun stator, 6× 14430 bay, NEO-M9N + patch).
