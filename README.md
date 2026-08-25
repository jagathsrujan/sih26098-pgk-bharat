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

### Team Map — Who Does What (Simple View)

> **New here? Start here.** 3 Mech now + 3 ECE/CSE to hire. We all work towards the top goal. Each colored box = 1 person. Read top to bottom: **Learn → Decide → Show**.

```mermaid
%%{init: {'theme':'base', 'themeVariables': {'fontSize':'15px', 'primaryTextColor':'#f8fafc', 'lineColor':'#94a3b8'}}}%%
flowchart TD
    GOAL[[OUR GOAL<br>Make a cheap add-on kit<br>so the shell lands within 30m<br>instead of 267m away]]

    subgraph M1 ["1 - THE PLANNER<br>Folder: research/A_system"]
        direction TB
        M1_R["Step 1: Learn<br>• Look at old kits<br>• Check size limits<br>• See who can build what"]
        M1_C["Step 2: Decide<br>• Pick the simplest design<br>• Make weight + cost list"]
        M1_D["Step 3: Show<br>• Main drawing + PPT<br>• Prove we save 74% shells"]
        M1_R --> M1_C --> M1_D
    end

    subgraph M2 ["2 - THE STEERING PERSON<br>Folder: research/B_aero"]
        direction TB
        M2_R["Step 1: Learn<br>• How small wings steer<br>• Why shell spins<br>• How to use spin to turn"]
        M2_C["Step 2: Decide<br>• Simple brake to steer<br>• No fancy motors"]
        M2_D["Step 3: Show<br>• Simulation video<br>• Graph: miss goes down"]
        M2_R --> M2_C --> M2_D
    end

    subgraph M3 ["3 - THE BRAIN<br>Folder: research/D_sensors"]
        direction TB
        M3_R["Step 1: Learn<br>• How GPS finds place<br>• Which sensors survive firing"]
        M3_C["Step 2: Decide<br>• Choose GPS + backup sensors<br>• Tiny AI if GPS fails"]
        M3_D["Step 3: Show<br>• Sensor demo on table<br>• Shows location on screen"]
        M3_R --> M3_C --> M3_D
    end

    subgraph M4 ["4 - THE FUZE PERSON<br>Folder: research/E_fuze"]
        direction TB
        M4_R["Step 1: Learn<br>• How fuze decides when to burst<br>• What is safe / not safe"]
        M4_C["Step 2: Decide<br>• Radar to see ground<br>• Safe switch before firing"]
        M4_D["Step 3: Show<br>• Circuit diagram<br>• Phone programs the fuze"]
        M4_R --> M4_C --> M4_D
    end

    subgraph M5 ["5 - THE BODY BUILDER<br>Folder: research/F_power"]
        direction TB
        M5_R["Step 1: Learn<br>• How to power without battery<br>• What material survives shock"]
        M5_C["Step 2: Decide<br>• Make power from spin<br>• Strong but light body"]
        M5_D["Step 3: Show<br>• 3D printed model<br>• Power turns on in 6 sec"]
        M5_R --> M5_C --> M5_D
    end

    subgraph M6 ["6 - THE TESTER<br>Folder: research/I_test"]
        direction TB
        M6_R["Step 1: Learn<br>• How to test without firing<br>• What army checks"]
        M6_C["Step 2: Decide<br>• Fake flight on computer<br>• Drop test for fuze"]
        M6_D["Step 3: Show<br>• Final demo video<br>• Proof it works"]
        M6_R --> M6_C --> M6_D
    end

    GOAL --> M1 & M2 & M3 & M4 & M5 & M6

    M5_D -. gives power to .-> M3
    M2_D -. tells which way is up to .-> M3
    M3_D -. tells when to burst to .-> M4
    M6_D -. checks all .-> M1

    classDef lead fill:#0f172a,stroke:#fbbf24,stroke-width:2px,color:#fef3c7
    classDef aero fill:#0f172a,stroke:#60a5fa,stroke-width:2px,color:#dbeafe
    classDef emb fill:#0f172a,stroke:#4ade80,stroke-width:2px,color:#dcfce7
    classDef rf fill:#0f172a,stroke:#f472b6,stroke-width:2px,color:#fce7f3
    classDef str fill:#0f172a,stroke:#818cf8,stroke-width:2px,color:#e0e7ff
    classDef sim fill:#0f172a,stroke:#fb923c,stroke-width:2px,color:#ffedd5

    class M1 lead
    class M2 aero
    class M3 emb
    class M4 rf
    class M5 str
    class M6 sim
```

**How to read for beginners:**
*   **Top black box = our shared goal.** Everything points there.
*   **Each colored box = one teammate.** You only need to understand your box — not all 6.
*   Inside each box, read top to bottom: **Step 1 Learn** (what to read), **Step 2 Decide** (what to choose), **Step 3 Show** (what you hand in).
*   Thin dotted lines = help between teammates. Example: Body Builder (5) must give power before Brain (3) can work.

> **Scared of hard words? Quick glossary:** `CEP` = how close to target (smaller is better) • `STANAG 2916` = standard screw size so it fits all guns • `Fuze` = the tiny computer on the nose that decides when to burst • `NavIC` = India's GPS

<details>
<summary>Need the full technical map (with codes like A1, B1, FMCW)? Click here</summary>

Technical version is in `SIH26098_Exhaustive_Ideas_Catalog.md` — same 6 boxes but with part numbers. Use this simple map to start, switch to technical after week 1.

</details>

### Quick Table (plain English)

| # | Role (simple name) | Folder | Learn About | Decide | Show At The End |
|---|-------------------|--------|-------------|--------|-----------------|
| 1 | The Planner | `A_system` | Old kits, size limits, who builds what | Simplest kit + cost | Main drawing, cost sheet, slides |
| 2 | The Steering Person | `B_aero` | Small wings, spin, brake | Simple steer, no motor | Simulation video, miss graph |
| 3 | The Brain | `D_sensors` | GPS + sensors | Best GPS + backup | Sensor demo on table |
| 4 | The Fuze Person | `E_fuze` | When to burst, safe switch | Radar + safe switch | Circuit, phone demo |
| 5 | The Body Builder | `F_power` | Battery-free power, strong cover | Spin-power + tough body | 3D model, power test |
| 6 | The Tester | `I_test` | How army tests | Fake flight + drop test | Demo video, proof |

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
