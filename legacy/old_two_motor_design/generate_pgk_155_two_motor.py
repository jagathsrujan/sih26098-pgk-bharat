# ============================================================================
# SIH26098 - Precision Guidance Kit (PGK) nose module - INERT DEMONSTRATOR
# ----------------------------------------------------------------------------
# Purpose : Educational, 3D-printable demonstrator showing the inner working
#           of a canard-actuated 155 mm guidance kit: motors + face-gear drive,
#           radial canard shafts, de-spun alternator power concept, PCB stack
#           (power / GNC / GNSS), battery bay, and a purely mechanical
#           safe-&-arm slider demo.  NO energetic or functional fuze parts.
# Fit     : Shank slip-fits the Ø50 x 90 mm fuze bore of the shell mockup
#           (generate_shell_155.py).  Local z=0 sits at the bore floor.
# Run     : freecadcmd generate_pgk_155.py
# Outputs : out_pgk/pgk_assembly.FCStd, pgk_exploded.FCStd, STEP, per-part STL
# ============================================================================

import os
import math
import json

import FreeCAD as App
import Part
import MeshPart
import Import

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_pgk")

# ------------------------------------------------------------- key dimensions
R_BODY   = 28.0      # module body outer radius (Ø56)
R_ID     = 25.5      # body inner radius
Z_SHANK  = 90.0      # shank length (into shell fuze bore)
Z_BODY0  = 92.0      # body shell start (flange at 88..92)
Z_BODY1  = 196.0     # body shell top / nose cap start
Z_NOSE   = 228.0     # nose tip
Z_SHAFT1 = 146.0     # x-axis canard pair centre height
Z_SHAFT2 = 152.0     # y-axis canard pair centre height (staggered, no clash)
FIN_TIP  = 75.5      # fin tip radius (span ~151 mm ~ shell diameter)

doc  = App.newDocument("PGK_Assembly")
docE = App.newDocument("PGK_Exploded")
PARTS = []   # (name, shape, explode_offset_vector)

def add(name, shape, explode=(0, 0, 0), color=None):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    s2 = shape.copy()
    s2.translate(App.Vector(*explode))
    oe = docE.addObject("Part::Feature", name)
    oe.Shape = s2
    PARTS.append((name, o))
    return o

def box(x0, y0, z0, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, App.Vector(x0, y0, z0))

def cyl(r, h, p=(0, 0, 0), d=(0, 0, 1)):
    return Part.makeCylinder(r, h, App.Vector(*p), App.Vector(*d))

def fuse(*shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.removeSplitter()

# ============================================================ 1. SHANK / BASE
# Slip-fit shank into the shell's Ø50 fuze bore; holds battery + fuze PCB.
prof = [
    (24.8, 0.0), (24.8, 88.0), (28.0, 88.0), (28.0, 92.0),   # flange
    (25.5, 92.0), (25.5, 90.0), (21.0, 90.0), (21.0, 75.0),
    (19.0, 75.0), (19.0, 73.0), (21.0, 73.0), (21.0, 2.0),   # PCB ledge
    (0.0, 2.0), (0.0, 0.0),
]
edges = []
for i in range(len(prof)):
    a = prof[i]; b = prof[(i + 1) % len(prof)]
    edges.append(Part.makeLine(App.Vector(a[0], 0, a[1]), App.Vector(b[0], 0, b[1])))
shank = Part.Face(Part.Wire(edges)).revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)
shank = shank.cut(cyl(2.5, 4, (0, 0, -1)))                    # wire pass-through
add("01_ShankAdapter", shank, (0, 0, -120))

add("02_Battery_18650", cyl(9.1, 65, (0, 0, 8)), (0, 0, -170))

fpcb = cyl(20.0, 1.6, (0, 0, 75))
fpcb = fuse(fpcb, box(-4, -4, 76.6, 8, 8, 2.5))               # power stage block
add("03_FuzePower_PCB", fpcb, (0, 0, -140))

# ============================================ 2. SAFE & ARM DEMONSTRATOR (INERT)
# Manual slider: an EMPTY through-hole (stand-in for out-of-line arming
# concept) slides into alignment only when armed. No energetic parts at all.
slider = box(-11, -6, 97, 22, 12, 7)
slider = slider.cut(cyl(3.0, 7, (-7, 0, 97)))                 # empty alignment hole
slider = fuse(slider, cyl(1.8, 20, (0, 6, 100.5), (0, 1, 0)))  # handle pin
add("04_SA_Slider_inert", slider, (0, 0, -40))

# ===================================================== 3. LOWER BODY (HOUSING)
body = cyl(R_BODY, Z_BODY1 - Z_BODY0, (0, 0, Z_BODY0))
body = body.cut(cyl(R_ID, Z_BODY1 - Z_BODY0 - 2, (0, 0, Z_BODY0 + 2)))  # cup, 2 mm floor
body = body.cut(cyl(2.5, 4, (0, 0, Z_BODY0)))                 # wire hole in floor
# canard shaft holes through the wall (x pair @146, y pair @152)
for sgn in (1, -1):
    body = body.cut(cyl(2.1, 6, (sgn * 23.5, 0, Z_SHAFT1), (sgn, 0, 0)))
    body = body.cut(cyl(2.1, 6, (0, sgn * 23.5, Z_SHAFT2), (0, sgn, 0)))
# S&A handle slot in wall (+y)
body = body.cut(box(-6, R_ID - 2, 98.5, 12, R_BODY - R_ID + 3, 4.5))
body = body.removeSplitter()
add("10_LowerBody", body, (0, 0, 0))

# ==================================================== 4. ACTUATORS (x2 motors)
# N20-style Ø12 gearmotors, vertical; pinion drives a face gear on each
# radial canard shaft (orthogonal-axis 'bevel/crown' drive concept).
m1 = cyl(6, 24, (-8, -13, 122))                               # motor 1 body
m1 = fuse(m1, cyl(1.5, 3, (-8, -13, 146)))                    # shaft stub
m1g = cyl(6, 3, (-8, -13, 146.5))                             # pinion (r6)
add("11_Motor_Xpair", m1, (0, 0, 35))
add("12_Pinion_X", m1g, (0, 0, 35))
m2 = cyl(6, 24, (13, -8, 128))                                # motor 2 body
m2 = fuse(m2, cyl(1.5, 3, (13, -8, 152)))
m2g = cyl(6, 3, (13, -8, 150.5))                              # pinion (r6)
add("13_Motor_Ypair", m2, (0, 0, 35))
add("14_Pinion_Y", m2g, (0, 0, 35))

# ============================================= 5. CANARD SHAFTS + FACE GEARS
shx = cyl(2.0, 68, (-34, 0, Z_SHAFT1), (1, 0, 0))             # x-pair shaft
gx = cyl(8, 3, (-6, 0, Z_SHAFT1 - 1.5), (1, 0, 0))            # face gear r8
gx = gx.cut(cyl(2.05, 3, (-6, 0, Z_SHAFT1 - 1.5), (1, 0, 0)))
add("15_CanardShaft_X", shx, (0, 0, 65))
add("16_FaceGear_X", gx, (0, 0, 65))
shy = cyl(2.0, 68, (0, -34, Z_SHAFT2), (0, 1, 0))             # y-pair shaft
gy = cyl(8, 3, (0, -6, Z_SHAFT2 - 1.5), (0, 1, 0))
gy = gy.cut(cyl(2.05, 3, (0, -6, Z_SHAFT2 - 1.5), (0, 1, 0)))
add("17_CanardShaft_Y", shy, (0, 0, 65))
add("18_FaceGear_Y", gy, (0, 0, 65))

# bearing rings (684-size) at wall exits
bear = []
for sgn in (1, -1):
    bx = cyl(4.5, 4, (sgn * 24, 0, Z_SHAFT1), (sgn, 0, 0)).cut(
         cyl(2.1, 4, (sgn * 24, 0, Z_SHAFT1), (sgn, 0, 0)))
    by = cyl(4.5, 4, (0, sgn * 24, Z_SHAFT2), (0, sgn, 0)).cut(
         cyl(2.1, 4, (0, sgn * 24, Z_SHAFT2), (0, sgn, 0)))
    bear += [bx, by]
add("19_Bearings_x4", fuse(*bear), (0, 0, 65))

# ================================================================= 6. CANARDS
def fin(zc):
    p = [(28.5, zc - 13), (FIN_TIP, zc - 12), (FIN_TIP, zc + 4), (28.5, zc + 13)]
    w = Part.makePolygon([App.Vector(x, 0, z) for x, z in p] + [App.Vector(*p[0][:1], 0, p[0][1])])
    f = Part.Face(w).extrude(App.Vector(0, 2.8, 0))
    f.translate(App.Vector(0, -1.4, 0))
    hub = cyl(5.5, 7.0, (28, 0, zc), (1, 0, 0))
    f = fuse(f, hub)
    f = f.cut(cyl(2.1, 9.0, (27.5, 0, zc), (1, 0, 0)))
    return f

finPX = fin(Z_SHAFT1)
finNX = fin(Z_SHAFT1); finNX.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 180)
finPY = fin(Z_SHAFT2); finPY.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 90)
finNY = fin(Z_SHAFT2); finNY.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 270)
add("20_Canard_+X", finPX, (30, 0, 65))
add("21_Canard_-X", finNX, (-30, 0, 65))
add("22_Canard_+Y", finPY, (0, 30, 65))
add("23_Canard_-Y", finNY, (0, -30, 65))

# ===================================================== 7. ELECTRONICS STACK
def pcb(z, r=22.0):
    return cyl(r, 1.6, (0, 0, z))

pcb1 = fuse(pcb(158), box(2, -4, 159.6, 8, 8, 3))             # power mgmt
add("30_PCB_Power", pcb1, (0, 0, 100))
pcb2 = fuse(pcb(164), box(-3.5, -3.5, 165.6, 7, 7, 1),        # MCU
            box(6, 2, 165.6, 5, 5, 1))                        # IMU
add("31_PCB_GNC_IMU", pcb2, (0, 0, 115))
pcb3 = fuse(pcb(170), box(-8, -6, 171.6, 16, 12, 2.4))        # GNSS receiver
add("32_PCB_GNSS", pcb3, (0, 0, 130))
so = []
for ang in (30, 150, 270):
    x, y = 17 * math.cos(math.radians(ang)), 17 * math.sin(math.radians(ang))
    so += [cyl(1.5, 4.4, (x, y, 159.6)), cyl(1.5, 4.4, (x, y, 165.6))]
add("33_PCB_Standoffs", fuse(*so), (0, 0, 107))

# ================================================== 8. ALTERNATOR (DE-SPIN)
# Rotor (spins with shell) carries magnets; stator (de-spun section) carries
# coils -> spin-energy power harvesting concept, M1156-style.
rotor = cyl(20, 3, (0, 0, 178))
rotor = fuse(rotor, *[cyl(2.5, 2, (13 * math.cos(math.radians(45 * k)),
                                   13 * math.sin(math.radians(45 * k)), 181))
                      for k in range(8)])
add("40_Alternator_Rotor", rotor, (0, 0, 150))
stator = cyl(20, 2, (0, 0, 186))
stator = fuse(stator, *[cyl(3.5, 2, (13 * math.cos(math.radians(60 * k)),
                                    13 * math.sin(math.radians(60 * k)), 184))
                        for k in range(6)])
add("41_Alternator_Stator", stator, (0, 0, 165))

# ======================================================= 9. TOP PLATE + GNSS
plate = cyl(25.3, 3, (0, 0, 193))
add("50_TopPlate", plate, (0, 0, 185))
patch = cyl(12.5, 4, (0, 0, 196))
add("51_GNSS_PatchAntenna", patch, (0, 0, 200))

# ================================================================ 10. NOSE CAP
nose = Part.makeCone(R_BODY, 7, Z_NOSE - Z_BODY0, App.Vector(0, 0, Z_BODY0))
nose = nose.cut(Part.makeCone(25.3, 5, Z_NOSE - Z_BODY0 - 1, App.Vector(0, 0, Z_BODY0 + 1)))
lip = cyl(R_BODY, 2, (0, 0, Z_BODY0)).cut(cyl(R_ID, 2, (0, 0, Z_BODY0)))
nose = fuse(nose, lip)
add("60_NoseCap_radome", nose, (0, 0, 230))

# =================================================================== EXPORTS
os.makedirs(OUT, exist_ok=True)
doc.saveAs(os.path.join(OUT, "pgk_assembly.FCStd"))
docE.saveAs(os.path.join(OUT, "pgk_exploded.FCStd"))
Import.export([o for _, o in PARTS], os.path.join(OUT, "pgk_assembly.step"))

for name, o in PARTS:
    m = MeshPart.meshFromShape(Shape=o.Shape, LinearDeflection=0.05,
                               AngularDeflection=0.3)
    m.write(os.path.join(OUT, name + ".stl"))

# ==================================================================== REPORT
allb = Part.makeCompound([o.Shape for _, o in PARTS]).BoundBox
report = {
    "units": "mm",
    "parts": len(PARTS),
    "module_length": round(allb.ZLength, 1),
    "module_max_diameter": round(max(allb.XLength, allb.YLength), 1),
    "body_diameter": R_BODY * 2,
    "shank": "OD 49.6 x 90 -> slip-fits shell fuze bore 50 x 90",
    "canard_span_across": round(2 * FIN_TIP, 1),
    "note": "inert educational demonstrator; no energetic components",
}
print("PGK REPORT: " + json.dumps(report, indent=2))
