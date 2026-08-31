---
id: I5-20260825-lshang-7flight-iterative-validation
category: I_test
author: @jagathsrujan
date: 2026-08-25
source_type: video
trl: 7
---

## Idea Title
7 Flight Tests in 30 Days with Open Failure Log — HITL -> Rail -> Field -> Yagi Tracking -> Parachute "定高开伞" Recovery

## Summary (2-3 lines)
Documents 7 launches: 2022.7.12 ascent ADRC test, 2022.7.17 improvement (failed, logged "控制性能恶化"), night "定高开伞成功" (altitude-triggered chute), final custom motor flight to 1100m. Pipeline: bench power-on (FFC stack) -> MissionPlanner HITL (wave FC) -> vertical rail 0-100cm baro/INS fusion -> field Yagi 15-element tracking -> drone top view + telemetry overlay + map, with 2/7 failures transparently titled. Gold standard for SIH I_test methodology (I1-I6).

## Source (MANDATORY - no URL = reject)
- URL: file:///Users/jagathsrujan/Downloads/Canard%20control%20vertical%20recovery%20guidance%20technology%20experimental%20rocket%20development%20-%20L%20Shang%20%28720p,%20h264%29.mp4
- Accessed: 2026-08-25
- Quote: "首次发射试验 上升段姿态控制测试 2022.7.12 | 第二次发射试验 针对第一次试验的问题进行改进 2022.7.17 | 改进失败 控制性能进一步恶化 姿态控制误差增大 开伞系统工作异常 下降段姿态控制异常 | 定高开伞成功 | 第七次发射试验 搭载自研火箭发动机"
- Evidence timestamps: HITL 05:15, Rail 05:30, Flight1 06:40 drone, Yagi 08:50, Failure slide 10:00, Night chute 14:10, Custom motor 20:00

## Evidence
- thumb_0315.jpg: HITL GCS Insta 360 trajectory green loop, speed dial 00.03 m/s, hand waving 3-board stack
- thumb_0330.jpg: Rail test: 0-100cm ruler + laptop "实时高度曲线" altitude plot 38-40, 3D rocket + horizon
- thumb_0450.jpg: Drone top view: smoke trail vertical over rice fields, launch point smoke puff
- thumb_0470/0730.jpg: Telemetry overlay splitscreen: left 3D model + compass/blue horizon + "ROL/PIT/YAW/Height" values (e.g., 68.5/-15.6/121.5/238.83) + bottom map blue trajectory kink, right sky cam
- thumb_0530.jpg: Yagi 15-element + red dot aiming, white cable = 900MHz telemetry tracking for recovery (field lesson)
- thumb_0600.jpg: Black failure slide 5 bullets verbatim (worse control, parachute anomaly, descent attitude anomaly) — proves iterative learning
- thumb_0650/0700.jpg: Ignition ground smoke + red drogue chute at apogee, transition to vertical descent (his "垂直回收")
- thumb_0850.jpg: Night "定高开伞成功" with map inset — altitude-triggered (e.g., 150m AGL) not timer
- thumb_1100.jpg: Custom motor sunset flight horizon ~1km altitude, proves propulsion independence
- cad_models/out_sim style trajectory: his flight resembles your `A. range vs altitude / B. cross-range` panels

## Indian Path
YIL proof: ARDE Aerobutt 20kG + G5 howitzer soft recovery into sand (I5) for post-fire IMU integrity (like his chute but 15kG). Replace Yagi with BEL telemetry + NavIC logging. MIL-STD-331C Group A (transport/vibration/humidity/thermal shock/2.1m drop hot/cold) before any hot fire — his failures show skipping environmental costs 1 extra launch.

## Pros / Cons
- Pros: Fast iterative <30 days, transparent failure culture wins SIH judges, full sensor-to-flight traceability (bench->HITL->rail->field), altitude-triggered recovery is directly reusable for PGK safe-separation logic, drone + map overlay template for SIH demo video
- Cons: No MIL-STD-331, no Aerobutt/G5 high-G, no 1000-run Monte Carlo CEP histogram (your I1), no PRESIMEN SDR HIL I2, no wind 7m/s robustness, only 1k altitude not 30km artillery, 2/7 failures would be 97% lot acceptance failure (PGK needs 41/42)

## Cost Estimate (lakhs)
His 7 flights ~₹0.35L (motors ₹0.03L each + PA12 prints + travel). SIH equivalent: bench HITL ₹0.1L + rail ₹0.05L + G5 single shot ₹0.5L + Aerobutt ₹0.2L + 300 Monte Carlo (free). Total I_test ₹1.5-2L vs gun fire ₹5L per shot — savings by emulating his subscale rocket first.

## Recommendation
**Use methodology, replace environment.** For SIH deliverable "Simulation + PoC": 1) Replicate his 3-stage table demo (HITL + rail 100cm) for internal review — film exactly like thumb_0330.jpg, 2) Run your `simulate_trajectory_155.py` Monte Carlo N=300 to generate CEP histogram (add panel C to his A+B), 3) Do 1x subscale rocket with your PGK nose (like his 7th flight) + 1x G5 soft recovery — don't attempt full gun yet. Document failures like his slide.

## Links to Code/CAD
- cad_models/simulate_trajectory_155.py:220 Monte Carlo + results.json (ballistic vs guided CEP)
- cad_models/out_sim/trajectory_comparison.svg (replicate his telemetry split)
- research/I_test/, research/F_power/ (PZT alternator recovery)
- SIH26098_Exhaustive_Ideas_Catalog.md:184 (I1-I6) + I5 Aerobutt
