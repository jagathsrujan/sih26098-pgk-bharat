# Render verification previews of the PGK demonstrator.
import os
import FreeCAD as App
import Mesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT = "/Users/jagathsrujan/Documents/smart india hackathon/cad_models/out_pgk"
SHELL = "/Users/jagathsrujan/Documents/smart india hackathon/cad_models/out"
PALETTE = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33",
           "#a65628", "#f781bf", "#999999", "#66c2a5", "#fc8d62", "#8da0cb",
           "#e78ac3", "#a6d854", "#ffd92f", "#e5c494", "#b3b3b3"]

def mesh_of_shape(shape, tol=0.3):
    pts, tris = shape.tessellate(tol)
    return [[(pts[i].x, pts[i].y, pts[i].z) for i in t] for t in tris]

def mesh_of_stl(path, dz=0.0):
    m = Mesh.read(path)
    return [[(p.x, p.y, p.z + dz) for p in f.Points] for f in m.Facets]

def render(doc_path, png, title, shell_stl=None, lim=None):
    doc = App.openDocument(doc_path)
    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_subplot(111, projection="3d")
    objs = [o for o in doc.Objects if hasattr(o, "Shape")]
    if shell_stl:
        ax.add_collection3d(Poly3DCollection(mesh_of_stl(shell_stl),
                        facecolor="#cccccc", edgecolor="none", alpha=0.35))
    for i, o in enumerate(objs):
        tris = mesh_of_shape(o.Shape)
        if shell_stl:                       # mate PGK onto shell (bore floor z=515)
            tris = [(x, y, z + 515.0) for t in tris for (x, y, z) in [t]]
            tris = [tris[i:i+3] for i in range(0, len(tris), 3)]
        ax.add_collection3d(Poly3DCollection(
            tris, facecolor=PALETTE[i % len(PALETTE)], edgecolor="none", alpha=0.95))
    if lim:
        (x0, x1), (y0, y1), (z0, z1) = lim
    else:
        bb = App.BoundBox()
        for o in objs:
            if not o.Shape.isNull():
                bb.add(o.Shape.BoundBox)
        x0, x1, y0, y1, z0, z1 = bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax
        if shell_stl:
            z1 = max(z1 + 515, 743); z0 = 0
    ax.set_xlim(x0 - 10, x1 + 10); ax.set_ylim(y0 - 10, y1 + 10)
    ax.set_zlim(z0, z1)
    ax.set_box_aspect((x1 - x0 + 20, y1 - y0 + 20, z1 - z0))
    ax.view_init(elev=14, azim=-62)
    ax.set_axis_off(); ax.set_title(title)
    plt.tight_layout(); plt.savefig(png, dpi=110)
    print("saved", png)
    App.closeDocument(doc.Name)

render(os.path.join(OUT, "pgk_assembly.FCStd"),
       os.path.join(OUT, "preview_assembly.png"),
       "Inert PGK demonstrator - common carrier assembly")
render(os.path.join(OUT, "pgk_exploded.FCStd"),
       os.path.join(OUT, "preview_exploded.png"),
       "Inert PGK demonstrator - exploded view")
render(os.path.join(OUT, "pgk_assembly.FCStd"),
       os.path.join(OUT, "preview_pgk_on_shell.png"),
       "Inert demonstrator on 155mm shell mockup (visual scale)",
       shell_stl=os.path.join(SHELL, "155mm_shell_FULL.stl"),
       lim=((-90, 90), (-90, 90), (0, 760)))
