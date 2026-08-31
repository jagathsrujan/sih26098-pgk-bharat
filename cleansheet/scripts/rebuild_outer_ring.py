import math, sys, time
import FreeCAD as App
import Part
def P(*a): print(*a); sys.stdout.flush()

t0 = time.time()
PATH = "/home/jagath-srujan/Documents/smart india hackathon/cleansheet/PGK_CleanSheet.FCStd"
doc = App.openDocument(PATH)

z_bot, z_seat = 606.0, 696.0
p = 25.4/12.0
r_tube = 24.10; r_obore = 21.5
r_bc = 20.0; r_grv = 2.0
rows = [612 + 9*k for k in range(10)]
torii = [Part.makeTorus(r_bc, r_grv, App.Vector(0, 0, z)) for z in rows]

tube = Part.makeCylinder(r_tube, z_seat - z_bot, App.Vector(0, 0, z_bot), App.Vector(0, 0, 1))
tube = tube.cut(Part.makeCylinder(r_obore, z_seat - z_bot + 2, App.Vector(0, 0, z_bot - 1), App.Vector(0, 0, 1)))

# male thread profile — SAME winding pattern as the proven female profile:
# inner radius first (+z), then outer radius (-z). Here inner = root, outer = crest.
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
P("sections:", nsec)
secs = []
for k in range(nsec):
    w = Part.Wire([Part.LineSegment(pts[i], pts[(i+1) % 4]).toShape() for i in range(4)])
    w.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360.0*k/steps)
    w.translate(App.Vector(0, 0, z0m + k*p/steps))
    secs.append(w)
ridge = Part.makeLoft(secs, True, True)
P("ridge: valid=%s vol=%.0f t=%.0fs" % (ridge.isValid(), ridge.Volume, time.time()-t0))

cut_hi = Part.makeBox(300, 300, 60, App.Vector(-150, -150, z_seat))
cut_lo = Part.makeBox(300, 300, 120, App.Vector(-150, -150, z_bot - 120))
ridge = ridge.cut(cut_hi).cut(cut_lo)

outer = tube.fuse(ridge)
for tor in torii:
    outer = outer.cut(tor)
outer = outer.removeSplitter()
P("outer ring v2: valid=%s vol=%.0f t=%.0fs" % (outer.isValid(), outer.Volume, time.time()-t0))

# sanity: ring vol should be ~ tube(35.3k) - grooves(~3k) + ridge(~11k) = ~43k
if not (outer.isValid() and 38000 < outer.Volume < 48000):
    P("GATE FAIL ring"); raise SystemExit(1)

box = doc.getObject("Section_Cutter").Shape
sec_shape = outer.cut(box)
P("section cut: valid=%s vol=%.0f (expect ~21.5k)" % (sec_shape.isValid(), sec_shape.Volume))
if not (sec_shape.isValid() and 18000 < sec_shape.Volume < 24000):
    sec_shape = outer.common(Part.makeBox(400, 400, 900, App.Vector(-200, -400, -50)))
    P("common fallback: valid=%s vol=%.0f" % (sec_shape.isValid(), sec_shape.Volume))
    if not (sec_shape.isValid() and 18000 < sec_shape.Volume < 24000):
        P("GATE FAIL section"); raise SystemExit(1)

# replace design part + section
for name, shape in (("Bearing_OuterRing_Threaded", outer),
                    ("Section_Bearing_OuterRing_Threaded", sec_shape)):
    old = doc.getObject(name)
    if old: doc.removeObject(name)
    ob = doc.addObject("Part::Feature", name)
    ob.Shape = shape
doc.getObject("Bearing_OuterRing_Threaded").ViewObject.Visibility = False
doc.getObject("Section_Bearing_OuterRing_Threaded").ViewObject.Visibility = True
try:
    doc.getObject("Section_Bearing_OuterRing_Threaded").ViewObject.ShapeColor = (0.55, 0.57, 0.60)
except Exception:
    pass
doc.recompute()
doc.save()
P("SAVED v2 ring + section, t=%.0fs" % (time.time()-t0))
