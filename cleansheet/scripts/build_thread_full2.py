import math, sys, time
import FreeCAD as App
import Part
def P(*a): print(*a); sys.stdout.flush()

t0 = time.time()
PATH = "/home/jagath-srujan/Documents/smart india hackathon/cleansheet/PGK_CleanSheet.FCStd"
doc = App.openDocument(PATH)
sh = doc.getObject("Shell_Body_155")
body = sh.Shape
P("opened: valid=%s vol=%.3f L" % (body.isValid(), body.Volume/1e6))

z_bot, z_seat = 606.0, 696.0
R_crest, R_root = 24.0, 25.45
p = 25.4/12.0
z_start = z_bot - 3.0
H = (z_seat + 3.0) - z_start
half_c, depth = 0.25, 1.30
half_r = half_c + depth*math.tan(math.radians(30))
pts = [App.Vector(R_crest, 0, z_start - half_c),
       App.Vector(R_crest, 0, z_start + half_c),
       App.Vector(R_crest + depth, 0, z_start + half_r),
       App.Vector(R_crest + depth, 0, z_start - half_r)]

steps = 8
nsec = int(H/p*steps) + 2
secs = []
for k in range(nsec):
    w = Part.Wire([Part.LineSegment(pts[i], pts[(i+1)%4]).toShape() for i in range(4)])
    w.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 360.0*k/steps)
    w.translate(App.Vector(0,0,k*p/steps))
    secs.append(w)
ridge = Part.makeLoft(secs, True, True)
P("ridge: valid=%s vol=%.0f" % (ridge.isValid(), ridge.Volume))
if not (ridge.isValid() and 7000 < ridge.Volume < 25000):
    P("GATE FAIL ridge"); raise SystemExit(1)

trimmer = Part.makeBox(300, 300, 60, App.Vector(-150,-150,z_seat))
ridge = ridge.cut(trimmer)
if not ridge.isValid(): P("GATE FAIL trim"); raise SystemExit(1)

zone = Part.makeCylinder(R_root, (z_seat - z_bot) + 10, App.Vector(0,0,z_bot), App.Vector(0,0,1))
newbody = body.cut(zone).fuse(ridge)
cham = Part.makeCone(R_root, 27.95, 2.5, App.Vector(0,0,z_seat-2.5), App.Vector(0,0,1))
newbody = newbody.cut(cham).removeSplitter()

# --- correct gates: thread material present in ring band, bore open at crest ---
ring = Part.makeCylinder(R_root, 80, App.Vector(0,0,610)).cut(Part.makeCylinder(R_crest, 80, App.Vector(0,0,610)))
thread_mat = newbody.common(ring).Volume
core = Part.makeCylinder(R_crest - 0.2, 80, App.Vector(0,0,610))
bore_open = newbody.common(core).Volume
P("thread material in ring band: %.0f mm3 (expect >5000)" % thread_mat)
P("material inside crest bore: %.1f mm3 (expect ~0)" % bore_open)
P("body: %.3f -> %.3f L, valid=%s, t=%.0fs" % (body.Volume/1e6, newbody.Volume/1e6, newbody.isValid(), time.time()-t0))
ok = newbody.isValid() and 11.6e6 < newbody.Volume < 11.8e6 and thread_mat > 5000 and bore_open < 50
P("gate:", "PASS" if ok else "FAIL")
if ok:
    sh.Shape = newbody
    doc.recompute()
    doc.save()
    P("SAVED full-depth thread")
else:
    P("aborted")
