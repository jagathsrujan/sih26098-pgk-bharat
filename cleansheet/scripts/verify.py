import FreeCAD as App
doc = App.openDocument("/home/jagath-srujan/Documents/smart india hackathon/cleansheet/PGK_CleanSheet.FCStd")
sh = doc.getObject("Shell_Body_155")
b = sh.Shape
bspl = sum(1 for f in b.Faces if "BSpline" in type(f.Surface).__name__)
print("RESULT valid=%s vol=%.3f L faces=%d bspline=%d" % (b.isValid(), b.Volume/1e6, len(b.Faces), bspl))
