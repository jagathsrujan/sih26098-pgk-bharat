# Active PGK 155mm exports

Regenerate everything here from the active baseline with:

```bash
cd cad_models
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd render_pgk_155mm.py
```

Source of truth: `../PGK_155mm.FCStd` (see `../PGK_155MM_ASSEMBLY.md` for the
part-by-part stack and demo script).

| File | What it is |
|---|---|
| `preview_mated.png` | matplotlib render, kit mated on the reference shell |
| `preview_mated_gui.png` | FreeCAD viewport capture (canonical hero shot) |
| `preview_assembly.png` | PGK nose module alone, per-part colors |
| `preview_section.png` | `SEC_*` half-section cutaway of shell + kit |
| `preview_section_pgk.png` | cutaway zoom: bearing, ring motor, stack, cells, GNSS |
| `PGK_155mm_mated.step` | full mated assembly (shell + kit) |
| `PGK_155mm_nose_module.step` | kit only (drop into any shell/flow sim) |
| `PGK_155mm_section.step` | half-section solids |
| `stl/*.stl` | per-part STLs (28 parts, meshed at 0.25 mm) |
| `viewer_data.json` | lathe profiles + coarse meshes feeding `../pgk_3d_viewer.html` |

The directory contains no launch interface, fuze, propellant, primer, detonator,
or other energetic component — inert geometry only.
