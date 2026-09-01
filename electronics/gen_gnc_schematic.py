#!/usr/bin/env python3
"""Generate the PGK SIH26098 GNC-board KiCad schematic skeleton (dome D3 board).

Deterministic generator (rerun == identical output). Produces:
  electronics/gnc_board.kicad_pro
  electronics/gnc_board.kicad_sch            (root: 4 sheet instances)
  electronics/gnc_power.kicad_sch            (power tree)
  electronics/gnc_mcu.kicad_sch              (MCU + buses)
  electronics/gnc_sensors.kicad_sch          (sensors)
  electronics/gnc_comms.kicad_sch            (comms + slip ring)

Netting is label-based (every pin gets a stub + global label or a no-connect) —
the skeleton's contract is ERC + netlist, per cleansheet/06_ELECTRONICS_ARCHITECTURE.md.
Custom symbols (ICM-45686, NEO-F10N, K-LD7, ADXL1004) are minimal and flagged in HANDOFF.

Pin maps: flight_sw/board/board_config.h (verified vs ST DS12288/DS12589 Tables 12/13).
"""
import json
import math
import re
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SYMDIR = Path.home() / ".local/share/kicad-appimage/usr/share/kicad/symbols"
NS = uuid.UUID("6f6c1a2e-0000-4000-8000-50474b323032")
ROOT_UUID = str(uuid.uuid5(NS, "sheet:gnc_board.kicad_sch"))


def uid(tag):
    return str(uuid.uuid5(NS, tag))


# ---------------------------------------------------------------- sexp helpers
def find_block(text, start_idx):
    depth, i, in_str = 0, start_idx, False
    while i < len(text):
        c = text[i]
        if in_str:
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return start_idx, i + 1
        i += 1
    raise ValueError("unbalanced")


def top_symbol_block(lib, name):
    p = SYMDIR / f"{lib}.kicad_symdir" / f"{name}.kicad_sym"
    if not p.exists():
        p = SYMDIR / f"{lib}.kicad_sym"
    txt = p.read_text()
    i = txt.find(f'(symbol "{name}"')
    s, e = find_block(txt, i)
    block = txt[s:e]
    m = re.search(r'\(extends\s+"([^"]+)"\)', block)
    if m:
        parent = top_symbol_block(lib, m.group(1))
        for pm in re.finditer(r'\(property\s+"([^"]+)"', block):
            ps, pe = find_block(block, pm.start())
            prop = block[ps:pe]
            pps = parent.find(f'(property "{pm.group(1)}"')
            if pps >= 0:
                _, ppe = find_block(parent, pps)
                parent = parent[:pps] + prop + parent[ppe:]
        block = re.sub(r'\(extends\s+"[^"]+"\)', "", block, count=1)
        head = re.match(r'\(symbol\s+"[^"]+"', parent)
        block = parent.replace(head.group(0), f'(symbol "{lib}:{name}"', 1)
        # nested unit blocks must carry the resolved symbol's name
        block = block.replace(f'"{m.group(1)}_', f'"{name}_')
        return block
    return block.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)


def parse_pins(block):
    pins, cur_unit, i = [], 1, 0
    unit_re = re.compile(r'\(symbol\s+"[^"]*_(\d+)_(\d+)"')
    pin_re = re.compile(r'\(pin\s+\w+\s+\w+')
    while i < len(block):
        mu = unit_re.search(block, i)
        mp = pin_re.search(block, i)
        if mp and (not mu or mp.start() < mu.start()):
            s, e = find_block(block, mp.start())
            blk = block[s:e]
            at = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)', blk)
            nm = re.search(r'\(name\s+"([^"]*)"', blk)
            nu = re.search(r'\(number\s+"([^"]*)"', blk)
            ty = re.search(r'\(pin\s+(\w+)\s+(\w+)', blk)
            if at and nu:
                pins.append(dict(num=nu.group(1), name=(nm.group(1) if nm else ""),
                                 ptype=ty.group(1), unit=cur_unit,
                                 x=float(at.group(1)), y=float(at.group(2)),
                                 ang=float(at.group(3))))
            i = e
        elif mu:
            cur_unit = int(mu.group(1))
            i = mu.start() + len(mu.group(0))
        else:
            break
    return pins


# ---------------------------------------------------------------- custom symbols
def custom_symbol(libname, ref_prefix, desc, pins, rect):
    out = [f'\t\t(symbol "pgk:{libname}"',
           '\t\t\t(pin_names (offset 0.254))',
           '\t\t\t(exclude_from_sim no)\n\t\t\t(in_bom yes)\n\t\t\t(on_board yes)'
           '\n\t\t\t(in_pos_files yes)\n\t\t\t(duplicate_pin_numbers_are_jumpers no)',
           f'\t\t\t(property "Reference" "{ref_prefix}"\n\t\t\t\t(at 0 6.35 0)'
           '\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)'
           '\n\t\t\t\t(effects (font (size 1.27 1.27))))',
           f'\t\t\t(property "Value" "{libname}"\n\t\t\t\t(at 0 -6.35 0)'
           '\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)'
           '\n\t\t\t\t(effects (font (size 1.27 1.27))))',
           '\t\t\t(property "Footprint" ""\n\t\t\t\t(at 0 0 0)\n\t\t\t\t(hide yes)'
           '\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)'
           '\n\t\t\t\t(effects (font (size 1.27 1.27))))',
           f'\t\t\t(property "Datasheet" "{desc}"\n\t\t\t\t(at 0 0 0)\n\t\t\t\t(hide yes)'
           '\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)'
           '\n\t\t\t\t(effects (font (size 1.27 1.27))))',
           '\t\t\t(property "Description" "Custom minimal symbol — PGK skeleton (flagged)"'
           '\n\t\t\t\t(at 0 0 0)\n\t\t\t\t(hide yes)'
           '\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)'
           '\n\t\t\t\t(effects (font (size 1.27 1.27))))',
           f'\t\t\t(symbol "{libname}_0_1"'
           f'\n\t\t\t\t(rectangle\n\t\t\t\t\t(start {rect[0]} {rect[1]})'
           f'\n\t\t\t\t\t(end {rect[2]} {rect[3]})'
           '\n\t\t\t\t\t(stroke (width 0.254) (type default))'
           '\n\t\t\t\t\t(fill (type background)))\n\t\t\t)',
           f'\t\t\t(symbol "{libname}_1_1"']
    for num, name, ptype, x, y, ang in pins:
        out.append(f'\t\t\t\t(pin {ptype} line\n\t\t\t\t\t(at {x} {y} {ang})'
                   '\n\t\t\t\t\t(length 2.54)'
                   f'\n\t\t\t\t\t(name "{name}" (effects (font (size 1.27 1.27))))'
                   f'\n\t\t\t\t\t(number "{num}" (effects (font (size 1.27 1.27)))))')
    out.append('\t\t\t)\n\t\t)')
    return "\n".join(out)


CUSTOM = {
    "ICM-45686": custom_symbol("ICM-45686", "U", "TDK ICM-45686 IMU (custom minimal)", [
        ("1", "SCLK", "input", -10.16, 5.08, 0),
        ("2", "SDI", "input", -10.16, 2.54, 0),
        ("3", "SDO", "output", -10.16, 0.0, 0),
        ("4", "CS", "input", -10.16, -2.54, 0),
        ("5", "INT1", "output", 10.16, 5.08, 180),
        ("6", "VDD", "power_in", 0, 10.16, 270),
        ("7", "VDDIO", "power_in", 10.16, 2.54, 180),
        ("8", "GND", "power_in", 0, -7.62, 90),
    ], (-10.16, -7.62, 10.16, 10.16)),
    "NEO-F10N": custom_symbol("NEO-F10N", "U", "u-blox NEO-F10N GNSS (custom minimal)", [
        ("1", "VCC", "power_in", -10.16, 7.62, 0),
        ("2", "GND", "power_in", 0, -10.16, 90),
        ("3", "TXD", "output", 10.16, 7.62, 180),
        ("4", "RXD", "input", 10.16, 5.08, 180),
        ("5", "TIMEPULSE", "output", 10.16, 2.54, 180),
        ("6", "V_BCKP", "power_in", -10.16, 5.08, 0),
        ("7", "LNA_EN", "input", -10.16, 2.54, 0),
        ("8", "RF_IN", "input", -10.16, -5.08, 0),
    ], (-10.16, -10.16, 10.16, 10.16)),
    "K-LD7": custom_symbol("K-LD7", "U", "RFbeam K-LD7 24 GHz radar (custom minimal)", [
        ("1", "VCC", "power_in", -10.16, 5.08, 0),
        ("2", "GND", "power_in", 0, -7.62, 90),
        ("3", "TXD", "output", 10.16, 5.08, 180),
        ("4", "RXD", "input", 10.16, 2.54, 180),
    ], (-10.16, -7.62, 10.16, 10.16)),
    "ADXL1004": custom_symbol("ADXL1004", "U", "ADI ADXL1004 accel signature (custom minimal)", [
        ("1", "VDD", "power_in", -10.16, 5.08, 0),
        ("2", "GND", "power_in", 0, -7.62, 90),
        ("3", "OUT", "output", 10.16, 5.08, 180),
    ], (-10.16, -7.62, 10.16, 10.16)),
    "TLV7031": custom_symbol("TLV7031", "U", "TI TLV7031 nanopower comparator (custom minimal)", [
        ("1", "OUT", "output", 10.16, 2.54, 180),
        ("2", "INP", "input", -10.16, 2.54, 0),
        ("3", "INN", "input", -10.16, 0.0, 0),
        ("4", "VPLUS", "power_in", 0, 7.62, 270),
        ("5", "VMINUS", "power_in", 0, -5.08, 90),
    ], (-10.16, -5.08, 10.16, 7.62)),
}


# ---------------------------------------------------------------- sheet emitter
class Sch:
    def __init__(self, fname, page, title):
        self.fname = fname
        self.page = page
        self.uuid = uid(f"sheet:{fname}")
        self.title = title
        self.libs = {}
        self.items = []

    def add_lib(self, lib_id, symtxt):
        self.libs[lib_id] = symtxt

    def ensure_lib(self, lib_id):
        if lib_id in self.libs:
            return
        lib, name = lib_id.split(":", 1)
        self.libs[lib_id] = top_symbol_block(lib, name)

    def place(self, lib_id, ref, value, x, y, rot=0, footprint=None, unit=1):
        # snap to the 1.27 mm connection grid (rotations unsupported: rot must be 0)
        assert rot == 0, "generator supports rot=0 only"
        x = round(round(x / 1.27) * 1.27, 3)
        y = round(round(y / 1.27) * 1.27, 3)
        self.ensure_lib(lib_id)
        pins = [p for p in parse_pins(self.libs[lib_id]) if p["unit"] == unit]
        su = uid(f"sym:{self.fname}:{ref}:{unit}")
        lines = [f'\t(symbol\n\t\t(lib_id "{lib_id}")\n\t\t(at {x} {y} {rot})'
                 f'\n\t\t(unit {unit})\n\t\t(body_style 1)'
                 '\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)'
                 '\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n\t\t(dnp no)'
                 f'\n\t\t(uuid "{su}")']
        fx, fy = x + 2.54, y - 3.81
        for pn, pv, py in (("Reference", ref, 0), ("Value", value, 2.54)):
            lines.append(f'\t\t(property "{pn}" "{pv}"\n\t\t\t(at {fx} {fy + py} 0)'
                         '\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)'
                         '\n\t\t\t(effects (font (size 1.27 1.27))))')
        for pn, pv in (("Footprint", footprint or ""), ("Datasheet", ""), ("Description", "")):
            lines.append(f'\t\t(property "{pn}" "{pv}"\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)'
                         '\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)'
                         '\n\t\t\t(effects (font (size 1.27 1.27))))')
        lines.append('\t\t(instances\n\t\t\t(project "gnc_board"'
                     f'\n\t\t\t\t(path "/{ROOT_UUID}/{self.uuid}"'
                     f'\n\t\t\t\t\t(reference "{ref}")'
                     f'\n\t\t\t\t\t(unit {unit})\n\t\t\t\t)\n\t\t)\n\t)\n\t)')
        self.items.append("\n".join(lines))
        pinmap = {}
        for p in pins:
            pinmap[p["num"]] = dict(x=x + p["x"], y=y - p["y"], ang=p["ang"], name=p["name"])
        return pinmap

    def wire(self, x1, y1, x2, y2):
        self.items.append(f'\t(wire\n\t\t(pts (xy {x1} {y1}) (xy {x2} {y2}))'
                          '\n\t\t(stroke (width 0) (type solid))'
                          f'\n\t\t(uuid "{uid(f"wire:{self.fname}:{len(self.items)}")}"))')

    def nc(self, x, y):
        self.items.append(f'\t(no_connect\n\t\t(at {x} {y})'
                          f'\n\t\t(uuid "{uid(f"nc:{self.fname}:{len(self.items)}")}"))')

    def glabel(self, x, y, name, angle=0):
        just = "right" if angle == 180 else "left"
        self.items.append(
            f'\t(global_label "{name}"\n\t\t(shape passive)\n\t\t(at {x} {y} {angle})'
            '\n\t\t(fields_autoplaced yes)'
            f'\n\t\t(effects (font (size 1.27 1.27)) (justify {just}))'
            f'\n\t\t(uuid "{uid(f"gl:{self.fname}:{name}:{len(self.items)}")}")'
            '\n\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}"'
            f'\n\t\t\t(at {x} {y} 0)\n\t\t\t(hide yes)'
            f'\n\t\t\t(effects (font (size 1.27 1.27)) (justify {just})))'
            '\n\t\t)')

    def pin_net(self, pin, net, stub=2.54):
        th = math.radians(pin["ang"] + 180.0)
        dx, dy = math.cos(th) * stub, -math.sin(th) * stub
        ex, ey = round(pin["x"] + dx, 3), round(pin["y"] + dy, 3)
        self.wire(pin["x"], pin["y"], ex, ey)
        self.glabel(ex, ey, net, 0 if dx >= 0 else 180)

    def pin_nc(self, pin):
        self.nc(pin["x"], pin["y"])

    def render(self):
        out = ['(kicad_sch', '\t(version 20260101)', '\t(generator "eeschema")',
               '\t(generator_version "10.0")', f'\t(uuid "{self.uuid}")', '\t(paper "A4")',
               '\t(title_block', f'\t\t(title "{self.title}")', '\t\t(date "2026-08-31")',
               '\t\t(rev "1.0")', '\t\t(company "PGK SIH26098 clean-sheet"))',
               '\t(lib_symbols']
        out.extend(self.libs.values())
        out.append('\t)')
        out.extend(self.items)
        out.append(f'\t(sheet_instances\n\t\t(path "/" (page "{self.page}"))\n\t)')
        out.append('\t(embedded_fonts no)')
        out.append(')')
        return "\n".join(out) + "\n"


def net_all(s, pm, num, net):
    s.pin_net(pm[num], net)


# ---------------------------------------------------------------- sheet contents
def sheet_power(s: Sch):
    pL1 = s.place("Device:FerriteBead", "L1", "600R@100MHz", 60, 50,
                  footprint="Inductor_SMD:L_0603_1608Metric")
    net_all(s, pL1, "1", "+5V")
    net_all(s, pL1, "2", "+5V_F")
    pD1 = s.place("Diode:SMAJ5.0A", "D1", "SMAJ5.0A", 80, 60, footprint="Diode_SMD:D_SMA")
    net_all(s, pD1, "1", "+5V_F")
    net_all(s, pD1, "2", "GND")
    pC1 = s.place("Device:C_Polarized", "C1", "470u/10V", 95, 60,
                  footprint="Capacitor_SMD:CP_Elec_8x10.5")
    net_all(s, pC1, "1", "+5V_F")
    net_all(s, pC1, "2", "GND")
    pU2 = s.place("Regulator_Switching:TPS62933", "U2", "TPS62933DRLR", 110, 50,
                  footprint="Package_TO_SOT_SMD:SOT-583-8")
    net_all(s, pU2, "3", "+5V_F")          # VIN
    net_all(s, pU2, "2", "+5V_F")          # EN tied high (VIN-present enable)
    net_all(s, pU2, "4", "GND")            # GND
    net_all(s, pU2, "5", "TPS_SW")         # SW
    net_all(s, pU2, "8", "+3V3")           # FB senses the rail
    net_all(s, pU2, "6", "TPS_BST")        # BST
    s.pin_nc(pU2["1"])                     # RT
    s.pin_nc(pU2["7"])                     # SS
    pC11 = s.place("Device:C", "C11", "22n BST-SW", 135, 65,
                   footprint="Capacitor_SMD:C_0402_1005Metric")
    net_all(s, pC11, "1", "TPS_BST")
    net_all(s, pC11, "2", "TPS_SW")
    pL2 = s.place("Device:L", "L2", "2.2uH", 150, 50,
                  footprint="Inductor_SMD:L_0805_2012Metric")
    net_all(s, pL2, "1", "TPS_SW")
    net_all(s, pL2, "2", "+3V3")
    pC2 = s.place("Device:C", "C2", "10u", 125, 80, footprint="Capacitor_SMD:C_0603_1608Metric")
    net_all(s, pC2, "1", "+5V_F")
    net_all(s, pC2, "2", "GND")
    pC3 = s.place("Device:C", "C3", "22u", 155, 80, footprint="Capacitor_SMD:C_0603_1608Metric")
    net_all(s, pC3, "1", "+3V3")
    net_all(s, pC3, "2", "GND")
    pU3 = s.place("Regulator_Linear:TLV75730PDBV", "U3", "TLV75730PDBV", 175, 50,
                  footprint="Package_TO_SOT_SMD:SOT-23-5")
    net_all(s, pU3, "1", "+5V_F")          # IN
    net_all(s, pU3, "2", "GND")            # GND
    net_all(s, pU3, "3", "+5V_F")          # EN tie-high
    s.pin_nc(pU3["4"])                     # NC
    net_all(s, pU3, "5", "+3V3_RF")        # OUT
    pC4 = s.place("Device:C", "C4", "10u", 200, 80, footprint="Capacitor_SMD:C_0603_1608Metric")
    net_all(s, pC4, "1", "+3V3_RF")
    net_all(s, pC4, "2", "GND")
    for i, net in enumerate(["+5V", "+5V_F", "+3V3", "GND"]):
        pf = s.place("power:PWR_FLAG", f"#FLG0{i+1}", "PWR_FLAG", 40 + i * 12.7, 100, unit=0)
        s.pin_net(pf["1"], net)
    # (+3V3_RF needs no flag: TLV75730P OUT is a power-output pin driving it)


def sheet_mcu(s: Sch):
    pin_nets = {
        1: "+3V3", 5: "OSC_IN", 6: "OSC_OUT", 7: "NRST", 12: "SETB_AN",
        14: "PROX_TX", 17: "PROX_RX", 18: "IMU_CS", 19: "IMU_SCK",
        20: "IMU_MISO", 21: "IMU_MOSI", 22: "IMU_DRDY", 25: "SETB_TRIG",
        30: "SLIP_UART", 37: "LNA_EN", 43: "GNSS_TX", 44: "GNSS_RX",
        49: "SWDIO", 50: "SWCLK", 51: "GNSS_PPS",
        56: "FL_SCK", 57: "FL_MISO", 58: "FL_MOSI", 59: "FL_CS",
    }
    power = {15: "GND", 27: "GND", 31: "GND", 47: "GND", 63: "GND",
             16: "+3V3", 32: "+3V3", 48: "+3V3", 64: "+3V3",
             28: "+3V3_RF", 29: "+3V3_RF"}
    pU = s.place("MCU_ST_STM32G4:STM32G474RETx", "U1", "STM32G474RET6", 150, 100,
                 footprint="Package_QFP:LQFP-64_10x10mm_P0.5mm")
    for num, pin in pU.items():
        n = int(num)
        if n in pin_nets:
            s.pin_net(pin, pin_nets[n])
        elif n in power:
            s.pin_net(pin, power[n])
        else:
            s.pin_nc(pin)
    pY1 = s.place("Device:Crystal", "Y1", "24MHz", 80, 100,
                  footprint="Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
    net_all(s, pY1, "1", "OSC_IN")
    net_all(s, pY1, "2", "OSC_OUT")
    pC5 = s.place("Device:C", "C5", "12p", 70, 115, footprint="Capacitor_SMD:C_0402_1005Metric")
    net_all(s, pC5, "1", "OSC_IN")
    net_all(s, pC5, "2", "GND")
    pC6 = s.place("Device:C", "C6", "12p", 90, 115, footprint="Capacitor_SMD:C_0402_1005Metric")
    net_all(s, pC6, "1", "OSC_OUT")
    net_all(s, pC6, "2", "GND")
    pJ6 = s.place("Connector_Generic:Conn_01x04", "J6", "SWD", 230, 100,
                  footprint="Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical")
    for num, net in [("1", "SWDIO"), ("2", "SWCLK"), ("3", "NRST"), ("4", "GND")]:
        net_all(s, pJ6, num, net)
    for i, (ref, net) in enumerate([("C7", "+3V3"), ("C8", "+3V3"), ("C9", "+3V3"),
                                    ("C10", "+3V3_RF")]):
        pc = s.place("Device:C", ref, "100n", 60 + i * 15, 135,
                     footprint="Capacitor_SMD:C_0402_1005Metric")
        net_all(s, pc, "1", net)
        net_all(s, pc, "2", "GND")


def sheet_sensors(s: Sch):
    s.add_lib("pgk:ICM-45686", CUSTOM["ICM-45686"])
    s.add_lib("pgk:NEO-F10N", CUSTOM["NEO-F10N"])
    s.add_lib("pgk:K-LD7", CUSTOM["K-LD7"])
    s.add_lib("pgk:ADXL1004", CUSTOM["ADXL1004"])
    s.add_lib("pgk:TLV7031", CUSTOM["TLV7031"])
    pU4 = s.place("pgk:ICM-45686", "U4", "ICM-45686", 90, 50,
                  footprint="Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm")
    for num, net in [("1", "IMU_SCK"), ("2", "IMU_MOSI"), ("3", "IMU_MISO"),
                     ("4", "IMU_CS"), ("5", "IMU_DRDY"), ("6", "+3V3"),
                     ("7", "+3V3"), ("8", "GND")]:
        net_all(s, pU4, num, net)
    pU5 = s.place("Memory_Flash:W25Q128JVS", "U5", "W25Q128JVSIQ", 90, 100,
                  footprint="Package_SO:SOIC-8_5.3x5.3mm_P1.27mm")
    for num, net in [("1", "FL_CS"), ("2", "FL_MISO"), ("5", "FL_MOSI"), ("6", "FL_SCK"),
                     ("4", "GND"), ("8", "+3V3")]:
        net_all(s, pU5, num, net)
    # WP#/HOLD# pulled high through 10k (passive↔bidirectional is ERC-clean)
    pR7 = s.place("Device:R", "R7", "10k", 115, 125, footprint="Resistor_SMD:R_0402_1005Metric")
    net_all(s, pR7, "1", "+3V3")
    net_all(s, pR7, "2", "FL_WP")
    net_all(s, pU5, "3", "FL_WP")
    pR8 = s.place("Device:R", "R8", "10k", 135, 125, footprint="Resistor_SMD:R_0402_1005Metric")
    net_all(s, pR8, "1", "+3V3")
    net_all(s, pR8, "2", "FL_HOLD")
    net_all(s, pU5, "7", "FL_HOLD")
    pU6 = s.place("pgk:NEO-F10N", "U6", "NEO-F10N-00B", 90, 160, footprint="")
    for num, net in [("1", "+3V3_RF"), ("2", "GND"), ("3", "GNSS_RX"), ("4", "GNSS_TX"),
                     ("5", "GNSS_PPS"), ("6", "+3V3_RF"), ("7", "LNA_EN"),
                     ("8", "GNSS_ANT")]:
        net_all(s, pU6, num, net)
    pU7 = s.place("pgk:K-LD7", "U7", "K-LD7-RFB-00H-01", 170, 50, footprint="")
    for num, net in [("1", "+5V"), ("2", "GND"), ("3", "PROX_RX"), ("4", "PROX_TX")]:
        net_all(s, pU7, num, net)
    pU8 = s.place("pgk:ADXL1004", "U8", "ADXL1004", 170, 100,
                  footprint="Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm")
    for num, net in [("1", "+3V3_RF"), ("2", "GND"), ("3", "SETB_AN")]:
        net_all(s, pU8, num, net)
    pU9 = s.place("pgk:TLV7031", "U9", "TLV7031", 170, 160,
                  footprint="Package_TO_SOT_SMD:SOT-23-5")
    net_all(s, pU9, "1", "SETB_TRIG")      # OUT
    net_all(s, pU9, "2", "SETB_AN")        # IN+
    net_all(s, pU9, "3", "SETB_THR")       # IN-
    net_all(s, pU9, "4", "+3V3_RF")        # V+
    net_all(s, pU9, "5", "GND")            # V-
    pR3 = s.place("Device:R", "R3", "100k", 200, 150, footprint="Resistor_SMD:R_0402_1005Metric")
    net_all(s, pR3, "1", "+3V3_RF")
    net_all(s, pR3, "2", "SETB_THR")
    pR4 = s.place("Device:R", "R4", "100k", 200, 170, footprint="Resistor_SMD:R_0402_1005Metric")
    net_all(s, pR4, "1", "SETB_THR")
    net_all(s, pR4, "2", "GND")
    pJ2 = s.place("Connector_Generic:Conn_01x02", "J2", "GNSS patch", 40, 160,
                  footprint="Connector_Coaxial:U.FL_Hirose_U.FL-R-SMT-1_Vertical")
    net_all(s, pJ2, "1", "GNSS_ANT")
    net_all(s, pJ2, "2", "GND")


def sheet_comms(s: Sch):
    pJ1 = s.place("Connector_Generic:Conn_01x03", "J1", "Slip ring C3", 60, 70,
                  footprint="Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical")
    net_all(s, pJ1, "1", "+5V")
    net_all(s, pJ1, "2", "GND")
    net_all(s, pJ1, "3", "SLIP_RING")
    pR5 = s.place("Device:R", "R5", "100R", 100, 65,
                  footprint="Resistor_SMD:R_0402_1005Metric")
    net_all(s, pR5, "1", "SLIP_RING")
    net_all(s, pR5, "2", "SLIP_PROT1")
    pR6 = s.place("Device:R", "R6", "100R", 135, 65,
                  footprint="Resistor_SMD:R_0402_1005Metric")
    net_all(s, pR6, "1", "SLIP_PROT2")
    net_all(s, pR6, "2", "SLIP_UART")
    pU10 = s.place("Power_Protection:USBLC6-2SC6", "U10", "USBLC6-2SC6", 115, 95,
                   footprint="Package_TO_SOT_SMD:SOT-23-6")
    for num, net in [("1", "SLIP_PROT1"), ("6", "SLIP_PROT1"), ("3", "SLIP_PROT2"),
                     ("4", "SLIP_PROT2"), ("2", "GND"), ("5", "+3V3")]:
        net_all(s, pU10, num, net)


def write_pro():
    # project symbol library for the custom parts (satisfies lib_symbol_issues)
    lib = ('(kicad_symbol_lib\n\t(version 20251024)\n\t(generator "kicad_symbol_editor")'
           '\n\t(generator_version "10.0")\n'
           + "\n".join(CUSTOM[n] for n in CUSTOM) + '\n)\n')
    (ROOT / "pgk.kicad_sym").write_text(lib)
    (ROOT / "sym-lib-table").write_text(
        '(sym_lib_table\n  (version 7)\n  (lib (name "pgk")(type "KiCad")'
        '(uri "${KIPRJMOD}/pgk.kicad_sym")(options "")'
        '(descr "PGK SIH26098 custom minimal symbols (flagged in HANDOFF)"))\n)\n')
    sheets = [[ROOT_UUID, "Root"], [uid("sheet:gnc_power.kicad_sch"), "Power"],
              [uid("sheet:gnc_mcu.kicad_sch"), "MCU+buses"],
              [uid("sheet:gnc_sensors.kicad_sch"), "Sensors"],
              [uid("sheet:gnc_comms.kicad_sch"), "Comms+slip"]]
    pro = {
        "board": {"design_settings": {}, "layer_presets": [], "viewports": []},
        "boards": [],
        "cvpcb": {"equivalence_files": []},
        "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
        "meta": {"filename": "gnc_board.kicad_pro", "version": 3},
        "net_settings": {"classes": []},
        "pcbnew": {"page_layout_descr_file": ""},
        "schematic": {"annotate_start_num": 0, "legacy_lib_dir": "", "legacy_lib_list": []},
        "sheets": sheets,
        "text_variables": {},
    }
    (ROOT / "gnc_board.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n")


def main():
    power = Sch("gnc_power.kicad_sch", 2, "GNC board — power tree")
    mcu = Sch("gnc_mcu.kicad_sch", 3, "GNC board — MCU + buses")
    sensors = Sch("gnc_sensors.kicad_sch", 4, "GNC board — sensors")
    comms = Sch("gnc_comms.kicad_sch", 5, "GNC board — comms + slip ring")
    sheet_power(power)
    sheet_mcu(mcu)
    sheet_sensors(sensors)
    sheet_comms(comms)
    for s in (power, mcu, sensors, comms):
        (ROOT / s.fname).write_text(s.render())
    sheets = [(power, "Power", 60, 40), (mcu, "MCU+buses", 120, 40),
              (sensors, "Sensors", 60, 90), (comms, "Comms+slip", 120, 90)]
    root = ['(kicad_sch', '\t(version 20260101)', '\t(generator "eeschema")',
            '\t(generator_version "10.0")', f'\t(uuid "{ROOT_UUID}")', '\t(paper "A4")',
            '\t(title_block',
            '\t\t(title "PGK SIH26098 — GNC board (dome D3) schematic skeleton")',
            '\t\t(date "2026-08-31")', '\t\t(rev "1.0")',
            '\t\t(company "PGK SIH26098 clean-sheet — see cleansheet/06_ELECTRONICS_ARCHITECTURE.md"))',
            '\t(lib_symbols)', '']
    for s, name, x, y in sheets:
        root.append(f'\t(sheet\n\t\t(at {x} {y})\n\t\t(size 40 30)'
                    '\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)'
                    '\n\t\t(stroke (width 0) (type solid))\n\t\t(fill (color 0 0 0 0))'
                    f'\n\t\t(uuid "{s.uuid}")'
                    f'\n\t\t(property "Sheetname" "{name}"\n\t\t\t(at {x} {y - 1.2} 0)'
                    '\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)'
                    '\n\t\t\t(effects (font (size 1.524 1.524)) (justify left bottom)))'
                    f'\n\t\t(property "Sheetfile" "{s.fname}"\n\t\t\t(at {x} {y + 30.6} 0)'
                    '\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)'
                    '\n\t\t\t(effects (font (size 1.524 1.524)) (justify left top)))'
                    '\n\t\t(instances\n\t\t\t(project "gnc_board"'
                    f'\n\t\t\t\t(path "/{ROOT_UUID}"\n\t\t\t\t\t(page "{s.page}"))'
                    '\n\t\t\t)\n\t)\n\t)')
    root.append('\t(sheet_instances\n\t\t(path "/" (page "1"))\n\t)')
    root.append('\t(embedded_fonts no)')
    root.append(')')
    (ROOT / "gnc_board.kicad_sch").write_text("\n".join(root) + "\n")
    write_pro()
    print("wrote gnc_board.kicad_sch + 4 subsheets + gnc_board.kicad_pro")


if __name__ == "__main__":
    main()
