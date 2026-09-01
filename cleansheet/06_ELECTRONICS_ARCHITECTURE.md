# 06 — Electronics Architecture (dual-domain, verified pin maps, C header contract)

**SIH26098 clean-sheet PGK · Rev 1.0 (2026-08-31)**
Companion to `03_DESIGN_REPORT.md` (§4.3/§4.5/§5), `05_SENSOR_SELECTION.md`, `04_GNC_METHODOLOGY.md`
§7 and `flight_sw/FLIGHT_SOFTWARE.md` (§3 module→ISR map). Evidence: `research/06_electronics-embedded-power/entry_20260831_*.md`
(8 sourced entries, one per source, URLs + access dates). The C-side of this document is
`flight_sw/board/board_config.h` — rates there are assert-equal to `flight_sw/fsw/config.py`
by `flight_sw/tests/test_board_config.py` (the board-config parity contract).

---

## 1. Domains — the dual-frame control split (design-report decision 23)

**Decision (user-set, do not revisit):** the electronics are split into **two control domains
across the two rotating frames**, and the 40 A braking current never crosses a frame:

| | **Shell frame — A6 power board (drive domain)** | **Rotor frame — D3 GNC board (GNC domain)** |
|---|---|---|
| MCU | **STM32G431CBT6** (LQFP48, 128 KB/32 KB, −40…+85 °C) | **STM32G474RET6** (LQFP64, 512 KB/128 KB, −40…+85 °C) |
| Owns | 3.7 V → 5 V/55 A boost (exists), **3-phase bridge + gate driver**, **FOC current loop 15 kHz**, MA732 commutation, Hall interface (A9), **A7b brake-chopper tie-in**, slip-ring link | **The whole GNC FSW** (`flight_sw/`): scheduler 400/100/40/1 Hz, NavEKF + RollEKF + DragAnchor + SlowFit, IPP + guidance laws, mode ladder, all dome sensors |
| Sensors | MA732 (collar-face, SPI), 3× Hall (A9), 3× shunt+INA240A2 (current), Vbus/NTC | ICM-45686 (SPI1), NEO-F10N (USART1+DMA), K-LD7 (USART2), ADXL1004 (ADC+EXTI), W25Q128 flash (SPI3) |
| Bus voltage | 5 V boost rail (motor) + 3.3 V LDO (logic) | 3.3 V buck + 3.3 V RF LDO (via slip ring, ≤ 0.5 W) |

**Rationale.** FOC commutation at the 3 kHz electrical frequency (250 rev/s × 12 pole pairs)
needs the commutation angle **local to the drive MCU** — a 3 kHz angle stream over a slip-ring
UART is latency-fragile, and the 40 A phase current belongs with its shunts. The GNC FSW, in
contrast, consumes the drag-referenced roll **estimate** (report §4.5 — the ctrl task nulls
`wrap_pi(pattern_azimuth(t) − psi_hat)` from its own sensors + commanded schedule), so it does
not need the angle sensor at all — it needs angle/spin-rate **telemetry** for de-spin progress
and the S&A spin signature only. Keeping the EKF/IPP computation and the drive stage on
separate dies also isolates the 15 kHz PWM EMI domain from the GNSS/IMU domain (§6).

**MA732 relocation (consequence, BOM D3b):** the sensor IC moves from the dome board to the
**collar-face (shell frame)** — the physical mount is unchanged (Ø6 diametral magnet on the
bell ID, potted collar-face carrier), but the IC is now wired to the **G431 SPI1** and fed
from the drive 3.3 V rail. The G474 receives the 14-bit angle + spin rate as 400 Hz telemetry
(§5). The dome board's SPI2 is freed (pads spare; flash lives on SPI3). Cost unchanged
(₹600/₹350 @1k) — BOM Rev 1.4 §I documents the relocation.

**Cross-frame link = the existing 3-contact slip ring C3** (Ø12 axial, Au alloy, BOM C3):
`+5 V | GND | UART` — see §5. Power crossing stays ≤ 0.5 W (§2); signal crossing is one
115.2 kBd half-duplex line with CRC and a 100 ms loss→safe-state rule (F6).

## 2. Power tree + per-rail budget

```
Li-ion 26500 3.7 V (A3.1, shell frame)
├─(exists)→ Boost 3.7→5 V / 55 A out (A6) ─┬─ 3-phase bridge VM (DRV8329, §4)   [shell]
│                                          ├─ Drive logic LDO 5→3.3 V (G431, INA240, MA732, DRV8329 logic)  [shell]
│                                          ├─ K-LD7 radar (5 V class, dome, via slip ring)                    [crosses]
│                                          └─ Slip ring C3 contact 1 (+5 V) ─→ dome 5 V entry                  [crosses]
│                                                                 ├─ TPS62933 buck 5→3.3 V (dome digital)
│                                                                 │    └─ G474 / ICM-45686 / W25Q128 / comparators
│                                                                 ├─ TLV757P LDO 3.3→3.0 V (dome RF/analog)
│                                                                 │    └─ NEO-F10N / ADXL1004 / TLV7031 ref
│                                                                 └─ (NEO-F10N V_BCKP ← 3.3 V via Schottky + 10 µF)
└─(direct)→ motor power path (stator/windings — no slip ring, report §5)
```

**Dome rail budget (the slip-ring load — gate: ≤ 0.25 W logic rail, ≥ 2× margin vs 1.5 W):**

| Rail | Load | Worst W |
|---|---|---|
| 3.3 V digital | G474 run 170 MHz (≈29.5 mA typ, 35 mA max @3.3 V — DS12288 Table 21) | 0.116 |
| 3.3 V digital | ICM-45686 (accel+gyro low-noise) | 0.005 |
| 3.3 V digital | W25Q128 active read | 0.010 |
| 3.3 V RF/analog | NEO-F10N acquisition (33 mA @3.0 V) | 0.099 |
| 3.3 V RF/analog | ADXL1004 + TLV7031 + TLV757P overhead | 0.015 |
| **3.3 V logic+analog total** | | **≈ 0.25 W ✓ (gate ≤ 0.25 W)** |
| 5 V rail (dome side) | K-LD7 (typ 0.15 W) | 0.20 |
| | TLV757P dropout dissipation ((3.3−3.0) × 0.13 A) | 0.04 |
| **Slip-ring total** | | **≈ 0.49 W worst vs 1.5 W allocation → 3.1× (≥ 2× gate) ✓** |

**Drive side (shell battery — no slip-ring constraint):** drive logic LDO ≈ 0.09 W
(G431 ≈ 26 mA @170 MHz + INA240×3 + MA732 + DRV8329 logic) — carried by the battery,
inside the existing ≥18× energy margin. **Energy-ledger delta vs report §5: dome
electronics ≈ 0.49 W × 90 s ≈ 0.012 Wh — inside the 0.025 Wh "electronics" line already
in the 0.9 Wh worst-case ledger → no change.** Slip-ring contact loss at 0.5 A over mΩ-class
rings: < 1 mW — negligible (design rule D6-2).

**Dome power sequencing (slip-ring hot-plug):** 5 V entry → ferrite + **470 µF bulk** +
SMAJ5.0A → TPS62933 (soft-start) → 3.3 V digital; TLV757P LDO → 3.0 V RF. Ride-through on
contact bounce ≥ 5 ms at the 0.5 W dome load; pre-boot (t < 2 s, setback window) brown-out
resets are benign — the electronics boot at muzzle exit (report §2.3) and contacts are
mechanically engaged before power-on. NEO-F10N V_BCKP rides a 10 ms dip (10 µF).

## 3. GNC board (D3, Ø62 4-layer) — STM32G474RET6, verified pin map

### 3.1 Block diagram

```
                     ┌───────────────────────────────────────────────────────────┐
 NEO-F10N ──USART1──▶│  STM32G474RET6   ┌── ICM-45686 (SPI1, 200 Hz, DRDY→EXTI4) │
 (1 Hz PVT, RX DMA)  │  170 MHz M4F     ├── W25Q128 flash (SPI3, 25 MHz)         │
 PPS ──TIM2_CH1──▶   │                  ├── K-LD7 (USART2, target list)          │
 K-LD7 ──USART2──▶   │  GNC FSW:        ├── ADXL1004 (ADC1_IN1) + TLV7031→EXTI1  │
 ADXL1004 ──ADC──▶   │  400/100/40/1 Hz ├── slip-link (USART3 HD, PB10)          │
 slip ──USART3──▶    │  NavEKF/RollEKF  ├── SWD (PA13/14), NRST, 24 MHz HSE      │
                     │  IPP/laws/ladder └────────────────────────────────────────┘
                     └───────┬───────────────────────────────────────────────────┘
                          USART3 half-duplex, 115200 8N1  (slip ring, 3.3 V logic,
                          USBLC6-2 + 100 Ω each end) — §5 protocol
```

### 3.2 Complete G474 pin map (every used pin, AF verified vs DS12288 Rev 6 Table 13 — see §3.5)

| Pin (LQFP64 #) | Signal | Function | AF / mode | Bus / rate | Verified |
|---|---|---|---|---|---|
| PA5 (19) | IMU_SCK | SPI1 SCK | AF5 | SPI1 10 MHz, 200 Hz×(burst) | ✓ T13 |
| PA6 (20) | IMU_MISO | SPI1 MISO | AF5 | ↑ | ✓ T13 |
| PA7 (21) | IMU_MOSI | SPI1 MOSI | AF5 | ↑ | ✓ T13 |
| PA4 (18) | IMU_CS | SPI1 NSS (software CS) | GPIO out | ↑ | ✓ T13 (SPI1_NSS) |
| PC4 (22) | IMU_DRDY | ICM-45686 data-ready | GPIO in → **EXTI4** | 200 Hz ISR | ✓ T13 (EXTI line 4) |
| PB3 (56) | FL_SCK | SPI3 SCK | AF6 | SPI3 25 MHz | ✓ T13 (SPI3_SCK; JTAG JTDO freed, SWD-only boot) |
| PB4 (57) | FL_MISO | SPI3 MISO | AF6 | ↑ | ✓ T13 (SPI3_MISO; JTRST freed; **UCPD1_DBDIS=1**) |
| PB5 (58) | FL_MOSI | SPI3 MOSI | AF6 | ↑ | ✓ T13 |
| PB6 (59) | FL_CS | flash chip-select | GPIO out | ↑ | ✓ T13 (GPIO; **UCPD1_DBDIS=1**) |
| PA9 (43) | GNSS_TX | USART1 TX → NEO-F10N | AF7 | 115200 8N1 (config 38400–921600) | ✓ T13 |
| PA10 (44) | GNSS_RX | USART1 RX ← NEO-F10N (**RX DMA via DMAMUX**) | AF7 | 1 Hz PVT + UBX stream | ✓ T13 |
| PA15 (51) | GNSS_PPS | TIM2_CH1 input capture | **AF1** | 1 Hz PPS | ✓ T13 (TIM2_CH1; JTDI pull-up released at init) |
| PA2 (14) | PROX_TX | USART2 TX → K-LD7 | AF7 | 115200 | ✓ T13 |
| PA3 (17) | PROX_RX | USART2 RX ← K-LD7 | AF7 | ≥ 10 Hz target list | ✓ T13 |
| PB10 (30) | SLIP_UART | USART3 **half-duplex single-wire** (TX+RX same pad) | AF7 | 115200 8N1, RX DMA | ✓ T13 (USART3_TX; HD mode) |
| PB11 (33) | — | spare (USART3_RX pad option; slip link test point) | GPIO | — | ✓ T13 |
| PA0 (12) | SETB_AN | ADXL1004 analog signature | **Analog** (ADC1_IN1) | 40 Hz sampling + event burst | ✓ T12 (ADC1_IN1) |
| PB1 (25) | SETB_TRIG | TLV7031 threshold-comparator out | GPIO in → **EXTI1** | event (setback detect) | ✓ T13 (EXTI line 1) |
| PB15 (37) | LNA_EN | GNSS external-LNA enable (provision) | GPIO out | static | ✓ T13 (GPIO) |
| PA13 (49) | SWDIO | debug | AF (SWD) | — | ✓ T13 |
| PA14 (50) | SWCLK | debug | AF (SWD) | — | ✓ T13 |
| PF0 (5) | OSC_IN | 24 MHz HSE crystal ±20 ppm | OSC | — | ✓ T12 (OSC_IN) |
| PF1 (6) | OSC_OUT | 24 MHz HSE crystal | OSC | PLL → 170 MHz (÷6×85÷2) | ✓ T12 (OSC_OUT) |
| VDD/VSS ×4, VDDA/VSSA, VREF+ (28), VBAT (1) | power | 3.3 V rails per DS12288 Fig. 16 decoupling | — | — | ✓ |
| PC13 (2), PB0/2/12/13/14, PA8/11/12, PC5… | spare | routed to DNP pads | — | — | ✓ T13 |

**Boot/reset/WDG:** BOOT0 = PB8 pad via **nBOOT0 option bit** (`nBOOT_SEL=1` → boot from
flash, PB8 free for growth); NRST 100 nF; BOR-2; **IWDG ≈ 1 s** kicked by the GNC task
deadline monitor (FLIGHT_SOFTWARE.md §6 checklist). WWDG available as spare.

### 3.3 ISR / NVIC map (every FSW task rate → named peripheral + ISR; vs FLIGHT_SOFTWARE.md §3)

| Rate | FSW module | Trigger | ISR / NVIC priority (0 = highest) |
|---|---|---|---|
| 200 Hz | `sensors` raw IMU read (decimated to 40 Hz) | PC4 DRDY → **EXTI4** | EXTI4, prio 2 |
| 100 Hz | `nav.NavEKF.predict` | SysTick 2 kHz slot (deployment EKF_DT=0.01) | SysTick, prio 4 |
| 40 Hz | `sensors`/roll predict + SlowFit twin | SysTick slot | SysTick, prio 4 |
| 400 Hz | `ctrl` pattern refresh + slip telemetry bookkeeping | SysTick slot | SysTick, prio 4 |
| 1 Hz | GNSS delivery (`nav.deliver_fix`), `guide` IPP + laws | USART1 **RX DMA TC** → fix queue (SPSC, depth 1) | DMA1_Channel*, prio 3 |
| 1 Hz | PPS time-tag | **TIM2 capture/compare** | TIM2, prio 5 |
| ≥10 Hz | K-LD7 target list | USART2 RX (IRQ, low volume) | USART2, prio 6 |
| event | setback signature | **EXTI1** (PB1) + ADC burst | EXTI1, prio 1 |
| event | slip-link frame | USART3 RX DMA TC + IDLE | DMA1_Channel*, prio 2 |

Priorities: EXTI1 (setback/safety) > IMU DRDY > GNSS DMA > SysTick > TIM2 > USART2 —
the guidance/IPP path runs in the 1 Hz SysTick slot; the < 0.5 ms worst-tick budget
(methodology §7) is not starved by any ISR (all ISRs < 20 µs except none). **Timer
conflicts: none — dome uses SysTick + TIM2 only (HRTIM unused, reserved to the drive
concern; TIM3/4/5/6/7/15/16/17 spare).** DMA: DMAMUX is fully routable — USART1 RX,
USART3 RX on distinct DMA1 channels (no fixed-channel conflicts). EXTI lines used: 1, 4
(no conflicts).

### 3.4 Bus timing + connectors

| Bus | Config | Rate | Margin |
|---|---|---|---|
| SPI1 (IMU) | master, CPOL=1 CPHA=1, 4-wire + DRDY | 10 MHz (ICM-45686 ≤ 24 MHz) | 2.4× clock margin |
| SPI3 (flash) | master, mode 0 | 25 MHz (W25Q128 ≤ 133 MHz) | 5× |
| USART1 (GNSS) | 115200 8N1, RX DMA ring | 1 Hz PVT + UBX | — |
| USART2 (prox) | 115200 8N1 | target list ≥ 10 Hz | — |
| USART3 (slip) | HD single-wire 115200 8N1, RX DMA + IDLE detect | §5 | 58 % idle wire margin |
| ADC1 | 12-bit, PA0, 47.5-cycle sample | 40 Hz + burst 4 kHz on EXTI1 | ≫ need |
| SWD | PA13/PA14 + NRST header (2×5 1.27 mm) | — | — |

**Connectors:** J1 dome↔slip-ring pigtail (3-wire: +5 V/GND/UART); J2 GNSS module
8-pin; J3 IMU 6-pin; J4 K-LD7 4-pin (UART+5 V); J5 ADXL1004 3-pin (analog/3.0 V/gnd);
J6 SWD 2×5; J7 spare I²C/UART breakout (PB0/2/12/13/14 + 3V3/GND). Board outline Ø62,
4-layer FR4-TG170, 2 oz outer — consistent with BOM D3.

### 3.5 Pin-map verification pass (documented check — plan step 5)

Every used pin above was checked line-by-line against **DS12288 Rev 6 Table 13
(Alternate function, pp. 73–79)** and Table 12 (pin definition, ADC channels), fetched
2026-08-31: PA5/6/7 = SPI1 SCK/MISO/MOSI (AF5); PB3/4/5 = SPI3 SCK/MISO/MOSI (AF6);
PA9/10 = USART1 TX/RX (AF7); PA2/3 = USART2 TX/RX (AF7); PB10/11 = USART3 TX/RX (AF7);
PA15 = TIM2_CH1 (AF1); PA0 = ADC1_IN1 (Table 12); PC4/PB1 free GPIOs on EXTI lines 4/1.
Checks passed: **(1) no pin carries two assignments; (2) EXTI lines 1/4 unique;
(3) DMA fully routable (DMAMUX) — USART1 RX and USART3 RX on separate channels;
(4) dome timers = SysTick + TIM2 only — no timer conflicts, HRTIM untouched;
(5) JTAG pins PB3/PB4 + PA15 default to JTAG AF at reset → SWD-only boot frees them
(DS12288 Table 12 note 5), reconfigured at init; (6) UCPD dead-battery pull-downs on
PB4/PB6 disabled via `PWR_CR3.UCPD1_DBDIS=1` at init (note 6).** The same table was
used for the KiCad schematic symbols (§ KiCad, electronics/gnc_board).

## 4. Drive domain (A6 power board, shell frame) — block level

```
 Li-ion 3.7 V ─▶ Boost 3.7→5 V/55 A (A6, exists) ─▶ VM bus (TVS + bulk)
                    │
        ┌───────────┴──────────────┐
        ▼                          ▼
  STM32G431CBT6 ──TIM1 6×PWM──▶ DRV8329AREER (3× half-bridge gate driver,
  (FOC 15 kHz ISR)   AF6        bootstrap + trickle charge pump, HW-config)
        │  ▲                        │ gates
        │  └── SPI1 ◀── MA732       ▼
        │      (collar-face,   6× NVMFS5C460NL (2∥ per switch, 40 V/4.5 mΩ)
        │       14-bit angle)       │ U/V/W ──▶ stator windings (A4/A5)
        ├── ADC1 @15 kHz ◀── 3× INA240A2 ◀── 3× 2 mΩ in-line shunts
        ├── ADC2: PA5 NTC, PA3 Vbus divider
        ├── TIM4 CH1-3 ◀── Hall ×3 (A9, startup/redundant commutation)
        ├── TIM16_CH1 (PA6) ──▶ A7b brake-chopper FET + 15 Ω/50 W dump
        ├── PA7 ◀── nFAULT (DRV8329) → EXTI7 → safe state
        └── PA2 USART2 HD ◀──▶ slip ring (commands down / telemetry up, §5)
```

**Bridge sizing:** de-spin demand 0.095 N·m @ ≤ 40 A for 15 s (report §4.3). Phase
current amplitude 40 A → I_rms ≈ 28.3 A/phase; conduction ≈ 3 × I_rms² × R_switch
≈ 3 × 800 × 2.25 mΩ ≈ **5.4 W over 15 s ≈ 81 J** across 6 devices (≈ 13.5 J each) —
adiabatic on 2 oz 4-layer copper with the collar as heat spreader; **QA thermal survey
added to the A6 line** (same class as the A7b 720 J winding survey). Switching loss at
15 kHz with smart-gate drive is ≪ conduction at this bus voltage (5 V); verified by the
survey, not assumed. The braking **energy** goes to the A7b dump resistor (report §5 Rev 1.2)
— the FETs see current, not energy.

**G431 allocation (LQFP48, every pin verified vs DS12589 Rev 6 Tables 12/13):**
PA8/PA9/PA10 = TIM1_CH1/2/3 (AF6); PB13/14/15 = TIM1_CH1N/2N/3N (AF6), ~200 ns dead time;
PB3/PB4/PB5 = SPI1 SCK/MISO/MOSI to MA732 (AF5, 15 kHz read at 25 MHz-class bus — angle
local to the commutation loop); PA4 = MA732 CS (GPIO); PA0/PA1/PB0 = ADC1_IN1/IN2/IN15
(three INA240A2 phase currents, 15 kHz scan triggered by TIM1 update); PB1 = ADC1_IN12
(Vbus divider); PA5 = ADC2_IN13 (winding NTC); PA3 = Vbus alt / spare (ADC2_IN4);
PA6 = TIM16_CH1 (AF1) → A7b chopper PWM 20 kHz, event-gated by the mode ladder;
PB6/PB7/PB8 = TIM4_CH1/2/3 (AF2) Hall capture (PB8 = BOOT0 dual-role — **nBOOT_SEL option
bit set, PB8 free**); PA2 = USART2 half-duplex single-wire (slip link, AF7, RX DMA);
PA7 = nFAULT → EXTI7; PB12 = DRV8329 EN_GATE; PA13/PA14 SWD; PF0/PF1 = 24 MHz HSE.
**IWDG 200 ms** kicked by FOC-loop health + link watchdog. Verification checks identical
to §3.5 (EXTI 7 unique; DMAMUX routable; timers TIM1/TIM4/TIM16 unique; JTAG pins freed
by SWD-only boot; UCPD1_DBDIS=1 for PB4/PB6).

**A7b tie-in:** the chopper is part of the drive domain — the dump path is armed whenever
the bridge is (safe state included), because regen transients are a drive-side event; the
G474 only commands the de-spin torque profile (§5).

## 5. Slip-ring protocol (C3: `+5 V | GND | UART`)

**Physical:** single-wire 3.3 V logic, half-duplex, **115200 8N1 fixed** (user-set).
Series 100 Ω + USBLC6-2SC6 at both ends; Au-alloy ring current ≤ 0.5 A (power) — the
UART is a signal contact, mΩ-class.

**Frame (12 bytes, fixed, both directions):**

| Off | Field | Size | Notes |
|---|---|---|---|
| 0–1 | SYNC | 2 | 0xA5 0xC3 |
| 2 | TYPE | 1 | 0x01 = command (dome→drive), 0x02 = telemetry (drive→dome) |
| 3 | SEQ | 1 | rolling counter (loss + duplication detection) |
| 4–9 | PAYLOAD | 6 | see below |
| 10–11 | CRC-16 | 2 | **CRC-16/CCITT-FALSE** (poly 0x1021, init 0xFFFF, no reflect) |

- **Telemetry 400 Hz** (drive→dome): `angle` = MA732 raw 14 bits + 2 status bits (u16);
  `spin_rate` = i16 rad/s ×256; `status` = u8 bitmask (mode, fault, Hall-valid, chopper-armed).
  12 B = 104 bits ≈ 0.90 ms → **41 % wire duty**.
- **Commands 50 Hz** (dome→drive): `mode` u8 (0 OFF, 1 COAST, 2 DE-SPIN torque, 3 ROLL-HOLD,
  4 BRAKE-PROFILE, 5 SAFE), `setpoint` i16 (torque ×256 or servo rate ×256), `sub` u8
  (chopper enable / profile index), `spare` u8. 50 Hz → 5 % duty. The G431 streams
  telemetry on its own 400 Hz grid; the G474 injects command frames only in the post-frame
  guard gap (≥ 0.35 ms) — no collisions by construction; total wire load ≈ 47 %.
- **Loss → safe state (F6 ladder consistency):**
  - Drive side: no valid (CRC-passing) command for **100 ms** (5 missed at 50 Hz) → mode
    5 locally: torque zero (neutral coast), chopper armed, bridge gates forced to safe
    combination. 40 A braking never crosses frames; on link loss the drive degrades to
    coast/ballistic — exactly the F6 neutral-coast behavior.
  - Dome side: no valid telemetry for **100 ms** → de-spin progress unknown: hold last
    setpoint 200 ms, then command SAFE; if de-spin completion cannot be confirmed by
    T_DESPIN_END (40 s), the spin-signature S&A gate fails **safe** (fuze stays safe) and
    the mode ladder logs a degraded entry.
  - GNC ladder hooks: link loss never triggers `denied` guidance demotion by itself
    (the ladder is GNSS/σ-driven per methodology §5); it gates the S&A chain and the
    de-spin timeline, which is the conservative direction.

## 6. QA / design rules

1. **Shock potting:** both boards potted (Aralite CT200/HT9517 class, BOM A10) — the
   ADXL1004 soft-mount attenuation (05 §4.4(4)) is part of the potting fixture QA; MA732
   collar-face pot uses the magnet-alignment fixture (BOM D3b QA). Connector pigtails
   strain-relieved.
2. **EMI motor ↔ GNSS coexistence:** the 15 kHz PWM domain is now physically on the
   shell side with its own return; the dome carries no switching load above the 2.2 MHz
   buck (spread-spectrum enabled). Radome-side antennas (NEO-F10N patch, K-LD7) get: 3.0 V
   LDO rail, buck + ferrite isolation, and the GNSS LNA_EN provision. Slip-ring UART is
   slew-limited (100 Ω series) and CRC-checked — the residual failure mode is frame loss
   (handled by §5), not corruption-in-silence.
3. **Derating:** capacitors ≥ 2× working voltage (5 V rail → 16 V-class ceramics); TVS
   clamps sized so buck input stays inside 3.8–30 V (TPS62933) through SMAJ conduction;
   FET Vds 40 V class vs 5 V bus + clamped transients (§4); MCU ambient −40…+85 °C vs
   env −40…+60 °C; INA240 common-mode −4…80 V vs 0–5 V in-line nodes.
4. **Slip-ring budget:** power ≤ 0.5 A (§2), UART duty ≤ 50 % (§5) — both inside the
   Ø12 3-ring micro-slip class with ≥ 2× margin; contact-resistance drift over 250 rev/s
   is absorbed by the 470 µF ride-through + 100 ms safe-state windows.
5. **FET Rds table check at schematic capture:** verify the NVMFS5C460NL Rds(on) at the
   DRV8329 actual gate-drive voltage (4.5 V-class) and re-run the §4 conduction estimate
   with that number before the thermal survey.
6. **ADXL1004 supply edge:** the TLV757P rail is 3.0 V; confirm ADXL1004 VDD min at
   schematic capture (flagged in the rails research entry) — fallback: move the signature
   chain to the 3.3 V digital rail.

## 7. BOM deltas (Rev 1.4 §I carries the table) + bench bring-up appendix

**New rows — A6 (drive domain, shell frame):** G431 MCU, DRV8329AREER gate driver,
6× NVMFS5C460NL bridge set, 3× INA240A2D + 3× WSL2512 2 mΩ shunts, USBLC6-2 + SMAJ5.0A,
drive-logic LDO. **D3 adds:** TPS62933, TLV75730P, W25Q128JVSIQ, TLV7031 comparator,
USBLC6-2 + SMAJ5.0A, passives. **D3b relocates** dome → collar (drive side; cost
unchanged). Cost/mass deltas: **§I of BOM Rev 1.4** (proto ≈ +₹3.3k, @1k ≈ +₹2.4k;
≈ +16 g — drive rows ≈ 12 g on the shell-frame power group, dome rails/protection
≈ 4 g; module ≈ 1.88 kg vs 2.0 kg limit).

**KiCad skeleton (delivered this rev):** `electronics/gnc_board.kicad_pro` + 4 sheets
(power / MCU+buses / sensors / comms+slip) — generated by `electronics/gen_gnc_schematic.py`
(deterministic; rerun == identical output). **ERC 0 violations** (`kicad-cli sch erc`,
KiCad 10.0.6); netlist `electronics/gnc_board.net` (34 components / 170 nodes). Stock
symbols used where the library has them; **5 custom minimal symbols** (ICM-45686,
NEO-F10N, K-LD7, ADXL1004, TLV7031) shipped in `electronics/pgk.kicad_sym` + project
`sym-lib-table` — pin numbering indicative until footprint-level capture (flagged).

**Bench bring-up appendix (devkit wiring → the same `board_config.h` contract):**

| Stage | Hardware | What proves out |
|---|---|---|
| B1 | Nucleo-G474RE + ICM-45686 breakout + NEO-F10N breakout (SparkFun) | SPI1 DRDY 200 Hz, USART1 DMA queue, PPS→TIM2 capture; `board_config.h` pin defines compile against the same map |
| B2 | B1 + W25Q128 breakout + K-LD7-EVAL | SPI3 logging, USART2 target list, ADXL1004 + TLV7031 on a breadboard shaker |
| B3 | B2 + Nucleo-G431RB + DRV8329 eval path + 6-FET half-board + MA732 TBMA732 eval | FOC 15 kHz on TIM1, MA732 commutation, 2-wire slip-link emulated over a twisted pair (§5 frames + CRC + safe-state by pulling the link) |
| B4 | B3 + real slip ring on the bench de-spin rig (report §10.2) | contact-bounce behavior, ride-through, 100 ms loss → safe state end-to-end |

All bring-up uses the same `flight_sw/board/board_config.h` constants — the C port
consumes the contract verbatim (README in `flight_sw/board/`).

## 8. Out of scope (next rungs)

PCB layout/routing + stackup (both boards); A6 full schematic (drive domain is block-level
here); motor FOC firmware + drive-side code (the header contract defines the interface
only); procurement/devkit purchases; per-sensor margin sweeps; 6DOF truth; STEP↔FreeCAD
mechanical fit loop of the populated board.

---

*Evidence chain: `research/06_electronics-embedded-power/entry_20260831_*.md` (8 sourced
entries) → this doc (§1–§7, pin maps verified vs DS12288/DS12589 Tables 12/13, access
2026-08-31) → `flight_sw/board/board_config.h` (+ `tests/test_board_config.py` parity)
→ `electronics/gnc_board.kicad_pro` (ERC + netlist) → BOM Rev 1.4 §I, report Rev 1.7,
HANDOFF.md. Selection is analysis-level; no changes to `scripts/sim_gnc_check.py`,
`flight_sw/fsw/*`, `flight_sw/tests/golden/*`, or `05_SENSOR_SELECTION.md` selections.*
