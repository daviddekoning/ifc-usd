#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "ifcopenshell",
#     "pydantic",
#     "usd-core",
# ]
# ///
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.placement
import ifcopenshell.util.unit
import numpy as np
from pxr import Usd, UsdGeom, Sdf, Vt, Gf
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Configure geometry settings for ifcopenshell
GEOM_SETTINGS = ifcopenshell.geom.settings()

# Data models
class IfcNode(BaseModel):
    id: str
    name: str
    ifc_type: str
    rel_type: str  # "decomposition" or "containment" or "root"
    start_collapsed: bool = False
    children: List["IfcNode"] = []
    attributes: Dict[str, Any] = {}
    relationships: List[Dict[str, Any]] = []
    type_properties: List[Dict[str, Any]] = []
    pset_properties: List[Dict[str, Any]] = []
    template_properties: List[Dict[str, Any]] = []
    placement_type: Optional[str] = None  # For placement nodes: IfcLocalPlacement, IfcGridPlacement, etc.
    verts: List[Any] = []
    face_counts: List[int] = []
    face_indices: List[int] = []
    global_matrix: Optional[List[float]] = None

def sanitize_value(value):
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    elif isinstance(value, (list, tuple)):
        return [sanitize_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: sanitize_value(v) for k, v in value.items()}
    elif hasattr(value, "is_a"):  # Check if it's an IFC entity
        # Return a simple representation, e.g., String or ID
        return f"[{value.is_a()}] (ID: {value.id()})"
    else:
        return str(value)


def get_attributes(entity):
    attrs = {}
    if hasattr(entity, "get_info"):
        try:
            # get_info() returns a dict where values might be other IFC entities
            raw_attrs = entity.get_info()
            # Clean up unneeded keys
            raw_attrs.pop("type", None)
            raw_attrs.pop("id", None)

            # Sanitize values for JSON serialization
            for k, v in raw_attrs.items():
                attrs[k] = sanitize_value(v)
        except:
            pass
    return attrs


def get_relationships(model, entity):
    """
    Get all relationships that this entity is part of.
    This includes inverse attributes that point to IfcRelationship entities.
    """
    rels = []
    try:
        # get_inverse returns entities that reference this entity
        inverses = model.get_inverse(entity)
        for inv in inverses:
            if inv.is_a("IfcRelationship"):
                rel_data = {
                    "id": inv.id(),
                    "type": inv.is_a(),
                    "attributes": get_attributes(inv),
                }
                rels.append(rel_data)
    except Exception as e:
        print(f"Error getting relationships for {entity}: {e}")
    return rels


def get_prop_value(prop):
    """Extract value from IfcProperty or IfcQuantity"""
    if prop.is_a("IfcPropertySingleValue"):
        val = prop.NominalValue
        return val.wrappedValue if val else None
    elif prop.is_a("IfcQuantityLength"):
        return prop.LengthValue
    elif prop.is_a("IfcQuantityArea"):
        return prop.AreaValue
    elif prop.is_a("IfcQuantityVolume"):
        return prop.VolumeValue
    elif prop.is_a("IfcQuantityCount"):
        return prop.CountValue
    elif prop.is_a("IfcQuantityWeight"):
        return prop.WeightValue
    elif prop.is_a("IfcSimpleProperty"):
        # PropertyEnumeratedValue, PropertyBoundedValue etc fallback
        return str(prop)
    return None


def get_detailed_properties(model, entity):
    """
    Extracts structured properties for Type, Properties (Psets), and Templates.
    """
    type_props = []
    pset_props = []
    template_props = []

    # Check for IsDefinedBy relationships
    try:
        # We look at inverses to find IfcRelDefinesBy...
        # Or commonly accessed via .IsDefinedBy if available in schema/wrapper
        # But .IsDefinedBy might not cover everything or be compliant in all schemas
        # Let's use get_inverse to be safe and comprehensive
        inverses = model.get_inverse(entity)

        for rel in inverses:
            # 1. IfcRelDefinesByType
            if rel.is_a("IfcRelDefinesByType"):
                relating_type = rel.RelatingType
                if relating_type:
                    # Properties of the Type Object itself
                    type_attrs = get_attributes(relating_type)
                    type_props.append(
                        {
                            "group": f"Type: {relating_type.Name or relating_type.is_a()}",
                            "properties": type_attrs,
                        }
                    )

                    # Psets attached to the Type
                    if (
                        hasattr(relating_type, "HasPropertySets")
                        and relating_type.HasPropertySets
                    ):
                        for pset in relating_type.HasPropertySets:
                            props = {}
                            if pset.is_a("IfcPropertySet"):
                                for prop in pset.HasProperties:
                                    props[prop.Name] = sanitize_value(
                                        get_prop_value(prop)
                                    )
                                type_props.append(
                                    {
                                        "group": f"Type PSet: {pset.Name}",
                                        "properties": props,
                                    }
                                )

            # 2. IfcRelDefinesByProperties
            elif rel.is_a("IfcRelDefinesByProperties"):
                defn = rel.RelatingPropertyDefinition
                if defn.is_a("IfcPropertySet"):
                    props = {}
                    for prop in defn.HasProperties:
                        props[prop.Name] = sanitize_value(get_prop_value(prop))
                    pset_props.append({"group": defn.Name, "properties": props})

                    # Check for Template definition for this PSet
                    # IfcRelDefinesByTemplate links IfcPropertySet to IfcPropertySetTemplate
                    # We check inverses of the PSet
                    pset_inverses = model.get_inverse(defn)
                    for pset_inv in pset_inverses:
                        if pset_inv.is_a("IfcRelDefinesByTemplate"):
                            template = pset_inv.RelatingTemplate
                            if template:
                                # Add the same properties but grouped by Template
                                template_props.append(
                                    {
                                        "group": f"Template: {template.Name}",
                                        "properties": props,  # Reuse the extracted properties
                                    }
                                )

                elif defn.is_a("IfcElementQuantity"):
                    props = {}
                    for q in defn.Quantities:
                        props[q.Name] = sanitize_value(get_prop_value(q))
                    pset_props.append({"group": defn.Name, "properties": props})

            # 3. IfcRelDefinesByTemplate (Directly on object - rare but possible for definitions)
            elif rel.is_a("IfcRelDefinesByTemplate"):
                # This would mean the object itself is being defined by a template
                template = rel.RelatingTemplate
                if template:
                    template_props.append(
                        {
                            "group": f"Direct Template: {template.Name}",
                            "properties": {
                                "info": "Object is directly defined by this template"
                            },
                        }
                    )

    except Exception as e:
        print(f"Error extraction detailed properties: {e}")

    return type_props, pset_props, template_props


def build_hierarchy(model, entity, rel_type="decomposition", recursive=True) -> IfcNode:
    name = entity.Name if hasattr(entity, "Name") and entity.Name else "(No Name)"
    global_id = entity.GlobalId if hasattr(entity, "GlobalId") else ""
    ifc_type = entity.is_a()

    type_p, pset_p, templ_p = get_detailed_properties(model, entity)

    global_matrix = None
    try:
        if hasattr(entity, "ObjectPlacement") and entity.ObjectPlacement:
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(model)
            matrix_np = ifcopenshell.util.placement.get_local_placement(entity.ObjectPlacement)
            matrix_np[0:3, 3] *= unit_scale
            # transpose for row-major format suitable for USD's Gf.Matrix4d
            global_matrix = matrix_np.transpose().flatten().tolist()
    except Exception as e:
        print(f"Error calculating placement for {entity}: {e}")

    node = IfcNode(
        id=global_id if global_id else str(entity.id()),
        name=name,
        ifc_type=ifc_type,
        rel_type=rel_type,
        children=[],
        attributes=get_attributes(entity),
        relationships=get_relationships(model, entity),
        type_properties=type_p,
        pset_properties=pset_p,
        template_properties=templ_p,
        global_matrix=global_matrix,
    )

    try:
        if hasattr(entity, "Representation") and entity.Representation:
            shape = ifcopenshell.geom.create_shape(GEOM_SETTINGS, entity)
            vertices = shape.geometry.verts
            faces = shape.geometry.faces
            node.verts = [(vertices[i], vertices[i+1], vertices[i+2]) for i in range(0, len(vertices), 3)]
            node.face_counts = [3] * (len(faces) // 3)
            node.face_indices = list(faces)
    except Exception:
        pass

    if recursive:
        # Handle spatial decomposition (IfcRelAggregates) and nesting (IfcRelNests)
        if hasattr(entity, "IsDecomposedBy"):
            for rel in entity.IsDecomposedBy:
                if rel.is_a("IfcRelAggregates") or rel.is_a("IfcRelNests"):
                    for child in rel.RelatedObjects:
                        node.children.append(
                            build_hierarchy(
                                model, child, rel_type="decomposition", recursive=True
                            )
                        )

        # Handle contained elements (IfcBuildingStorey -> IfcWall, IfcDoor, etc.)
        if hasattr(entity, "ContainsElements"):
            for rel in entity.ContainsElements:
                if rel.is_a("IfcRelContainedInSpatialStructure"):
                    for element in rel.RelatedElements:
                        node.children.append(
                            build_hierarchy(
                                model, element, rel_type="containment", recursive=True
                            )
                        )

    return node


def build_group_hierarchy(model):
    """Builds the Groups subtree."""
    groups_root = IfcNode(
        id="groups-root",
        name="",
        ifc_type="Groups",
        rel_type="category",
        children=[],
    )

    # Simple Groups (IfcGroup and subclasses, excluding structural systems if desired, but user said "list of groups")
    # IfcSystem, IfcZone are also groups.
    all_groups = model.by_type("IfcGroup")
    for group in all_groups:
        group_node = build_hierarchy(model, group, rel_type="group", recursive=False)

        # Manually add assigned products
        if hasattr(group, "IsGroupedBy"):
            for rel in group.IsGroupedBy:  # IfcRelAssignsToGroup
                if hasattr(rel, "RelatedObjects"):
                    for obj in rel.RelatedObjects:
                        group_node.children.append(
                            build_hierarchy(
                                model, obj, rel_type="assigned", recursive=False
                            )
                        )

        groups_root.children.append(group_node)

    return groups_root


def build_type_hierarchy(model):
    """Builds the Types subtree."""
    types_root = IfcNode(
        id="types-root",
        name="",
        ifc_type="Types",
        rel_type="category",
        children=[],
    )

    # Type Definitions
    all_types = model.by_type("IfcTypeProduct")  # Focusing on products
    for ifc_type in all_types:
        type_node = build_hierarchy(model, ifc_type, rel_type="type", recursive=False)

        # content (Types defines objects)
        if hasattr(ifc_type, "Types"):  # IfcRelDefinesByType inverse attribute
            for rel in ifc_type.Types:
                if hasattr(rel, "RelatedObjects"):
                    for obj in rel.RelatedObjects:
                        type_node.children.append(
                            build_hierarchy(
                                model, obj, rel_type="defined_by", recursive=False
                            )
                        )

        types_root.children.append(type_node)

    return types_root


def build_material_hierarchy(model):
    """Builds the Materials subtree."""
    materials_root = IfcNode(
        id="materials-root",
        name="",
        ifc_type="Materials",
        rel_type="category",
        children=[],
    )

    # We iterate IfcRelAssociatesMaterial to find materials actually in use
    rels = model.by_type("IfcRelAssociatesMaterial")

    # Group by material
    material_map = {}  # material_id -> {monitor: node, objects: []}

    for rel in rels:
        mat = rel.RelatingMaterial
        if not mat:
            continue

        mat_id = mat.id()
        if mat_id not in material_map:
            # Create node for this material definition
            # Rel type is "material_source" - slightly different usage
            material_map[mat_id] = build_hierarchy(
                model, mat, rel_type="material", recursive=False
            )

        # Add objects
        if hasattr(rel, "RelatedObjects"):
            for obj in rel.RelatedObjects:
                child_node = build_hierarchy(
                    model, obj, rel_type="associated_with", recursive=False
                )
                material_map[mat_id].children.append(child_node)

    # Add all unique materials to root
    for node in material_map.values():
        materials_root.children.append(node)

    return materials_root


def build_placement_hierarchy(model):
    """
    Builds the Placements subtree. Returns a list of root placement nodes.
    
    The hierarchy shows IFC objects (not placement objects) arranged according to
    their placement relationships. If object A is placed by IfcLocalPlacement X,
    and object B is placed by IfcLocalPlacement Y which is relative to X,
    then B appears as a child of A in this hierarchy.
    """
    # Find all IfcObjectPlacement subtypes
    all_placements = model.by_type("IfcObjectPlacement")

    # Map placement ID -> the product that uses it (each placement is used by one object)
    placement_to_product = {}
    for p in all_placements:
        inverses = model.get_inverse(p)
        products = [inv for inv in inverses if inv.is_a("IfcProduct")]
        if products:
            # Typically only one product per placement
            placement_to_product[p.id()] = products[0]

    # Build nodes for products that have placements
    product_nodes = {}
    for p in all_placements:
        product = placement_to_product.get(p.id())
        if not product:
            # Skip placements that don't place any object
            continue
        
        prod_name = product.Name if hasattr(product, "Name") and product.Name else "(No Name)"
        global_id = product.GlobalId if hasattr(product, "GlobalId") else ""
        
        type_p, pset_p, templ_p = get_detailed_properties(model, product)
        
        node = IfcNode(
            id=global_id if global_id else str(product.id()),
            name=prod_name,
            ifc_type=product.is_a(),
            rel_type="placement",
            placement_type=p.is_a(),
            children=[],
            attributes=get_attributes(product),
            relationships=get_relationships(model, product),
            type_properties=type_p,
            pset_properties=pset_p,
            template_properties=templ_p,
        )
        # Key by placement ID since that's how we'll build the hierarchy
        product_nodes[p.id()] = node

    # Build the hierarchy based on placement parent-child relationships
    roots = []
    for p in all_placements:
        if p.id() not in product_nodes:
            # This placement doesn't have an associated product, skip
            continue
        
        node = product_nodes[p.id()]
        
        # Check if this placement has a parent placement
        rel_to = getattr(p, "PlacementRelTo", None)
        
        # Walk up the placement chain to find a parent that has a product
        parent_found = False
        current_parent = rel_to
        while current_parent:
            if current_parent.id() in product_nodes:
                # Found a parent placement that has an associated product
                parent_node = product_nodes[current_parent.id()]
                parent_node.children.append(node)
                parent_found = True
                break
            # Continue up the chain
            current_parent = getattr(current_parent, "PlacementRelTo", None)
        
        if not parent_found:
            roots.append(node)

    return roots

import json
import sys
import argparse

def convert_ifc_to_usd(ifc_file: str, output_usd_path: str = None):
    print(f"Loading IFC file: {ifc_file}")
    model = ifcopenshell.open(ifc_file)

    # Build the main hierarchy starting from IfcProject
    projects = model.by_type("IfcProject")
    if not projects:
        print("No IfcProject found in the file.")
        sys.exit(1)

    project_node = build_hierarchy(model, projects[0])

    # Build additional hierarchies
    groups_node = build_group_hierarchy(model)
    types_node = build_type_hierarchy(model)
    materials_node = build_material_hierarchy(model)
    placements_nodes = build_placement_hierarchy(model)

    # Combine everything into a single structure
    output = {
        "project": project_node.model_dump(),
        "groups": groups_node.model_dump(),
        "types": types_node.model_dump(),
        "materials": materials_node.model_dump(),
        "placements": [i.model_dump() for i in placements_nodes],
    }

    # Generate USD
    usd_file = output_usd_path if output_usd_path else ifc_file.replace(".ifc", ".usda")
    stage = Usd.Stage.CreateNew(usd_file)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    
    # Calculate scale to meters for USD metadata
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(model)
    UsdGeom.SetStageMetersPerUnit(stage, unit_scale)
    
    stage.SetMetadata("customLayerData", {"ifc:schema": "IFC4x3"})
    stage.SetMetadata("documentation", f"Translated from {ifc_file.split('/')[-1]} using IFC to USD pragmatic mapping spec")
    
    import re
    def sanitize_name(name: str):
        # Must start with letter or underscore, and contain only letters numbers and underscores
        safe = re.sub(r'[^a-zA-Z0-9_]+', '_', name)
        if not safe or safe[0].isdigit():
            safe = "_" + safe
        return safe

    # Root Scope "My_Project"
    safe_project_name = sanitize_name(project_node.name)
    project_prim = stage.DefinePrim(f"/{safe_project_name}", "Scope")
    stage.SetDefaultPrim(project_prim)
    Usd.ModelAPI(project_prim).SetKind("group")
    project_prim.SetMetadata("documentation", "IFC Project")
    project_prim.CreateAttribute("ifc:globalId", Sdf.ValueTypeNames.String).Set(project_node.id)
    project_prim.CreateAttribute("ifc:name", Sdf.ValueTypeNames.String).Set(project_node.name)
    project_prim.CreateAttribute("ifc:ifcClass", Sdf.ValueTypeNames.Token).Set(project_node.ifc_type)

    def write_properties(prim, node: IfcNode):
        for pset in node.pset_properties:
            group_name = sanitize_name(pset.get("group", "UnknownPset"))
            for prop_name, prop_val in pset.get("properties", {}).items():
                safe_prop_name = sanitize_name(prop_name)
                attr_name = f"{group_name}:{safe_prop_name}"
                
                # Determine Sdf type
                sdf_type = Sdf.ValueTypeNames.String
                if isinstance(prop_val, bool):
                    sdf_type = Sdf.ValueTypeNames.Bool
                elif isinstance(prop_val, int):
                    sdf_type = Sdf.ValueTypeNames.Int
                elif isinstance(prop_val, float):
                    sdf_type = Sdf.ValueTypeNames.Double
                    
                prim.CreateAttribute(attr_name, sdf_type).Set(prop_val if not sdf_type == Sdf.ValueTypeNames.String else str(prop_val))

    write_properties(project_prim, project_node)

    # 1. Build Types scope
    object_to_types = {}
    types_scope = stage.DefinePrim("/Types", "Scope")
    types_scope.SetMetadata("documentation", "IFC Type Objects")
    Usd.ModelAPI(types_scope).SetKind("group")

    for type_node in types_node.children:
        type_safe_name = sanitize_name(type_node.name)
        if type_safe_name == "_":
            type_safe_name = sanitize_name(f"{type_node.ifc_type}_{type_node.id[-6:]}")
        type_path = f"/Types/{type_safe_name}"
        
        type_prim = stage.CreateClassPrim(type_path)
        type_prim.SetTypeName("Xform")
        Usd.ModelAPI(type_prim).SetKind("component")
        
        type_prim.CreateAttribute("ifc:globalId", Sdf.ValueTypeNames.String).Set(type_node.id)
        type_prim.CreateAttribute("ifc:name", Sdf.ValueTypeNames.String).Set(type_node.name)
        type_prim.CreateAttribute("ifc:ifcClass", Sdf.ValueTypeNames.Token).Set(type_node.ifc_type)
        
        write_properties(type_prim, type_node)

        # The children of the type node are the elements that are defined by this type
        for obj_node in type_node.children:
            if obj_node.id not in object_to_types:
                object_to_types[obj_node.id] = []
            if type_path not in object_to_types[obj_node.id]:
                object_to_types[obj_node.id].append(type_path)

    # 2. Build Materials scope
    object_to_materials = {}
    materials_scope = stage.DefinePrim("/Materials", "Scope")
    materials_scope.SetMetadata("documentation", "IFC Materials")
    
    for mat_node in materials_node.children:
        mat_safe_name = sanitize_name(mat_node.name)
        mat_path = f"/Materials/{mat_safe_name}"
        # In USD, materials are usually created with type "Material"
        mat_prim = stage.DefinePrim(mat_path, "Material")
        mat_prim.CreateAttribute("ifc:globalId", Sdf.ValueTypeNames.String).Set(mat_node.id)
        mat_prim.CreateAttribute("ifc:name", Sdf.ValueTypeNames.String).Set(mat_node.name)
        mat_prim.CreateAttribute("ifc:ifcClass", Sdf.ValueTypeNames.Token).Set(mat_node.ifc_type)

        # The children of the material node are the elements that use this material
        for obj_node in mat_node.children:
            if obj_node.id not in object_to_materials:
                object_to_materials[obj_node.id] = []
            if mat_path not in object_to_materials[obj_node.id]:
                object_to_materials[obj_node.id].append(mat_path)

    def write_stage_prims(node: IfcNode, parent_path: str, parent_global_matrix_list: Optional[List[float]] = None, seen_paths: Optional[set] = None):
        if seen_paths is None:
            seen_paths = set([parent_path])
            
        for child in node.children:
            child_safe_name = sanitize_name(child.name)
            if not child_safe_name or child_safe_name == "_":
                child_safe_name = sanitize_name(f"{child.ifc_type}_{child.id[-6:]}")
                
            child_path = f"{parent_path}/{child_safe_name}"
            original_path = child_path
            counter = 1
            while child_path in seen_paths:
                child_path = f"{original_path}_{counter}"
                counter += 1
            seen_paths.add(child_path)

            # IfcBuildingStorey, IfcSite, IfcBuilding, etc -> Xform
            prim = stage.DefinePrim(child_path, "Xform")
            Usd.ModelAPI(prim).SetKind("group")
            prim.CreateAttribute("ifc:globalId", Sdf.ValueTypeNames.String).Set(child.id)
            prim.CreateAttribute("ifc:name", Sdf.ValueTypeNames.String).Set(child.name)
            prim.CreateAttribute("ifc:ifcClass", Sdf.ValueTypeNames.Token).Set(child.ifc_type)
            
            if child.ifc_type in ("IfcSpace", "IfcSpatialZone"):
                imageable = UsdGeom.Imageable(prim)
                imageable.CreatePurposeAttr(UsdGeom.Tokens.guide)
                imageable.CreateVisibilityAttr(UsdGeom.Tokens.invisible)
                
            if child.ifc_type.lower() == "ifcbuildingelementproxy":
                obj_type = str(child.attributes.get("ObjectType") or child.attributes.get("objectType") or "")
                if obj_type.lower() == "origin":
                    imageable = UsdGeom.Imageable(prim)
                    imageable.CreateVisibilityAttr(UsdGeom.Tokens.invisible)

            # Apply hierarchical transform based on global placement matrix
            child_matrix_list = child.global_matrix if child.global_matrix else parent_global_matrix_list
            if child_matrix_list:
                child_gf_matrix = Gf.Matrix4d(*child_matrix_list)
                if parent_global_matrix_list:
                    parent_gf_matrix = Gf.Matrix4d(*parent_global_matrix_list)
                    # To retrieve the child's local transform relative to its USD scene parent:
                    # Target transform = child_global * parent_global.GetInverse()
                    rel_gf_matrix = child_gf_matrix * parent_gf_matrix.GetInverse()
                else:
                    rel_gf_matrix = child_gf_matrix
                
                xformable = UsdGeom.Xformable(prim)
                xform_op = xformable.AddTransformOp()
                xform_op.Set(rel_gf_matrix)

            write_properties(prim, child)

            # Record decomposition structure
            if child.rel_type == "decomposition":
                rel = prim.CreateRelationship("ifc:decomposes", False)
                rel.AddTarget(parent_path)
            elif child.rel_type == "containment":
                rel = prim.CreateRelationship("ifc:containedInSpatialStructure", False)
                rel.AddTarget(parent_path)

            # Record type relationships (references)
            if child.id in object_to_types:
                for type_path in object_to_types[child.id]:
                    prim.GetReferences().AddInternalReference(type_path)

            # Record material relationships
            if child.id in object_to_materials:
                mat_rel = prim.CreateRelationship("ifc:material", False)
                for mat_path in object_to_materials[child.id]:
                    mat_rel.AddTarget(mat_path)

            if child.verts and child.face_counts and child.face_indices:
                geom_path = f"{child_path}/Geometry"
                geom_prim = stage.DefinePrim(geom_path, "Mesh")
                mesh = UsdGeom.Mesh(geom_prim)
                mesh.CreatePointsAttr(Vt.Vec3fArray([Gf.Vec3f(*v) for v in child.verts]))
                mesh.CreateFaceVertexCountsAttr(Vt.IntArray(child.face_counts))
                mesh.CreateFaceVertexIndicesAttr(Vt.IntArray(child.face_indices))
                Usd.ModelAPI(geom_prim).SetKind("component")

            write_stage_prims(child, child_path, child_matrix_list, seen_paths)

    write_stage_prims(project_node, f"/{safe_project_name}", project_node.global_matrix)

    stage.GetRootLayer().Save()
    print(f"Generated USD structure: {usd_file}")
    
    return usd_file, unit_scale

if __name__ == "__main__":
    import os
    parser = argparse.ArgumentParser(description="Convert IFC files to USD and generate a coordination file.")
    parser.add_argument("inputs", nargs="+", help="Path to one or more input IFC files")
    parser.add_argument("--output", "-o", help="Path to output USD coordination file", default="coordination.usda")
    parser.add_argument("--colour", action="store_true", help="Assign colors to prims based on their source file")
    args = parser.parse_args()

    output_dir = os.path.dirname(args.output)
    if not output_dir:
        output_dir = "."
    os.makedirs(output_dir, exist_ok=True)

    sublayers = []
    unit_scale = 1.0
    for ifc_file in args.inputs:
        base_name = os.path.basename(ifc_file)
        out_name = os.path.splitext(base_name)[0] + ".usda"
        out_usd_path = os.path.join(output_dir, out_name)
        
        out_usd, scale = convert_ifc_to_usd(ifc_file, out_usd_path)
        
        # Link relatively so the coordination file remains portable
        sublayers.append(f"./{out_name}")
        unit_scale = scale  # Assuming uniform units across files, or last file defines coordination scale

    coord_stage = Usd.Stage.CreateNew(args.output)
    UsdGeom.SetStageUpAxis(coord_stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(coord_stage, unit_scale)
    coord_stage.GetRootLayer().subLayerPaths = sublayers
    coord_stage.GetRootLayer().Save()
    
    if args.colour:
        colours_path = os.path.join(output_dir, "colours.usda")
        if os.path.exists(colours_path):
            os.remove(colours_path)
            
        colours_layer = Sdf.Layer.CreateNew(colours_path)
        coord_stage.GetRootLayer().subLayerPaths.insert(0, "./colours.usda")
        coord_stage.SetEditTarget(Usd.EditTarget(colours_layer))
        
        def hex_to_rgb(hex_code):
            hex_code = hex_code.lstrip('#')
            return tuple(int(hex_code[i:i+2], 16) / 255.0 for i in (0, 2, 4))

        palette = [hex_to_rgb(h) for h in [
            "#558d47", "#ac3e0e", "#518ba4", "#9e2a2a", 
            "#6226ab", "#202eee"
        ]]
        
        layer_colors = {}
        for prim in coord_stage.Traverse():
            if prim.IsA(UsdGeom.Gprim):
                defining_layer = None
                for spec in prim.GetPrimStack():
                    if spec.specifier == Sdf.SpecifierDef:
                        defining_layer = spec.layer.identifier
                        break
                        
                if defining_layer:
                    if defining_layer not in layer_colors:
                        color = palette[len(layer_colors) % len(palette)]
                        layer_colors[defining_layer] = Vt.Vec3fArray([Gf.Vec3f(*color)])
                        
                    gprim = UsdGeom.Gprim(prim)
                    gprim.CreateDisplayColorAttr().Set(layer_colors[defining_layer])
                    
        colours_layer.Save()
        coord_stage.GetRootLayer().Save()
        print(f"Generated coordination colours layer: {colours_path}")

    print(f"Generated coordination USD structure: {args.output}")


