# ============================================================================
# SIH26098 - 155 mm Artillery Shell - INERT FIT-CHECK MOCKUP (1:1)
# ----------------------------------------------------------------------------
# Purpose : Full-scale, 3D-printable *inert* model of a standard 155 mm
#           artillery projectile envelope (M107-style, public-domain dims)
#           for ideation / form-fit testing of a guidance kit (CAA + fuze).
#           Exterior geometry only. No energetic / functional features.
# Run     : /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd \
#               generate_shell_155.py
# Outputs : .FCStd (parametric source), .STEP + .STL (full), .STL segments
# All dimensions in millimetres. Edit the PARAMETERS block and re-run.
# ============================================================================

import os
import math
import json

import FreeCAD as App
import Part
import MeshPart

# ---------------------------------------------------------------- PARAMETERS
P = {
    # --- overall envelope (approx. public-domain M107-style 155 mm dims) ---
    "body_dia":      154.9,   # projectile body / bourrelet diameter
    "band_dia":      157.9,   # rotating band diameter (engraves in bore)
    "body_len":      400.0,   # base -> start of ogive
    "ogive_len":     205.0,   # ogive length  (total OAL = 605 mm)
    "tip_radius":    25.0,    # radius at fuze-well mouth (ogive terminates)
    "base_chamfer":  3.0,     # 45 deg edge break on base

    # --- rotating band position ---
    "band_start":    38.0,    # from base face to band start
    "band_width":    24.0,
    "band_ramp":     3.0,     # 45 deg ramps at band edges (FDM friendly)

    # --- nose fuze well (for the fuze / CAA mockup) ---
    "fuze_bore_dia": 50.0,    # slip-fit bore; real interface is threaded 2"
    "fuze_bore_depth": 90.0,
    "fuze_lip_chamfer": 0.0,  # >0 adds a mouth chamfer but shortens OAL ~same

    # --- print segmentation (fits ~250 mm tall printers) ---
    "make_segments": True,
    "joint_planes":  [200.0, 400.0],   # axial split positions
    "dowel_dia":     6.0,              # alignment dowel holes (3 per joint)
    "dowel_depth":   15.0,             # hole depth into each mating face
    "dowel_radius":  55.0,             # bolt-circle radius of dowel pattern

    # --- misc ---
    "scale":         1.0,     # 1.0 = life size; 0.5 for a desk prototype
    "mesh_lin_defl": 0.10,    # STL linear deflection (mm)
    "mesh_ang_defl": 0.5,     # STL angular deflection (rad)
    "out_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"),
}

# ------------------------------------------------------------- DERIVED VALUES
S      = P["scale"]
r_body = P["body_dia"] / 2.0 * S
r_band = P["band_dia"] / 2.0 * S
r_tip  = P["tip_radius"] * S
cham   = P["base_chamfer"] * S
z_og   = P["body_len"] * S
z_tip  = (P["body_len"] + P["ogive_len"]) * S
L_og   = z_tip - z_og
bs     = P["band_start"] * S
bw     = P["band_width"] * S
br     = P["band_ramp"] * S

# Tangent (secant) ogive: arc tangent to the body cylinder at (r_body, z_og),
# passing through (r_tip, z_tip). Circle centre lies at (r_body - R, z_og).
R_og = ((r_body - r_tip) ** 2 + L_og ** 2) / (2.0 * (r_body - r_tip))
cx, cz = r_body - R_og, z_og                 # ogive circle centre
th_end = math.atan2(z_tip - cz, r_tip - cx)  # angle of tip point on the arc
th_mid = th_end / 2.0
ogive_A = App.Vector(r_body, 0, z_og)
ogive_M = App.Vector(cx + R_og * math.cos(th_mid), 0, cz + R_og * math.sin(th_mid))
ogive_B = App.Vector(r_tip, 0, z_tip)

# ------------------------------------------------------------------- PROFILE
# Closed wire in the XZ plane (x = radius), revolved 360 deg about Z.
pts = [
    App.Vector(0, 0, 0),                        # base centre
    App.Vector(r_body - cham, 0, 0),            # base face
    App.Vector(r_body, 0, cham),                # base edge chamfer
    App.Vector(r_body, 0, bs),                  # body wall
    App.Vector(r_band, 0, bs + br),             # band ramp out
    App.Vector(r_band, 0, bs + bw - br),        # band land
    App.Vector(r_body, 0, bs + bw + br),        # band ramp back
    App.Vector(r_body, 0, z_og),                # body wall up to ogive
]
edges = [Part.makeLine(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
edges.append(Part.Arc(ogive_A, ogive_M, ogive_B).toShape())   # ogive
edges.append(Part.makeLine(ogive_B, App.Vector(0, 0, z_tip))) # nose face
edges.append(Part.makeLine(App.Vector(0, 0, z_tip), pts[0]))  # axis

wire = Part.Wire(edges)
face = Part.Face(wire)
shell = face.revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)

# ------------------------------------------------------- FUZE WELL (INERT BORE)
# Slip-fit cylindrical bore + chamfered mouth. Solid below -> no cavity that
# could hold anything; this is a mounting hole for the fuze/CAA mockup only.
bd  = P["fuze_bore_depth"] * S
lc  = P["fuze_lip_chamfer"] * S
bore = Part.makeCylinder(P["fuze_bore_dia"] / 2.0 * S, bd,
                         App.Vector(0, 0, z_tip - bd))
shell = shell.cut(bore)
if lc > 0:   # optional mouth chamfer (consumes ~lc of nose height)
    lip = Part.makeCone(P["fuze_bore_dia"] / 2.0 * S + lc,
                        P["fuze_bore_dia"] / 2.0 * S, lc,
                        App.Vector(0, 0, z_tip - lc))
    shell = shell.cut(lip)
shell = shell.removeSplitter()

# ------------------------------------------------------------- DOCUMENT SETUP
doc = App.newDocument("Shell_155mm_Inert_Mockup")
objs = []

def add_shape(name, shape):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    objs.append(o)
    return o

full = add_shape("Shell_Full", shell)

# ------------------------------------------------------ PRINT SEGMENTATION
segments = []
if P["make_segments"]:
    joints = [j * S for j in P["joint_planes"]]
    bounds = [0.0] + joints + [z_tip]
    names = ["SEG1_base", "SEG2_body", "SEG3_ogive"][: len(bounds) - 1]
    for i, (z0, z1) in enumerate(zip(bounds[:-1], bounds[1:])):
        box = Part.makeBox(2.2 * r_band, 2.2 * r_band, z1 - z0,
                           App.Vector(-1.1 * r_band, -1.1 * r_band, z0))
        seg = shell.common(box)
        # dowel holes at each internal joint face (3 @ 120 deg)
        rd = P["dowel_dia"] / 2.0 * S
        dd = P["dowel_depth"] * S
        rr = P["dowel_radius"] * S
        for zj, side in ((z0, +1), (z1, -1)):
            if zj in (0.0, z_tip):
                continue
            for k in range(3):
                a = math.radians(90 + 120 * k)
                x, y = rr * math.cos(a), rr * math.sin(a)
                h0 = zj if side > 0 else zj - dd
                seg = seg.cut(Part.makeCylinder(rd, dd, App.Vector(x, y, h0)))
        seg = seg.removeSplitter()
        segments.append(add_shape(names[i], seg))

# ------------------------------------------------------------- EXPORT FILES
os.makedirs(P["out_dir"], exist_ok=True)
fcstd = os.path.join(P["out_dir"], "155mm_shell_inert_mockup.FCStd")
doc.saveAs(fcstd)

def export(o, base):
    stl = os.path.join(P["out_dir"], base + ".stl")
    m = MeshPart.meshFromShape(Shape=o.Shape,
                               LinearDeflection=P["mesh_lin_defl"],
                               AngularDeflection=P["mesh_ang_defl"])
    m.write(stl)
    return stl

export(full, "155mm_shell_FULL")
step = os.path.join(P["out_dir"], "155mm_shell_FULL.step")
import Import
Import.export([full], step)
for s in segments:
    export(s, "155mm_shell_" + s.Name)

# ------------------------------------------------------------------ REPORT
bb = shell.BoundBox
report = {
    "units": "mm",
    "scale": S,
    "overall_length": round(bb.ZLength, 2),
    "max_diameter":   round(max(bb.XLength, bb.YLength), 2),
    "ogive_radius_R": round(R_og, 1),
    "solid_volume_cm3": round(shell.Volume / 1000.0, 1),
    "solid_mass_PLA_kg": round(shell.Volume / 1000.0 * 1.24 / 1000.0, 2),
    "segments": {s.Name: round(s.Shape.BoundBox.ZLength, 1) for s in segments},
    "out_dir": P["out_dir"],
}
print("BUILD REPORT: " + json.dumps(report, indent=2))
