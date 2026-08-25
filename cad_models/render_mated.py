# Render PGK mated on shell - standalone, with error trace.
import os, traceback
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
try:
    fig = plt.figure(figsize=(8, 11))
    ax = fig.add_subplot(111, projection="3d")
    m = Mesh.read(os.path.join(SHELL, "155mm_shell_FULL.stl"))
    shell_tris = [[(p[0], p[1], p[2]) for p in f.Points] for f in m.Facets]
    ax.add_collection3d(Poly3DCollection(shell_tris, facecolor="#bbbbbb",
                                         edgecolor="none", alpha=0.30))
    doc = App.openDocument(os.path.join(OUT, "pgk_assembly.FCStd"))
    objs = [o for o in doc.Objects if hasattr(o, "Shape")]
    for i, o in enumerate(objs):
        pts, tris = o.Shape.tessellate(0.3)
        ts = [[(pts[k].x, pts[k].y, pts[k].z + 515.0) for k in t] for t in tris]
        ax.add_collection3d(Poly3DCollection(ts, facecolor=PALETTE[i % len(PALETTE)],
                                             edgecolor="none", alpha=0.95))
    ax.set_xlim(-95, 95); ax.set_ylim(-95, 95); ax.set_zlim(0, 760)
    ax.set_box_aspect((190, 190, 760))
    ax.view_init(elev=12, azim=-62)
    ax.set_axis_off()
    ax.set_title("PGK mated on 155mm shell mockup (total ~743 mm)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "preview_pgk_on_shell.png"), dpi=110)
    print("saved pgk_on_shell")
except Exception:
    traceback.print_exc()
