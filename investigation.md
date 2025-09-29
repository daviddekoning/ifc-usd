# Investigation: OpenUSD Schema for IFC Semantics

Date: 2025-09-29  
Author: (draft generated with AI assistance)

## 1. Aim / Problem Statement

Define an OpenUSD (USD) schema (or cohesive set of schemas + conventions) that can represent IFC (starting with IFC 4.3) data structures and semantics in a USD stage so that:

* IFC identity, typing, decomposition, relationships, property sets, classifications, geometry, units, and constraints are preserved (enabling reliable round‑trip or at least high‑fidelity import -> enrich -> export workflows).
* Authoring & consumption leverage native USD composition, layering, and schema mechanisms (typed schemas, API schemas, relationships, variants, references) rather than ad‑hoc metadata blobs.
* The result can evolve to support partial / view‑based exchanges (Reference View, Design Transfer View, Alignment, etc.) analogous to IFC Model View Definitions (MVDs) / “Views”.
* The solution remains maintainable across evolving IFC releases and USD versions.

Success Criterion (initial milestone): Provide a minimal yet extensible set of .usda schema definition files and supporting documentation that encode a selected subset of IFC (e.g., core spatial structure + a few building element classes + property sets) with demonstrable fidelity for: identity, decomposition, basic geometry referencing, property sets, and at least one relationship class.

## 2. Scope (Initial Phase)

In-Scope (Phase 0 / Prototype):
* Mapping of a small curated subset of IFC entities (e.g., IfcProject, IfcSite, IfcBuilding, IfcBuildingStorey, IfcSlab, IfcBeam, IfcColumn, IfcWall, IfcOpeningElement) to USD typed prim schemas.
* Representation of GlobalId, Name, Description, and object type referencing.
* Basic decomposition (spatial containment, aggregation) via USD prim hierarchy & relationships.
* Property Sets: at least one PSet expressed via an API schema pattern or namespaced attributes.
* Units + coordinate reference (project units + geolocation minimal strategy).
* Export/import conceptual prototype scripts (optional stretch) or documented mapping rules.

Out-of-Scope (Phase 0):
* Full EXPRESS coverage for all IFC 4.3 entities.
* Advanced constraint checking / full WHERE rule engine.
* Full MVD coverage, alignment view specifics, infrastructure alignment geometry.
* Performance optimization of massive federated projects.

## 3. Assumptions & Constraints
* Target IFC baseline: IFC 4.3 (with awareness of earlier 2x3 compatibility gaps).
* Target USD version: Latest stable (TBD, assume ≥ 24.x) — confirm feature availability (e.g., schema generation tooling, API schema layering).
* Desire to leverage USD-native composition (references, payloads) for reuse/typing rather than duplicating IFC type-instance semantics externally.
* Need for forward compatibility: avoid hard-coding transient enumerations where a parametric or code-generated approach is feasible.
* Must allow partial adoption: consumers can ignore IFC-specific metadata without breaking core USD scene validity.
* Licensing: IFC is open (buildingSMART), USD schema additions should be under a permissive license (e.g., Apache 2.0) — confirm repository licensing.

## 4. Key Questions (Organized by Theme)

### 4.1 Schema Strategy
1. Do we create a USD typed schema per IFC entity (1:1) or prioritize a core subset with generic extension points?
2. How to represent IFC inheritance & SELECT/TYPE constructs (e.g., measure/value types, enumerations) within USD schema type system which does not model scalar type hierarchy the same way?
3. How to encode IFC enumerations: as token-valued attributes, string, or dedicated API schemas with constrained metadata?
4. Should property set definitions become API schemas (reusable attachable sets) vs inline namespaced attributes vs dynamic dictionaries?

### 4.2 Identity & Metadata
5. Placement of GlobalId (stable GUID) — attribute name & namespace (e.g., `ifc:globalId`)? Uniqueness constraints enforcement strategy?
6. Representation for IFC OwnerHistory / provenance — store now or reserve extension slot?
7. Strategy for versioning IFC schema sets (ifc4_3, future ifc5) within USD plugin discovery to avoid collisions.

### 4.3 Typing & Reuse
8. IFC Type Objects (e.g., IfcWallType) -> USD references, class prims, or API schema attachments?
9. How to differentiate an ‘instance defined by type + local overrides’ using USD composition arcs (reference vs inherit vs specialization)?
10. Handling of parametric vs explicit geometry (e.g., profile-based extrusions) — preserve parameters or only store baked geometry initially?

### 4.4 Decomposition & Relationships
11. Spatial containment (IfcRelAggregates / IfcRelContainedInSpatialStructure) -> USD prim hierarchy vs explicit relationship prims — which relationships require an explicit intermediary prim?
12. Distinguish aggregation vs nesting (ordered hosting) — do we need metadata flags on children or relationship objects with order indices?
13. Non-hierarchical relationships (e.g., IfcRelConnects, IfcRelAssociates) — model as USD relationships on source prim or create dedicated prims typed as relation entities?
14. Multi-target relationships: best practice for sets of target paths (listOp vs multiple relationship attributes)?

### 4.5 Property Sets & Attributes
15. Canonical naming scheme: `ifc:pset_<PSetName>:<PropertyName>` vs separate API schema per PSet (e.g., `UsdIfcPsetDoorCommon`)?
16. How to handle data typing (IfcLabel, IfcIdentifier, IfcLengthMeasure) — flatten to core scalar types (string, double) + unit metadata? Include original EXPRESS type name for round-trip?
17. Should we define a generic key/value container (e.g., dictionary attribute) for unforeseen properties or dynamic vendor extensions?

### 4.6 Units & Coordinate Reference
18. Project units: store as stage-level metadata vs schema attribute on root prim vs dedicated `UsdGeomUnitsAPI` style extension?
19. Georeferencing (IfcMapConversion, IfcCoordinateReferenceSystem): minimal initial representation? Use Xform + metadata vs dedicated prim types?
20. Elevation/sea-level vs local engineering coordinate origins — layering strategy to allow repositioning without geometry edits?

### 4.7 Geometry Representation
21. Strategy for parametric shapes (profiles, sweeps) — define interim schema or postpone and only reference tessellated geometry (e.g., USD Mesh) with extra parameters reserved?
22. Mapping of IFC surface/solid representations (BRep, CSG) — rely on USD existing geometry schemas + custom attributes? External translator plugin needed early?
23. Level of detail: handle multiple LODs now (variants, purpose attribute) or later?

### 4.8 Validation & Constraints
24. WHERE rules & domain constraints: implement as separate validation engine referencing USD schema introspection? How to attach rule provenance for reporting?
25. Model View Definitions (MVDs) mapping: variant set, layer grouping, or external profile manifest file that states required/optional attributes?

### 4.9 Performance & Scalability
26. Risk of schema explosion if 800+ IFC entities become typed schemas — impact on plugin load & authoring usability?
27. Are large property sets better flattened or modularized for performance / memory locality?
28. Layering strategy for federation (discipline / domain layers) aligning with IFC domain separation (Core, Shared, Domain).

### 4.10 Authoring & Round‑Trip
29. Is lossless round-trip a near-term requirement or is a high-fidelity import (read-only) acceptable first?
30. How to track provenance/source for each prim to enable differential updates (change sets) when re-importing updated IFC?

### 4.11 Versioning & Extensibility
31. Mechanism to declare schema version (semantic version attribute vs plugin metadata).
32. Handling deprecation of attributes/entities across IFC versions.

### 4.12 Implementation Mechanics
33. Tooling to generate schema .usda from a definition source (Express parser -> intermediate -> USD schema generation)?
34. Packaging: single plugin vs multiple (ifcCore, ifcBuilding, ifcInfrastructure) for selective load.
35. Testing strategy (golden round-trip cases, structural validation, performance benchmarks).

## 5. Options for Proceeding

### Option A: 1:1 Typed Schema Generation (Full Fidelity)
Description: Generate a USD typed schema (UsdIfc<IfcEntityName>) for each IFC entity in chosen subset (eventually all). Attributes map explicitly to IFC attributes. Relationships become either hierarchy or relationship attributes.
Pros: High fidelity, explicitness aids tooling & validation, clearer introspection, easier MVD conformance mapping.
Cons: Large number of schemas; maintenance overhead; requires robust generation pipeline before delivering MVP.
Risks: Early design missteps propagate widely; plugin initialization overhead.
Best When: Long-term commitment to full IFC coverage; need strong validation.

### Option B: Hybrid Core + API Schemas for Property Sets (Recommended Starting Point)
Description: Typed schemas only for structural / high-value entities (Project, Site, Building, Storey, Element super-classes + a few element types). Property Sets realized as attachable API schemas (e.g., `UsdIfcPsetCommon`). Less common IFC entities represented using a Generic IFC Object typed schema with a classification code.
Pros: Reduces initial schema count; keeps strong typing where most impactful; API schemas modular; scalable.
Cons: Some loss of granularity for rarely used entities; round-trip for unmodeled attributes might require generic containers.
Risks: Generic fallback may grow uncontrolled; complexity in deciding promotion from generic -> typed later.
Best When: Need early deliverable with room to expand; incremental adoption.

### Option C: Single Generic IFC Prim + Namespaced Attributes
Description: One main typed schema (e.g., `UsdIfcObject`) with flexible dictionaries for attributes, relationships encoded as arrays of paths + relationship type tokens.
Pros: Fastest to prototype; minimal plugin complexity.
Cons: Weak validation; poor discoverability; higher risk of divergence; not idiomatic USD for rich semantics.
Risks: Hard to migrate to strongly typed model later without data transformation.
Best When: Rapid exploratory prototyping only.

### Option D: Progressive Layered Views
Description: Align “Views” with layer stacks: Core structural + identity layer; Properties layer; Geometry detail layer; Parametrics layer; Constraints/Validation layer. Each layer adds API schemas or enriches attributes.
Pros: Natural alignment with USD layering; supports partial consumption; mirrors IFC MVD incremental complexity.
Cons: Requires discipline around layer definitions; complexity for authoring pipelines to maintain coherence across layers.
Risks: Fragmentation if layers become inconsistent; dependency ordering errors.
Best When: Expect multi-discipline workflows consuming only slices of data.

### Option E: EXPRESS-Driven Code Generation Pipeline
Description: Build (or adopt) an EXPRESS parser generating an intermediate model -> emit USD schema definitions (.usd/.usda) + Python/C++ wrappers + documentation automatically.
Pros: Automation reduces maintenance; can regenerate for new IFC versions; consistent naming.
Cons: Upfront engineering cost; need mapping rules for EXPRESS constructs (SELECT, WHERE, DERIVE) to USD constructs.
Risks: Parser correctness; complexity of edge cases (derived attributes, inverse relationships).
Best When: Sustainable long-term maintenance and broad coverage are goals.

## 6. Comparative Summary

| Option | Speed to MVP | Fidelity | Maintainability | USD Idiomatic | Scalability |
| ------ | ------------ | -------- | --------------- | ------------- | ----------- |
| A      | Medium       | High     | Medium (w/o gen) | High          | High        |
| B      | High         | High (core), Medium (long tail) | High | High | High |
| C      | Very High    | Low      | Medium           | Low           | Medium      |
| D      | Medium       | Medium → High | Medium      | High          | High        |
| E*     | Long (pipeline) | High  | Very High (once built) | High | High |

(*Option E is an enabler rather than a standalone mapping stance; it complements A or B.)

## 7. Recommended Initial Approach

Adopt Option B (Hybrid Core + API Schemas) combined with foundational work for Option E (generation pipeline) and elements of Option D (layering) to allow progressive enrichment.

Rationale:
* Provides tangible schemas quickly with strong typing for the most queried concepts (spatial structure + core building elements).
* Keeps door open to automated expansion via generation pipeline once rules are stabilized.
* Layering can separate concerns: identity/core vs property sets vs geometry parametrics.
* Minimizes early irreversible design decisions while remaining idiomatic USD.

## 8. Initial Deliverables (Phase 0)
1. Schema package skeleton: `usdIfc` plugin directory with schema.usda, plugInfo.json placeholders.
2. Typed Schemas: `UsdIfcProject`, `UsdIfcSite`, `UsdIfcBuilding`, `UsdIfcBuildingStorey`, `UsdIfcElement` (abstract), `UsdIfcWall`, `UsdIfcSlab`, `UsdIfcColumn`, `UsdIfcBeam`.
3. API Schemas: `UsdIfcPsetIdentity`, one example domain PSet (e.g., `UsdIfcPsetWallCommon`).
4. Attributes (illustrative): globalId (token/string), name, description, typeRef (path), decomposition (via prim hierarchy), classificationCodes (array of tokens), property set attributes.
5. Relationship representation prototype: A relationship API schema or simple relationships (e.g., hosting) expressed as a relationship attribute `rel:host` (list of path targets) with an ordering metadata if needed.
6. Units: Root prim metadata block `ifc:units` (dictionary or struct) + placeholder for CRS.
7. Documentation: mapping glossary, attribute naming conventions, layering guidelines.
8. Validation stub: simple Python script verifying uniqueness of globalId and presence of required attributes per schema.

## 9. Risks & Mitigations
| Risk | Impact | Mitigation |
| ---- | ------ | ---------- |
| Scope creep on entity coverage | Delays MVP | Enforce curated entity list freeze for Phase 0 |
| Ambiguous property typing | Loss of fidelity | Store original IFC type name as companion attribute (e.g., `propType:<attr>`) in early phases |
| Relationship semantics mismatch | Incorrect structural interpretation | Start with documentation + tests mapping one IFC example model |
| Performance degradation with many property attributes | Slow load | Group PSet attributes under API schema namespaces; measure after sample dataset |
| Round-trip lossy for unmodeled entities | Data loss risk | Provide Generic fallback + capture IFC entity name token |

## 10. Open Issues (Unresolved)
* Decision on attribute naming case/style (camelCase vs snake_case vs IFC original names).
* Final data type mapping table (EXPRESS primitive -> USD attribute type).
* Strategy for inverse relationships (explicit vs derived at runtime during import/export).
* Representing IFC partial geometry definitions (profiles) to enable parametric edits post-import.
* Safe namespace prefix (ifc:, usdIfc:, or rely on schema domain?).
* Handling localized units / multi-unit contexts (rare but present in IFC for certain property sets).
* Security / injection considerations for externally sourced GUIDs (validation patterns).

## 11. Next Steps (Action Plan)
1. Confirm core entity subset & naming conventions (Q1–Q7 subset decisions).
2. Draft schema naming + prefix policy.
3. Create plugin skeleton & initial schema.usda with one entity (Project) to validate build & discovery.
4. Add remaining core typed schemas; define base attributes.
5. Implement first API schema for a property set; attach to sample prim.
6. Author sample stage demonstrating spatial decomposition + one element with property set.
7. Implement simple validation script (globalId uniqueness, required attributes present).
8. Evaluate need for EXPRESS parser vs manual curated YAML definition for Phase 0.
9. Document mapping decisions; update open issues with resolutions.
10. Prepare roadmap for adding geometry parametrics (sweeps) & more entities (Phase 1).

## 12. References
* IFC 4.3 Official Documentation: https://ifc43-docs.standards.buildingsmart.org/
* IFC 2x3 Documentation: https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/FINAL/HTML/
* OpenUSD (USD): https://www.openusd.com/
* (Future) Internal design notes & mapping tables (TBD)

---
This document is a living investigation artifact; revisions expected as decisions form.
