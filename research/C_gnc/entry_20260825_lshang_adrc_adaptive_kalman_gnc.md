---
id: C11-20260825-lshang-adrc-adaptive-kalman
category: C_gnc
author: @jagathsrujan
date: 2026-08-25
source_type: video
trl: 6
---

## Idea Title
L Shang ADRC Simulink + Adaptive Kalman Combined Nav (INS/Baro/GNSS) for Canard Rocket — Port to Spin-Stabilized PGK

## Summary (2-3 lines)
Simulink block "制御火箭仿真模型 Copyright 2022 LShang" shows ADRC (TD+ESO+NLSEF) for pitch/yaw, not PID. Combined nav "惯性导航 气压计 GNSS 基于自适应卡尔曼滤波" = 15-state INS+baro+GNSS adaptive EKF (MS5611 + FDISYSTEMS Data10 + Beitian). HITL via MissionPlanner fork (green 3D trajectory) + vertical rail baro test 0-100cm real-time altitude curve. Proven for fin-stabilized rocket; needs spin/Magnus adaptation for SIH.

## Source (MANDATORY - no URL = reject)
- URL: file:///Users/jagathsrujan/Downloads/Canard%20control%20vertical%20recovery%20guidance%20technology%20experimental%20rocket%20development%20-%20L%20Shang%20%28720p,%20h264%29.mp4
- Accessed: 2026-08-25
- Quote: "火箭飞行控制建模与仿真 MATLAB SIMULINK | 组合导航系统 惯性导航 气压计 GNSS 基于自适应卡尔曼滤波 | 惯导 气压计 融合定高 实时高度曲线 | Attitude_Control_ADRC"
- Tools: MATLAB/Simulink, JLCEDA Flight Controller STM32F405 QFP64 (thumb_0045/0095.jpg)

## Evidence
- thumb_0285.jpg: Simulink full sheet with " 제어火箭仿真模型 Copyright 2022 LShang", left Target/IMU, center ESO+nonlinear feedback + 4-way servo allocator, right canard bus
- thumb_0300.jpg: Black slide "组合导航系统 | 惯性导航 气压计 GNSS | 基于自适应卡尔曼滤波" (blue bars)
- thumb_0315.jpg: MissionPlanner-like GCS: 3D green trajectory loop, compass dial, hand waving FC board -> model follows, secondary laptop with code
- thumb_0330.jpg: Ladder test: hand holds rocket at 50cm vs wall ruler 0-100cm, laptop shows "实时高度曲线" altitude vs time ~38-40, bottom 3D rocket vertical + horizon, text "惯导 气压计 融合定高"
- thumb_0095.jpg: Power-on: 3 boards FFC + JST, LEDs red/blue/green, UART TELEM/SWD, proofs EKF runs on STM32F405 @168MHz
- thumb_0470.jpg: Flight telemetry overlay "ROL 68.5 PIT -15.6 YAW 121.5 Height 238.83" + map blue kink = EKF output rate ~10-20Hz

## Indian Path
ARDE GNC + IIT Madras 10m CEP (Hindu) + MeitY NavIC chip (10L) + DRDO ECCM. Port ADRC to STM32H743 (your `C_gnc`): add roll state p=~300Hz, bank-to-turn for A1 brake. Replace Beitian with ZED-F9P+NavIC L5 SPS 2.048MSPS (ION navi.573 RTL-SDR validated) + Atlantic gun-hard IMU D6 (20kG G5 howitzer). Keep MS5611 only for lab altitude demo, not flight (baro fails supersonic).

## Pros / Cons
- Pros: ADRC superior to PID for canard non-linearity + wind/CoP shift (treats as total disturbance), adaptive R scales with GNSS HDOP (his "自适应"), HITL + rail test method directly copyable for SIH table demo, STM32F4 proven 20Hz control loop
- Cons: Model is fin-stabilized (no gyroscopic 10k rpm, no Magnus, no despin coupling), no GNSS-denied backup (your C7 LSTM <5m), no NavIC, no high-G IMU, baro vertical channel useless at Mach 2, no model predictive (MPC C11) or PN (C9)

## Cost Estimate (lakhs)
Dev: STM32H7 ₹0.08L + ZED-F9P ₹0.15L + Data10 ₹0.3L + MS5611 ₹0.02L. Flight hardened: Atlantic IMU ₹2L. Algorithm NRE ₹2L (Simulink autocode). Total GNC ₹4-5L prototype, ₹0.8L production.

## Recommendation
**Use as simulation/reference material only.** If the team later studies the flight problem, the Simulink ADRC/EKF discussion can inform `cad_models/simulate_trajectory_155.py`. For the current exhibit, stop at a guarded low-speed relative-angle/LED bench test; do not stage rail, rocket, launch, or fuze tests.

## Links to Code/CAD
- simulate_trajectory_155.py:90 ZEM + CLS_CAN 0.005m2 (replace with ADRC coeff from thumb_0285)
- SIH26098_Exhaustive_Ideas_Catalog.md:74 (C1-C14) + C7 LSTM, C3 NavIC, C11 MPC
- research/C_gnc/, research/D_sensors/
