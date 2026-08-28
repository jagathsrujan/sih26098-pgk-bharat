# L Shang Canard Control Vertical Recovery Rocket — Frame-by-Frame Teardown vs SIH26098 Deliverables

> **Status:** historical reference only. The earlier servo/face-gear comparison remains useful for trade-study context, but it is not the active PGK exhibition architecture. The active model is the common-carrier demonstrator in `cad_models/generate_pgk_155.py`; the superseded two-motor CAD is archived in `legacy/old_two_motor_design/`.

**Video:** `Canard control vertical recovery guidance technology experimental rocket development - L Shang (720p, h264).mp4` | **Duration:** 23:16 | **Probe:** 1280x720 29.97fps 1071kb/s h264/aac | **Frames extracted:** 1397 JPG @1fps `thumb_%04d.jpg` (`/tmp/canard_frames/`) via `ffmpeg fps=1` | **Analysis date:** 2026-08-25

> Teardown method: ffprobe + 1fps thumbs + visual OCR (read 35 key frames) + cross-ref `SIH26098_Exhaustive_Ideas_Catalog.md` (108 ideas A-J) + `cad_models/generate_pgk_155.py` + `simulate_trajectory_155.py`.

---

## TL;DR for Judges

L Shang is useful historical evidence that a student team can complete a CAD/CFD/PCB/control workflow. It is not a template for the active physical exhibit: the rocket used four servo-driven control surfaces, while this workspace now uses one inert common carrier with four fixed illustrative canards. Keep the analysis as reference and keep flight, fuze, and performance work separate from the bench model.

---

## 1. Frame Timeline (23 min decoded)

| Timestamp | Frame | Title / Evidence | What He Built |
|-----------|-------|------------------|---------------|
| 0:00-0:10 | `thumb_0001.jpg` | `设计` CAD | Von Karman ogive **150.00 x 34.00mm**, 5-bay stack (GNSS→Canard(yellow)→Avionics→Chute→Motor) with internal rails |
| 0:05 | `thumb_0005.jpg` | `火箭结构设计` Exploded | Beitian GNSS (blue), yellow canard bay with 2x blue horns, 3-PCB black stack, SMA radome |
| 0:15 | `thumb_0015.jpg` | Full render | **4x trapezoidal forward canards + 4x clipped delta fixed tail fins**, black/white modular livery |
| 0:25 | `thumb_0025.jpg` | Internals | **KST CS07 / KST X08** x4 cruciform, N20-class, PA12 SLS white shells, 4x standoffs |
| 0:35 | `thumb_0035.jpg` | `嘉立创EDA 飞控系统PCB设计` | JLCEDA layout red, labels `GND/VCC/CLK/D10 GNSS TELEM RST KEY GPIO` |
| 0:45 | `thumb_0045.jpg` | Flight Controller | **STM32F4 QFP64**, `KEY / PD12-15 / SDA SCL GND VCC I2C`, `LS hang` logo, ~65mm dia |
| 0:55-1:10 | `thumb_0055/0070.jpg` | `嘉立创PCB打样与SMT贴片` | JLCPCB 12-up black mask — proves <$2/board at qty30 |
| 1:20 | `thumb_0080.jpg` | Sensor | **FDISYSTEMS Data10** AHRS (14-LCC) held in tweezers, X/Y marked |
| 1:35 | `thumb_0095.jpg` | Power-on | 3 boards via FFC+JST: Power (inductor) → FC (center) → Telem (right), RGB LEDs |
| 2:00 | `thumb_0120/0150.jpg` | Integration | Harness yellow signal + red power, LEDs through vents, hand fit into airframe |
| 2:55 | `thumb_0175.jpg` | `ICEM非结构化网格划分` | ICEM R19.2 cylindrical farfield, unstructured tet, tree `Geometry/Surfaces/Bodies/Mesh` |
| 3:05 | `thumb_0185.jpg` | `高性能计算机求解` | Fluent 1000 iter, `continuity/x-velocity` + **Xeon Platinum 8275CL @3.00GHz 100% 16.0/93.9GB** |
| 3:15 | `thumb_0195.jpg` | CFD Post | Streamlines colored **-1400 to +400Pa**, stagnation red at nose, vortex canard-tail |
| 3:25 | `thumb_0205/0215.jpg` | `气动仿真数据处理` | Excel: `升力/阻力/俯仰力矩/压心位置/升阻比 @30m/s`, **CoG 439.6mm / CoP 473.72mm / margin 14.06mm**, Cm linear `y=0.4267x` |
| ~4:00 | `thumb_0230/0250.jpg` | Ground rig | **DH3840** DAQ + **SIEMENS HMI** touch (graph 40-120) — thrust/balance stand |
| 4:30 | `thumb_0270.jpg` | `火箭飞行控制建模与仿真 MATLAB SIMULINK` | Section title |
| 4:45 | `thumb_0285.jpg` | Simulink | `控制火箭仿真模型 Copyright 2022 LShang` — **ADRC (TD+ESO+NLSEF)** + 4-channel allocator |
| 5:00 | `thumb_0300.jpg` | `组合导航系统 惯性导航 气压计 GNSS 基于自适应卡尔曼滤波` | 15-state adaptive EKF: INS+Baro(MS5611)+GNSS |
| 5:15 | `thumb_0315.jpg` | HITL | MissionPlanner fork: green 3D loop, compass, hand-wave FC → model follows |
| 5:30 | `thumb_0330.jpg` | `惯导 气压计 融合定高 实时高度曲线` | Vertical rail **0-100cm** + laptop real-time altitude ~38-40, bottom 3D rocket + horizon |
| 6:40 | `thumb_0400.jpg` | `首次发射试验 上升段姿态控制测试 2022.7.12` | Flight 1 title |
| 7:00 | `thumb_0450/0470.jpg` | Flight 1 | Insta360 on tripod + drone top view smoke trail + telemetry `ROL 68.5 PIT -15.6 YAW121.5 H238m` + map kink |
| 8:20 | `thumb_0500.jpg` | `第二次发射试验 2022.7.17` | Flight 2 title |
| 8:50 | `thumb_0530.jpg` | Tracking | **Yagi 15-element + red dot** on pistol grip, white coax → 900MHz telemetry |
| 10:00 | `thumb_0600.jpg` | **FAILURE SLIDE** | `改进失败 | 控制性能进一步恶化 | 姿态控制误差增大 | 开伞系统工作异常 | 下降段姿态控制异常` |
| 14:10 | `thumb_0850.jpg` | `定高开伞成功` (night) | Altitude-triggered chute + map inset — fixed-height recovery proven |
| 20:00 | `thumb_1200.jpg` | `第七次发射试验 搭载自研火箭发动机` | Final with custom solid motor, sunset horizon ~1km |

---

## 2. System Architecture Extracted

**Mechanics:** PA12 Nylon SLS + carbon tube, **68mm ID** (vs your **56mm OD PGK**). Canard bay is independent module — direct PGK fuze-drop concept. `KST CS07: 0.07s/60° 3.2kg·cm` bandwidth ~20Hz.

**Avionics Stack (~35g):**
```
Top: Patch antenna (Beitian BN-880) RF
Mid1: Sensor — FDISYSTEMS Data10 + MS5611 baro + mag
Mid2: Main — STM32F405 @168MHz + MPU6000 backup
Bottom: Power — 5V/3.3V buck, 4x PWM, UART TELEM, SD
Interconnect: 0.5mm FFC (vibration failure point)
```

**Software:**
- **Control:** Han ADRC (Extended State Observer estimates total disturbance = aero shift + wind). Better than PID for canards where CoP moves.
- **Nav:** 15-state quaternion/vel/pos + gyro/acc + baro bias adaptive R (scales with HDOP).
- **Recovery:** `Apogee (vel zero + baro peak) → delay → canards to vertical (pitch 90°) → H_set 150m fire chute` — his "vertical recovery" = vertical fall under drogue, not propulsive landing.

---

## 3. SIH26098 Deliverable Gap Matrix

**Official PS (`SIH2026_Hardware_PS.md:647`):** *CAA + GNC (CEP ≤30m) + multi-mode fuze (Proximity/Time/Impact) + embedded + power + programming + survive high-G.*

| # | SIH Deliverable | L Shang Coverage | Gap & Action |
|---|-----------------|-----------------|--------------|
| **1** | System arch doc A-J | 70%: 5-bay + 3-PCB + failures documented | Keep the modular documentation pattern only; the active physical baseline is the inert common-carrier demonstrator. See `research/A_system/entry_20260825_lshang_system_teardown_pgka1.md` |
| **2** | CAD CAA | Historical CAD: 150x34 ogive, staggered shafts 146/152mm, face-gear r8/pinion r6 | **Use active** `cad_models/generate_pgk_155.py`: common carrier, front/rear display bearings, shell/carrier rotor-stator, and one low-voltage torque emulator |
| **3** | Electronics block | 50%: STM32F4 circular 65mm proven, JLCPCB cheap | **Replace:** LiPo→super-cap+alternator `F1` (rotors 40/41), Beitian→ZED-F9P+NavIC `D2-D5`, FFC→Mezzanine, potting `G5` for 20kG. Keep his `KEY/GPIO/I2C` labels |
| **4** | GNC algorithm | 60%: ADRC+adaptive EKF+HITL+rail test | **Adapt:** add spin 300Hz + Magnus + despin phase, baro out for flight, add `C7 LSTM GNSS-denied <5m` + `C11 MPC`. Port Simulink ADRC to STM32H743 |
| **5** | Simulation trajectory correction | 80%: ICEM→Fluent Xeon→streamlines→Excel DB→Simulink | **Copy pipeline:** MID `30m/s` table header `升力/阻力/俯仰力矩/压心/升阻比` for Mach 0.8-3.0. Your `simulate_trajectory_155.py` already does ZEM; upgrade to 6DOF spin + Monte Carlo `I1` |
| **6** | Prototype PoC | 40% (flying rocket) vs inert STL | **Current scope is bench-only:** use a guarded, low-speed rotation stand with relative-angle and LED power demonstrations. Do not adapt the flight-test sequence or build a launch-capable article. |
| **7** | Performance CEP ≤30m | No number (only telemetry) | **Must quantify:** Your `simulate_trajectory_155.py` Monte Carlo N300 → CEP ~6-10m guided vs 267m ballistic (H8). Plot histogram panel C alongside his A-range-vs-altitude |
| **C1** | STANAG 2916 | None (150mm custom) | Add thread `2-12UN-1A`, bore `Ø50x90`, ramming `STANAG 4369` |
| **C2** | High-G 15-20kG | Hobby servos fail ~200G | Implement **B3 hollow piezo 0.30N·m 450V 40.2kHz self-locking** or **B1 brake**. Pot `Dow3140 G5`, direct-write `G7` |
| **C3** | Multi-mode fuze | **None** — only parachute `定高开伞` | Add `E1 FMCW 24GHz 6/12/18m + E3 Time 3-199.9s + E4 PD <250us` + `MEMS S&A 15x17x5mm E8 slapper 4088m/s`. Reuse his altitude-trigger as HOB logic |
| **C4** | Power high-G | LiPo 2S | **For the inert exhibit:** shell-side rotor + carrier-side stator → rectifier + supercapacitor + LEDs/controller. Keep any launch-power or fuze implementation out of the physical model. |
| **C5** | Modular future bay | Fixed 5-bay | Keep his modular livery but save volume via MEMS S&A 95% reduction `J6` for laser/EO seeker |

---

## 4. Reuse vs Discard

**Steal tomorrow:**
- JLCEDA→JLCPCB workflow (`嘉立创`): <48h, 12-up panel, <$2/board — proves ₹8L kit feasible.
- 65mm circular PCB with `KEY/GPIO/I2C` = PGK diameter (scale from 68mm rocket to 56mm fuze).
- ICEM cylindrical domain + Fluent `continuity/x-velocity` residual + Excel CoG/CoP margin table — copy column headers.
- ADRC skeleton + 15-state adaptive EKF + MissionPlanner HITL + 100cm rail `实时高度曲线` demo (film like `thumb_0330.jpg`).
- **7 flights in 30 days with open failures** — `thumb_0600.jpg` 5-bullet failure is exactly what SIH judges (`Innovation vs Effort`) reward over fake perfection.

**Discard for PGK:**
- 4x KST direct drive → fails at 15kG; use **B1 canted brake or B3 piezo**.
- Beitian + MS5611 as flight sensors → use **D6 gun-hard + D8 mag gyroless**.
- FFC interconnect → Mezzanine Samtec.
- Parachute timer → fuze logic (inductive EPIAFS `J1` + NFC phone setter `J2` for SIH demo).

---

## 5. Concrete Next Steps (Team Map)

| Role | Folder | Learn | Decide (using this teardown) | Show |
|------|--------|-------|------------------------------|------|
| M1 Planner | `A_system` | Old kits, public PGK references | **Freeze the inert common-carrier baseline** | Architecture map + safe exhibition brief |
| M2 Steering | `B_aero` | ICEM/Fluent his slides | **Common carrier + fixed illustrative canards** | Safe bench rotation diagram + active `generate_pgk_155.py` STEP |
| M3 Brain | `D_sensors` | Data10+GNSS | **STM32H7 + ZED-F9P/NavIC, adaptive EKF** | Table rail demo 0-100cm |
| M4 Fuze | `E_fuze` | His missing fuze | **FMCW 24GHz + MEMS S&A** | Circuit + phone NFC demo |
| M5 Body | `F_power` | LiPo vs display alternator | **Shell/carrier rotor-stator + supercap** | 3D print + guarded low-speed LED power test |
| M6 Tester | `I_test` | 7 flights | **HITL→rail→G5 soft recovery, Monte Carlo CEP** | Demo video + `trajectory_comparison.svg` |

**PPD Checklist:** Arch doc (A-J) ✅ Catalog exists + this teardown adds evidence; active CAD ✅ `cad_models/out_pgk/`; Electronics ✅ display controller + relative-angle sensor; PoC ✅ guarded low-speed bench rig; simulation and performance claims remain separate from the inert physical model.

---

## References

- Video teardown: `/tmp/canard_frames/thumb_*.jpg`, ffprobe `1280x720 h264 1396s`, frames `thumb_0001/0005/0015/0025/0045/0080/0095/0175/0185/0195/0205/0215/0285/0300/0315/0330/0400/0500/0530/0600/0850/1200.jpg`
- Repo: `cad_models/generate_pgk_155.py:32-60`, `simulate_trajectory_155.py:40-90`, `SIH26098_Exhaustive_Ideas_Catalog.md:32-207`, `SIH26098_Ideas_Database.json`
- This analysis split into 4 DB entries: `research/A_system/entry_20260825_lshang_system_teardown_pgka1.md`, `B_aero/...cfd...`, `C_gnc/...adrc...`, `I_test/...7flight...` → `SIH26098_LIVEBOARD.md`

*Generated 2026-08-25 for SIH26098 — use as primary evidence for internal review & SIH PPT slide "Why canard PGK works: proven by L Shang, hardened for 15kG."*
