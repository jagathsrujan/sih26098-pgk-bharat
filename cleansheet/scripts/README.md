# Clean-sheet build scripts

Provenance for `PGK_CleanSheet.FCStd` — run headless (`freecadcmd`) not in GUI (heavy booleans crash GUI).

Scripts included (curated final set):
- `verify.py` — quick shell validity gate
- `build_bearing.py` — bearing rings v1 (male thread + grooves, inner ring, balls)
- `bearing_sections.py` — bearing v2 (corrected winding) + Section_Bearing_* cuts
- `bearing_piecewise2.py` — piecewise half-fuse fix for `Section_Bearing_OuterRing_Threaded` (final, supersedes `bearing_piecewise.py`)
- `build_thread_full3.py` — full-depth well thread (48 steps/turn ruled loft; final, supersedes `build_thread.py`, `build_thread_full.py`, `build_thread_full2.py`)

Superseded local iterations kept locally but not in repo: `build_thread.py`, `build_thread_full.py`, `build_thread_full2.py`, `bearing_piecewise.py`, `fix_outer_section.py`, `rebuild_outer_ring.py`, `bearing_piecewise.py` (v1).
