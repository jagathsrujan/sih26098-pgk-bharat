---
id: WELCOME-D-anvitapranjal18-glitch-20260826
category: D_sensors
author: @anvitapranjal18-glitch
date: 2026-08-26
source_type: assignment
trl: N/A
---

## Idea Title
Welcome — Anvita Pranjal (ECE 2nd yr) — D_sensors Primary + C_gnc Backup

## Summary
Assigned primary: **D_sensors (Navigation Sensors D1-D16)** — best fit for Embedded Systems + PCB Design. Owns NavIC/GPS/IMU/baro/mag hardware, PCB for flight computer, driver bring-up. Backup: **C_gnc** — overlaps with GNC interest (flight computer runs PID/MPC/LSTM, feeds C_gnc team). Interest in GNC + Sensors + Embedded maps directly to sensor-to-GNC pipeline.

## Why This Fit (Decision Logic)
- Skills: Embedded Systems + PCB Design → D_sensors needs PCB for STA8090/MeitY NavIC + MEMS IMU (Atlantic 20kG) + MS5611 baro + LIS3MDL mag → custom 4-layer potted board (G5). C_gnc is algorithm-heavy (MATLAB) - less PCB.
- Interest: "GNC, sensors, Embedded" → D_sensors is embedded hardware for sensors, C_gnc is algorithm that consumes sensor data. You sit at the interface — ideal.
- ECE 2nd yr: D_sensors lets you deliver tangible PCB + sensor drivers early (high demo value for SIH), while learning GNC controls alongside C_gnc lead.
- Indian Path lever: YIL/BEL/ECIL + MeitY 10L NavIC chip + ISRO — PCB is the integration point.

## Assignment
- **Primary: D_sensors (Sensors & Embedded)** — Owns D1-D16, flight computer PCB, sensor drivers
- **Backup/Secondary: C_gnc (GNC)** — Support tightly-coupled GPS/INS, baro-aid, gyroless mag+accel
- Branch: `research/D_sensors-anvitapranjal18-glitch`

## First 3 Research Questions (gaps in catalog)
1. **D3 vs D5 trade:** STA8090 Teseo III + STA5635 vs MeitY 10L NavIC+GPS chip — which has public devkit/SDK for STM32H7? Find pricing, lead time, driver availability. [Source: Elena NavIC, MeitY RFP]
2. **Gun-hard IMU D6:** Atlantic Inertial gun-hard MEMS (20kG Aerobutt) — what's the COTS eval board cost/pinout? Compare vs ADXL1004 (±500g) + LIS3MDL (D7/D8) discrete gyroless approach for SIH demo budget. [Source: Atlantic datasheet, ADXL1004 potted 10kG]
3. **Baro + FMCW D9/D10:** MS5611 10cm resolution vs 24GHz FMCW radar for HOB — can a `₹2k` MS5611 demo the proximity fuze (E1) accurately in last 3s induction window? Power/sample rate? [Source: MS5611 datasheet, FOX mini radar]

## Next 3 Concrete Tasks
1. Read `SIH26098_Exhaustive_Ideas_Catalog.md` §4 Category D (D1-D16) and `SIH26098_Ideas_Database.json` D1-D16 entries — pick one sensor to deep-dive.
2. Run `research/templates/agent_prompt.md` with `{CATEGORY}=D_sensors` via your AI agent — create `research/D_sensors/entry_20260827_<topic>.md` for question 1 above (with URL + TRL + cost ₹L).
3. Checkout branch and push: `git checkout research/D_sensors-anvitapranjal18-glitch && git add . && git commit -m "feat(D): welcome anvitapranjal18-glitch"` && `git push -u origin research/D_sensors-anvitapranjal18-glitch` then `python3 research/merge.py`.

## Links to Code/CAD
- `research/D_sensors/` (your folder)
- `research/templates/agent_prompt.md` (paste with D_sensors)
- `research/templates/entry_template.md`
- `SIH26098_Exhaustive_Ideas_Catalog.md:95-115` Category D

## Source
- Invite: https://github.com/jagathsrujan/sih26098-pgk-bharat/invitations (accept)
- Onboarding: `ONBOARDING_PROMPT.md:1`
