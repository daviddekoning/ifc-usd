import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.placement

model = ifcopenshell.open("ifc-files/Building-Architecture.ifc")
print("Unit scale:", ifcopenshell.util.unit.calculate_unit_scale(model))
print("Global scaling:", ifcopenshell.util.placement.get_local_placement(model.by_type("IfcWall")[0].ObjectPlacement))
