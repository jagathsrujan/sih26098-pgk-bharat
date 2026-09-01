# SIH26098 — Flight-Article BOM: PGK for 155mm Shell (Production Build)

**Version:** 2.0 | **Date:** 2026-08-29 | **Scope:** Submission deliverable — per-unit build of materials for the
**Precision Guidance Kit (nose module)** fitted to standard 155mm HE bodies (STANAG 2916 fuze interface, 39/45/52 cal, ATAGS/Dhanush/K9/M777).

**Basis:** Frozen architecture from `SIH26098_PGK_KIT_DEEP_DIVE.md` §2, now **detailed in CAD** (`PGK_155mm.FCStd`):
shell-spin rotor hub → **one 61811-class thin-section de-spin bearing (55×72×9)** → Ø106 dome-nosed **de-spun stator**
carrying **4 fixed strakes** (Ø148 aero envelope), a **12-pole ring motor** (roll-torque steering + regen power, FOC-driven),
a **detent pawl + solenoid launch lock**, Ø87 GNC PCB (dual MCU lockstep, IMU, mag, dual Hall index), **6× 14430 buffer cells**,
GNSS receiver + Ø25 patch under the RF dome. Four fixed strakes on ONE common de-spun frame replace the 4-servo canard story.

> **Boundary & compliance note (read before costing):**
> 1. This is a **paper-design BOM** for the SIH submission. Nothing here has been manufactured or fired.
> 2. **Energetics (S&A, firing train) appear as cost allocations only**, procured through OFB/DRDO channels under
>    MIL-STD-1316B / STANAG 4187. This document intentionally contains **no energetics design content**.
> 3. Export-controlled items (SAASM/M-code, CRPA arrays) are **not specified**; indigenous equivalents are named instead.
> 4. All prices are engineering estimates (Aug 2026) for planning — not quotes. Figures are INR.

---

## 1. Kit-level envelope (design targets, per briefing §1)

| Parameter | Value |
|---|---|
| Kit mass | ~770 g target (replaces standard fuze in the fuze well) |
| Kit envelope (CAD) | Ø148 × 168 mm above the shell nose (`PGK_155mm.FCStd`) |
| Interface | STANAG 2916 2-12UN thread (Ø56 insert), fuze-well length ≤ 228 mm class |
| Survivability target | 15,000 g setback, ~250 rev/s spin, −40 to +71 °C storage (JSS 55555) |
| Accuracy target | CEP ≤ 30 m (simulation evidence: `out_sim/`, 1000-run Monte Carlo) |
| Setback power-on | MEMS sensors unpowered through bore exit; g-switch power-up after setback (the key to COTS-grade survival) |

---

## 2. BOM — Guidance, Navigation & Control (GNC) section

| # | Item | Spec class | Make/Buy | Source (India) | Qty/kit | ₹ @10 (pilot) | ₹ @1000 (prod) |
|---|---|---|---|---|---|---|---|
| 2.1 | GNSS receiver module | Multi-constellation + NavIC, 20+ dB jamming margin via robust processing; gun-hard packaging | Buy | Indigenous: Astra Microwave / DCB / Alpha Design; alt: u-blox ZED-F9T class | 1 | 1,50,000 | 80,000 |
| 2.2 | GNSS patch antenna | Ø25 mm ceramic patch, radome-matched | Buy | Indigenous RF houses | 1 | 15,000 | 8,000 |
| 2.3 | Tactical MEMS IMU | 3-axis gyro (gyro bias drift ≤ 10°/h class) + accel; **unpowered during setback**, powered post-exit | Buy | Epson G330/G370 class / ADI ADIS class; indigenous option via IRDE transfer | 1 | 1,10,000 | 55,000 |
| 2.4 | GNC processor board | Dual MCU lockstep (STM32F405-class ×2 on the Ø87 demo PCB; flight: rugged FPGA+MCU), conformal-coated, potted | Make (PCB) | JLCPCB-class fab + in-house assembly | 1 | 50,000 | 30,000 |
| 2.5 | Setback g-switch + power sequencing | Acceleration-actuated, arms post-bore-exit (safety interlock) | Buy | Indigenous electro-mech | 1 | 15,000 | 6,000 |
| 2.6 | De-spin bearing | **ONE** thin-section gun-hard bearing, 61811 class (55×72×9, steel races), single-point A↔B isolation per `PGK_155mm.FCStd` | Buy | Indigenous bearing OEM (SRB/NBC custom) | 1 | 40,000 | 18,000 |
| | | | | | **Subtotal** | **3,80,000** | **1,97,000** |

## 3. BOM — Strake steering (single-frame roll-torque architecture)

| # | Item | Spec class | Make/Buy | Source (India) | Qty/kit | ₹ @10 | ₹ @1000 |
|---|---|---|---|---|---|---|---|
| 3.1 | Ring torque motor | 12-pole coil ring (Ø84) on stator + rotor magnet ring in hub; FOC-driven; **dual-mode: steering torque + spin-power regen** | Buy (custom winding) | Indigenous actuation house (e.g., Alpha Design / Precimax class) | 1 | 1,10,000 | 45,000 |
| 3.2 | Strake set | 4× fixed strakes, Ø148 envelope, z788–876, machined/composite, on the de-spun frame | Make | Local CNC / composite vendor | 1 set | 30,000 | 10,000 |
| 3.3 | De-spun stator body | Machined Ø106 dome-nosed frame, z778–915, integral strake roots + bearing seat | Make | Local CNC vendor | 1 | 35,000 | 14,000 |
| 3.4 | Angle feedback | Dual Hall index (per-rev latch) + IMU/mag soft estimator on carrier PCB | Buy | Indigenous | 1 | 8,000 | 3,000 |
| 3.5 | Detent launch lock | Pawl + solenoid D12×20 class, couples rotor↔stator through setback/spin; release = armed | Buy | Indigenous electro-mech | 1 | 12,000 | 5,000 |
| | | | | | **Subtotal** | **1,95,000** | **77,000** |

## 4. BOM — Power section

| # | Item | Spec class | Make/Buy | Source (India) | Qty/kit | ₹ @10 | ₹ @1000 |
|---|---|---|---|---|---|---|---|
| 4.1 | Spin-power regen (ring-motor drag mode) | **No separate alternator** — the §3.1 ring motor regenerates in drag mode; rectifier/boost front-end only | Make | In-house + winding subcontract | 1 | 10,000 | 4,000 |
| 4.2 | Power conditioning | 3φ rectifier + boost + LDO, potted | Make | In-house | 1 | 20,000 | 9,000 |
| 4.3 | Buffer energy bank | 6× 14430 high-temp Li-ion in hex bay (r36.5) + BMS, per `PGK_155mm.FCStd`; sized for terminal-guidance burst | Buy | Indian cell OEM | 1 | 18,000 | 7,000 |
| 4.4 | Backup thermal battery *(optional — recommended for fuze section)* | Short-duration, > 125 °C, e.g., High Energy Batteries Ltd (HEBL) product | Buy | **HEBL (controlled procurement)** | 1 | 60,000 | 35,000 |
| 4.5 | Gun-hard harness/connectors | Potted, lock-wired | Make/Buy | Indigenous | 1 | 20,000 | 8,000 |
| | | | | | **Subtotal** | **68,000** | **28,000** |

## 5. BOM — Fuze section (multi-mode PD/MT/VT)

| # | Item | Spec class | Make/Buy | Source (India) | Qty/kit | ₹ @10 | ₹ @1000 |
|---|---|---|---|---|---|---|---|
| 5.1 | Fuze electronics board | Safety state machine per MIL-STD-1316B logic philosophy, dual independent safety paths | Make (PCB) | In-house + fab | 1 | 55,000 | 28,000 |
| 5.2 | VT/Doppler sensor module | Gun-hard microwave Doppler front-end (K-band class), range-gated | Buy | Indigenous RF (Astra/ECIL class) | 1 | 45,000 | 22,000 |
| 5.3 | Safety & Arming (S&A) mechanism | **CONTROLLED ITEM — allocation only.** STANAG 4187-compliant, setback+spin-actuated | Buy | **OFB / DRDO channel** | 1 | 1,40,000 | 70,000 |
| 5.4 | Firing train | **CONTROLLED ITEM — allocation only.** Standard OFB fuze-train components; **no energetics design in this document** | Buy | **OFB channel** | 1 | 50,000 | 22,000 |
| | | | | | **Subtotal** | **2,90,000** | **1,42,000** |

## 6. BOM — Structures & interface

| # | Item | Spec class | Make/Buy | Source (India) | Qty/kit | ₹ @10 | ₹ @1000 |
|---|---|---|---|---|---|---|---|
| 6.1 | Nose dome | Dome-nosed stator crown, Ø106→apex; **RF window at apex for the GNSS patch** (GFRP/quartz insert or dielectric dome on the flight article — the CAD dome is machined metal for the demonstrator) | Make | Composite vendor | 1 | 35,000 | 16,000 |
| 6.2 | Rotor hub + thread insert + seals | Machined 7075/SS, STANAG 2916 2-12UN insert (Ø56), Ø63 rotor hub w/ magnet ring + detent notches, Ø96 O-ring bay seal | Make | Local CNC vendor | 1 | 85,000 | 38,000 |
| 6.3 | Seals, coatings, keeper | Environmental sealing per JSS 55555, lubricant for 250 rev/s spin | Buy | Indigenous | 1 | 15,000 | 5,000 |
| | | | | | **Subtotal** | **1,35,000** | **59,000** |

## 7. Recurring integration cost (per kit)

| # | Item | ₹ @10 | ₹ @1000 |
|---|---|---|---|
| 7.1 | Assembly, potting, QA, acceptance test (spin-table + environment screen) | 40,000 | 15,000 |
| 7.2 | Gun-qualification amortization (setback/spin/telemetry shots at TBRL/ARDE ranges) | 1,20,000 | 40,000 |
| | **Subtotal** | **1,60,000** | **55,000** |

---

## 8. Cost roll-up vs PS target (₹8–11 L per kit)

| Section | Pilot (10 units) | Production (1,000 units) |
|---|---|---|
| GNC (§2) | 3,80,000 | 1,97,000 |
| Strake steering (§3) | 1,95,000 | 77,000 |
| Power (§4) | 68,000 | 28,000 |
| Fuze (§5) | 2,90,000 | 1,42,000 |
| Structures (§6) | 1,35,000 | 59,000 |
| Integration (§7) | 1,60,000 | 55,000 |
| **Per-kit total (excl. optional thermal battery)** | **≈ ₹12.3 L** | **≈ ₹5.6 L** |
| *(Incl. optional thermal battery)* | *(≈ ₹12.9 L)* | *(≈ ₹5.9 L)* |

**Honest reading for the pitch:** pilot-batch units land ~₹12.3–12.9 L because GNSS/IMU/S&A carry prototype pricing + qual amortization;
**the PS band (₹8–11 L) is met between ~100–250 units, and production volume beats it (~₹5.6 L excl. thermal battery)**. The v2 CAD detail
(single bearing, ring-motor-does-both, Hall feedback instead of resolver, Li-ion buffer) pulled ~₹1.3 L/kit out of v1 while
keeping every safety item intact. Say this explicitly — it reads as engineering maturity, and the ₹8–11 L claim is defensible
at volumes OFB actually buys.

## 9. One-time NRE (not per-unit, one sentence for the budget slide)

Design, CAD/FEA, firmware, tooling, and 5–8 gun-qual shots: **~₹0.8–1.2 Cr one-time**, comparable to any DRDO prototype cycle.

## 10. Standards & qualification matrix (tick-list for the submission)

| Standard | Applies to | Status in this BOM |
|---|---|---|
| STANAG 2916 | Fuze interface geometry (§6.2) | Spec'd |
| MIL-STD-1316B / STANAG 4187 | Fuze safety logic + S&A (§5.1, §5.3) | S&A via OFB; logic philosophy in design |
| JSS 55555 | Environmental (temp/vibe/humidity) | Qual line §7.2 |
| MIL-STD-461 class | EMI/EMC | Potting + screened harness §4.5 |
| 15,000 g setback | All electronics | Unpowered-at-setback design + g-switch (§2.5) |

## 11. Procurement risk notes

1. **S&A + firing train are the schedule-critical items** (OFB channel lead time) — start the MoU conversation with Yantra India early; this is also why they're cost allocations, not designs.
2. GNSS jamming: single patch + robust receiver processing only — CRPA was rejected on cost/SWaP; state the trade honestly.
3. IMU: if indigenous gun-hard MEMS transfer (IRDE/DRDO) materializes, §2.3 drops 40–50% — that is the single biggest cost lever toward the PS band.
4. Regen harvesting vs thermal battery: ring-motor regen is the primary (power-on after ~4–6 s of spin, same motor does steering + harvest — one less subsystem than v1's alternator), thermal battery kept as fuze-section backup; a judge-facing trade slide exists here.
