import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.placement

model = ifcopenshell.open("ifc-files/Building-Architecture.ifc")
walls = model.by_type("IfcWall")

settings = ifcopenshell.geom.settings()
shape_local = ifcopenshell.geom.create_shape(settings, walls[0])

settings.set(settings.USE_WORLD_COORDS, True)
shape_world = ifcopenshell.geom.create_shape(settings, walls[0])

print("Local verts:", shape_local.geometry.verts[:6])
print("World verts:", shape_world.geometry.verts[:6])

matrix = ifcopenshell.util.placement.get_local_placement(walls[0].ObjectPlacement)
print("Global matrix translations:", matrix[0][3], matrix[1][3], matrix[2][3])
