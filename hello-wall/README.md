# Hello Wall, OpenUSD

This set of files explores what the Hello Wall IFC might look like in OpenUSD. The file `v1 - pure usd, single layer/hello-wall.usda` is a commented representation of
`hello-wall.ifc` in OpenUSD. It is a text file that can be read in any text editor. I suggest starting with that file, then reading this document for background and 
explanations of tradeoffs.

The last section of this readme, **Levels of Integration**, details three options for integration with OpenUSD, with increasing levels of effort / coordination.

NB: in these examples, OpenUSD takes the place of STEP, not IFC. This exercise is an exploration of what IFC might look like if expressed using OpenUSD's vocabulary,
but with minimal changes to the semantic strutcure of IFC.

## Directory structure

Each folder contains a different representation of the same data. In each case, the base layer to open is called `hello-wall.usda`, and is in OpenUSD text format.
Each folder also contains a file called `hello-wall_flattened.usda`. This is the result of openning `hello-wall.usda` and exporting the data as it is presented
to a reader.

v1 to v3 all show how IFC data can be represented in OpenUSD without plugins, and without changes to USD (see **Levels of Integration**, below).

- v1, single layer: all the data is in a single file (the flattened file simply strips the comments). the v1 `hello-wall.usda` is commented.
- v2, multi layer: same data as v1, but the materials and types are split into separate files
- v3, catalogue layer: same data as v2, but it is split differently. All window-related info (types and materials) are in one file, and project-specific materials in another.

## Vocabulary

There are some differences between IFC and OpenUSD vocabulary. 

|      IFC      |  OpenUSD   |
|---------------|------------|
| Object        | Prim       |
| Instance      | Placement  |
| DefinesByType | references |

The terms object and prim are used interchangeably in this README.

## General approach

### IFC Hierarchies

IFC has two primary hierarchies: the spatial and composition hierarchy (IfcRelContainedInSpatialStructure, IfcRelDecomposes), and the the placement hierarchy (IfcPlacement, etc...).

These are all represented using USD scenegraph - the single hierarchy that organizes the model and places objects in 3D space.

This approach is consistent with
 [OBJ001](https://buildingsmart.github.io/ifc-gherkin-rules/branches/main/features/OJP001_Relative-placement-for-elements-aggregated-to-another-element.html) that requires
that elements that are agregated by other elements must also be placed by those elements.

[Model Hierarchy](https://openusd.org/release/glossary.html#usdglossary-modelhierarchy): OpenUSD has a mechanism for annotating the important parts of the scenegraph as 'models'.
This does not introduce a separate hierarchy, but annotates a set of prims (objects) starting from the root. These examples use the model kind `group` to note the elements that are part of the spatial structure hierarchy, and the model kinds `assembly` and `component` to note decomposition relationships.

Some elements in IFC, such as materials and types, 'float' outside the IFC hierarchy. Since OpenUSD requires all prims to sit in the scenegraph, these examples
simply place them under a `Types` and `Materials` nodes, adjacent to `IfcProject`.

### GUIDs and Prim Names

OpenUSD does not currently allow GUIDs as prim names, so these examples use human-readable names. The guids are still attached to each prim, but are not used for internal referencing or composition. This is a similar situation to IFC files in the STEP format, where references within the STEP file use the line number, not the GUID. The OpenUSD namespace replaces the STEP line numbers, and the GUIDs are preserved as object attributes.

Note: when a wall type has a GUID, each wall placement ***must*** overwrite it.

### DefinesByType

IFC's mechanism for defining an object by a 'type' object requires a matching 'type' class for every class of object. That is, for `IfcWall`, we need `IfcWallType`. OpenUSD has a significnatly more flexible mechanism: `def` vs `class` and the `references` composition arc.

When a prim is defined using the `class` specifier, it signals that the prim is abstract data, not direclty placed into the scene. `def IfcWall "My_Wall` is equivalent to an IFC `IfcWall` and `class IfcWall "My_Wall_Type"` is equivalent to an IFC `IfcWallType`.

To use these types, we simply define a window prim, and use the `references` composition arc to pull in all the data from the type object. The example below, where `Window_001` *references* `WT01` is equivalent to the IFC statement that `Window_001` is defined by type `WT01`.

```
def Xform "Window_001" (
    references = </Types/WT01>
)
{
    # ...
}
```

OpenUSD's referencing mechanism is significantly more flexible that the `DefinesByType` mechanism in IFC, but these examples use it in a similar way to IFC's types.

### Geometry

OpenUSD has two geometrical simplifications, compared to IFC:

1. No boolean operations are carried out when reading the file.
2. BREPs, extrusions and other general shapes are not supported.

Item 1 is unlikely to ever change, but item 2 may change in the future.

These examples use meshes for geometry, with opennings already cut.

### Relationships

OpenUSD has a type of prim attribute called `rel` that stores a reference to another prim in the stage. These examples use this mechanism to represent relationships. Relationships are, in general, not objectified.

**Spatial hierarchy**: these examples do include explicit links from children to parents for contained in spatial structure and decomposes. These do not provide any more information than the OpenUSD hierarchy, but are included to show that they can be natively represented.

**Voids**: all information about a void's relationships is consolidated into the void. Since there is no support for carrying out boolean operations to cut voids in walls at read time, the void objects are purely informative. These examples consolidate all void information into the void object: its geometry, the relationship to the object it cuts avoid out of, and the relationship to the object that fills the void. (`voided_by` and `fills` relationships could just as easily be added to the related elements.)

**Materials**: OpenUSD has a pre existing material schema, but it refers to rendering materials, not physical materials. Materials are connected to prims via a relationships called `ifc:material`.

## Levels of integration

### Vanilla OpenUSD

These samples show how IFC data can be stored in OpenUSD files in plain vanilla OpenUSD.

**v1**: shows the whole hello wall example in a single file.

**v2** & **v3**: these have the same content as the first file, but split it across multiple files. These three examples should look identical when they are openned. This shows the effectivenes of OpenUSD's 'compose on read' behaviour. Data can be split into arbitrary layers (files), and still read as if it were a single model.

### IFC plugins to OpenUSD

Writing a plugin allows us to introduce new strict object types. This opens up three advantages over plain vanilla OpenUSD:

**IsA schemas for IFC element types**: we can write class definitions for elements such as IfcProject, and IfcWall. These can come with pre-applied attributes (such as class). For example, if IfcWall is a subclass of `Xform`, then we can replace:

```
def Xform "My_Wall"
{
    token ifc:class = "IfcWall"
}
```

with 

```
def IfcWall "My_Wall"
{
    # ...
}
```

since the ifc:class can be assigned its value in the class definition

**API schemas for Psets**: OpenUSD's API Schemas allow a fixed set of properties (with optional default values) to be added to prims. Each IFC PSet can have an equivalent API Schema definition. These can be applied to specific prims in a scene, or can be applied in an IsA schema definiton (e.g. an IfcWall can always have a set of PSets / API Schemas applied).

**Validation**: OpenUSD has a validation framework, which can be leveraged to check the validity of a usd stage, layer or prim. It is a flexible, programatic framework, and can capture all requirements from WHERE rules, IDS and MVDs.

### Modifications to OpenUSD

The above demonstrates that much of the capacity of IFC can be expressed in OpenUSD as it is currently defined. However, these is a possibility that OpenUSD may be extended to
allow BREPs and other geometric representations, and mechanisms for specifying guids.