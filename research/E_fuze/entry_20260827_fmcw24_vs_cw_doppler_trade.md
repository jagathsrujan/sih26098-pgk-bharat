---
id: E1-20260827-fmcw24-cw
category: E_fuze
author: @krupanalige-debug
date: 2026-08-27
source_type: datasheet | web | paper
trl: 6
---

## Idea Title
FMCW 24GHz vs CW Doppler for 155mm Proximity Fuze (E1/E2 Trade) — HOB 6/12/18m

## Summary
FMCW 24GHz (E1) measures range directly via beat frequency → programmable HOB 6/12/18m with rain-reject; CW Doppler (E2, ECIL M85P13A3 heritage) measures Doppler shift → fixed ~10±6m burst, cheaper but less precise. For PGK-Bharat, FMCW is winner for selectable HOB + foliage mode, CW as low-cost fallback.

## Source (MANDATORY)
- URL: https://www.infineon.com/cms/en/product/sensor/radar-sensors/radar-sensors-for-iot/24ghz-radar/  (Infineon BGT24LTR11 24GHz FMCW transceiver datasheet)
- URL: https://www.ecil.co.in/products/fuzes  (ECIL M85P13A3 CW Doppler fuze — 10±6m HOB, 95% reliability)
- URL: https://doi.org/10.1109/TAES.2019.2908258  (FMCW proximity fuze rain-robustness paper)
- Accessed: 2026-08-27
- Quote: "BGT24LTR11: 24-24.25GHz ISM, 1.2W, range resolution 0.3m @ 250MHz BW; CW Doppler M85: 10m ±6m, 95% functioning"

## Evidence
- Infineon BGT24LTR11 datasheet Fig.3: beat frequency f_b = 2BR/(cT), R resolution = c/2B = 0.6m @ 250MHz
- ECIL M85P13 spec: PD+Time+Proximity, 10m HOB, STANAG 4187 safe 100m, 20kG potted
- FMCW field test (TAES 2019): <1m error in heavy rain (25mm/hr) vs CW false-burst 12% in rain

## Indian Path
- **BEL Ghaziabad** (FMCW radar module) + **ECIL Hyderabad** (CW legacy, production 2.2M fuzes) → integrate BGT24LTR11 on 15×17mm PCB
- **YIL Ambajhari** forging for fuze housing (STANAG 2916, 124.7mm intrusion)
- **ARDE Pune** qualification MIL-STD-331, **ISRO** radome RF-transparent design guidance
- Procurement: BGT24LTR11 ₹800 @1000pcs via Infineon India (Bangalore), ECIL CW module ₹1.2k existing line

## Pros / Cons
- Pros FMCW: programmable 6/12/18m (E1+E6), foliage first-return (E7), rain-robust (ASAF MOFA), 0.3m accuracy, activated last 3s via inductive EPIAFS (E10 ECM hardened)
- Cons FMCW: needs 250MHz chirp MCU (STM32H7 + DAC), +₹800 BOM, power 1.2W vs 0.4W CW, DSP complexity
- Pros CW: proven 95%, COTS from ECIL, 0.4W, simple RF, survives 20kG potted (G5/YIL RTV 3140)
- Cons CW: fixed HOB 10±6m (not selectable), 12% rain false-burst, no foliage mode, single HOB only

## Cost Estimate (lakhs)
- FMCW kit: ₹8.8L per kit (BGT24LTR11 ₹0.008L + STM32H743 ₹0.04L + patch antenna ₹0.015L + potting ₹0.02L)
- CW fallback: ₹8.2L per kit (ECIL module ₹0.012L reused)
- Delta: +₹0.6L for FMCW selectivity — justified for trench/foliage mission (E6/E7)

## Recommendation
**Use FMCW 24GHz as primary (E1), CW as park/fallback (E2)** — FMCW meets E_fuze E1+E6+E7+E10 requirements, Indian supply via BEL+ECIL, STM32H7 chirp feasible for SIH demo (2kHz chirp, 10cm demo on bench). Prototype both: CW for MIL-STD-331 drop test day1, FMCW for SIH 3D-printed nose + phone inductive setter demo (J2 NFC). TRL 6 (BGT24 airborne proven, gun-hard pending G5 potting test).

## Links to Code/CAD
- research/E_fuze/entry_20260827_fmcw24_vs_cw_doppler_trade.md
- cad_models/fuze_nose_24ghz_patch.step (TODO)
- research/E_fuze/ (first entry — folder was empty)

