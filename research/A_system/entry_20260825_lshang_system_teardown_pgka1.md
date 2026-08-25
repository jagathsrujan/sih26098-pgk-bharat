---
id: A1-20260825-lshang-system-teardown
category: A_system
author: @jagathsrujan
date: 2026-08-25
source_type: video
trl: 7
---

## Idea Title
L Shang Canard-Control Vertical-Recovery Rocket — Full System Teardown vs SIH26098 PGK Baseline A1

## Summary (2-3 lines)
23:16 video analysis (1397 frames @1fps, 1280x720) of L Shang's 4-canard guided rocket: 5-bay architecture (GNSS/canard/avionics/chute/motor), 3-PCB stack, ICEM/Fluent CFD, ADRC Simulink, 7 flight tests (2022.7.12-2022.7.17) with 2 documented failures. Architecture maps 1:1 to SIH26098 A1 (PGK-clone screw-in fuze, despun brake) but uses A2 (4x proportional servo) which is not gun-hard.

## Source (MANDATORY - no URL = reject)
- URL: file:///Users/jagathsrujan/Downloads/Canard%20control%20vertical%20recovery%20guidance%20technology%20experimental%20rocket%20development%20-%20L%20Shang%20%28720p,%20h264%29.mp4 (local teardown, original Bilibili: L Shang / 尚工, search "鸭舵控制垂直回收")
- Accessed: 2026-08-25
- Quote: "火箭结构设计 | 嘉立创EDA 飞控系统PCB设计 | 嘉立创PCB打样与SMT贴片 | ICEM非结构化网格划分 | 高性能计算机求解 Intel Xeon Platinum 8275CL | 火箭飞行控制建模与仿真 MATLAB SIMULINK | 组合导航系统 惯性导航 气压计 GNSS 基于自适应卡尔曼滤波 | 首次发射试验 上升段姿态控制测试 2022.7.12 | 第二次发射试验 2022.7.17 | 改进失败 控制性能进一步恶化 | 定高开伞成功 | 第七次发射试验 搭载自研火箭发动机"
- Frames extracted: /tmp/canard_frames/thumb_%04d.jpg (1397 jpgs, ffprobe 1280x720 29.97fps 1071kb/s)

## Evidence
- thumb_0001.jpg: CAD nose 150.00mm x 34.00mm ogive, 5-module transparent layout with rails
- thumb_0005.jpg: Exploded yellow canard bay with 2x blue servo horns + Beitian GNSS + 3-PCB stack
- thumb_0015.jpg: Full rocket 4x forward trapezoidal canards + 4x rear fixed fins, black/white livery
- thumb_0025.jpg: KST CS07 servos x4 in cruciform, N20-class, white PA12 shells
- thumb_0045.jpg: Flight Controller STM32F4 QFP64, KEY/GPIO PD12-15, I2C SDA/SCL, 65mm circular cut (fits 56mm PGK bore)
- thumb_0055/0070.jpg: JLCPCB panel 12-up black mask, "嘉立创PCB打样与SMT"
- thumb_0120/0150.jpg: Wiring harness yellow/red, LEDs through vents
- Video timeline: 0:00 CAD -> 0:35 PCB -> 1:20 sensor -> 2:55 ICEM -> 3:05 Fluent -> 4:30 Simulink -> 5:00 EKF -> 6:40 Flight 1

## Indian Path
YIL Ambajhari 10,000-ton extrusion press (19 Jun 2026) for 56mm OD housing forging, BEL/ECIL for RF, ARDE for 6DOF/bourrelet, ISRO NavIC chip (MeitY 10L), IIT Madras 10m CEP algorithm. Replace L Shang's Beitian BN880 with ZED-F9P+NavIC L5 (D2-D5), hobby servos with B1 despun brake (no servo) for 20yr storage.

## Pros / Cons
- Pros: Complete proven toolchain (CAD->CFD->PCB->Simulink->HITL->field) in 30 days, JLCEDA/JLCPCB <$2/board, STM32F4 65mm circular proven, rapid iterative failures documented, open failure culture, 74% similar to PGK (canard + GNSS/INS)
- Cons: Architecture is A2 (4-servo proportional) not SIH winner A1 (brake) — costs ₹14-18L vs ₹8-11L, needs slip ring, cannot survive 15kG gun; battery LiPo not thermal/super-cap; no STANAG thread; no fuze

## Cost Estimate (lakhs)
L Shang BOM ~₹0.15L (PCB ₹0.02L x3 + KST x4 ₹0.08L + Data10 IMU ₹0.03L + PA12 print). PGK A1 clone target ₹8-11L (YIL forging ₹1.5L + BEL RF ₹2L + MEMS S&A ₹1L + NavIC ₹0.3L). Reusing his JLCPCB workflow saves ₹0.5L NRE.

## Recommendation
**Use as system template, Park A2 servo for subscale rocket demo, Use A1 brake for SIH final.** Copy his 5-bay stacking and 3-PCB circular layout directly into `cad_models/generate_pgk_155.py:162-177`. Switch actuation from direct servo to `B1/B2 bearing-isolated` before MIL-STD-331 testing.

## Links to Code/CAD
- cad_models/generate_pgk_155.py (R_BODY 28mm, FIN_TIP 75.5mm, staggered shafts Z_SHAFT1 146/Z_SHAFT2 152)
- cad_models/out_pgk/pgk_assembly.FCStd + preview_pgk_on_shell.png
- SIH26098_Exhaustive_Ideas_Catalog.md:32 (Category A, A1 winner)
- docs/LShang_Video_Teardown_Gap_Analysis.md (full 23min teardown)
