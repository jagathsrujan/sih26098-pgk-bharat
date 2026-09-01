# SIH26098 — Flight-Article BOM: PGK for 155mm Shell (Production Build)

**Version:** 3.0 | **Date:** 2026-09-01 | **Scope:** Submission deliverable — per-unit build of materials for the
**Precision Guidance Kit (nose module)** fitted to standard 155mm HE bodies (2"-12UN fuze-well interface, 39/45/52 cal, ATAGS/Dhanush/K9/M777).

**Basis:** **S-series single time-share machine** — design of record `cad_models/PGK_SPEC_SHEET.md` + canonical CAD
`cad_models/PGK_Motor_Assembly.FCStd` (+ part files `cad_models/parts/S01–S10, M01/M04/M09/M10`). One 12s10p ring PMSM
(stator Ø58.5 / rotor Ø70, 25 mm zone, z138–163) is the windmill alternator during ascent and the fin-actuator servo during
descent; 4 mirror-canted fins (Ø108, ±12°, S05/S06) ride the rotor; annular supercap 0.6 F @ 54 V (S09) replaces every
battery; nose RF section S07 (GFRP ogive radome + GNSS antenna + inductive setter coupler); nav ring S08; fuze-well stack S10.

> **Boundary & compliance note (read before costing):**
> 1. This is a **paper-design BOM** for the SIH submission. Nothing here has been manufactured or fired.
> 2. **Energetics (S&A, firing train) appear as cost allocations only**, procured through OFB/DRDO channels under
>    MIL-STD-1316B / STANAG 4187. This document intentionally contains **no energetics design content**.
> 3. Export-controlled items (SAASM/M-code, CRPA arrays, SiIMU02) are **not specified**; indigenous equivalents are named instead.
> 4. All prices are engineering estimates (Sep 2026) for planning — not quotes. Figures are INR.

---

## 1. Kit-level envelope (as modeled, per spec sheet §1/§2)

| Parameter | Value |
|---|---|
| Kit mass | **~1.23 kg modeled** (motor 810 g + nose 127 g + fuze stack 269 g + control ring 21 g; wire/energetics pending) |
| Kit envelope (CAD) | Ø110 max × z=0–220 (external Ø108, z=125–220 above the shell nose datum) |
| Interface | 2"-12UN fuze-well thread (S10 thread ring), Ø30 explosive-train bore reserved through z=173 |
| Survivability target | 15,500 g setback, 15,480 rpm spin, −40 to +71 °C storage (JSS 55555) |
| Accuracy target | CEP ≤ 30 m (simulation evidence: `sim/RESULTS_SINGLE_MACHINE.md` — guided 28.5 m vs 196 m unguided, 100-run MC) |
| Power-on | **Phase 0 pre-fire inductive programming** (EPIAFS-style setter through the nose coupler), power latched OFF at fire; bus live from the windmill ~2 s after muzzle exit — nothing powered during setback |

---

## 2. BOM — Guidance, Navigation & Control (GNC) section

| # | Item | Spec class | Make/Buy | Source (India) | Qty/kit | ₹ @10 (pilot) | ₹ @1000 (prod) |
|---|---|---|---|---|---|---|---|
| 2.1 | GNSS receiver module | NavIC L1/L5 + multi-GNSS, SAC NavASIC V3 class; software-AJ via deep IMU coupling; gun-hard packaging | Buy | Indigenous: Astra Microwave / DCB / Alpha Design; SAC reference design | 1 | 1,50,000 | 80,000 |
| 2.2 | GNSS patch antenna | Ø30 mm stacked patch (L1/L5), ground Ø42, radome-matched, on-axis in S07 | Buy | Indigenous RF houses | 1 | 15,000 | 8,000 |
| 2.3 | Tactical MEMS IMU | Gun-hard (20,000 g setback), roll-axis gyro ≥±25,000°/s variant; indigenous NavIC-integrated munitions IMU route (spec §9.1) | Buy | Indigenous (SAC/IRDE transfer); SiIMU02-class is export-controlled reference | 1 | 1,10,000 | 55,000 |
| 2.4 | Processor boards (split) | **M04** stator PCB: 3-phase gate driver + 16–20 A bridge + C2000-class core 1 (FOC); **S08** control ring: GNSS Rx + core 2 (nav/EKF) + FRAM; conformal-coated, potted | Make (PCB) | JLCPCB-class fab + in-house assembly | 2 | 50,000 | 30,000 |
| 2.5 | Phase-0 inductive coupler + power-path mux | Ferrite-cup coupler (S07, z185.5–191.5, ~1 W, ≥115 kbaud) + setter⇄bus auto-select mux, latch-off on fire (spec §8.1) | Make/Buy | Indigenous (ferrite + electro-mech) | 1 | 25,000 | 10,000 |
| 2.6 | Rotor bearings | **TWO** angular-contact Ø40×Ø52×8 class (M09: z130, z166), gun grease; rotor spins on the static shaft tube — no de-spin bearing exists | Buy | Indigenous bearing OEM (SRB/NBC custom) | 2 | 60,000 | 25,000 |
| 2.7 | Rotor-angle sensor set | 2-pole diametral bias ring (S04, Ø41/Ø51.6×3, N42SH) + sin/cos Hall/MR array on the shaft-tube board (z163–166) + 3× digital Hall fallback | Buy | Indigenous sensor houses (ams/iC-Haus die class) | 1 | 8,000 | 3,000 |
| 2.8 | Magnetometer roll module | RM3100-class / raw MR bridge, ≥2 kHz sampling (body spin 258 rev/s), ring board on M01 z≈115–120 | Buy | PNI/indigenous | 1 | 8,000 | 3,000 |
| 2.9 | VNS camera module | Gun-hard EO (or LWIR) camera + sapphire flank window, roll-gated exposure, scene-match correlator on S08 core 2 (§9.10) — GPS-denied terminal fallback | Buy | Indigenous imaging (SAC/IRDE route) | 1 | 60,000 | 28,000 |
| | | | | | **Subtotal** | **4,86,000** | **2,42,000** |

## 3. BOM — Fin steering (single time-share machine)

| # | Item | Spec class | Make/Buy | Source (India) | Qty/kit | ₹ @10 | ₹ @1000 |
|---|---|---|---|---|---|---|---|
| 3.1 | Ring PMSM (12s10p) | Stator Ø58.5 (S01 M250-35A laminations + S02 12×~150-turn coils), rotor Ø70 (S04 back-iron + 10× N42SH arcs + carrier + bias ring), 0.75 mm gap, z138–163; FOC dual-mode: alternator ⇄ servo | Buy (custom winding) | Indigenous actuation house (Alpha Design / Precimax class) | 1 | 1,20,000 | 48,000 |
| 3.2 | Fin set | 4× fins S05/S06 (±12° mirror pairs @0/90/180/270), root 25/tip 15/span 16 mm, 7075, bolted to the **S11 canard shell** — Ø108 < bore Ø155: **no deployment mechanism** | Make | Local CNC vendor | 1 set | 30,000 | 10,000 |
| 3.3 | **Canard shell (S11, SLS)** | AlSi10Mg SLS-printed drum Ø76 z136–172.5: carries fins (8× M5), sleeves back-iron (8× M4), seats bearing-B race; **integral 8-station lateral impulse thruster (LIT) cavities + nozzles + igniter bores** (§2.7) | Make (AM) | Indian metal-AM bureau (WIPRO 3D / Raja Ramanna Centre class) | 1 | 85,000 | 32,000 |
| 3.4 | Static structure | M01 shaft tube (Ø30/Ø40, 7075, wire slots full-length, datum flange + fwd ext) + M10 aft endbell | Make | Local CNC vendor | 1 | 40,000 | 15,000 |
| 3.5 | LIT propellant + igniters | **CONTROLLED ITEM — allocation only.** Solid micro-grains (~5 g/kit) + e-match igniters, OFB/DRDO channel; loading/qualification per STANAG 4187 philosophy | Buy | **OFB / DRDO channel** | 1 set | 40,000 | 18,000 |
| | | | | | **Subtotal** | **2,95,000** | **85,000** |

*(v2's de-spin bearing, de-spun strake frame, Hall index and detent launch lock are all eliminated: the fins ride the
rotor, the shell keeps its spin, and Ø108 fins need no deployment or launch lock.)*

## 4. BOM — Power section

| # | Item | Spec class | Make/Buy | Source (India) | Qty/kit | ₹ @10 | ₹ @1000 |
|---|---|---|---|---|---|---|---|
| 4.1 | Spin-power regen front-end | Same three half-bridges as the motor (§3.1) run as active rectifier; buck charger 85%; mode switch is software (spec §2.3) | Make | In-house + winding subcontract | 1 | 10,000 | 4,000 |
| 4.2 | Power conditioning | Wide-Vin bucks (54→20 V window) + 3.3/5 V rails + local holdup caps; potted | Make | In-house | 1 | 20,000 | 9,000 |
| 4.3 | Annular supercap stack | **0.6 F @ 54 V = 875 J** custom annular-wound EDLC (S09, Ø49/Ø31×30 + bus discs, z70–100) — charged in flight, never stored charged; **no cells, no BMS, no battery of any kind** | Buy (custom) | Indian EDLC OEM / imported cells-annular | 1 | 25,000 | 9,000 |
| 4.4 | Gun-hard harness/connectors | Potted, lock-wired; incl. S10 connector (7-pin) + flex through housing web slot | Make/Buy | Indigenous | 1 | 20,000 | 8,000 |
| | | | | | **Subtotal** | **75,000** | **30,000** |

*(v2's 6× Li-ion 14430 buffer and the optional thermal battery are **removed** — rejected by calculation and replaced by
the in-flight-charged supercap; see `legacy/` and spec §8.)*

## 5. BOM — Fuze section (multi-mode PD/MT/VT; S10 stack z0–70)

| # | Item | Spec class | Make/Buy | Source (India) | Qty/kit | ₹ @10 | ₹ @1000 |
|---|---|---|---|---|---|---|---|
| 5.1 | Fuze electronics board | Safety state machine per MIL-STD-1316B logic philosophy, dual independent safety paths (S10 firing PCB ring) | Make (PCB) | In-house + fab | 1 | 55,000 | 28,000 |
| 5.2 | VT/Doppler sensor module | Gun-hard microwave Doppler front-end (K-band class), range-gated; microstrip ring antenna on S10 | Buy | Indigenous RF (Astra/ECIL class) | 1 | 45,000 | 22,000 |
| 5.3 | Safety & Arming (S&A) mechanism | **CONTROLLED ITEM — allocation only.** STANAG 4187-compliant, setback+set-forward+spin-actuated (S10 rotor z34–40) | Buy | **OFB / DRDO channel** | 1 | 1,40,000 | 70,000 |
| 5.4 | Firing train | **CONTROLLED ITEM — allocation only.** Standard OFB fuze-train components; **no energetics design in this document** | Buy | **OFB channel** | 1 | 50,000 | 22,000 |
| | | | | | **Subtotal** | **2,90,000** | **1,42,000** |

## 6. BOM — Structures & interface

| # | Item | Spec class | Make/Buy | Source (India) | Qty/kit | ₹ @10 | ₹ @1000 |
|---|---|---|---|---|---|---|---|
| 6.1 | Nose RF section | **S07** GFRP ogive radome (ρ=109.55, z173–220, 2.5 mm wall — RF-transparent full-time, not a metal demonstrator) + antenna support + coupler seat; flange to M10 | Make | Composite vendor | 1 | 35,000 | 16,000 |
| 6.2 | Fuze-well structure | **S10** steel thread ring (2"-12UN) + 7075 double-wall housing (Ø30.4 bore liner, cavity slot) + connector disc | Make | Local CNC vendor | 1 | 70,000 | 30,000 |
| 6.3 | Seals, coatings, keeper | Environmental sealing per JSS 55555, grease for the two rotor bearings | Buy | Indigenous | 1 | 15,000 | 5,000 |
| | | | | | **Subtotal** | **1,20,000** | **51,000** |

## 7. Recurring integration cost (per kit)

| # | Item | ₹ @10 | ₹ @1000 |
|---|---|---|---|
| 7.1 | Assembly, potting, QA, acceptance test (spin-table + inductive-setter BIT screen) | 40,000 | 15,000 |
| 7.2 | Gun-qualification amortization (setback/spin/telemetry shots at TBRL/ARDE ranges) | 1,20,000 | 40,000 |
| | **Subtotal** | **1,60,000** | **55,000** |

---

## 8. Cost roll-up vs PS target (₹8–11 L per kit)

| Section | Pilot (10 units) | Production (1,000 units) |
|---|---|---|
| GNC (§2, incl. VNS) | 4,86,000 | 2,42,000 |
| Fin steering / machine + LIT structure (§3) | 2,95,000 | 85,000 |
| Power (§4) | 75,000 | 30,000 |
| Fuze (§5) | 2,90,000 | 1,42,000 |
| Structures (§6) | 1,20,000 | 51,000 |
| Integration (§7) | 1,60,000 | 55,000 |
| **Per-kit total (no battery anywhere)** | **≈ ₹14.3 L** | **≈ ₹6.1 L** |

**Honest reading for the pitch:** pilot-batch units land ~₹14.3 L with the VNS camera and LIT
structure included (GNSS/IMU/S&A carry prototype pricing + qual amortization); **the PS band
(₹8–11 L) is met between ~150–300 units, and production volume beats it (~₹6.1 L)**. The v3
S-series detail (one machine does both jobs, two plain bearings instead of a de-spin ring,
supercap instead of cells+BMS, no deployment mechanism) kept every safety item while removing
the battery and its certification story entirely; the VNS + LIT add ~₹1.4 L at pilot but buy
GPS-denial resilience and a servo-failure backup — price them as the differentiator, not the base kit.

## 9. One-time NRE (not per-unit, one sentence for the budget slide)

Design, CAD/FEA, firmware, tooling, and 5–8 gun-qual shots: **~₹0.8–1.2 Cr one-time**, comparable to any DRDO prototype cycle.

## 10. Standards & qualification matrix (tick-list for the submission)

| Standard | Applies to | Status in this BOM |
|---|---|---|
| 2"-12UN fuze interface (STANAG 2916 class) | S10 thread ring (§6.2) | Spec'd |
| MIL-STD-1316B / STANAG 4187 | Fuze safety logic + S&A (§5.1, §5.3) | S&A via OFB; logic philosophy in design |
| JSS 55555 | Environmental (temp/vibe/humidity) | Qual line §7.2 |
| MIL-STD-461 class | EMI/EMC | Potting + screened harness §4.5 |
| 15,500 g setback | All electronics | **Unpowered-at-setback architecture** (Phase 0 latch-off §8.1; FRAM retains state) |

## 11. Procurement risk notes

1. **S&A + firing train are the schedule-critical items** (OFB channel lead time) — start the MoU conversation with Yantra India early; this is also why they're cost allocations, not designs.
2. GNSS jamming: single patch + robust receiver processing only — CRPA was rejected on cost/SWaP; state the trade honestly.
3. IMU: if indigenous gun-hard MEMS transfer (IRDE/DRDO) materializes, §2.3 drops 40–50% — that is the single biggest cost lever toward the PS band.
4. **No-battery architecture:** the supercap charges in flight from the same machine that steers (windmill → 12 W into 875 J bank, 35% end-of-flight margin per `sim/RESULTS_SINGLE_MACHINE.md`). The single-point failure is windmill self-start (spec §10.3) — mitigation is CFD/spin-tunnel evidence, not a battery. v2's thermal-battery backup option is **withdrawn** (rejected by calculation, `legacy/`).
