import ifcopenshell
import ifcopenshell.geom

model = ifcopenshell.open("ifc-files/Building-Architecture.ifc")
walls = model.by_type("IfcWall")

settings = ifcopenshell.geom.settings()
shape_local = ifcopenshell.geom.create_shape(settings, walls[0])

print("Shape matrix:", shape_local.transformation.matrix.data)
