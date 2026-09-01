---
id: E06-20260831-w25q128jv-spi-flash
category: 06_electronics-embedded-power
author: @jagathsrujan
date: 2026-08-31
source_type: datasheet
trl: 9
---

## Idea Title
GNC board SPI flash: Winbond W25Q128JVSIQ (16 MB, 133 MHz SPI, SOIC-8)

## Summary (2-3 lines)
The GNC board carries one SPI flash for telemetry/log storage, golden-vector self-test
tables, and pre-flight calibrated data (Cd calibration ships with the kit — config.py
CD_CAL note). W25Q128JVSIQ: 16 MB, SPI up to 133 MHz, standard 208-mil SOIC-8 —
library-supported, cheap, and 10× the log capacity of the 64 Mbit class at similar cost.

## Source (MANDATORY - no URL = reject)
- URL: https://www.winbond.com/hq/support/documentation/levelOne.jsp?__locale=en&__Path=/support/resources/documentation/resource/w25q128jv
  (W25Q128JV Datasheet) — mirror: https://www.mouser.com/datasheet/2/949/w25q128jv_revj_02232018_plus-1489807.pdf
- Accessed: 2026-08-31
- Quote: "Fast clock speeds: Up to 133 MHz SPI bus clock speed" (W25Q128JV family, SPI
  serial flash, 128 Mbit / 16 MB, SOIC-8 208-mil, −40…+85 °C industrial grade).

## Evidence
- Usage budget: 90 s flight at ~50 KB/s telemetry burst = <5 MB even unthrottled — 16 MB
  holds ~3 flights; sector-erased logging with wear-aware round-robin.
- Interface: SPI3 on the G474 dome board at 25 MHz (≫ the ~50 KB/s need; the 133 MHz
  ceiling leaves 5× headroom); DMA not required for the flash path.
- Power: active read ~15 mA class, standby ~1 µA — inside the dome rail budget line
  (0.010 W active worst in 06 §2).

## Indian Path
Winbond via Mouser/Digi-Key India; drop-in alternates: GigaDevice GD25Q128 (pin-compatible,
₹80 class — recorded as second source for the India supply chain).

## Pros / Cons
- Pros: ubiquitous, cheap, industrial temp; 133 MHz SPI; standard SOIC-8 with KiCad
  library symbol (no custom symbol needed).
- Cons: consumer-grade endurance 100k cycles — irrelevant at 3 flights/kit (recorded).

## Cost Estimate (lakhs)
≈ US$1.0–1.3 → ≈ ₹100–120 @1k; proto ≈ ₹180. D3 board line add.

## Recommendation
**Select W25Q128JVSIQ.** Runner-up: GigaDevice GD25Q128ESIGR (pin-compatible, India-stock
cheaper — qualify at PO).

## Links to Code/CAD
- cleansheet/06_ELECTRONICS_ARCHITECTURE.md §3 (SPI3 bus), §7 BOM
- flight_sw/fsw/config.py (CD_CAL pre-flight data storage rationale)
