# Verify generated STLs and dump an axial cross-section of the full solid.
import os, json
import FreeCAD as App
import Mesh

out = "/Users/jagathsrujan/Documents/smart india hackathon/cad_models/out"

# 1) STL checks
for f in sorted(os.listdir(out)):
    if f.endswith(".stl"):
        m = Mesh.read(os.path.join(out, f))
        bb = m.BoundBox
        print("STL %-28s facets=%7d  bbox X %.1f Y %.1f Z %.1f..%.1f (h=%.1f)"
              % (f, m.CountFacets, bb.XLength, bb.YLength, bb.ZMin, bb.ZMax, bb.ZLength))

# 2) Cross-section of the parametric solid (plane y=0) for visual check
doc = App.openDocument(os.path.join(out, "155mm_shell_inert_mockup.FCStd"))
solid = doc.getObject("Shell_Full").Shape
wires = solid.slice(App.Vector(0, 1, 0), 0)
polys = []
for w in wires:
    polys.append([[round(p.x, 2), round(p.z, 2)]
                  for p in w.discretize(Number=400)])
with open(os.path.join(out, "section.json"), "w") as fh:
    json.dump(polys, fh)
print("SECTION wires=%d -> section.json" % len(wires))
