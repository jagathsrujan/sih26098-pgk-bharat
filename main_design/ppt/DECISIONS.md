# SIH26098 Idea Deck — Decision Log

Built from `main_design/PGK_SPEC_SHEET.md`, `main_design/simulation/RESULTS_SINGLE_MACHINE.md`,
CAD renders in `main_design/renders/`, against the official SIH 2026 idea template
(`SIH2026-IDEA-Presentation-Format.pdf`). One block per page: headline, bullets, numbers, image,
source spec sections. Deck stance: **full engineering design with evidence labels**
(TARGET / SIMULATION / VERIFIED).

## Template facts (verified via pdftotext)
- 6 slides max (title slide included); this deck = exactly 6 pages.
- Footer on every page: `(c)SIH Idea submission- Template` + page number.
- Left sidebar on every content page: `Your Team Name` (two lines).
- P1 TITLE PAGE fields: Problem Statement ID · Problem Statement Title · Theme · PS Category
  (Software/Hardware) · Team ID · Team Name (Registered on portal).
- P2 IDEA TITLE — Proposed Solution: detailed explanation · how it addresses the problem ·
  innovation and uniqueness.
- P3 TECHNICAL APPROACH — technologies to be used (languages, frameworks, hardware) ·
  methodology and process (flow charts / images / working prototype).
- P4 FEASIBILITY AND VIABILITY — feasibility analysis · potential challenges and risks ·
  strategies for overcoming them.
- P5 IMPACT AND BENEFITS — impact on target audience · benefits (social, economic, environmental…).
- P6 RESEARCH AND REFERENCES — details / links of reference and research work.

## Global facts
- PS ID: **SIH26098** — Development of a Low-Cost Precision Guidance and Smart Electronic Fuze
  System for a 155 mm Artillery Shell (PS title on template: "Design and Development of a
  Precision Guidance Kit with Canard Actuation and Multi-Mode Electronic Fuze for a 155 mm
  Artillery Shell")
- Organization: Ministry of Defence (MoD) — Yantra India Limited (YIL), Ambajhari, Nagpur
- Theme: **Miscellaneous** · Category: **Hardware** · Deadline: 20 September 2026
- Team name: **LARP** (Step 1 decision) — title page + "Your Team Name" sidebar on every page
- Team ID: placeholder `[Team ID — fill before upload]` (Step 1 decision)
- Institution line: none — title page carries template fields only (Step 1 decision)

---

## P1 — TITLE PAGE
- Strict template reproduction; no hook line, no image (user decisions).
- Problem Statement ID – SIH26098
- Problem Statement Title – Development of a Low-Cost Precision Guidance and Smart Electronic
  Fuze System for a 155 mm Artillery Shell
- Theme – Miscellaneous
- PS Category – Hardware
- Team ID – [Team ID — fill before upload]
- Team Name – LARP (Registered on portal)
- Sidebar "Your Team Name" → renders as LARP on every content page.
- Image: none.

## P2 — IDEA TITLE
- Headline (user choice): **"One Machine, No Battery — Precision Guidance Kit + 3-Mode Electronic
  Fuze for the 155 mm Shell"**
- Hero image: `main_design/renders/complete_iso.png` (mated round isometric) — class A.
- Layout: hero right; 4 pillar boxes + PS-requirement mapping strip; evidence labels on every number.

Pillars (grounded copy):
1. **ONE MACHINE** (spec §2) — a single 12s10p ring PMSM time-shares two jobs:
   ascent = windmill generator, descent = fin actuator for 4 mirror-pitched fins (±12°).
2. **NO BATTERY** (spec §2.3, §5) — annular supercap 0.6 F @ 54 V stores **875 J** harvested from
   the shell's own flight; mission needs **344 J** → ~2.5× energy margin. [SIMULATION]
3. **3-MODE FUZE** (spec §9.9, §8.1) — Proximity (FM-CW ring antenna) / **Time** (timed
   self-destruct) / Impact (inertia); SAFE→ARM set through the inductive programmer interface.
4. **7× CEP** (sim) — **28.5 m** CEP vs **196 m** unguided at 30 km; PS target ≤ 30 m met.
   [SIMULATION]

PS-requirement mapping strip (one row of checks):
CAA ✓(S05/S06/S11) · GNC ✓(EKF §9, sensors §2.4) · 3 fuze modes ✓(§9.9) · embedded SW ✓
(single MCU, 3 loops §2.3) · power mgmt ✓(§2.3/§5) · programming interface ✓(inductive §8.1) ·
CEP ≤30 m ✓(sim 28.5 m) · standard shell ✓(§9.11) · high-g ✓(13,400–15,500 g §2.6) ·
SWaP-C ✓(1.18 kg kit) · modular ✓(S-series)

## P3 — TECHNICAL APPROACH
- Layout (user choice): **balanced split** — left: architecture block diagram + mission timeline;
  right: hardware spec table + section-view inset.
- Barometer (user choice): listed as **"Barometric altitude — optional GNC aiding (PS example;
  trade study open)"** — honest open item, not silently added as a baseline sensor.

Left — METHODOLOGY (template bullet 2):
- Architecture block diagram (class C, to draw): Sensors (NavIC L1/L5+GPS, ±25,000°/s gyro,
  high-g IMU, RM3100-class mag ≥2 kHz, [baro — open]) → single MCU (EKF nav + 3 control loops
  §2.3) → ring-motor drive / fuze / inductive setter interface.
- Mission timeline strip (class C): t=0 launch 15,000 g setback → t≈3 s GPS reacquire →
  ascent generator mode (cap charges 10–15 W) → apogee mode switch (regen brake, recovers
  15–25 J) → descent servo-hold fins ±12° → terminal fuze (PROX/TIME/IMPACT).

Right — TECHNOLOGIES (template bullet 1), hardware table rows:
- Machine: 12s10p ring PMSM, Kt 0.095 N·m/A [TARGET], generated EMF 150–200 V
- Storage: annular EDLC supercap 0.6 F @ 54 V — 875 J, charged in flight
- Actuation: 4 mirror-pitched fins, ±12°, 15–25 N lateral, 200–300 m correction authority
- Navigation: NavIC L1/L5 + GPS; EKF fusion; roll ≥2 kHz magnetic + spin gyro
- Fuze: FM-CW proximity ring antenna / TIME (timed self-destruct) / inertia impact
- Interface: 2"-12 UNEF inductive fuze setter (pre-fire programming)
- Embedded: single MCU, 3 loops (power, guidance, fuze) — C/C++ on bare metal

Inset image: `main_design/renders/sec_quarter_iso.png` (quarter-section isometric).

## P4 — FEASIBILITY AND VIABILITY
- Ledger visual (user choice): **bar chart** — Bank 875 J / Consumed 344 J / Remaining 310 J
  (35% of bank) [SIMULATION]; spec ledger states ~28% end margin — cite both, chart uses sim.
- Risks (user choice): **risks→gates table** with 4 rows.
- Cost (user choice): **qualitative levers only**, no currency figures.

Feasibility analysis (template bullet 1):
- Energy ledger closes: 412–450 J generated in ascent + 15–25 J regen; 344 J consumed;
  310 J (35% of bank) left at impact [SIMULATION; spec §4 conservative ~28%]
- Also closes at 20 km (25%) and 40 km (20%) range cases [SIMULATION]
- Fits the existing shell: 2"-12 UNEF fuze well, Ø50.8 mm well, Ø30 through-bore leaves the
  explosive train untouched (§9.11); 1.18 kg kit, SWaP-C
- Gun-hard by construction: 13,400–15,500 g setback (§2.6), no battery chemistry, no cold gas,
  no pyrotechnics in the kit; electronics dark through launch, state held in FRAM, reboot ~2–3 s

Challenges and risks → strategies (template bullets 2+3, one table):
1. Windmill self-start is the single-point failure (no generation AND no actuation)
   → mitigation: self-start reliability target ≥0.999, dedicated test gate (§10)
2. 3DOF point-mass sim not enough → 6DOF rung (Magnus, precession, yaw-of-repose) before PDR (§10.1)
3. Motor Kt 0.095 N·m/A is analytical → FEMM/prototype verification gate
4. Annular EDLC gun-hard qualification data lacking → shock-test gate at 15,000 g

Manufacturability/cost (qualitative): YIL already manufactures the shell body — the kit adds
one custom motor, one custom supercap stack, and COTS sensors; modular S-series parts enable
single-part upgrades without redesign.

## P5 — IMPACT AND BENEFITS
- Framing (user choice): **operational first**, indigenous/Atmanirbhar second, environment/social third.
- Visual (user choice): **CEP target rings** — two concentric circles to scale (196 m unguided vs
  28.5 m guided) on a grid, class C graphic.

Impact on target audience (YIL / MoD):
- Every existing 155 mm casing becomes a PGM by swapping the fuze — no casing change, no new
  shell line; the kit threads into the standard 2"-12 UNEF fuze well
- Ammunition-effectiveness multiplier ~7×: median miss 196 m → 28.5 m [SIMULATION] — fewer
  rounds per target, less transport, less exposure of firing positions

Economic benefits:
- Casing stays YIL-made; kit adds one custom motor + one custom supercap + COTS sensors
  (qualitative cost levers — no invented figures)
- No battery → no shelf-life expiry, no logistics of charged/battery-dated stock (stack is
  charged in flight, never stored charged — §5)

Social / environmental benefits:
- 30 m-class precision reduces collateral damage and Dud-risk via TIME self-destruct mode
- NavIC-based navigation → indigenous PNT supply chain (Atmanirbhar route)
- Modular S-series parts → upgrades without redesign; no battery disposal stream

## P6 — RESEARCH AND REFERENCES
- Format (user choice): **titled entries** + one-line descriptions (no repo paths).
- Legend (user choice): **TARGET/SIMULATION/VERIFIED legend box** included.

References:
1. **PGK Spec Sheet — design of record** — single 12s10p ring-machine architecture, power
   architecture, energy ledger, fin loads, sensors/electronics/fuze/shell sections.
2. **Trajectory & Energy Verification (single machine)** — 3DOF RK4 point-mass + 100-run Monte
   Carlo: Cd 0.203 @ 30 km, CEP 28.5 m guided vs 196 m unguided, 412 J generated / 344 J used.
3. **Simulation script** — Python RK4 ballistic + guidance + energy model (reproducible run).
4. **CAD assemblies & S-series part library** — FreeCAD; mated round, half/quarter sections,
   one-body-per-part parametric parts.
5. **SIH 2026 Problem Statement SIH26098** — Ministry of Defence / Yantra India Limited,
   Ambajhari (Nagpur).
6. **SIH 2026 Idea Presentation Template** — official 6-slide format.
7. **Internal trade studies (prior revisions)** — dual-rotor comparison and prior-lineage
   design studies; historical reference for the single-machine decision.

Evidence-label legend:
- **TARGET** — design goal set by analysis, not yet measured (e.g. Kt 0.095 N·m/A)
- **SIMULATION** — produced by the trajectory/energy Monte Carlo (e.g. CEP 28.5 m)
- **VERIFIED** — confirmed against the dimensioned CAD model (e.g. interface diameters)

---

## Build & verification record (Step 4–5)
- `deck.html`: 6 fixed 1280×720 pages, `@page` print CSS, footer `(c)SIH Idea submission- Template`
  + page number + LARP sidebar on every page.
- PDF: `google-chrome --headless --no-pdf-header-footer --print-to-pdf=SIH26098_IDEA_Deck.pdf deck.html`
- Verified: exactly 6 pages (pdfinfo), 960×540 pt = 16:9; every page rendered to PNG and visually
  checked (fixed: SVG text overflow in arch diagram, timeline annotation collisions, CEP-ring
  label overlap, P1 tagline removal); footer string present exactly 6× in extracted text.
- Assets: `assets/{arch_diagram,mission_timeline,energy_ledger,cep_rings}.svg` (drawn, class C) +
  `{complete_iso,sec_quarter_iso,sec_half_front}.png` (class A). No class B CAD exports or class D
  AI prompts were needed (user chose existing renders).

## PS-coverage checklist — all verified in final deck
CAA ✓(P2/P3, S05/S06/S11) · GNC ✓(P3 EKF + sensor rows) · 3 fuze modes ✓(P2/P3/P5 — TIME named) ·
embedded SW ✓(P3 single MCU, 3 loops) · power mgmt ✓(P2/P4) · programming interface ✓(P3/P4 inductive
setter) · CEP ≤ 30 m ✓(P2/P5 sim 28.5 m) · standard-shell compatibility ✓(P4/P5 2"-12 UNEF) ·
high-g ✓(P2/P4 13,400–15,500 g) · SWaP-C ✓(1.18 kg) · modularity ✓(S-series P4/P5) ·
deliverables mapping ✓(arch doc→P3, CAD→P2/P3, electronics block diag→P3, G&C algo→P3,
sim correction→P2/P5, CEP estimate→P4; prototype noted as gap below)

## Owed by the team before upload (Step 6)
1. **Team ID** — placeholder `[Team ID — fill before upload]` on page 1.
2. **Prototype / proof-of-concept** — PS lists it as "preferred"; deck claims CAD + simulation only.
3. **Cost figures** — intentionally absent (qualitative levers only, per decision).
4. Team name **LARP** is used verbatim on title page + sidebars — confirm it matches the portal
   registration exactly.
