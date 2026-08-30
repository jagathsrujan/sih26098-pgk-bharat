import math, sys, time
import FreeCAD as App
import Part

def P(*a):
    print("[%7.0fs]" % (time.time()-t0, ), *a)
    sys.stdout.flush()

t0 = time.time()
PATH = "/home/jagath-srujan/Documents/smart india hackathon/cleansheet/PGK_CleanSheet.FCStd"
BP = "/tmp/opencode/"
doc = App.openDocument(PATH)
box = doc.getObject("Section_Cutter").Shape
P("doc opened, objects=%d" % len(doc.Objects))

z_bot, z_seat = 606.0, 696.0
p = 25.4/12.0
r_tube = 24.10; r_obore = 21.5
r_iro = 18.5;  r_ibore = 16.0
r_bc = 20.0; r_grv = 2.0
rows = [612 + 9*k for k in range(10)]

# ---- grooved tube (build order that is SAFE: grooves into plain tube) ----
tube = Part.makeCylinder(r_tube, z_seat - z_bot, App.Vector(0, 0, z_bot), App.Vector(0, 0, 1))
tube = tube.cut(Part.makeCylinder(r_obore, z_seat - z_bot + 2, App.Vector(0, 0, z_bot - 1), App.Vector(0, 0, 1)))
tube_g = tube
for tor in [Part.makeTorus(r_bc, r_grv, App.Vector(0, 0, z)) for z in rows]:
    tube_g = tube_g.cut(tor)
P("tube_g vol=%.0f valid=%s" % (tube_g.Volume, tube_g.isValid()))

# ---- thread ridge loft (proven 48-step winding), 0.05 root interference ----
half_c, depth = 0.20, 1.25
half_r = half_c + depth*math.tan(math.radians(30))
r_crest = 25.35
r_root = r_tube - 0.05
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
P("ridge vol=%.0f valid=%s" % (ridge.Volume, ridge.isValid()))

# ---- halve each piece separately (piecewise core) ----
h_tube = tube_g.cut(box)
h_ridge = ridge.cut(box)
P("h_tube vol=%.0f valid=%s | h_ridge vol=%.0f valid=%s" %
  (h_tube.Volume, h_tube.isValid(), h_ridge.Volume, h_ridge.isValid()))
h_tube.exportBrep(BP + "pw2_h_tube.brep")
h_ridge.exportBrep(BP + "pw2_h_ridge.brep")

# ---- fuse the two y<=0 halves; compound fallback ----
sec_out = None; how = None
try:
    c = h_tube.fuse(h_ridge)
    P("fuse raw: valid=%s vol=%.0f solids=%d" % (c.isValid(), c.Volume, len(c.Solids)))
    if c.isValid() and 18000 < c.Volume < 24000:
        sec_out = c; how = "fuse"
    else:
        c2 = c.removeSplitter()
        P("fuse+rs: valid=%s vol=%.0f solids=%d" % (c2.isValid(), c2.Volume, len(c2.Solids)))
        if c2.isValid() and 18000 < c2.Volume < 24000:
            sec_out = c2; how = "fuse+rs"
except Exception as e:
    P("fuse err:", e)
if sec_out is None:
    comp = Part.makeCompound([h_tube, h_ridge])
    P("compound fallback: valid=%s vol=%.0f" % (comp.isValid(), comp.Volume))
    if comp.isValid() and 18000 < comp.Volume < 24000:
        sec_out = comp; how = "compound"
P("sec_out via %s: %s" % (how, "OK vol=%.0f" % sec_out.Volume if sec_out else "FAILED"))

# ---- inner ring + balls sections (proven cuts) ----
iring = Part.makeCylinder(r_iro, z_seat - z_bot, App.Vector(0, 0, z_bot), App.Vector(0, 0, 1))
iring = iring.cut(Part.makeCylinder(r_ibore, z_seat - z_bot + 2, App.Vector(0, 0, z_bot - 1), App.Vector(0, 0, 1)))
for tor in [Part.makeTorus(r_bc, r_grv, App.Vector(0, 0, z)) for z in rows]:
    iring = iring.cut(tor)
sph = []
for z in rows:
    for j in range(16):
        a = 2*math.pi*j/16
        sph.append(Part.makeSphere(1.5, App.Vector(r_bc*math.cos(a), r_bc*math.sin(a), z)))
balls = Part.makeCompound(sph)
sec_in = iring.cut(box)
sec_bal = balls.cut(box)
P("sec_in valid=%s vol=%.0f | sec_bal valid=%s vol=%.0f" %
  (sec_in.isValid(), sec_in.Volume, sec_bal.isValid(), sec_bal.Volume))

# ---- gates (HANDOFF): out 18k-24k, in 9k-14k, balls 0.5k-4k ----
g1 = sec_out is not None and sec_out.isValid() and 18000 < sec_out.Volume < 24000
g2 = sec_in.isValid() and 9000 < sec_in.Volume < 14000
g3 = sec_bal.isValid() and 500 < sec_bal.Volume < 4000
P("GATES out=%s in=%s bal=%s" % (g1, g2, g3))
if not (g1 and g2 and g3):
    if sec_out is not None:
        sec_out.exportBrep(BP + "pw2_sec_out_fail.brep")
    P("GATE FAIL - no save")
    raise SystemExit(1)

def put(name, shape):
    old = doc.getObject(name)
    if old: doc.removeObject(name)
    ob = doc.addObject("Part::Feature", name)
    ob.Shape = shape
    return ob

put("Section_Bearing_OuterRing_Threaded", sec_out)
put("Section_Bearing_InnerRing_Smooth", sec_in)
put("Section_Bearing_Balls", sec_bal)
doc.recompute()
P("recompute ok, saving...")
doc.save()
P("SAVED (how=%s) t=%.0fs" % (how, time.time()-t0))
