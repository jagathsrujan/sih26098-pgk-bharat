# SIH26098 — Low-Cost Precision Guidance & Smart Fuze for 155mm

**PS:** `SIH26098` | **Org:** Ministry of Defence / Yantra India Limited, Ambajhari | **Category:** Hardware | **Deadline:** 20 September 2026

> Development of a Low-Cost Precision Guidance and Smart Electronic Fuze System for a 155mm Artillery Shell (STANAG 2916, 39/45/52 cal - ATAGS/Dhanush/K9/M777)

**Target:** CEP ≤30m (stretch 10m), 74% logistics saving 301→77 shells, ₹8-11L/kit

### Quick Start for Team

1. **Clone:** `git clone https://github.com/jagathsrujan/sih26098-pgk-bharat.git`
2. **Pick your category** in `research/` (see table below)
3. **Read:** `SIH26098_Exhaustive_Ideas_Catalog.md` (108 ideas) + `SIH26098_Ideas_Database.json`
4. **Research:** Add `research/<category>/entry_YYYYMMDD_<topic>.md` using `research/templates/entry_template.md`
5. **Push:** `git add . && git commit -m "feat(B): piezo motor wind load test" && git push` → auto-updates `LIVEBOARD.md` + Notion

### Team Stack (6)

| Folder | Role | Owns | Key Files |
|--------|------|------|-----------|
| `research/A_system` | System Architect | A1 PGK-Clone architecture, cost | `SIH26098_Ideas_Database.json:1-12` |
| `research/B_aero` | Aero + Canard | B1-B16 actuation, CFD | `cad_models/generate_pgk_155.py` |
| `research/C_gnc` | GNC / Controls | C1-C14 GPS/NavIC/LSTM + PID/MPC | `cad_models/simulate_trajectory_155.py` |
| `research/D_sensors` | Sensors + RF | D1-D16 NavIC/IMU/baro | - |
| `research/E_fuze` | Fuze Electronics | E1-E10 FMCW/PD/S&A | - |
| `research/F_power` | Power + Structure | F1-F10 + G1-G10 high-G | `cad_models/generate_shell_155.py` |
| `research/I_test` | Sim/Test | I1-I6 6DOF/MIL-STD-331 | - |
| `research/J_integration` | Integration | J1-J6 EPIAFS/ATAGS | - |

### CAD Models

```bash
cd cad_models
python generate_shell_155.py   # 155mm inert mockup
python generate_pgk_155.py     # PGK nose module
python simulate_trajectory_155.py # 6DOF ballistic vs guided
```

### Live Research Board

*   **GitHub:** `research/` folders + `SIH26098_LIVEBOARD.md` (auto-generated)
*   **Realtime:** Push → GitHub Action merges entries → Discord/Slack webhook
*   **AI Agents:** Each member runs same prompt in `research/templates/agent_prompt.md` via opencode/Perplexity

### Deliverables Checklist

- [ ] System architecture doc (Categories A-J)
- [ ] CAD (FreeCAD/Fusion) + electronics block
- [ ] GNC algorithm (PID/MPC/LSTM)
- [ ] 6DOF simulation + Monte Carlo CEP
- [ ] Prototype PoC (3D print + despin rig)
- [ ] Cost + manufacturability (YIL forging, BEL electronics)

### References

*   `SIH2026_Hardware_PS.json:349` (Official PS)
*   `SIH26098_Exhaustive_Ideas_Catalog.md` (108 ideas, 30+ sources)
*   `SIH2026_Hardware_PS.md` / `SIH2026_Hardware_MECHANICAL.md`
