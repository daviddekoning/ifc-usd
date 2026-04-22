# /// script
# requires-python = ">=3.13"
# dependencies = ["ifcopenshell", "usd-core"]
# ///
import ifcopenshell
import ifcopenshell.geom

try:
    model = ifcopenshell.open("ifc-files/Building-Architecture.ifc")
    walls = model.by_type("IfcWall")

    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_PYTHON_OPENCASCADE, True)
    shape = ifcopenshell.geom.create_shape(settings, walls[0])
    
    print("verts", len(shape.geometry.verts))
    print("faces", len(shape.geometry.faces))
except Exception as e:
    print(e)
