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
r_iro  = 18.5;  r_ibore = 16.0
r_bc = 20.0; r_grv = 2.0
rows = [612 + 9*k for k in range(10)]
torii = [Part.makeTorus(r_bc, r_grv, App.Vector(0, 0, z)) for z in rows]
box = doc.getObject("Section_Cutter").Shape

def half(s):
    return s.cut(box)

def gate(cond, msg):
    P(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        raise SystemExit(1)

# ---- 1) outer ring v2 (corrected winding: root/inner first) ----
tube = Part.makeCylinder(r_tube, z_seat - z_bot, App.Vector(0, 0, z_bot), App.Vector(0, 0, 1))
tube = tube.cut(Part.makeCylinder(r_obore, z_seat - z_bot + 2, App.Vector(0, 0, z_bot - 1), App.Vector(0, 0, 1)))

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
P("loft sections:", nsec)
secs = []
for k in range(nsec):
    w = Part.Wire([Part.LineSegment(pts[i], pts[(i+1) % 4]).toShape() for i in range(4)])
    w.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360.0*k/steps)
    w.translate(App.Vector(0, 0, z0m + k*p/steps))
    secs.append(w)
ridge = Part.makeLoft(secs, True, True)
gate(ridge.isValid() and 9000 < ridge.Volume < 16000, "ridge vol=%.0f" % ridge.Volume)
ridge = ridge.cut(Part.makeBox(300, 300, 60, App.Vector(-150, -150, z_seat))) \
             .cut(Part.makeBox(300, 300, 120, App.Vector(-150, -150, z_bot - 120)))

outer = tube.fuse(ridge)
for tor in torii:
    outer = outer.cut(tor)
outer = outer.removeSplitter()
gate(outer.isValid() and 38000 < outer.Volume < 48000, "outer v2 vol=%.0f t=%.0fs" % (outer.Volume, time.time()-t0))

# ---- 2) inner ring ----
iring = Part.makeCylinder(r_iro, z_seat - z_bot, App.Vector(0, 0, z_bot), App.Vector(0, 0, 1))
iring = iring.cut(Part.makeCylinder(r_ibore, z_seat - z_bot + 2, App.Vector(0, 0, z_bot - 1), App.Vector(0, 0, 1)))
for tor in torii:
    iring = iring.cut(tor)
iring = iring.removeSplitter()
gate(iring.isValid() and 18000 < iring.Volume < 28000, "inner ring vol=%.0f" % iring.Volume)

# ---- 3) balls ----
sph = []
for z in rows:
    for j in range(16):
        a = 2*math.pi*j/16
        sph.append(Part.makeSphere(1.5, App.Vector(r_bc*math.cos(a), r_bc*math.sin(a), z)))
balls = Part.makeCompound(sph)

# ---- 4) sections (cut each with y>0 box) ----
sec_out = half(outer)
gate(sec_out.isValid() and 18000 < sec_out.Volume < 24000, "sec outer vol=%.0f" % sec_out.Volume)
sec_in = half(iring)
gate(sec_in.isValid() and 9000 < sec_in.Volume < 14000, "sec inner vol=%.0f" % sec_in.Volume)
sec_bal = half(balls)
gate(sec_bal.isValid() and 500 < sec_bal.Volume < 4000, "sec balls vol=%.0f" % sec_bal.Volume)
P("all sections ok t=%.0fs" % (time.time()-t0))

# ---- 5) write objects ----
def put(name, shape):
    old = doc.getObject(name)
    if old: doc.removeObject(name)
    ob = doc.addObject("Part::Feature", name)
    ob.Shape = shape
    return ob

o_out  = put("Bearing_OuterRing_Threaded", outer)
o_in   = put("Bearing_InnerRing_Smooth", iring)
o_bal  = put("Bearing_Balls", balls)
s_out  = put("Section_Bearing_OuterRing_Threaded", sec_out)
s_in   = put("Section_Bearing_InnerRing_Smooth", sec_in)
s_bal  = put("Section_Bearing_Balls", sec_bal)

for o in (o_out, o_in, o_bal):
    o.ViewObject.Visibility = False
for s, col in ((s_out, (0.55, 0.57, 0.60)), (s_in, (0.45, 0.47, 0.52)), (s_bal, (0.85, 0.86, 0.88))):
    s.ViewObject.Visibility = True
    try: s.ViewObject.ShapeColor = col
    except Exception: pass

doc.recompute()
allok = all(doc.getObject(n).Shape.isValid() for n in
            ("Bearing_OuterRing_Threaded", "Bearing_InnerRing_Smooth", "Bearing_Balls",
             "Section_Bearing_OuterRing_Threaded", "Section_Bearing_InnerRing_Smooth", "Section_Bearing_Balls"))
gate(allok, "all objects valid")
doc.save()
P("SAVED bearing v2 + sections, t=%.0fs" % (time.time()-t0))
