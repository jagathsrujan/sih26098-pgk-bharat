# 05 — Sensor Selection (COTS NavIC-first suite, error-budget validated by co-sim)

**SIH26098 clean-sheet PGK · Rev 1.0 (2026-08-31)**
Companion to `03_DESIGN_REPORT.md` (§4.5/§4.6), `02_BOM_MANUFACTURING_ASSEMBLY.md` (Rev 1.3 §H
deltas) and `flight_sw/fsw/config.py` (the GNC sensor constants). Evidence:
`research/D_sensors/entry_20260831_*.md` (six sourced entries, one per source) and
`out_sim/RESULTS_SENSORS.md` (machine-generated co-sim validation).

**Method:** for each of the five GNC sensors — GNSS receiver, IMU, collar↔bell angle sensor,
setback sensor, proximity head — COTS candidates were surveyed from datasheets (sources with
access dates recorded in the research entries), one part selected per family, and every GNC
sensor constant in `flight_sw/fsw/config.py` flowed down to a cited datasheet parameter with
stated margin. The selected sigmas were then pushed through the existing paired-MC co-sim
(`cosim/run_sensors.py`, runtime profiles — neither `scripts/sim_gnc_check.py` nor
`fsw/config.py` was edited) to prove the terminal-accuracy gate still closes.

**Selections (one line each):**
u-blox **NEO-F10N** (NavIC L5 + GPS/GAL/BDS dual-band) · TDK **ICM-45686** (4,000 °/s gyro,
20,000 g shock) · MPS MagAlpha **MA732** (14-bit, 60,000 rpm) · **mechanical setback armer
(interface) + ADXL1004 electronic signature** · RFbeam **K-LD7** 24 GHz digital radar.

---

## 1. Requirements flow-down (per sensor)

### 1.1 GNSS receiver (BOM D4)

| Requirement | Value | Source |
|---|---|---|
| Constellations | NavIC primary (REQ F2 sovereign stance) + GPS fallback, concurrent | `00_REQUIREMENTS.md` F2 |
| Position σ | ≤ 5 m | `fsw/config.py` GPS_POS_SIG (EKF R) |
| Velocity σ | ≤ 0.3 m/s | `fsw/config.py` GPS_VEL_SIG (EKF R + drag-ref anchor reference) |
| Fix latency | ≤ 100 ms, time-tagged | `fsw/config.py` GNSS_LAT |
| Fix rate | 1 Hz (PVT) | `fsw/config.py` GNSS_HZ |
| First fix after enable at t=45 s | ≤ 5 s (BOM D4 cold-start spec) | BOM §D4 / report §2.3 |
| Altitude / velocity / dynamics | apogee 9.9–12 km, muzzle 827 m/s, lateral ≤ 0.14 g | report §3 / methodology §1 |
| Environment | −40…+60 °C; setback 15,000 g powered-off; antenna Ø25 patch zenith | L1/L5, report §4.5 |
| Interface | UART (DMA) at 3.3 V, NMEA/UBX | FLIGHT_SOFTWARE.md §3 |

### 1.2 IMU (BOM D3)

| Requirement | Value | Source |
|---|---|---|
| Gyro full-scale | ≥ 4,000 °/s (design clip level) | `fsw/config.py` GYRO_SAT_RPS |
| Gyro bias | ≤ 0.5 °/s 1σ at nav start | `fsw/config.py` GYRO_BIAS_INIT_SIG |
| Gyro per-sample noise | 0.2 °/s incl. vibration (roll EKF Q) | harness constant (run_cosim) |
| Accel noise | ≤ 0.08 m/s² per 200 Hz sample incl. vib | `fsw/config.py` ACC_NOISE_SIG |
| Accel bias | ≤ 0.25 m/s² 1σ | `fsw/config.py` ACC_BIAS_INIT_SIG |
| Sample rate | 200 Hz raw (SPI ≥ 10 MHz) | `fsw/config.py` IMU_DT |
| Shock | 15,000 g axial, powered off (electronics boot at muzzle exit) | L1 |
| Temp | −40…+60 °C | L5 |
| Pre-despin gyro saturation 22× | accepted by design (drag-ref anchoring owns roll) | report §4.5, decision 12 |

### 1.3 Collar↔bell angle sensor (new BOM line D3b — no line item existed)

| Requirement | Value | Source |
|---|---|---|
| Type | absolute magnetic rotary, strap-on (no bearings of its own) | report §4.3 |
| Resolution | ≥ 12-bit (0.088° quantization) | `fsw/config.py` ANGLE_BITS |
| Max relative rate | 15,000 rpm (250 rev/s braking transient ×) | report §4.3 (250 rev/s de-spin) |
| Electrical frequency | 3 kHz (250 rev/s × 12 pole pairs) — must track through it | report §4.3 Rev 1.3 |
| Read rate | SPI ≥ 10 kHz (FOC commutation; 400 Hz servo task) | FLIGHT_SOFTWARE.md §3 |
| Roles | FOC commutation, de-spin progress, S&A spin signature (NOT a roll reference) | decision 12 |
| Cost | ≤ ₹1.5k (user-set) | plan constraint |

### 1.4 Setback sensor (new BOM line D3c — no part, no spec)

| Requirement | Value | Source |
|---|---|---|
| Function | S&A signature 1: setback ≥ threshold; plus launch detect / electronics enable | report §4.6, F5 |
| Threshold window | above manhandling (< 100 g), below kinematic mean (~5,000 g); peak 15,000 g | report §3/§7 |
| Boundary | live S&A stays with partner ESAF (inert exhibition design — architecture only) | project boundary |
| Environment | 15,000 g, −40…+60 °C, ms-class response | L1/L5 |

### 1.5 Proximity head (BOM D5)

| Requirement | Value | Source |
|---|---|---|
| Mode | FMCW ranging (not Doppler-only), HOB gates 6/12/18 m | report §4.6, F3 |
| Range accuracy | ±1 m class at ≤ 20 m + closing-rate gate | BOM D5 HOB bench |
| Radome | GFRP E-glass, RF ≥ 85 % transmission | report §4.5 D1 |
| Beam | de-spun steady, downward, through dome apex | report §2.3/§4.6 |
| Interface | serial (UART), 3.2–5.5 V class | BOM D5 |

---

## 2. Trade matrices (datasheet-backed; full citations in research entries)

### 2.1 GNSS (BOM D4)

| Candidate | NavIC | pos σ | vel σ | TTFF (hot) | Alt limit | Notes | Source (accessed 2026-08-31) |
|---|---|---|---|---|---|---|---|
| **u-blox NEO-F10N** | **L5 (SPG 6.00)** | 1 m CEP | 0.05 m/s | 2 s | 80 km | prof. grade, UART, −40…+85 °C | [DS UBX-23002117 R05](https://content.u-blox.com/sites/default/files/documents/NEO-F10N_DataSheet_UBX-23002117.pdf) |
| Quectel LC29H(AI) | L5 | 1.8 m CEP | 0.1 m/s | 1 s | **10 km — FAIL** (apogee 9.9–12 km) | cheapest NavIC module | [spec V1.8](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/7133/Quectel_LC29H_Series_GNSS_Specification_V1.8.pdf) |
| u-blox NEO-M9N | **none** (GPS/GLONASS/BDS/GAL only) | — | — | — | — | fails REQ F2 | [DS UBX-19014285](https://content.u-blox.com/sites/default/files/NEO-M9N-00B_DataSheet_UBX-19014285.pdf) |
| u-blox ZED-F9P | not listed | RTK class | — | — | — | US$127.50 list — 38× over budget | [product page](https://www.u-blox.com/en/product/zed-f9p-module) |
| Elena NavIC MIL (catalog D4) | yes | — | — | <30 s | — | defense lead time, NMEA 0183 | catalog D4 |
| MeitY sovereign ASIC (catalog D5) | yes (native) | — | — | — | — | **sovereign upgrade path only** (user constraint) | catalog D5 |

### 2.2 IMU (BOM D3)

| Candidate | Gyro FS | Gyro RND | ZRO init | Accel FS | Shock (off) | Verdict | Source (accessed 2026-08-31) |
|---|---|---|---|---|---|---|---|
| **TDK ICM-45686** | **±4000 dps** | 0.0038 °/s/√Hz | ±0.3 °/s | ±32 g | 20,000 g/0.2 ms | **selected** | [DS-000577](https://www.mouser.com/catalog/specsheets/TDK_DS_000577_ICM_45686.pdf) |
| TDK ICM-42688-P | ±2000 dps — **fails 4,000 °/s gate** | 0.0028 °/s/√Hz | ±0.5 °/s | ±16 g | 20,000 g/0.2 ms | runner-up | [DS-000347 v1.6](https://product.tdk.com/system/files/dam/doc/product/sensor/mortion-inertial/imu/data_sheet/ds-000347-icm-42688-p-v1.6.pdf) |
| Bosch BMI088 | ±2000 dps — fails | — | — | ±24 g | — | fails | datasheet |
| TDK IIM-42352 | — (3-axis **accelerometer only**) | — | — | — | — | not an IMU | [DS-000390](https://product.tdk.com/system/files/dam/doc/product/sensor/mortion-inertial/imu/data_sheet/ds-000390-iim-42352.pdf) |
| Tactical (ADIS / Atlantic 20kG) | — | — | — | — | 20kG proven | growth path only — not traded (user constraint) | catalog D6 |

### 2.3 Collar↔bell angle sensor (new D3b)

| Candidate | Bits | Max speed | SPI | Cost class | Verdict | Source (accessed 2026-08-31) |
|---|---|---|---|---|---|---|
| **MPS MagAlpha MA732** | **14** | **60,000 rpm** | 25 MHz | ≈US$3–4 @1k | **selected** (4× speed margin) | [product](https://www.monolithicpower.com/en/ma732.html) / [DS](https://www.mouser.com/datasheet/2/277/MA732-1855903.pdf) |
| ams AS5047P | 14 | 28 kRpm | 10 MHz | ≈US$4–5 | runner-up (1.9× margin) | [DS000324](https://www.mouser.com/datasheet/2/588/AS5047P_DS000324_3_00-1843440.pdf) |
| ams AS5048A | 14 | lower | — | ≈US$4 | dominated by AS5047P | datasheet |
| MagAlpha MA800 | 12 | high | — | ≈US$2–3 | alt (exact 12-bit; fewer features) | product family |
| RLS AksIM-2 | up to 20 | high | — | **₹10k+ — over budget** | rejected (precision-module cost for a commutation role) | datasheet/quote class |

### 2.4 Setback sensor (new D3c)

| Candidate | Range/threshold | Shock | Role fit | Verdict | Source (accessed 2026-08-31) |
|---|---|---|---|---|---|
| **Mechanical setback armer (PAS-class)** | threshold between <100 g and ~5,000 g | 15k g class by design | flight S&A signature 1 (partner ESAF path) | **selected (flight)** | [Precision Arming Solutions](https://www.select-controls.com/category/95/setback-inertial-high-g-switches.html) |
| **ADI ADXL1004** | ±500 g FS, dc–24 kHz | immune to 10,000 g | electronic launch signature (saturating detect, soft-mounted) | **selected (electronic)** | [product/DS](https://www.analog.com/en/products/ADXL1004.html) |
| TE semiconductor g-switches (A100 class) | ≤ ~1.5k g | — | threshold too low for setback window | rejected | family datasheets |
| Endevco 7280A(-20k) piezoresistive | ±20k g | instrument grade | telemetry rounds only — ₹50k+ instrumentation, not BOM | rejected (test asset) | [7280A](https://buy.endevco.com/contentstore/docs/pcb_corporate/endevco//products/specsheets/7280a-20k_a.pdf) |
| IMU accel channel | ±32 g | — | saturates at setback — cannot own signature 1 | rejected (role) | §2.2 |

### 2.5 Proximity head (BOM D5)

| Candidate | Method | Range output | HOB fit | Verdict | Source (accessed 2026-08-31) |
|---|---|---|---|---|---|
| **RFbeam K-LD7** | 24 GHz digital radar (FFT + tracking) | distance + speed + angle, serial target list; typical detect 15 m (person)/30 m (car) | 6/12/18 m gates via range + closing-rate; **AN03 radome app note** for GFRP | **selected** | [product](https://rfbeam.ch/product/k-ld7-radar-transceiver/) |
| RFbeam K-LC series | Doppler only | no distance | would need external ranging | rejected | family datasheets |
| innoSenT iSYS/iMQ | Doppler/ranging class | varies | alt source, no radome app note equivalent cited | parked | vendor pages |
| TI IWR6843 | 60 GHz FMCW | yes | **overkill** (power/cost/integration) | rejected (plan-set note) | datasheet |
| MS5611 baro (catalog D9) | pressure | 10 cm | **rejected above Mach 2** (LShang teardown — keep rejected) | rejected | `research/C_gnc/entry_20260825_lshang_*.md` |

---

## 3. Selections, rationale, runner-ups

| # | Role | Selected (PN) | Runner-up | Rationale (one line) |
|---|---|---|---|---|
| 1 | GNSS receiver | **u-blox NEO-F10N-00B** (module) + Ø25 ceramic patch | Quectel LC29H(AI) | only COTS standard-precision module with datasheet-backed NavIC L5 + GPS dual-band; 1 m CEP / 0.05 m/s / hot-start 2 s / 80 km — every GNC constant met with ≥3× margin. Runner-up fails the 10 km vs 12 km apogee ceiling. |
| 2 | IMU | **TDK ICM-45686** | ICM-42688-P | exact ±4,000 dps match to GYRO_SAT_RPS (the named baseline part tops at ±2,000 — the sim constant would not have mapped to it); ±0.3 °/s ZRO; ±32 g accel; 20,000 g unpowered shock ≥ 15,000 g setback with 1.33×. |
| 3 | Angle sensor | **MPS MA732GQ-Z** + Ø6 diametral magnet | AS5047P | 14-bit > 12-bit gate; 60,000 rpm = 4× the 15,000 rpm braking transient; 25 MHz SPI for commutation; ≤ ₹1.5k gate met (≈₹600 with magnet). |
| 4 | Setback | **Mechanical setback armer (partner ESAF interface) + ADXL1004 signature** | — | power-free qualifiable armer for S&A (flight path); ADXL1004 (±500 g, 20k g-class family, 10k g immunity) as the electronic launch signature with soft-mount attenuation. Honors the inert-exhibition boundary. |
| 5 | Prox head | **RFbeam K-LD7-RFB-00H-01** | innoSenT modules (parked) | digital distance + speed + angle over serial = two-condition HOB signature (range gate AND closing-rate gate); AN03 radome app note maps onto the GFRP dome QA. |

---

## 4. Error-budget flow-down + co-sim validation

### 4.1 Derivation method

Datasheet tolerance bounds are read two ways — the bracket defines the MC profiles:
**selected** = bound treated as 2σ, flight temperature span ΔT = 40 °C, RSS-combined,
then rounded *up*; **worstcase** = bound taken at face value as 1σ (full-temp terms
RSS-combined), GNSS held at the GNC interface requirement (receiver assumed to meet only
that). GNSS CEP→σ: CEP50 ≈ 1.1774·σ₁D. Per-sample noise at sample rate f_s from a rate
noise density n: σ = n·√(f_s/2).

**Environment-figure rule:** the gyro per-sample noise (0.2 °/s) and the accel per-sample
vibration allowance (0.08 m/s²) are *airframe-environment* figures (vibration, servo
jitter), not part-limited figures — the selected part's sensor-only contributions
(0.017 °/s, 0.011 m/s²) are 12×/7× below them. They are therefore held constant across
profiles; the part-level margins are recorded below. This also keeps the sim-side and
FSW-side draw streams identical (the sim's own literals are frozen), so RNG-stream parity
holds at every profile.

### 4.2 Flow-down table (every GNC sensor constant → cited datasheet parameter)

| Constant (config.py) | Sim value | Datasheet basis (part · spec · source) | Selected σ | Margin verdict |
|---|---|---|---|---|
| GPS_POS_SIG | 5.0 m | NEO-F10N · 1 m CEP (GPS+NavIC) · [DS R05](https://content.u-blox.com/sites/default/files/documents/NEO-F10N_DataSheet_UBX-23002117.pdf) → σ≈0.85 m, rounded up for dynamics/multipath | 1.2 m | **conservative 4.2×** (sim/selected ratio) |
| GPS_VEL_SIG | 0.3 m/s | NEO-F10N · 0.05 m/s (50 % @ 30 m/s dynamic) → σ≈0.042, 2× rounding | 0.1 m/s | **conservative 3×** |
| GNSS_LAT | 0.10 s | no receiver max-latency spec; UBX time-tagged delivery over UART ≥ 115200 baud | 0.10 s | **equal** (unverifiable — kept) |
| GYRO_BIAS_INIT_SIG | 0.5 °/s | ICM-45686 · ZRO init ±0.3 °/s (→0.15 @2σ) + temp ±0.005 °/s/°C × 40 °C (→0.10 @2σ), RSS | 0.18 °/s | **conservative 2.8×** |
| gyro per-sample | 0.2 °/s | environment figure (vibration/servo jitter); part-only: ICM-45686 RND 0.0038 °/s/√Hz × √(40/2) = 0.017 °/s | 0.2 °/s (held) | **conservative 12×** vs part-only |
| ACC_NOISE_SIG | 0.08 m/s² | environment + part: ICM-45686 RND 110 µg/√Hz @ ±32 g FS × 9.80665 × √(200/2) = 0.0108 m/s² | 0.0108 m/s² | **conservative 7.4×** (environment-dominated) |
| ACC_BIAS_INIT_SIG | 0.25 m/s² | ICM-45686 · zero-g ±10 mg (→0.049 @2σ) + temp ±0.15 mg/°C × 40 °C (→0.03 @2σ), RSS, rounded up | 0.08 m/s² | **conservative 3.1×** |
| ANGLE_BITS | 12 bit | MA732 · 14-bit absolute (0.022°) exceeds the 12-bit requirement | 12 (unchanged) | **conservative 4×** (part finer than modeled) |
| GYRO_SAT_RPS | 4,000 °/s | ICM-45686 · FS ±4,000 dps — exact match | — | **equal (by part selection)** |
| temp rating | −40…+60 °C | NEO-F10N −40…+85, ICM-45686 −40…+85, MA732 −40…+125, K-LD7 −40…+85 (per datasheets) | — | **conservative** (parts outrate the env spec) |
| setback | 15,000 g powered-off | ICM-45686/42688-P 20,000 g/0.2 ms (1.33×); ADXL1004 10,000 g immunity → **soft-mount attenuation QA on D3c** | — | **IMU pass / signature element needs mount QA** |

### 4.3 Co-sim validation (generated numbers: `out_sim/RESULTS_SENSORS.md`)

Harness: `cosim/run_sensors.py` — applies runtime sensor profiles to BOTH the truth-side
sim globals and the FSW-side filter constants (patch-before-construct), runs pair-check +
det cases + paired MC (250 primary + 80×4 secondary, seed 20260901) per profile. Gate:
**CEP50 ≤ 30 m (PS M2), ≥ 98 % guide/degraded, 0 denied**; baseline must reproduce the
Rev 1.5 run (21.5 m).

| Profile | CEP50 (fsw_l0) | guided share | denied | Verdict |
|---|---|---|---|---|
| baseline | **21.5 m** (mean 22.1 / p90 33.1 / max 149.5; 233 guide + 17 degraded) | 100.0 % | 0 | reproduces Rev 1.5 (21.5 m) **PASS** |
| selected | **21.7 m** (mean 21.6 / p90 32.9 / max 45.8; 236 guide + 14 degraded) | 100.0 % | 0 | **PS M2 gate PASS** |
| worstcase | 21.1 m (mean 21.1 / p90 32.3 / max 53.4; 249 guide + 1 degraded) | 100.0 % | 0 | reported **PASS** |

*(all values generated by `cosim/run_sensors.py` — see `out_sim/RESULTS_SENSORS.md`; pair-check
draw-count AND miss parity ALL OK at every profile, max |miss sim−fsw| 0.00 m)*

**Reading:**
- The baseline row reproduces the Rev 1.5 paired-MC run bit-for-bit (CEP50/mean/p90/max and
  the 233+17 mode split match `out_sim/RESULTS_FSW.md`) — the profile mechanism is inert at
  today's constants, so the selected/worstcase rows are a clean experiment.
- **Selected parts close the gate with the CEP50 essentially unchanged (21.5 → 21.7 m) but
  the tail shrinks 3.3× (max 149.5 → 45.8 m)** — the pre-selection error model was already
  conservative; the selected parts' value shows up in robustness, not in the median. The
  residual error floor is the guidance deadband (8 m) + IPP/actuator limits, not sensors.
- Cd +5 % stays ~104 m in every profile (authority-limited physics, untouched by sensors —
  as expected); BLIND/never-lock fail-safes unchanged.

**Interpretation guardrails (carried from Rev E):** the Cd +5 % case remains
authority-limited (~105 m — sensor quality cannot fix fin authority; do not tune it away);
BLIND and never-lock fail-safes are behavior checks, not accuracy gates.

### 4.4 Findings and honest gaps

1. **GYRO_SAT_RPS part match (the headline finding):** the named baseline IMU
   (ICM-42688-P) has a ±2,000 dps maximum — the 4,000 °/s design constant would NOT have
   mapped to it. ICM-45686 (±4,000 dps) closes this exactly. `config.py` was not edited
   (pairing contract); the part was selected to match the constant.
2. **GNSS ITAR dynamics ceiling:** both COTS receivers specify 500 m/s velocity limits
   (< the 827 m/s muzzle velocity). Flight procurement must order the unlimited-dynamics
   variant (u-blox professional track) or transition to the sovereign ASIC — a
   procurement item, not an error-budget item (the sim's error model is unaffected).
3. **NavIC band coverage:** both COTS parts are NavIC **L5-only** (no NavIC L1). L5 is
   the ranging-grade signal; noted for the sovereign-upgrade-path discussion.
4. **ADXL1004 immunity 10,000 g < 15,000 g design peak:** the electronic signature
   element must be soft-mounted (potting isolation) so setback remains a saturating
   *detect*, not a measurement. QA item recorded on BOM D3c.
5. **GYRO_NOISE_DENS placeholder:** the config's 0.015 °/s/√Hz placeholder is ~4× the
   ICM-45686 RND (0.0038) — conservative; the operative sim figure (0.2 °/s per-sample)
   is the environment figure (§4.1).
6. **GNSS first-fix ≤ 5 s spec:** met by hot-start (2 s) *because the receiver tracks
   from boot* (t≈2 s, co-rotating antenna) and only the solution is enabled at t=45 s —
   cold-start (27–29 s) is never in the path. BOM D4 spec wording retained.

---

## 5. Electrical / interface map (Ø62 4-layer GNC board, report §4.5)

| Peripheral | Part | Bus / signal | Rate | Rail | Notes |
|---|---|---|---|---|---|
| MCU | STM32G474 | — | 170 MHz; FOC 15 kHz HRTIM | 3.3 V | FOC + GNC share the die (methodology §7) |
| IMU | ICM-45686 | SPI1, 4-wire, ≤ 24 MHz + DRDY→INT | 200 Hz raw (IMU_DT), decimated to EKF | 3.3 V (VDD/VDDIO 1.71–3.6) | FS ±4000 dps gyro / ±32 g accel; AAF configured at init |
| GNSS | NEO-F10N-00B | UART1 + RX DMA, 38400–921600 baud | 1 Hz PVT, time-tagged (UBX) | 3.0–3.3 V (2.7–3.6), backup V_BCKP | patch antenna fed from VCC_RF (≤ 50 mA LNA budget); LNA_EN |
| Angle sensor | MA732 | SPI2 ≤ 25 MHz | ≥ 10 kHz commutation reads; 400 Hz servo task | 3.3 V | Ø6 diametral magnet on bell ID; ABZ/PWM outputs spare |
| Setback signature | ADXL1004 | analog → ADC (threshold comparator to EXTI) | event-driven | 3.3 V | soft-mount per §4.4(4); threshold between manhandling and setback mean |
| Prox head | K-LD7 | UART2, 115200 baud | target list ≥ 10 Hz in terminal window | 3.2–5.5 V (from 5 V boost rail) | behind radome; AN03 radome practice |
| Rails | — | 5 V boost (A6) → 3.3 V buck → per-rail LDO for RF cleanliness | — | 5 V / 3.3 V | slip-ring budget unchanged (dome ~1.5 W; +radar ≈ 0.15 W → ~1.65 W, still ≪ slip rating — see BOM §H) |

Bus contention: SPI1 (IMU) and SPI2 (angle) are separate peripherals — no arbitration
sharing with the FOC-critical angle read; UART DMA is the GNSS ISR path (FLIGHT_SOFTWARE.md
§6 checklist).

---

## 6. BOM deltas (Rev 1.3 — see `02_BOM_MANUFACTURING_ASSEMBLY.md` §H)

| Line | Change | Cost impact (proto / @1k) |
|---|---|---|
| D3 GNC board | ICM-42688 → **ICM-45686** (part-number fill; board footprint same LGA-14 class) | +≈₹150 / +≈₹150 |
| **D3b angle sensor (NEW)** | **MA732GQ-Z + Ø6 diametral NdFeB magnet**, potted collar-face mount | +₹600 / +₹350 |
| **D3c setback sensor (NEW)** | setback-armer interface (inert demo; flight = partner ESAF) + **ADXL1004** signature + threshold circuit | +₹2,500 / +₹800 |
| D4 GNSS | "L1/L5 M9N-class" → **NEO-F10N-00B** + Ø25 patch (spec now datasheet-backed; envelope unchanged) | ±0 / ±0 |
| D5 prox head | note **K-LD7-RFB-00H-01** as the candidate PN (HOB gates bench-verified on K-LD7-EVAL) | ±0 / ±0 |
| **Rollup** | §D table | **₹1,54,200 → ₹1,57,450 proto; ₹27,100 → ₹28,400 @1k** (ex-works ≈ +1.6 %, PS ceiling share unchanged 8–12 %) |

Zero "no part number" gaps remain for the five GNC sensors.

## 7. Sourcing / procurement notes (India)

| Part | Availability | Devkit / bench path | Watch items |
|---|---|---|---|
| NEO-F10N-00B | u-blox mass production (DS R05, 09-Oct-2025); global distributors ship to India | SparkFun NEO-F10N breakout (published datasheet mirror); u-blox evaluation kit via distributor | **flight units need the unlimited-dynamics factory variant** (§4.4(2)); NavIC L5 enabled by constellation config in standard SPG 6.00 — no special firmware tier |
| LC29H(AI) | Quectel + Indian distributors (cheap bench NavIC L5 path) | Quectel EVB via sales | rejected for flight (10 km ceiling) — bench HIL only |
| ICM-45686 | Mouser/Digi-Key/Arrow stock (2024 part) | TDK evaluation boards via distributors | new part — confirm long-term availability at PO |
| MA732 | MPS distributors | TBMA732-Q-LT-00A / TBMA732-Q-RD-01A eval boards (Digi-Key/Mouser) | magnet alignment tolerance sets angle accuracy — potting fixture QA |
| ADXL1004 | Analog Devices + distributors | — | soft-mount QA (§4.4(4)) |
| K-LD7 | RFbeam via Digi-Key/Mouser | **K-LD7-EVAL** with PC visualization — direct HOB-bench use | bench-verify 6/12/18 m gates behind a GFRP coupon per AN03 |
| Setback armer | partner ESAF domain (BEL/ECIL class) | inert interface for the exhibition build | STANAG 4187 qual path (outside this project's boundary) |

Lead times and prices are distributor list classes at access date (2026-08-31) — verify at PO.

## 8. Design-report decision log additions (decisions 20–22)

| # | Decision | Alternatives rejected | Rationale |
|---|---|---|---|
| 20 | GNSS = **u-blox NEO-F10N** (NavIC L5 + GPS dual-band COTS), patch + UART DMA; sovereign MeitY ASIC recorded as upgrade path | LC29H(AI) (10 km altitude ceiling < 12 km apogee); NEO-M9N (no NavIC — datasheet-verified); ZED-F9P (NavIC not listed, 38× cost); Elena MIL module (lead time) | only standard-precision COTS part whose datasheet closes every GNC flow-down with ≥3× margin at BOM cost; sovereign path preserved by user constraint |
| 21 | IMU = **ICM-45686** | ICM-42688-P (±2,000 dps < 4,000 °/s design constant — the named baseline failed the range gate); BMI088 (±2,000 dps); IIM-42352 (accel-only); tactical ADIS/Atlantic (growth path, not traded) | exact GYRO_SAT_RPS match, lower ZRO spec, ±32 g accel, 20,000 g unpowered shock ≥ 15,000 g setback (1.33×), drop-in LGA-14 |
| 22 | Fill the two missing sensor lines: D3b angle = **MA732** (14-bit/60 kRpm/25 MHz SPI); D3c setback = **mechanical armer interface + ADXL1004 electronic signature**; D5 prox PN = **K-LD7** | AS5047P (1.9× speed margin vs 4×); AksIM-2 (over budget); IMU-own-setback (saturates — no role); K-LC (Doppler-only); TI 60 GHz (overkill); baro HOB (rejected above Mach 2) | closes the BOM's "no part number" gaps for the GNC sensor set with datasheet-backed margins at ₹1.5k-class cost gates |

---

*Evidence chain: `research/D_sensors/entry_20260831_*.md` (6 sourced entries) → this doc
(§2–§4) → `out_sim/RESULTS_SENSORS.md` (machine-generated validation) → BOM Rev 1.3 §H,
report Rev 1.6, HANDOFF.md. Sim/reference files untouched (`py_compile` clean; pytest 22
green; config-parity contract intact).*
