# IFC → USD Mapping Spec (Pragmatic)

Status: Draft (Phase 0)

This document defines a **pragmatic, USD-idiomatic** mapping of selected IFC (starting with IFC 4.3) semantics into an OpenUSD stage using a small set of custom USD schemas plus conventions.

It is intentionally **not** a complete, normative, or exclusive representation of IFC in USD. The goal is to preserve as much useful semantics as practical while remaining maintainable and easy for USD tools to consume.

---

## 1. Non-goals

- Full 1:1 coverage of all IFC entities and attributes (no full EXPRESS mirroring in Phase 0).
- Representing IFC relationship entities as `IfcRel*` prims.
- Full WHERE-rule / constraint engine (Phase 0).
- Preserving IFC parametric / procedural geometry (sweeps, CSG, BReps) as-editable USD-native parametrics in Phase 0.

---

## 2. Guiding principles

1. **USD-idiomatic first**
   - Prefer USD prim hierarchy for primary decomposition.
   - Prefer USD relationships for non-hierarchical semantics.
   - Avoid creating relationship prims for `IfcRel*` entities.

2. **Semantics are explicit**
   - Identity and key IFC concepts are represented as strongly named attributes and relationships.

3. **Curated typed schemas + generic fallback**
   - Provide typed schemas for a small, high-value subset.
   - Use a generic base schema + `ifc:ifcClass` token to preserve IFC class identity when a typed schema is not available.

4. **Property sets are modular**
   - Standardized buildingSMART PSets are expressed as attachable API schemas.
   - Non-standard properties can be authored directly as USD properties using a reserved namespace.

---

## 3. Names, namespaces, and packaging

### 3.1 Proposed package / plugin naming (TBD)

We want a name that communicates “IFC-to-USD mapping” but does not imply it is the only correct mapping.

Candidate directions:
- `usdIfcPragmatic` / `UsdIfcPragmatic` (explicitly non-normative)
- `usdIfcMapping` / `UsdIfcMapping` (descriptive)
- `usdIfcInterop` / `UsdIfcInterop` (interoperability focus)
- `usdIfcConventions` / `UsdIfcConventions` (highly explicit that it’s conventions)

(We will choose one and keep the schema prefix consistent, e.g., `UsdIfc...`.)

### 3.2 Attribute namespaces

- IFC identity and core fields are in the `ifc:` namespace.
- Relationship attributes use the `rel:` namespace.
- Non-standard / ad-hoc property sets and properties use the `ifcPset:` namespace.

---

## 4. Prim hierarchy strategy

### 4.1 Spatial / decomposition as hierarchy

Primary spatial decomposition should be represented as USD prim hierarchy for usability in USD-native tools.

Example (illustrative):

- `/World/Ifc/Project_.../Site_.../Building_.../Storey_.../Wall_...`

Hierarchy is not the sole source of truth. Key IFC semantics are also preserved via explicit relationships (below).

---

## 5. Relationships (USD relationships; no IfcRel prims)

IFC relationship semantics are preserved using USD relationship attributes.

Recommended relationship attributes (Phase 0):

- `rel:containedInSpatialStructure` (0..1 target)
- `rel:decomposes` (0..1 target)
- `rel:aggregates` (0..N targets)
- `rel:definesType` (0..1 target)

Notes:
- Even if containment/decomposition is represented in hierarchy, we still author the relationship for round-tripping, validation, and disambiguation.

---

## 6. Identity and base metadata

### 6.1 Required identity (for IfcRoot-like objects)

- `ifc:globalId` (string) — required; must be unique within a stage.

### 6.2 Optional identity / descriptive fields

- `ifc:name` (string)
- `ifc:description` (string)
- `ifc:ifcClass` (token) — e.g. `"IfcWall"`; required when using generic fallback schemas.

---

## 7. Typed schemas (Phase 0 curated subset)

Initial typed prim schemas (proposed):

- `UsdIfcProject`
- `UsdIfcSite`
- `UsdIfcBuilding`
- `UsdIfcBuildingStorey`
- `UsdIfcElement` (base)
- `UsdIfcWall` (example element)

Everything else may be represented as `UsdIfcElement` (or a generic `UsdIfcObject`) with `ifc:ifcClass` set.

---

## 8. Geometry interoperability (Phase 0)

### 8.1 Geometry must be resolved prior to USD

There are two core interoperability constraints between IFC geometry and USD geometry:

1. Some IFC geometry representations (e.g., BReps, CSG, sweeps, procedural profiles) are not representable as editable, equivalent USD-native geometry schemas in a universally supported way.
2. IFC uses semantic relationships (e.g., openings/voiding elements) that can drive *final* geometry via boolean operations. While USD can express relationships, it does not standardize an equivalent boolean-result evaluation across consumers.

**Phase 0 requirement:** the IFC reader/converter MUST resolve these into final representable geometry before authoring USD.

Concretely:

- Boolean results (e.g., a wall voided by openings) must be computed in the converter, and the authored USD geometry for the wall must already have openings cut out.
- Non-representable IFC geometry must be converted to a USD-representable form, typically triangulated meshes (e.g., `UsdGeomMesh`).

We may still preserve semantic references (e.g., relationships to openings) for downstream uses, but geometry correctness must not depend on USD consumers re-evaluating booleans.

### 8.2 Future direction (non-binding)

Later phases may introduce optional parametric preservation (e.g., storing sweep/profile parameters as metadata or custom schemas) while still producing resolved geometry for interchange.

## 9. Property sets (PSets)

### 8.1 Standardized PSets as API schemas

- Each standardized PSet we support is expressed as a dedicated API schema.
- Example starter: `UsdIfcPsetWallCommonAPI`.

### 8.2 Non-standard / ad-hoc properties

Non-standard property sets and properties may be authored directly as USD properties using:

- `ifcPset:<PsetName>:<PropName>`

Example:

- `string ifcPset:MyCompanyPset:FireRating = "2hr"`

Rationale:
- Keeps data grouped by intended PSet name.
- Avoids collisions with other USD schemas.

---

## 10. Validation (Phase 0) and WHERE rules

### 9.1 WHERE rules philosophy

In IFC, WHERE rules express schema-level constraints.

In this mapping, the USD-idiomatic equivalent is a **validation framework**: WHERE rules (to the extent we implement them) are encoded as **validators** that inspect a USD stage and report conformance issues.

Phase 0 does not aim to implement all IFC WHERE rules, but any implemented WHERE rules MUST be expressed as validators.

### 9.2 Minimal Phase 0 checks

A minimal validator should check:

- Uniqueness of `ifc:globalId` across all prims that have it.
- Presence of required identity fields for typed schemas.
- (Optional) Consistency between hierarchy and relationships for containment/decomposition.

---

## 11. Acceptance testing

Acceptance testing is specified in:

- `testing-strategy.md`

Implementations (converters, plugins) should be considered conforming for Phase 0 when they satisfy the validators and expectations described there.

## 12. Open decisions

- Final plugin/package name.
- Final prim path strategy (how to incorporate GlobalId vs sanitized Name vs incremental indices).
- Which standardized PSets to support first.
