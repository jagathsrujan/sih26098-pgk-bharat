import math, sys, time
import FreeCAD as App
import Part
def P(*a): print(*a); sys.stdout.flush()

t0 = time.time()
PATH = "/home/jagath-srujan/Documents/smart india hackathon/cleansheet/PGK_CleanSheet.FCStd"
doc = App.openDocument(PATH)

z_bot, z_seat = 606.0, 696.0
p = 25.4/12.0

# geometry: outer ring male thread crest r25.35 root r24.10, race bore r21.5
# inner ring: OD r18.5, smooth bore r16.0; balls r1.5 at r20.0, 10 rows x 16
r_tube = 24.10; r_obore = 21.5
r_iro  = 18.5;  r_ibore = 16.0
r_ball = 1.5;   r_bc = 20.0
r_grv  = 2.0
rows  = [612 + 9*k for k in range(10)]
nball = 16

torii = [Part.makeTorus(r_bc, r_grv, App.Vector(0, 0, z)) for z in rows]

# 1) outer ring
tube = Part.makeCylinder(r_tube, z_seat - z_bot, App.Vector(0, 0, z_bot), App.Vector(0, 0, 1))
tube = tube.cut(Part.makeCylinder(r_obore, z_seat - z_bot + 2, App.Vector(0, 0, z_bot - 1), App.Vector(0, 0, 1)))

half_c, depth = 0.20, 1.25
half_r = half_c + depth * math.tan(math.radians(30))
r_crest, r_root = 25.35, 25.35 - depth
z0m = (603.0 + p/2.0) - 2.0*p          # phase-aligned with female groove
H = (z_seat + 3.0) - z0m
pts = [App.Vector(r_crest, 0, -half_c), App.Vector(r_crest, 0, half_c),
       App.Vector(r_root, 0, half_r), App.Vector(r_root, 0, -half_r)]
secs = []
steps = 48
nsec = int(H / (p/steps)) + 2
P("male thread sections:", nsec)
for k in range(nsec):
    w = Part.Wire([Part.LineSegment(pts[i], pts[(i+1) % 4]).toShape() for i in range(4)])
    w.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360.0*k/steps)
    w.translate(App.Vector(0, 0, z0m + k*p/steps))
    secs.append(w)
ridge = Part.makeLoft(secs, True, True)
cut_hi  = Part.makeBox(300, 300, 60, App.Vector(-150, -150, z_seat))
cut_lo  = Part.makeBox(300, 300, 120, App.Vector(-150, -150, z_bot - 120))
ridge = ridge.cut(cut_hi).cut(cut_lo)
outer = tube.fuse(ridge)
for tor in torii:
    outer = outer.cut(tor)
outer = outer.removeSplitter()
P("outer ring: valid=%s vol=%.0f t=%.0fs" % (outer.isValid(), outer.Volume, time.time()-t0))

# 2) inner ring (smooth bore)
iring = Part.makeCylinder(r_iro, z_seat - z_bot, App.Vector(0, 0, z_bot), App.Vector(0, 0, 1))
iring = iring.cut(Part.makeCylinder(r_ibore, z_seat - z_bot + 2, App.Vector(0, 0, z_bot - 1), App.Vector(0, 0, 1)))
for tor in torii:
    iring = iring.cut(tor)
iring = iring.removeSplitter()
P("inner ring: valid=%s vol=%.0f" % (iring.isValid(), iring.Volume))

# 3) balls compound
sph = []
for z in rows:
    for j in range(nball):
        a = 2*math.pi*j/nball
        sph.append(Part.makeSphere(r_ball, App.Vector(r_bc*math.cos(a), r_bc*math.sin(a), z)))
balls = Part.makeCompound(sph)
P("balls: %d" % len(sph))

# save as objects
for name, shape in (("Bearing_OuterRing_Threaded", outer),
                    ("Bearing_InnerRing_Smooth", iring)):
    old = doc.getObject(name)
    if old: doc.removeObject(name)
    ob = doc.addObject("Part::Feature", name)
    ob.Shape = shape
old = doc.getObject("Bearing_Balls")
if old: doc.removeObject(old)
ob = doc.addObject("Part::Feature", "Bearing_Balls")
ob.Shape = balls

try:
    doc.getObject("Bearing_OuterRing_Threaded").ViewObject.ShapeColor = (0.55, 0.57, 0.60)
    doc.getObject("Bearing_InnerRing_Smooth").ViewObject.ShapeColor = (0.45, 0.47, 0.52)
    doc.getObject("Bearing_Balls").ViewObject.ShapeColor = (0.85, 0.86, 0.88)
except Exception:
    pass

doc.recompute()
ok = all(doc.getObject(n).Shape.isValid() for n in
         ("Bearing_OuterRing_Threaded", "Bearing_InnerRing_Smooth", "Bearing_Balls"))
P("validity:", ok)
if ok:
    doc.save()
    P("SAVED bearing parts, t=%.0fs" % (time.time()-t0))
else:
    P("aborted")
