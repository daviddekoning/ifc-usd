# /// script
# requires-python = ">=3.13"
# dependencies = ["usd-core", "ifcopenshell", "numpy"]
# ///
import ifcopenshell
import ifcopenshell.util.placement
import ifcopenshell.util.unit
import numpy as np
from pxr import Usd, UsdGeom, Sdf, Gf

model = ifcopenshell.open("ifc-files/Building-Architecture.ifc")
unit_scale = ifcopenshell.util.unit.calculate_unit_scale(model)

walls = model.by_type("IfcWall")
wall = walls[0]

matrix_np = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
# Scale translation by unit_scale
matrix_np[0:3, 3] *= unit_scale

# Convert numpy array (M * v) to row-major tuple for Gf.Matrix4d (v * M)
# If matrix_np is a standard transformation matrix:
# [R R R Tx]
# [R R R Ty]
# [R R R Tz]
# [0 0 0 1 ]
# We need to transpose it:
matrix_transposed = matrix_np.transpose()
matrix_tuple = tuple(matrix_transposed.flatten())

gf_mat = Gf.Matrix4d(*matrix_tuple)
print("Gf Matrix:", gf_mat)
print("Translations in Gf Matrix:", gf_mat.ExtractTranslation())
