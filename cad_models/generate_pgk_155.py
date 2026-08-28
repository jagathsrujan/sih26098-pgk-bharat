# ============================================================================
# SIH26098 - PGK public-architecture demonstrator - INERT / BENCH ONLY
# ----------------------------------------------------------------------------
# Active baseline: a printed 155 mm shell mock-up with a common four-canard
# carrier, coaxial bearing isolation, a shell-to-carrier alternator concept,
# and one low-voltage torque-emulator placeholder. This is an educational
# model, not a flight article and not a functional fuze.
#
# Important architecture boundary:
#   * The projectile/outer housing is the spin-side frame.
#   * One inner carrier holds all four fixed canards.
#   * The carrier is free to rotate relative to the outer housing.
#   * The generator and torque element bridge those two frames.
#
# The exact production M1156 internal stack is not public. This file is a
# clearly labelled, non-launchable visual/mechanical demonstrator.
#
# Fit: uses a nonfunctional slip-fit adapter for the existing printed shell
# mock-up. No live-compatible fuze interface, energetic part, or firing path.
# Run: freecadcmd generate_pgk_155.py
# Outputs: out_pgk/pgk_assembly.FCStd, pgk_exploded.FCStd, STEP, STL parts
# ============================================================================

import os
import math
import json

import FreeCAD as App
import Part
import MeshPart
import Import


OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_pgk")

# ---------------------------------------------------------------- dimensions
# These are display dimensions inherited from the printed shell mock-up, not
# a claim about production M1156 hardware.
R_BODY = 28.0
R_ID = 25.5
Z_SHANK = 90.0
Z_HOUSING0 = 92.0
Z_HOUSING1 = 196.0
Z_NOSE = 228.0

R_CARRIER = 22.2
R_CARRIER_ID = 17.5
Z_CARRIER0 = 132.0
Z_CARRIER1 = 188.0
R_BEARING_OUTER = 24.8
R_BEARING_INNER = 22.6
BEARING_H = 5.0
Z_FRONT_BEARING = 128.0
Z_REAR_BEARING = 187.0

Z_CANARD = 157.0
FIN_TIP = 75.5
FIN_THICK = 2.8

doc = App.newDocument("PGK_Assembly")
docE = App.newDocument("PGK_Exploded")
PARTS = []


def add(name, shape, explode=(0, 0, 0)):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape

    exploded = shape.copy()
    exploded.translate(App.Vector(*explode))
    obj_e = docE.addObject("Part::Feature", name)
    obj_e.Shape = exploded

    PARTS.append((name, obj))
    return obj


def box(x0, y0, z0, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, App.Vector(x0, y0, z0))


def cyl(radius, height, p=(0, 0, 0), direction=(0, 0, 1)):
    return Part.makeCylinder(radius, height, App.Vector(*p), App.Vector(*direction))


def ring(outer, inner, height, z):
    return cyl(outer, height, (0, 0, z)).cut(cyl(inner, height, (0, 0, z)))


def fuse(*shapes):
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    return result.removeSplitter()


def compound(*shapes):
    return Part.makeCompound(list(shapes))


def polar_xy(radius, angle_deg):
    angle = math.radians(angle_deg)
    return radius * math.cos(angle), radius * math.sin(angle)


# ============================================================ 1. BASE / POWER
# A dummy mechanical adapter fits the existing printed shell. It is deliberately
# a slip-fit display part rather than a reproduction of a live fuze interface.
profile = [
    (24.8, 0.0), (24.8, 88.0), (28.0, 88.0), (28.0, 92.0),
    (25.5, 92.0), (25.5, 90.0), (21.0, 90.0), (21.0, 75.0),
    (19.0, 75.0), (19.0, 73.0), (21.0, 73.0), (21.0, 2.0),
    (0.0, 2.0), (0.0, 0.0),
]
profile_edges = []
for index in range(len(profile)):
    a = profile[index]
    b = profile[(index + 1) % len(profile)]
    profile_edges.append(
        Part.makeLine(App.Vector(a[0], 0, a[1]), App.Vector(b[0], 0, b[1]))
    )
shank = Part.Face(Part.Wire(profile_edges)).revolve(
    App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360
)
shank = shank.cut(cyl(2.5, 4.0, (0, 0, -1)))
add("01_DemoShankAdapter", shank, (0, 0, -120))

# A supercapacitor placeholder represents the display power store. It is not a
# battery and is not connected to any firing or energetic function.
supercap = fuse(cyl(8.0, 46.0, (0, 0, 12)), cyl(9.0, 2.0, (0, 0, 10)))
add("02_Supercapacitor_Display", supercap, (0, 0, -165))

power_board = fuse(cyl(20.0, 1.6, (0, 0, 72)), box(-5, -4, 73.6, 10, 8, 2.5))
add("03_PowerConditioning_PCB", power_board, (0, 0, -145))


# ============================================ 2. INERT STATUS INDICATOR
# A manually visible slider and empty alignment hole communicate the idea of a
# safe/armed status indicator without containing any initiator or firing path.
status_slider = box(-11, -6, 98, 22, 12, 7)
status_slider = status_slider.cut(cyl(3.0, 7.0, (-7, 0, 98)))
status_slider = fuse(status_slider, cyl(1.8, 20.0, (0, 6, 101.5), (0, 1, 0)))
add("04_Inert_Status_Slider", status_slider, (0, 0, -55))


# ===================================================== 3. OUTER SPIN-SIDE BODY
# The inspection window is intentional: the audience can see the separate
# carrier, bearing pair, alternator rings, and electronics placeholders.
outer_body = cyl(R_BODY, Z_HOUSING1 - Z_HOUSING0, (0, 0, Z_HOUSING0))
outer_body = outer_body.cut(
    cyl(R_ID, Z_HOUSING1 - Z_HOUSING0 - 2, (0, 0, Z_HOUSING0 + 2))
)
inspection_window = box(-12, R_ID - 3, 133, 24, R_BODY - R_ID + 6, 50)
outer_body = outer_body.cut(inspection_window).removeSplitter()
add("10_OuterHousing_SpinSide", outer_body, (0, 0, 0))


# ================================================= 4. DE-SPIN BEARING INTERFACE
def display_bearing(z):
    outer = ring(R_BEARING_OUTER, R_BEARING_INNER, BEARING_H, z)
    balls = []
    for angle in range(0, 360, 45):
        x, y = polar_xy((R_BEARING_OUTER + R_BEARING_INNER) / 2.0, angle)
        balls.append(Part.makeSphere(1.45, App.Vector(x, y, z + BEARING_H / 2.0)))
    return compound(outer, *balls)


add("12_FrontBearing_Demo", display_bearing(Z_FRONT_BEARING), (0, 0, 55))
add("13_RearBearing_Demo", display_bearing(Z_REAR_BEARING), (0, 0, 65))


# ==================================================== 5. COMMON CANARD CARRIER
# This is one inner carrier. Every canard is fixed to it and all four move as
# a single assembly; there are no independent fin hinges or fin motors.
carrier = ring(R_CARRIER, R_CARRIER_ID, Z_CARRIER1 - Z_CARRIER0, Z_CARRIER0)
carrier = fuse(
    carrier,
    ring(R_CARRIER, R_CARRIER_ID, 4.0, Z_CARRIER0 - 1.0),
    ring(R_CARRIER, R_CARRIER_ID, 4.0, Z_CARRIER1 - 3.0),
)
add("14_CommonCanardCarrier", carrier, (0, 0, 75))


def fixed_canard():
    # A deliberately generic display fin. Its incidence is illustrative only;
    # this model is not intended for aerodynamic or flight use.
    points = [
        (R_CARRIER - 1.0, Z_CANARD - 13.0),
        (FIN_TIP, Z_CANARD - 10.0),
        (FIN_TIP, Z_CANARD + 9.0),
        (R_CARRIER - 1.0, Z_CANARD + 13.0),
    ]
    polygon = [App.Vector(x, -FIN_THICK / 2.0, z) for x, z in points]
    polygon.append(polygon[0])
    fin = Part.Face(Part.makePolygon(polygon)).extrude(App.Vector(0, FIN_THICK, 0))
    root = box(R_CARRIER - 2.0, -3.5, Z_CANARD - 6.0, 5.0, 7.0, 12.0)
    return fuse(fin, root)


for index, angle in enumerate((0, 90, 180, 270), start=1):
    fin = fixed_canard()
    fin.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle)
    explode = (38, 0, 70) if index == 1 else (
        (-38, 0, 70) if index == 3 else (0, 38 if index == 2 else -38, 70)
    )
    add("20_FixedCanard_%02d" % index, fin, explode)


# ================================================== 6. SINGLE TORQUE ELEMENT
# A compact placeholder stands for the one relative-rotation torque element in
# the exhibition rig. It is intentionally not a multi-fin gearbox assembly.
torque_body = cyl(5.0, 18.0, (0, -14.0, 145))
torque_mount = box(-5.0, -19.0, 150.0, 10.0, 5.0, 13.0)
torque_link = box(-2.0, -11.0, 155.0, 4.0, 8.0, 5.0)
add("22_Torque_Emulator_LowVoltage", compound(torque_body, torque_mount, torque_link), (0, 0, 95))


# ================================================== 7. SPIN-POWER ALTERNATOR
# The two rings are deliberately named by their mechanical reference frame:
# rotor = outer shell/spin side; stator = inner carrier side.
rotor_ring = ring(24.0, 19.0, 3.0, 166.0)
rotor_magnets = []
for angle in range(0, 360, 45):
    x, y = polar_xy(21.5, angle)
    rotor_magnets.append(box(x - 1.4, y - 1.4, 169.0, 2.8, 2.8, 2.0))
add("40_AlternatorRotor_ShellSide", compound(rotor_ring, *rotor_magnets), (0, 0, 150))

stator_ring = ring(18.8, 15.8, 3.0, 173.0)
stator_coils = []
for angle in range(0, 360, 60):
    x, y = polar_xy(17.3, angle)
    stator_coils.append(box(x - 1.6, y - 1.6, 171.0, 3.2, 3.2, 2.0))
add("41_AlternatorStator_CarrierSide", compound(stator_ring, *stator_coils), (0, 0, 165))


# ================================================ 8. DISPLAY ELECTRONICS STACK
def pcb(z, radius=20.0):
    return cyl(radius, 1.6, (0, 0, z))


power_pcb = fuse(pcb(140), box(2, -4, 141.6, 8, 8, 3))
add("30_PowerManagement_DisplayPCB", power_pcb, (0, 0, 105))

controller_pcb = fuse(
    pcb(146),
    box(-4, -4, 147.6, 8, 8, 2.5),
    box(7, 2, 147.6, 5, 5, 1.5),
)
add("31_Controller_IMU_DisplayPCB", controller_pcb, (0, 0, 120))

sensor_board = fuse(pcb(180, 18.0), box(-7, -4, 181.6, 14, 8, 2.0))
add("32_RelativeAngleSensor_DisplayPCB", sensor_board, (0, 0, 132))

gnss_board = fuse(pcb(188, 18.0), box(-7, -5, 189.6, 14, 10, 2.0))
add("33_GNSS_AntennaPlaceholderPCB", gnss_board, (0, 0, 143))

standoffs = []
for angle in (30, 150, 270):
    x, y = polar_xy(16.0, angle)
    standoffs.append(cyl(1.4, 4.0, (x, y, 141.6)))
    standoffs.append(cyl(1.4, 4.0, (x, y, 147.6)))
add("34_PCB_Standoffs", compound(*standoffs), (0, 0, 112))

# A visible index marker and sensor body make the relative-angle measurement
# easy to explain without implementing guidance or navigation.
index_marker = box(22.0, -1.5, 158.0, 2.0, 3.0, 8.0)
hall_sensor = box(18.0, -2.5, 158.0, 4.0, 5.0, 8.0)
add("35_RelativeAngle_IndexAndSensor", compound(index_marker, hall_sensor), (0, 0, 155))


# ================================================ 9. TOP PLATE / RADOME
top_plate = ring(25.3, 15.5, 3.0, 193.0)
add("50_TopPlate", top_plate, (0, 0, 185))

antenna = cyl(12.5, 3.0, (0, 0, 196.0))
add("51_GNSS_PatchAntenna_Placeholder", antenna, (0, 0, 200))

nose = Part.makeCone(R_BODY, 7.0, Z_NOSE - Z_HOUSING0, App.Vector(0, 0, Z_HOUSING0))
nose = nose.cut(
    Part.makeCone(25.3, 5.0, Z_NOSE - Z_HOUSING0 - 1.0, App.Vector(0, 0, Z_HOUSING0 + 1.0))
)
lip = ring(R_BODY, R_ID, 2.0, Z_HOUSING0)
nose = fuse(nose, lip)
add("60_NoseCap_InertRadome", nose, (0, 0, 230))


# =================================================================== EXPORTS
os.makedirs(OUT, exist_ok=True)
doc.recompute()
docE.recompute()
doc.saveAs(os.path.join(OUT, "pgk_assembly.FCStd"))
docE.saveAs(os.path.join(OUT, "pgk_exploded.FCStd"))
Import.export([obj for _, obj in PARTS], os.path.join(OUT, "pgk_assembly.step"))

for name, obj in PARTS:
    mesh = MeshPart.meshFromShape(
        Shape=obj.Shape,
        LinearDeflection=0.05,
        AngularDeflection=0.3,
    )
    mesh.write(os.path.join(OUT, name + ".stl"))


# ==================================================================== REPORT
all_shape = Part.makeCompound([obj.Shape for _, obj in PARTS])
bound_box = all_shape.BoundBox
report = {
    "units": "mm",
    "parts": len(PARTS),
    "module_length": round(bound_box.ZLength, 1),
    "module_max_diameter": round(max(bound_box.XLength, bound_box.YLength), 1),
    "body_diameter": R_BODY * 2,
    "architecture": "common four-canard carrier + coaxial bearing pair + shell/carrier alternator",
    "torque_element": "single low-voltage exhibition torque emulator placeholder",
    "power_path": "shell-side rotor -> carrier-side stator -> rectifier/supercapacitor (concept)",
    "adapter": "nonfunctional printed slip-fit display adapter; not a live-compatible fuze interface",
    "note": "inert educational demonstrator; no energetic or functional fuze parts",
}
print("PGK DEMO REPORT: " + json.dumps(report, indent=2))
