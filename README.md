## IFC ↔ OpenUSD Schema Project

This repository explores and implements a mapping of IFC (Industry Foundation Classes, starting with IFC 4.3) semantics into OpenUSD via custom schemas and conventions. The goal is to enable USD stages that retain core IFC meaning: identity (GlobalId), spatial structure, element typing, property sets, relationships, and units—while staying idiomatic to USD composition and layering.

### Objectives (Phase 0)
* Define a minimal set of USD typed schemas for core spatial + element entities (Project, Site, Building, Storey, Wall, Slab, Column, Beam, etc.).
* Represent IFC property sets using API schemas or namespaced attributes.
* Encode decomposition and selected relationships using USD prim hierarchy + relationship attributes.
* Establish naming + namespace conventions (`ifc:` or schema-scoped attributes) and a validation stub (e.g., GlobalId uniqueness).
* Produce example `.usda` stages demonstrating the mapping.

### Non‑Goals (Early Phase)
* Full coverage of every IFC entity.
* Complete WHERE rule / constraint engine.
* Full geometric parametric reconstruction (sweeps, CSG, alignment models) — may be added later.

### Repository Contents
* `investigation.md` – Detailed investigation, key questions, architectural options, and recommended path.
* `main.py` – Placeholder / future tooling entry point (e.g., schema generation, validation, converters).
* `USD IFC Conceptual Data Mapping.md` – Early conceptual notes.
* (Future) `schemas/` – Generated or authored USD schema definition files (`.usda`) and `plugInfo.json`.

### Planned Deliverables
1. USD schema package skeleton (`usdIfc`) with core typed + API schemas.
2. Example USD stage demonstrating spatial structure and one element with a property set.
3. Validation script for basic structural and identity checks.

### Getting Involved / Next Steps
* Review `investigation.md` for open questions.
* Help decide naming conventions & subset of initial entities.
* Prototype first schema (`UsdIfcProject`) and ensure plugin discovery works.

### References
* IFC 4.3: https://ifc43-docs.standards.buildingsmart.org/
* OpenUSD: https://www.openusd.com/

---
This is an early-stage exploration; structure and naming may change rapidly.

