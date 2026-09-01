---
id: E06-20260831-stm32g474ret6-dome-mcu
category: 06_electronics-embedded-power
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
Dome GNC MCU variant: STM32G474RET6 (LQFP64, 512 KB flash / 128 KB SRAM)

## Summary (2-3 lines)
The GNC methodology budgets the dome FSW against a 128 K RAM / 170 MHz M4F part
(`04_GNC_METHODOLOGY.md` §7: <0.5 ms worst 1 Hz tick, <5 KB RAM). STM32G474RET6 is the
LQFP64 member of that family: 512 KB flash, 128 KB SRAM (with CCM SRAM), 170 MHz
Cortex-M4F + FPU, math accelerator, 4× 12-bit ADC, DMAMUX — pins are ample for
SPI1 (IMU) + SPI3 (flash) + 3× USART + ADC + PPS capture + SWD with room to spare.

## Source (MANDATORY - no URL = reject)
- URL: https://www.st.com/resource/en/datasheet/stm32g474cb.pdf (DS12288 Rev 7)
- Accessed: 2026-08-31
- Quote: "up to 512 Kbytes of Flash memory, and 128 Kbytes of SRAM"; "Arm® Cortex®-M4
  32-bit MCU+FPU, 170 MHz / 213 DMIPS".

## Evidence
- Memory close-out vs methodology §7: FSW budget < 5 KB RAM / < 20 KB flash — the RE
  density gives 25× flash headroom (config tables, telemetry logging into SPI flash, OTA
  margin) without changing the RAM class the budget was written against.
- LQFP64 (64 pins): enough GPIO to dedicate one USART per link (GNSS / K-LD7 / slip-ring)
  with DMA, and still hold SWD + spare — the LQFP48 G474C would force pin muxing gymnastics
  around the flash and DRDY lines for ~₹100 saving.
- Temp grade Q (−40…+85 °C) covers the −40…+60 °C env spec.

## Indian Path
ST via Arrow/Avnet/Mouser India; Nucleo-G474RE devkit for the bench bring-up appendix.

## Pros / Cons
- Pros: exact family/methodology match; 128 KB SRAM closes the §7 gate verbatim; pin count
  eliminates mux contention; DMAMUX makes UART DMA flexible (no fixed-channel conflicts).
- Cons: 512 KB flash is over-provisioned for GNC-only code (accepted — reuse headroom for
  telemetry logging and bootloader).

## Cost Estimate (lakhs)
≈ US$6–8 @1k → ≈ ₹550–700; proto unit ≈ ₹850. D3 board line impact ≈ +₹0 (replaces the
"STM32G474" placeholder in D3).

## Recommendation
**Select STM32G474RET6** for the dome GNC board. Runner-up: STM32G474CET6 (LQFP48,
same memory — rejected on pin count: 3× USART + 2× SPI + ADC + EXTI + SWD is tight).

## Links to Code/CAD
- cleansheet/06_ELECTRONICS_ARCHITECTURE.md §3 (pin map), flight_sw/board/board_config.h
- flight_sw/FLIGHT_SOFTWARE.md §3 (module→ISR map)
