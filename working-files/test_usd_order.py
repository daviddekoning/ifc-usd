# /// script
# requires-python = ">=3.13"
# dependencies = ["usd-core"]
# ///
from pxr import Gf

child_global = Gf.Matrix4d().SetTranslate(Gf.Vec3d(10, 0, 0))
parent_global = Gf.Matrix4d().SetTranslate(Gf.Vec3d(5, 0, 0))

# We want child relative such that: child_rel * parent_global = child_global
# So child_rel = child_global * parent_global_inv
child_rel = child_global * parent_global.GetInverse()

print("Child relative translation:", child_rel.ExtractTranslation())
