# flight_sw/board/ — the embedded hardware contract

**`board_config.h`** is the single C header the future firmware C-port consumes for
both control domains (design-report decision 23):

- **Dome G474** — GNC FSW task rates, ISR/NVIC priorities, verified pin map,
  bus rates.
- **Drive G431** — verified pin map (TIM1 3-phase PWM, MA732 SPI, ADC channels,
  Hall, chopper), PWM/loop rates.
- **Slip-ring link** — frame struct (`slip_frame_t`), CRC-16/CCITT-FALSE, rates,
  100 ms loss→safe-state timeout.

## How the C port consumes it

1. `#include "board_config.h"` — every rate, pin and protocol constant comes from
   here; the C port writes **no** local copies of these numbers.
2. Task rates (`BOARD_SERVO_HZ`, `BOARD_SENSOR_HZ`, `BOARD_NAV_PREDICT_HZ`,
   `BOARD_GNSS_HZ`, `BOARD_GUIDE_HZ`, `BOARD_IMU_HZ`, `BOARD_GNSS_LAT`) are
   **assert-equal to `fsw/config.py`** by `tests/test_board_config.py` — the same
   parity discipline as the sim↔FSW pairing contract. Never edit one side alone.
3. The scheduler mirrors `fsw/timebase.py`: SysTick 2 kHz (`BOARD_SYSTICK_HZ`,
   integer divisor of all task rates) dispatching fixed slots (400/100/40/1 Hz),
   static registration, no dynamic allocation (FLIGHT_SOFTWARE.md §6 checklist).
4. The slip link uses `slip_frame_t` + `SLIP_*` constants verbatim; the frame
   format, CRC and safe-state behavior are specified in
   `cleansheet/06_ELECTRONICS_ARCHITECTURE.md` §5.

## Provenance

- Pin maps verified against ST DS12288 Rev 6 (G474 LQFP64) and DS12589 Rev 6
  (G431 LQFP48) Tables 12/13 — per-pin check documented in 06 §3.5 / §4.
- IC selections: `research/06_electronics-embedded-power/entry_20260831_*.md`.
- Architecture: `cleansheet/06_ELECTRONICS_ARCHITECTURE.md` (Rev 1.0).
