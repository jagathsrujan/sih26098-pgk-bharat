# Interfaces — Example (edit for real build)

| From → To | Bus | Connector | Rate | Notes |
|---|---|---|---|---|
| IMU → MCU | SPI3 + DRDY | board-to-board 0.5mm FFC | 8MHz 1kHz | CRC |
| GNSS → MCU | UART4+PPS | MMCX → FFC | 921600 | RTK |
| Baro/Mag → MCU | I²C1 | FFC | 400kHz | — |
| Roll Hall → MCU | SPI2 | slip-ring 6w | 1kHz | phasing for CAA |
| Encoders → MCU | SPI | — | 1kHz | FOC feedback |
| MCU → DRV8313 | PWM+DIR | — | 20kHz | synchronized to roll |
| RF IF → CPLD | Analog diff | — | 10kHz BW | OPA320 → ADC CPLD |
| Impact → CPLD | SPI | — | 20kHz BW | direct, not via MCU |
| CPLD ↔ MCU | GPIO | — | — | Arm/Time cmd + inhibit |
| CPLD → EED | FIRE (2oo2) | HV cap + 2x FETs | — | 1A NO-FIRE / 2.5A ALL-FIRE |
| Setter ↔ MCU/CPLD | NFC+RS422 | inductive coil / pogo | 115200 | AES-128, pre-launch only |
| Internal | CAN-FD | M8 flex | 2Mbps | backbone |
| Power 3.3/5/12/12iso | — | copper pour | — | sequenced, isolated S&A |

**Safety:** CPLD 2oo2 independent of MCU. 12V_iso disconnected (series FETs + iso DCDC off) until setback+spin+traj gate passed. DS3231 RTC for time mode auto-fires if GNSS jammed.

**High-g rules (example):** Underfill QFN/BGA, tantalum not MLCC for bulk, 4-point mount for IMU, conformal coat (PU), 100% ICT+8000g centrifuge test placeholder.
