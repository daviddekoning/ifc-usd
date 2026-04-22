from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateInMemory()
prim = stage.DefinePrim("/TestPrim", "Xform")
imageable = UsdGeom.Imageable(prim)
imageable.CreatePurposeAttr(UsdGeom.Tokens.guide)
imageable.CreateVisibilityAttr(UsdGeom.Tokens.invisible)

print(stage.GetRootLayer().ExportToString())
