import math, sys, time
import FreeCAD as App
import Part
def P(*a): print(*a); sys.stdout.flush()

t0 = time.time()
PATH = "/home/jagath-srujan/Documents/smart india hackathon/cleansheet/PGK_CleanSheet.FCStd"
doc = App.openDocument(PATH)
sh = doc.getObject("Shell_Body_155")
body = sh.Shape
P("opened: valid=%s vol=%.2f L" % (body.isValid(), body.Volume/1e6))

# FULL-DEPTH thread: cavity z=606..696, all threaded
z_bot, z_seat = 606.0, 696.0
R_crest, R_root = 24.0, 25.45
p = 25.4/12.0
z_start = z_bot - 3.0
H = (z_seat + 3.0) - z_start   # 96
half_c, depth = 0.25, 1.30
half_r = half_c + depth*math.tan(math.radians(30))
pts = [App.Vector(R_crest, 0, z_start - half_c),
       App.Vector(R_crest, 0, z_start + half_c),
       App.Vector(R_crest + depth, 0, z_start + half_r),
       App.Vector(R_crest + depth, 0, z_start - half_r)]

steps = 8
nsec = int(H/p*steps) + 2
P("loft sections:", nsec)
secs = []
for k in range(nsec):
    w = Part.Wire([Part.LineSegment(pts[i], pts[(i+1)%4]).toShape() for i in range(4)])
    w.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 360.0*k/steps)
    w.translate(App.Vector(0,0,k*p/steps))
    secs.append(w)
ridge = Part.makeLoft(secs, True, True)
P("ridge: valid=%s vol=%.0f t=%.0fs" % (ridge.isValid(), ridge.Volume, time.time()-t0))
if not (ridge.isValid() and 7000 < ridge.Volume < 25000):
    P("GATE FAIL ridge"); raise SystemExit(1)

trimmer = Part.makeBox(300, 300, 60, App.Vector(-150,-150,z_seat))
ridge = ridge.cut(trimmer)
P("trimmed: vol=%.0f valid=%s" % (ridge.Volume, ridge.isValid()))
if not ridge.isValid(): P("GATE FAIL trim"); raise SystemExit(1)

zone = Part.makeCylinder(R_root, (z_seat - z_bot) + 10, App.Vector(0,0,z_bot), App.Vector(0,0,1))
newbody = body.cut(zone).fuse(ridge)
cham = Part.makeCone(R_root, 27.95, 2.5, App.Vector(0,0,z_seat-2.5), App.Vector(0,0,1))
newbody = newbody.cut(cham).removeSplitter()

dv = newbody.Volume - body.Volume
P("body: %.3f -> %.3f L (delta %.2f cm3) t=%.0fs" % (body.Volume/1e6, newbody.Volume/1e6, dv/1000.0, time.time()-t0))
ok = newbody.isValid() and 11.5e6 < newbody.Volume < 12.0e6 and 6000 < dv < 25000
P("gate:", "PASS" if ok else "FAIL")
if ok:
    sh.Shape = newbody
    doc.recompute()
    doc.save()
    P("SAVED full-depth thread")
else:
    P("aborted")
