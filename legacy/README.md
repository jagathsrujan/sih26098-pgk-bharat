# legacy/ — archived history

**Rule: new work never goes here.** Everything in `legacy/` is superseded or history-only,
kept readable for provenance. The current design of record lives in `cleansheet/` (Rev 1.7)
+ `electronics/` (KiCad architecture) + the 6 active `research/01–06` team folders.

| Item | What it is | Why archived (2026-08-31) |
|---|---|---|
| `old_two_motor_design/` | Superseded two-motor CAD + output | Replaced by the common-carrier bench demonstrator (`cad_models/`) and then by `cleansheet/` |
| `attachments/` | Frozen pre-cleansheet baseline backups (`.FCBak` of `PGK_155mm`, COTS library) | `cleansheet/PGK_CleanSheet.FCStd` supersedes `PGK_155mm` (see `cleansheet/HANDOFF.md`) |
| `docs/` | PS dumps (aerospace/software-filtered) + HTML viewers + Excalidraw VALID copy | Reference-only dumps; the official PS is `SIH2026_Hardware_PS.*` at root |
| `output/` | `electronics_example/` — example BOM/interfaces/block diagram | Superseded by the real electronics architecture: `cleansheet/06_ELECTRONICS_ARCHITECTURE.md` + `electronics/gnc_board.kicad_pro` |
| `research-A-J/` | The letter-category research round (`A_system`, `B_aero`, `C_gnc`, `E_fuze`, `G_structure`, `I_test`) | Superseded by the 6 PS-driven team folders `research/01–06`; `research/D_sensors/` stayed (cited by `cleansheet/05_SENSOR_SELECTION.md`) |
| `SIH26098_LShang_Video_Teardown_Gap_Analysis.md` | 23-min L Shang student-rocket teardown | Historical gap analysis; the actionable evidence lives in the research entries |
| `SIH26098_Excalidraw.excalidraw` | 6-panel problem→team whiteboard | Static board; a copy also exists in `legacy/docs/archive/SIH26098_Excalidraw_VALID.excalidraw` |

Note: `research/merge.py` scans only `research/*/entry_*.md` — archived letter-folder entries no
longer appear on `SIH26098_LIVEBOARD.md`, but the 108-idea `SIH26098_Ideas_Database.json` and git
history retain everything.
