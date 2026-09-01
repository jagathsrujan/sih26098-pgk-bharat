---
id: E06-20260831-stm32g431cbt6-drive-mcu
category: 06_electronics-embedded-power
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
Drive-domain MCU variant: STM32G431CBT6 (LQFP48, 128 KB flash / 32 KB SRAM)

## Summary (2-3 lines)
The dual-domain split (decision 23) moves the FOC current loop to the shell frame.
STM32G431CBT6: 170 MHz Cortex-M4F, 128 KB flash / 32 KB SRAM, TIM1 advanced timer with
complementary outputs + dead-time insertion (the 15 kHz 3-phase PWM engine — the G431
has no HRTIM, which is reserved to the dome G474 per the architecture plan), 5 MPCPs,
2× 12-bit ADC, rich timers for the brake-chopper PWM and Hall capture.

## Source (MANDATORY - no URL = reject)
- URL: https://www.st.com/resource/en/datasheet/stm32g431c6.pdf (DS13105)
- Product: https://www.st.com/en/microcontrollers-microprocessors/stm32g431cb.html
- Accessed: 2026-08-31
- Quote: "up to 128 Kbytes of Flash memory, and 32 Kbytes of SRAM"; "Arm® Cortex®-M4
  32-bit MCU+FPU, 170 MHz / 213 DMIPS".

## Evidence
- FOC current loop at 15 kHz on TIM1 (complementary, center-aligned, ~200 ns dead time)
  is the standard G4 deployment — the ~10 µs ISR budget (methodology §7 note) fits with
  >10× headroom at 170 MHz.
- 32 KB SRAM / 128 KB flash: FOC + commutation + slip-link stack is < 20 KB flash,
  < 4 KB RAM — comfortable.
- HRTIM is a G474/G484-only peripheral; the drive side does not need it at 15 kHz
  (TIM1 resolution is sufficient at this frequency and bus voltage).

## Indian Path
ST via Arrow/Avnet/Mouser India; Nucleo-G431RB devkit for bench bring-up.

## Pros / Cons
- Pros: value line of the same G4 family (shared toolchain/HAL with the dome G474 — one
  C header contract drives both); TIM1 + 2 ADCs + timers exactly cover PWM/current/chopper/
  Hall; LQFP48 leaves pins for MA732 SPI + slip UART + nFAULT + SWD.
- Cons: no HRTIM (irrelevant at 15 kHz); no CCM SRAM (not needed).

## Cost Estimate (lakhs)
≈ US$3–4 @1k → ≈ ₹300–400; proto ≈ ₹500. New A6 row (drive MCU).

## Recommendation
**Select STM32G431CBT6** for the A6 drive domain. Runner-up: STM32G431RBT6 (LQFP64 —
more pins than needed at +₹100; keep for layout escape if the bridge routing congests).

## Links to Code/CAD
- cleansheet/06_ELECTRONICS_ARCHITECTURE.md §4 (drive domain), decision 23 in 03 §8
- flight_sw/board/board_config.h (SLIP_* protocol contract consumed by the drive stack)
