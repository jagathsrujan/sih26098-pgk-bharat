/*
 * board_config.h — PGK SIH26098 embedded hardware contract (Rev 1.0, 2026-08-31)
 *
 * The single header the future firmware C-port consumes (dome G474 + drive G431).
 * Companion to cleansheet/06_ELECTRONICS_ARCHITECTURE.md; pin maps are verified
 * against DS12288 Rev 6 (G474 LQFP64) and DS12589 Rev 6 (G431 LQFP48) Tables 12/13.
 *
 * PARITY CONTRACT: task rates + GNSS_LAT in this file are assert-equal to
 * flight_sw/fsw/config.py by flight_sw/tests/test_board_config.py — never edit
 * one side alone. Units are stated on every line. No dynamic allocation anywhere.
 */
#ifndef BOARD_CONFIG_H
#define BOARD_CONFIG_H

#include <stdint.h>

/* ============================================================ task rates
 * Deployment task rates — MUST equal fsw/config.py (parity-tested). */
#define BOARD_SERVO_HZ       400.0  /* Hz, pattern/servo task (ctrl)          */
#define BOARD_SENSOR_HZ      40.0   /* Hz, gyro/accel sample + roll EKF       */
#define BOARD_NAV_PREDICT_HZ 100.0  /* Hz, translational EKF predict          */
#define BOARD_GNSS_HZ        1.0    /* Hz, GNSS delivery                      */
#define BOARD_GUIDE_HZ       1.0    /* Hz, guidance tick (IPP + laws)         */
#define BOARD_IMU_HZ         200.0  /* Hz, raw IMU sample rate (=1/IMU_DT)    */
#define BOARD_GNSS_LAT       0.10   /* s, GNSS fix latency (time-tagged)      */

/* ============================================================ scheduler
 * SysTick 2 kHz dispatches fixed integer slots: 400 Hz servo (every 5th),
 * 100 Hz EKF predict (every 20th), 40 Hz sensors/roll (every 50th),
 * 1 Hz GNSS + guidance. Registration static, no malloc. */
#define BOARD_SYSTICK_HZ     2000.0 /* Hz, base tick (integer divisor of all rates) */

/* ============================================================ ISR / NVIC map
 * Priorities (0 = highest) per 06 §3.3 / §4:                              */
#define BOARD_PRIO_SETBACK_EXTI   1  /* EXTI1  PB1 comparator (dome)          */
#define BOARD_PRIO_IMU_DRDY_EXTI  2  /* EXTI4  PC4 IMU DRDY 200 Hz (dome)     */
#define BOARD_PRIO_SLIP_DMA       2  /* USART RX DMA TC/IDLE (both boards)    */
#define BOARD_PRIO_GNSS_DMA       3  /* USART1 RX DMA TC -> fix queue (dome)  */
#define BOARD_PRIO_SYSTICK        4  /* task scheduler slots (both)           */
#define BOARD_PRIO_PPS_TIM2       5  /* TIM2_CC PPS capture 1 Hz (dome)       */
#define BOARD_PRIO_PROX_USART     6  /* USART2 K-LD7 target list (dome)       */
#define BOARD_PRIO_FAULT_EXTI     1  /* EXTI7  PA7 nFAULT (drive)             */

/* ============================================================ dome pins
 * STM32G474RET6 LQFP64 — verified vs DS12288 Rev 6 Table 13 (06 §3.2). */
#define DOME_PIN_IMU_SCK      "PA5"  /* SPI1 SCK, AF5                          */
#define DOME_PIN_IMU_MISO     "PA6"  /* SPI1 MISO, AF5                         */
#define DOME_PIN_IMU_MOSI     "PA7"  /* SPI1 MOSI, AF5                         */
#define DOME_PIN_IMU_CS       "PA4"  /* SPI1 NSS (software CS), GPIO out       */
#define DOME_PIN_IMU_DRDY     "PC4"  /* GPIO in -> EXTI4, 200 Hz               */
#define DOME_PIN_FL_SCK       "PB3"  /* SPI3 SCK (flash), AF6                  */
#define DOME_PIN_FL_MISO      "PB4"  /* SPI3 MISO, AF6 (UCPD1_DBDIS=1)         */
#define DOME_PIN_FL_MOSI      "PB5"  /* SPI3 MOSI, AF6                         */
#define DOME_PIN_FL_CS        "PB6"  /* GPIO out (UCPD1_DBDIS=1)               */
#define DOME_PIN_GNSS_TX      "PA9"  /* USART1 TX, AF7                         */
#define DOME_PIN_GNSS_RX      "PA10" /* USART1 RX + DMA, AF7                   */
#define DOME_PIN_GNSS_PPS     "PA15" /* TIM2_CH1 input capture, AF1            */
#define DOME_PIN_PROX_TX      "PA2"  /* USART2 TX -> K-LD7, AF7                */
#define DOME_PIN_PROX_RX      "PA3"  /* USART2 RX <- K-LD7, AF7                */
#define DOME_PIN_SLIP_UART    "PB10" /* USART3 half-duplex single-wire, AF7    */
#define DOME_PIN_SETB_AN      "PA0"  /* ADC1_IN1 analog (ADXL1004)             */
#define DOME_PIN_SETB_TRIG    "PB1"  /* GPIO in -> EXTI1 (TLV7011 out)         */
#define DOME_PIN_LNA_EN       "PB15" /* GPIO out (GNSS LNA provision)          */
#define DOME_PIN_SWDIO        "PA13" /* SWD                                    */
#define DOME_PIN_SWCLK        "PA14" /* SWD                                    */
#define DOME_OSC_HZ           24000000.0 /* Hz, HSE crystal +/-20 ppm          */
#define BOARD_DOME_CPU_HZ     170000000.0 /* Hz, SYSCLK (PLL from HSE)         */

/* Dome bus rates (06 §3.4). */
#define DOME_SPI1_HZ       10000000.0 /* Hz, ICM-45686 (<=24 MHz part limit)   */
#define DOME_SPI3_HZ       25000000.0 /* Hz, W25Q128 (<=133 MHz part limit)    */
#define DOME_GNSS_BAUD     115200.0   /* Bd, USART1 (config 38400..921600)     */
#define DOME_PROX_BAUD     115200.0   /* Bd, USART2 K-LD7                      */

/* ============================================================ drive pins
 * STM32G431CBT6 LQFP48 — verified vs DS12589 Rev 6 Tables 12/13 (06 §4). */
#define DRIVE_PIN_PWM_CH1     "PA8"  /* TIM1_CH1, AF6 (15 kHz 3-phase)         */
#define DRIVE_PIN_PWM_CH2     "PA9"  /* TIM1_CH2, AF6                          */
#define DRIVE_PIN_PWM_CH3     "PA10" /* TIM1_CH3, AF6                          */
#define DRIVE_PIN_PWM_CH1N    "PB13" /* TIM1_CH1N, AF6                         */
#define DRIVE_PIN_PWM_CH2N    "PB14" /* TIM1_CH2N, AF6                         */
#define DRIVE_PIN_PWM_CH3N    "PB15" /* TIM1_CH3N, AF6                         */
#define DRIVE_PIN_MA_SCK      "PB3"  /* SPI1 SCK -> MA732, AF5                 */
#define DRIVE_PIN_MA_MISO     "PB4"  /* SPI1 MISO, AF5 (UCPD1_DBDIS=1)         */
#define DRIVE_PIN_MA_MOSI     "PB5"  /* SPI1 MOSI, AF5                         */
#define DRIVE_PIN_MA_CS       "PA4"  /* GPIO out                               */
#define DRIVE_PIN_ADC_IU      "PA0"  /* ADC1_IN1, phase-U INA240A2             */
#define DRIVE_PIN_ADC_IV      "PA1"  /* ADC1_IN2, phase-V INA240A2             */
#define DRIVE_PIN_ADC_IW      "PB0"  /* ADC1_IN15, phase-W INA240A2            */
#define DRIVE_PIN_ADC_VBUS    "PB1"  /* ADC1_IN12, Vbus divider                */
#define DRIVE_PIN_ADC_NTC     "PA5"  /* ADC2_IN13, winding NTC                 */
#define DRIVE_PIN_CHOP_PWM    "PA6"  /* TIM16_CH1, AF1 -> A7b chopper          */
#define DRIVE_PIN_HALL_U      "PB6"  /* TIM4_CH1, AF2 (nBOOT_SEL=1 frees PB8)  */
#define DRIVE_PIN_HALL_V      "PB7"  /* TIM4_CH2, AF2                          */
#define DRIVE_PIN_HALL_W      "PB8"  /* TIM4_CH3, AF2 (BOOT0 via option bit)   */
#define DRIVE_PIN_SLIP_UART   "PA2"  /* USART2 half-duplex single-wire, AF7    */
#define DRIVE_PIN_NFAULT      "PA7"  /* GPIO in -> EXTI7 (DRV8329)             */
#define DRIVE_PIN_EN_GATE     "PB12" /* GPIO out (DRV8329)                     */
#define DRIVE_PIN_SWDIO       "PA13" /* SWD                                    */
#define DRIVE_PIN_SWCLK       "PA14" /* SWD                                    */
#define DRIVE_OSC_HZ          24000000.0 /* Hz, HSE crystal +/-20 ppm          */
#define BOARD_DRIVE_CPU_HZ    170000000.0 /* Hz, SYSCLK                        */
#define DRIVE_PWM_HZ          15000.0    /* Hz, FOC/PWM (TIM1 center-aligned)  */
#define DRIVE_ADC_LOOP_HZ     15000.0    /* Hz, ADC1 scan trigger (TIM1 upd)   */
#define DRIVE_CHOP_HZ         20000.0    /* Hz, TIM16 chopper PWM              */
#define DRIVE_DEADTIME_NS     200.0      /* ns, TIM1 dead-time insertion       */

/* MA732 angle sensor (drive side — relocated from dome, decision 23). */
#define DRIVE_MA_BITS         14     /* bit, absolute angle word (part)        */
/* NOTE: fsw/config.py ANGLE_BITS=12 models the GNC-side angle quantization
 * (pairing contract, unchanged); the FSW consumes the drag-ref roll ESTIMATE,
 * not this sensor — telemetry only (06 §1).                             */

/* ============================================================ slip-ring link
 * C3: +5V | GND | UART — 115200 8N1 half-duplex, CRC-16/CCITT-FALSE (06 §5). */
#define SLIP_BAUD             115200.0 /* Bd, fixed (user-set)                  */
#define SLIP_FRAME_SIZE       12       /* bytes, fixed frame both directions    */
#define SLIP_SYNC0            0xA5     /* frame sync byte 0                     */
#define SLIP_SYNC1            0xC3     /* frame sync byte 1                     */
#define SLIP_TYPE_CMD         0x01     /* dome->drive command frame             */
#define SLIP_TYPE_TELEM       0x02     /* drive->dome telemetry frame           */
#define SLIP_CRC_POLY         0x1021   /* CRC-16/CCITT-FALSE polynomial         */
#define SLIP_CRC_INIT         0xFFFF   /* CRC-16/CCITT-FALSE initial value      */
#define SLIP_TELEM_HZ         400.0    /* Hz, telemetry (drive->dome)           */
#define SLIP_CMD_HZ           50.0     /* Hz, command refresh (dome->drive)     */
#define SLIP_LINK_TIMEOUT_MS  100.0    /* ms, no-valid-frame -> safe state (F6) */

/* Slip-link frame layout (packed, little-endian; C port consumes verbatim). */
typedef struct {
    uint8_t  sync0;   /* 0xA5                                                       */
    uint8_t  sync1;   /* 0xC3                                                       */
    uint8_t  type;    /* SLIP_TYPE_CMD or SLIP_TYPE_TELEM                           */
    uint8_t  seq;     /* rolling counter (loss/duplication detection)               */
    uint8_t  payload[6]; /* mode/setpoint (cmd) or angle/rate/status (telem)        */
    uint8_t  crc_hi;  /* CRC-16/CCITT-FALSE, high byte                              */
    uint8_t  crc_lo;  /* CRC-16/CCITT-FALSE, low byte                               */
} slip_frame_t;

/* Command modes (dome->drive payload[0]) — the modes-ladder hooks (06 §5). */
#define SLIP_MODE_OFF         0   /* bridge idle, gates safe                    */
#define SLIP_MODE_COAST       1   /* neutral (motor freewheels)                 */
#define SLIP_MODE_DESPIN      2   /* torque setpoint (braking profile)          */
#define SLIP_MODE_ROLL_HOLD   3   /* servo rate setpoint (roll-hold)            */
#define SLIP_MODE_BRAKE_PROF  4   /* indexed braking profile segment            */
#define SLIP_MODE_SAFE        5   /* safe state: torque zero, chopper armed     */

#endif /* BOARD_CONFIG_H */
