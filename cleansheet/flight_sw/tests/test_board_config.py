"""Board-config parity test: flight_sw/board/board_config.h must agree with
fsw/config.py on every deployment task rate + GNSS latency (the board↔FSW
contract — companion to the sim↔FSW pairing contract in test_config.py).
Also asserts the slip-ring protocol constants and pin-map presence per
cleansheet/06_ELECTRONICS_ARCHITECTURE.md §3.2/§4/§5."""
import math
import re
from pathlib import Path

import pytest

import fsw.config as C

BOARD_DIR = Path(__file__).resolve().parent.parent / "board"
HEADER = BOARD_DIR / "board_config.h"


def _defines():
    text = HEADER.read_text()
    defs = {}
    for m in re.finditer(r"^#define\s+(\w+)\s+([^\s/*]+)", text, re.M):
        defs[m.group(1)] = m.group(2)
    return defs


@pytest.fixture(scope="module")
def defs():
    return _defines()


def _num(defs, name):
    assert name in defs, f"missing #define {name}"
    return float(defs[name].rstrip("fF"))


# ---------------------------------------------------------------- rates == config.py
def test_task_rates_match_config(defs):
    assert _num(defs, "BOARD_SERVO_HZ") == C.SERVO_HZ
    assert _num(defs, "BOARD_SENSOR_HZ") == C.SENSOR_HZ
    assert _num(defs, "BOARD_NAV_PREDICT_HZ") == C.NAV_PREDICT_HZ
    assert _num(defs, "BOARD_GNSS_HZ") == C.GNSS_HZ
    assert _num(defs, "BOARD_GUIDE_HZ") == C.GUIDE_HZ


def test_gnss_latency_matches_config(defs):
    assert _num(defs, "BOARD_GNSS_LAT") == C.GNSS_LAT


def test_imu_rate_matches_config(defs):
    assert _num(defs, "BOARD_IMU_HZ") == pytest.approx(1.0 / C.IMU_DT)


def test_systick_superset_of_rates(defs):
    systick = _num(defs, "BOARD_SYSTICK_HZ")
    for rate in (C.SERVO_HZ, C.NAV_PREDICT_HZ, C.SENSOR_HZ, C.GNSS_HZ, C.GUIDE_HZ):
        assert systick % rate == pytest.approx(0.0)


# ---------------------------------------------------------------- slip-ring protocol
def test_slip_protocol_constants(defs):
    assert int(defs["SLIP_FRAME_SIZE"]) == 12
    assert int(defs["SLIP_SYNC0"], 0) == 0xA5
    assert int(defs["SLIP_SYNC1"], 0) == 0xC3
    assert int(defs["SLIP_CRC_POLY"], 0) == 0x1021
    assert int(defs["SLIP_CRC_INIT"], 0) == 0xFFFF
    assert _num(defs, "SLIP_TELEM_HZ") == 400.0
    assert _num(defs, "SLIP_CMD_HZ") == 50.0
    assert _num(defs, "SLIP_LINK_TIMEOUT_MS") == 100.0
    assert _num(defs, "SLIP_BAUD") == 115200.0


def test_slip_frame_struct_present():
    text = HEADER.read_text()
    assert "typedef struct" in text and "slip_frame_t" in text
    # every frame field named in 06 §5 exists in the struct (uint8_t typed)
    for field in ("sync0", "sync1", "type", "seq", "payload", "crc_hi", "crc_lo"):
        assert re.search(rf"uint8_t\s+{field}\b", text), f"struct field {field} missing"


# ---------------------------------------------------------------- pin maps
def test_dome_pin_map_complete(defs):
    pins = {k: defs[k] for k in defs if k.startswith("DOME_PIN_")}
    required = {
        "DOME_PIN_IMU_SCK": "PA5", "DOME_PIN_IMU_MISO": "PA6",
        "DOME_PIN_IMU_MOSI": "PA7", "DOME_PIN_IMU_CS": "PA4",
        "DOME_PIN_IMU_DRDY": "PC4", "DOME_PIN_FL_SCK": "PB3",
        "DOME_PIN_FL_MISO": "PB4", "DOME_PIN_FL_MOSI": "PB5",
        "DOME_PIN_FL_CS": "PB6", "DOME_PIN_GNSS_TX": "PA9",
        "DOME_PIN_GNSS_RX": "PA10", "DOME_PIN_GNSS_PPS": "PA15",
        "DOME_PIN_PROX_TX": "PA2", "DOME_PIN_PROX_RX": "PA3",
        "DOME_PIN_SLIP_UART": "PB10", "DOME_PIN_SETB_AN": "PA0",
        "DOME_PIN_SETB_TRIG": "PB1", "DOME_PIN_SWDIO": "PA13",
        "DOME_PIN_SWCLK": "PA14",
    }
    for name, pin in required.items():
        assert pins.get(name, "").strip('"') == pin, f"{name}: got {pins.get(name)!r}, want {pin}"


def test_dome_pins_unique(defs):
    pins = [defs[k].strip('"') for k in defs if k.startswith("DOME_PIN_")]
    assert len(pins) == len(set(pins)), "duplicate dome pin assignment"


def test_drive_pin_map_complete(defs):
    pins = {k: defs[k] for k in defs if k.startswith("DRIVE_PIN_")}
    required = {
        "DRIVE_PIN_PWM_CH1": "PA8", "DRIVE_PIN_PWM_CH2": "PA9",
        "DRIVE_PIN_PWM_CH3": "PA10", "DRIVE_PIN_PWM_CH1N": "PB13",
        "DRIVE_PIN_PWM_CH2N": "PB14", "DRIVE_PIN_PWM_CH3N": "PB15",
        "DRIVE_PIN_MA_SCK": "PB3", "DRIVE_PIN_MA_MISO": "PB4",
        "DRIVE_PIN_MA_MOSI": "PB5", "DRIVE_PIN_MA_CS": "PA4",
        "DRIVE_PIN_ADC_IU": "PA0", "DRIVE_PIN_ADC_IV": "PA1",
        "DRIVE_PIN_ADC_IW": "PB0", "DRIVE_PIN_ADC_VBUS": "PB1",
        "DRIVE_PIN_ADC_NTC": "PA5", "DRIVE_PIN_CHOP_PWM": "PA6",
        "DRIVE_PIN_HALL_U": "PB6", "DRIVE_PIN_HALL_V": "PB7",
        "DRIVE_PIN_HALL_W": "PB8", "DRIVE_PIN_SLIP_UART": "PA2",
        "DRIVE_PIN_NFAULT": "PA7", "DRIVE_PIN_EN_GATE": "PB12",
        "DRIVE_PIN_SWDIO": "PA13", "DRIVE_PIN_SWCLK": "PA14",
    }
    for name, pin in required.items():
        assert pins.get(name, "").strip('"') == pin, f"{name}: got {pins.get(name)!r}, want {pin}"


def test_drive_pins_unique(defs):
    pins = [defs[k].strip('"') for k in defs if k.startswith("DRIVE_PIN_")]
    assert len(pins) == len(set(pins)), "duplicate drive pin assignment"


# ---------------------------------------------------------------- clock plans
def test_clock_plans(defs):
    for osc, cpu in (("DOME_OSC_HZ", "BOARD_DOME_CPU_HZ"),
                     ("DRIVE_OSC_HZ", "BOARD_DRIVE_CPU_HZ")):
        assert _num(defs, osc) == 24_000_000.0
        assert _num(defs, cpu) == 170_000_000.0
    # PLL math: 24 MHz / 6 * 85 / 2 = 170 MHz
    assert 24e6 / 6 * 85 / 2 == pytest.approx(170e6)
    assert _num(defs, "DRIVE_PWM_HZ") == 15000.0
