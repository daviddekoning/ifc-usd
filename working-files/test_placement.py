import ifcopenshell
import ifcopenshell.util.placement
import numpy as np

model = ifcopenshell.open("ifc-files/Building-Architecture.ifc")
walls = model.by_type("IfcWall")
wall = walls[0]

if hasattr(wall, "ObjectPlacement") and wall.ObjectPlacement:
    matrix = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
    print("Wall global matrix:", matrix)

