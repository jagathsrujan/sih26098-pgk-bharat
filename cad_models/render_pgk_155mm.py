# ============================================================================
# SIH26098 - renders + exports for the PGK_155mm.FCStd flight-envelope model
# ----------------------------------------------------------------------------
# Source of truth : ../PGK_155mm.FCStd  (single 61811 bearing, ring-motor
#                   torque actuator, detent lock, 4 strakes, Ø106 de-spun
#                   stator with GNC stack + 6x 14430 bay, NEO-M9N + patch)
# Run             : freecadcmd render_pgk_155mm.py
# Outputs (out_pgk/): preview_assembly.png, preview_mated.png,
#                   preview_section.png, STEP (mated + PGK + section),
#                   per-part STL in stl/, viewer_data.json for pgk_3d_viewer
# ============================================================================
import os
import sys
import json
import base64
import struct

import FreeCAD as App
import Part
import Mesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "out_pgk")
DOC = os.path.join(ROOT, "PGK_155mm.FCStd")
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(OUT, "stl"), exist_ok=True)

# part name -> display color (matches the FreeCAD look)
COLORS = {
    "Projectile_Body":       "#5d6b3f",
    "REF_Driving_Band":      "#c47f3a",
    "PGK_Rotor_Adapter":     "#aeb6bf",
    "PGK_Rotor_Adapter001":  "#8f979f",
    "PGK_Seal_ORing":        "#1f1f1f",
    "PGK_Bearing_61811":     "#c8ccd0",
    "PGK_Bearing_61811_Balls": "#e0e4e8",
    "PGK_RingMotor_Coils":   "#b06a2f",
    "PGK_Detent_Pawl":       "#6b7280",
    "PGK_Stator_Body":       "#9aa3ad",
    "PGK_Strakes":           "#2e2e30",
    "Carrier_PCB_D87":       "#1e5c3a",
    "BlackPill_A":           "#111111",
    "BlackPill_B":           "#111111",
    "ICM42688":              "#27536b",
    "MMC5983":               "#27536b",
    "FOC_Driver":            "#27536b",
    "Hall_A":                "#333333",
    "Hall_B":                "#333333",
    "Detent_Solenoid":       "#3a3f44",
    "Cell_14430_1":          "#c9ced4",
    "Cell_14430_2":          "#c9ced4",
    "Cell_14430_3":          "#c9ced4",
    "Cell_14430_4":          "#c9ced4",
    "Cell_14430_5":          "#c9ced4",
    "Cell_14430_6":          "#c9ced4",
    "NEO_M9N":               "#2f7d4f",
    "Shelf":                 "#7d8794",
    "GPS_Patch":             "#e8e4da",
}

def tris_of(shape, tol=0.25):
    pts, tris = shape.tessellate(tol)
    v = np.array([(p.x, p.y, p.z) for p in pts])
    t = np.array(tris, dtype=np.int64).reshape(-1, 3)
    return v, t

def has_geom(o):
    try:
        return (not o.Shape.isNull()) and o.Shape.Volume > 0.0 and len(o.Shape.Faces) > 0
    except Exception:
        return False

def shaded_collection(v, t, color, alpha=1.0):
    p3 = v[t]  # (n,3,3)
    n = np.cross(p3[:, 1] - p3[:, 0], p3[:, 2] - p3[:, 0])
    norm = np.linalg.norm(n, axis=1, keepdims=True)
    norm[norm == 0] = 1
    n = n / norm
    light = np.array([0.4, -0.5, 0.77])
    lam = np.clip(n @ light, 0, 1) * 0.65 + 0.35
    base = np.array(matplotlib.colors.to_rgb(color))
    fc = np.clip(base[None, :] * lam[:, None], 0, 1)
    return Poly3DCollection(p3, facecolors=fc, edgecolor="none", alpha=alpha)

def base_color(name):
    return COLORS.get(name.removeprefix("SEC_"), "#999999")

def render(doc, names, png, title, alpha_map=None, view=(16, -58), zlim=None):
    objs = [o for o in doc.Objects if o.Name in names and has_geom(o)]
    if zlim:
        objs = [o for o in objs if o.Shape.BoundBox.ZMax > zlim[0] and o.Shape.BoundBox.ZMin < zlim[1]]
    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_subplot(111, projection="3d")
    bb = App.BoundBox()
    import math
    az = math.radians(view[1])
    fwd = np.array([-math.cos(az) * math.cos(math.radians(view[0])),
                    -math.sin(az) * math.cos(math.radians(view[0])),
                    -math.sin(math.radians(view[0]))])
    objs = sorted(objs, key=lambda o: -float(np.dot(o.Shape.BoundBox.Center, fwd)))
    for i, o in enumerate(objs):
        v, t = tris_of(o.Shape)
        a = (alpha_map or {}).get(o.Name, 1.0)
        col = shaded_collection(v, t, base_color(o.Name), a)
        col.set_zorder(i)
        ax.add_collection3d(col)
        bb.add(o.Shape.BoundBox)
    if zlim:
        bb.ZMin, bb.ZMax = zlim
    rx = max(bb.XLength, bb.YLength) * 0.62 + 4
    cx, cy = (bb.XMin + bb.XMax) / 2, (bb.YMin + bb.YMax) / 2
    ax.set_xlim(cx - rx, cx + rx); ax.set_ylim(cy - rx, cy + rx)
    ax.set_zlim(bb.ZMin - 5, bb.ZMax + 5)
    ax.set_box_aspect((2 * rx, 2 * rx, bb.ZLength + 10))
    ax.view_init(elev=view[0], azim=view[1])
    ax.set_axis_off(); ax.set_title(title, fontsize=11)
    plt.tight_layout(); plt.savefig(png, dpi=120)
    plt.close(fig)
    print("saved", png)

# ---------------------------------------------------------------- load doc
doc = App.openDocument(DOC)
full = [o for o in doc.Objects if not o.Name.startswith("SEC_") and has_geom(o)]
sec  = [o for o in doc.Objects if o.Name.startswith("SEC_") and has_geom(o)]
full_names = {o.Name for o in full}
sec_names = {o.Name for o in sec}
pgk_names = {o.Name for o in full if o.Name not in ("Projectile_Body", "REF_Driving_Band")}

# ---------------------------------------------------------------- renders
render(doc, full_names, os.path.join(OUT, "preview_mated.png"),
       "PGK_155mm.FCStd - mated on 155mm shell (latest design)",
       alpha_map={"Projectile_Body": 0.45, "PGK_Strakes": 0.9})
render(doc, pgk_names, os.path.join(OUT, "preview_assembly.png"),
       "PGK nose module - rotor/stator split, ring motor, detent, strakes")
render(doc, sec_names, os.path.join(OUT, "preview_section.png"),
       "Cutaway (SEC_ half-sections) - GNC stack, 6x 14430 bay, GNSS on top", view=(6, 178))
sec_pgk = {n for n in sec_names if n not in ("SEC_Projectile_Body", "SEC_REF_Driving_Band")}
render(doc, sec_pgk, os.path.join(OUT, "preview_section_pgk.png"),
       "Cutaway zoom - rotor adapter, 61811 bearing, ring motor, detent, stack, cells, GNSS",
       view=(6, 178), zlim=(740, 925))

# ---------------------------------------------------------------- STEP exports
def export_step(names, path):
    objs = [o for o in doc.Objects if o.Name in names]
    Part.export(objs, path)
    print("saved", path)

export_step(full_names, os.path.join(OUT, "PGK_155mm_mated.step"))
export_step(pgk_names, os.path.join(OUT, "PGK_155mm_nose_module.step"))
export_step(sec_names, os.path.join(OUT, "PGK_155mm_section.step"))

# ---------------------------------------------------------------- per-part STL
for o in full:
    if o.Name == "Projectile_Body":
        continue
    path = os.path.join(OUT, "stl", o.Name + ".stl")
    Mesh.export([o], path)
print("saved per-part STL x", len(full) - 1)

# ---------------------------------------------------------------- viewer data
# hybrid: lathe profiles for axisymmetric parts, coarse meshes for strakes /
# pawl / bearing balls, box/cylinder primitives for board-level parts
LATHE = [
    "Projectile_Body", "REF_Driving_Band", "PGK_Rotor_Adapter",
    "PGK_Rotor_Adapter001", "PGK_Stator_Body", "PGK_Bearing_61811",
    "PGK_RingMotor_Coils", "PGK_Seal_ORing", "Carrier_PCB_D87", "Shelf",
]
MESH = ["PGK_Strakes", "PGK_Detent_Pawl"]
TORUS = "PGK_Bearing_61811_Balls"
PRIM = ["BlackPill_A", "BlackPill_B", "ICM42688", "MMC5983", "FOC_Driver",
        "Hall_A", "Hall_B", "Detent_Solenoid", "Cell_14430_1", "Cell_14430_2",
        "Cell_14430_3", "Cell_14430_4", "Cell_14430_5", "Cell_14430_6",
        "NEO_M9N", "GPS_Patch"]

def lathe_profile(o, dz=1.5):
    v, _ = tris_of(o.Shape, 0.8)
    z0, z1 = v[:, 2].min(), v[:, 2].max()
    r = np.sqrt(v[:, 0] ** 2 + v[:, 1] ** 2)
    nb = max(2, int((z1 - z0) / dz) + 1)
    idx = np.clip(((v[:, 2] - z0) / (z1 - z0 + 1e-9) * (nb - 1)).round().astype(int), 0, nb - 1)
    prof = np.zeros((nb, 2))
    cnt = np.zeros(nb)
    for i in range(nb):
        m = idx == i
        cnt[i] = m.sum()
        if m.any():
            prof[i] = (z0 + (z1 - z0) * i / (nb - 1), r[m].max())
    # fill empty bins (straight walls tessellate sparsely) by interpolation
    valid = cnt > 0
    if valid.any() and not valid.all():
        prof[~valid, 1] = np.interp(prof[~valid, 0], prof[valid, 0], prof[valid, 1])
    # run-length compress: drop collinear-ish points on straight sections
    out = []
    last = None
    for z, rr in prof:
        if last is None or abs(rr - last) > 0.12:
            out.append([round(float(z), 1), round(float(rr), 2)])
            last = rr
    if out[-1][0] != round(float(z1), 1):
        out.append([round(float(z1), 1), out[-1][1]])
    return out

def mesh_entry(o, tol=0.5):
    v, t = tris_of(o.Shape, tol)
    lo = v.min(axis=0)
    q = np.clip(np.round(v - lo).astype(np.int64), 0, 65535).astype(np.uint16)
    qq = q[t.reshape(-1)]
    return {
        "name": o.Name,
        "color": COLORS.get(o.Name, "#999999"),
        "min": [round(float(x), 2) for x in lo],
        "q": base64.b64encode(qq.astype("<u2").tobytes()).decode("ascii"),
    }

def prim_entry(o):
    bb = o.Shape.BoundBox
    return {
        "name": o.Name,
        "color": COLORS.get(o.Name, "#999999"),
        "c": [round((bb.XMin + bb.XMax) / 2, 2), round((bb.YMin + bb.YMax) / 2, 2)],
        "z": [round(bb.ZMin, 2), round(bb.ZMax, 2)],
        "r": round(max(bb.XLength, bb.YLength) / 2, 2),
        "s": [round(bb.XLength, 2), round(bb.YLength, 2)],
        "shape": "cyl" if abs(bb.XLength - bb.YLength) < 0.4 else "box",
    }

data = {"lathe": [], "mesh": [], "prim": [], "torus": []}
for n in LATHE:
    o = doc.getObject(n)
    data["lathe"].append({"name": n, "color": COLORS[n], "p": lathe_profile(o)})
for n in MESH:
    data["mesh"].append(mesh_entry(doc.getObject(n)))
o = doc.getObject(TORUS)
bb = o.Shape.BoundBox
data["torus"].append({"name": TORUS, "color": COLORS[TORUS],
                      "c": [round((bb.XMin + bb.XMax) / 2, 2), round((bb.YMin + bb.YMax) / 2, 2)],
                      "z": round((bb.ZMin + bb.ZMax) / 2, 2),
                      "R": round(bb.XLength / 2 - bb.ZLength / 2, 2),
                      "r": round(bb.ZLength / 2, 2)})
for n in PRIM:
    data["prim"].append(prim_entry(doc.getObject(n)))
with open(os.path.join(OUT, "viewer_data.json"), "w") as f:
    json.dump(data, f, separators=(",", ":"))
kb = os.path.getsize(os.path.join(OUT, "viewer_data.json")) / 1024
print("saved viewer_data.json (%.0f KB)" % kb)

App.closeDocument(doc.Name)
print("done")
