import math, sys, time
import FreeCAD as App
import Part
def P(*a): print(*a); sys.stdout.flush()

t0 = time.time()
PATH = "/home/jagath-srujan/Documents/smart india hackathon/cleansheet/PGK_CleanSheet.FCStd"
BP = "/tmp/opencode/"
doc = App.openDocument(PATH)
box = doc.getObject("Section_Cutter").Shape

z_bot, z_seat = 606.0, 696.0
p = 25.4/12.0
r_tube = 24.10; r_obore = 21.5
r_iro  = 18.5;  r_ibore = 16.0
r_bc = 20.0; r_grv = 2.0
rows = [612 + 9*k for k in range(10)]
torii = [Part.makeTorus(r_bc, r_grv, App.Vector(0, 0, z)) for z in rows]

def put(name, shape, vis=False, col=None):
    old = doc.getObject(name)
    if old: doc.removeObject(name)
    ob = doc.addObject("Part::Feature", name)
    ob.Shape = shape
    ob.ViewObject.Visibility = vis
    if col:
        try: ob.ViewObject.ShapeColor = col
        except Exception: pass
    return ob

# ---- outer ring v2: grooves cut into tube FIRST, then fuse ridge ----
tube = Part.makeCylinder(r_tube, z_seat - z_bot, App.Vector(0, 0, z_bot), App.Vector(0, 0, 1))
tube = tube.cut(Part.makeCylinder(r_obore, z_seat - z_bot + 2, App.Vector(0, 0, z_bot - 1), App.Vector(0, 0, 1)))
tube_g = tube
for tor in torii:
    tube_g = tube_g.cut(tor)
P("tube_g vol=%.0f" % tube_g.Volume)

half_c, depth = 0.20, 1.25
half_r = half_c + depth*math.tan(math.radians(30))
r_crest, r_root = 25.35, 25.35 - depth
z0m = (603.0 + p/2.0) - 2.0*p
H = (z_seat + 3.0) - z0m
pts = [App.Vector(r_root, 0, -half_r),
       App.Vector(r_root, 0, half_r),
       App.Vector(r_crest, 0, half_c),
       App.Vector(r_crest, 0, -half_c)]
steps = 48
nsec = int(H/(p/steps)) + 2
secs = []
for k in range(nsec):
    w = Part.Wire([Part.LineSegment(pts[i], pts[(i+1) % 4]).toShape() for i in range(4)])
    w.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360.0*k/steps)
    w.translate(App.Vector(0, 0, z0m + k*p/steps))
    secs.append(w)
ridge = Part.makeLoft(secs, True, True)
ridge = ridge.cut(Part.makeBox(300, 300, 60, App.Vector(-150, -150, z_seat))) \
             .cut(Part.makeBox(300, 300, 120, App.Vector(-150, -150, z_bot - 120)))
P("ridge vol=%.0f t=%.0fs" % (ridge.Volume, time.time()-t0))

outer = tube_g.fuse(ridge).removeSplitter()
ok_outer = outer.isValid() and 38000 < outer.Volume < 48000
P("outer v2: valid=%s vol=%.0f  %s" % (outer.isValid(), outer.Volume, "PASS" if ok_outer else "FAIL"))

# ---- checkpoints ----
outer.exportBrep(BP + "outer_v2.brep")
ridge.exportBrep(BP + "ridge_trimmed.brep")

# ---- inner ring + balls ----
iring = Part.makeCylinder(r_iro, z_seat - z_bot, App.Vector(0, 0, z_bot), App.Vector(0, 0, 1))
iring = iring.cut(Part.makeCylinder(r_ibore, z_seat - z_bot + 2, App.Vector(0, 0, z_bot - 1), App.Vector(0, 0, 1)))
for tor in torii:
    iring = iring.cut(tor)
iring = iring.removeSplitter()
sph = []
for z in rows:
    for j in range(16):
        a = 2*math.pi*j/16
        sph.append(Part.makeSphere(1.5, App.Vector(r_bc*math.cos(a), r_bc*math.sin(a), z)))
balls = Part.makeCompound(sph)

# ---- piecewise section for outer ring ----
sec_out = None
try:
    h_tube = tube_g.cut(box)
    h_ridge = ridge.cut(box)
    P("halves: tube %.0f (valid=%s), ridge %.0f (valid=%s)" %
      (h_tube.Volume, h_tube.isValid(), h_ridge.Volume, h_ridge.isValid()))
    cands = []
    cands.append(h_tube.fuse(h_ridge))
    cands.append(h_tube.fuse(h_ridge).removeSplitter())
    for i, c in enumerate(cands):
        P("sec candidate %d: valid=%s vol=%.0f" % (i, c.isValid(), c.Volume))
        if c.isValid() and 18000 < c.Volume < 24000:
            sec_out = c
            break
except Exception as e:
    P("piecewise err:", e)
P("sec_out:", "OK vol=%.0f" % sec_out.Volume if sec_out else "FAILED")

# ---- other sections (proven) ----
sec_in = iring.cut(box)
sec_bal = balls.cut(box)
P("sec_in: valid=%s vol=%.0f | sec_bal: valid=%s vol=%.0f" %
  (sec_in.isValid(), sec_in.Volume, sec_bal.isValid(), sec_bal.Volume))

# ---- write design parts regardless; sections only if all valid ----
put("Bearing_OuterRing_Threaded", outer)
put("Bearing_InnerRing_Smooth", iring)
put("Bearing_Balls", balls)
allok = sec_out is not None and sec_in.isValid() and sec_bal.isValid()
if allok:
    put("Section_Bearing_OuterRing_Threaded", sec_out, True, (0.55, 0.57, 0.60))
    put("Section_Bearing_InnerRing_Smooth", sec_in, True, (0.45, 0.47, 0.52))
    put("Section_Bearing_Balls", sec_bal, True, (0.85, 0.86, 0.88))
for n in ("Bearing_OuterRing_Threaded", "Bearing_InnerRing_Smooth", "Bearing_Balls"):
    doc.getObject(n).ViewObject.Visibility = False
doc.recompute()
doc.save()
P("SAVED (sections included: %s), t=%.0fs" % (allok, time.time()-t0))
