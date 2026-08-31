import sys, time
import FreeCAD as App
import Part
def P(*a): print(*a); sys.stdout.flush()

t0 = time.time()
PATH = "/home/jagath-srujan/Documents/smart india hackathon/cleansheet/PGK_CleanSheet.FCStd"
doc = App.openDocument(PATH)
outer = doc.getObject("Bearing_OuterRing_Threaded").Shape

cutter_cut   = Part.makeBox(400, 400, 900, App.Vector(-200, 0, -50))     # removes y>0
cutter_common = Part.makeBox(400, 400, 900, App.Vector(-200, -400, -50)) # keeps y<0

candidates = []
try:
    s = outer.cut(cutter_cut)
    candidates.append(("cut", s))
except Exception as e:
    P("cut failed:", e)
try:
    s2 = outer.common(cutter_common)
    candidates.append(("common", s2))
except Exception as e:
    P("common failed:", e)

# fix pass on all candidates
fixed = []
for tag, s in candidates:
    try:
        f = s.copy()
        f.fix(1e-7, 1e-7, 1e-7)
        fixed.append((tag + "+fix", f))
    except Exception as e:
        P("fix err", tag, ":", e)

allc = candidates + fixed
best = None
for tag, s in allc:
    P("%-12s valid=%s vol=%.0f" % (tag, s.isValid(), s.Volume))
    if best is None and s.isValid() and 18000 < s.Volume < 23000:
        best = (tag, s)
if best:
    P("CHOSEN:", best[0])
    name = "Section_Bearing_OuterRing_Threaded"
    old = doc.getObject(name)
    if old: doc.removeObject(name)
    ob = doc.addObject("Part::Feature", name)
    ob.Shape = best[1]
    ob.ViewObject.Visibility = True
    try:
        ob.ViewObject.ShapeColor = (0.55, 0.57, 0.60)
    except Exception:
        pass
    doc.recompute()
    doc.save()
    P("SAVED outer-ring section, t=%.0fs" % (time.time()-t0))
else:
    P("no valid candidate - aborted")
