# IFC ↔ OpenUSD Explorations

This repository explores and implements a mapping of IFC (Industry Foundation Classes, starting with IFC 4.3) semantics into OpenUSD. The goal is to enable USD stages that retain core IFC meaning: identity (GlobalId), spatial structure, element typing, property sets, relationships, and units—while staying idiomatic to USD composition and layering.

## Hello Wall example

The `hello-wall` folder shows what the hello-wall.ifc file might look like in USD

## ifc-to-usd

This script can take a set of IFC files, and convert them to a set of USD files, along with a main USD layer that adds each of the other files / layers as a sublayer. When you open this layer in usdview or any USD-compatible software, you'll get the full composed model.

If you also pass a `--colour` option, an extra layer is also created that colours each prim based on what layer defines it.

Outstanding work:

- [ ] trim the layer data so that objects that are defined in multiple IFC files (e.g. the IfcProject) are only defined in a single USD layer.
- [ ] add support for voiding relationships (semantic decoration)
- [ ] ...

---

That's as far as we've gotten so far ... see below for some other ideas.

## Objectives (Phase 0)
* Define a minimal set of USD typed schemas for core spatial + element entities (Project, Site, Building, Storey, Wall, Slab, Column, Beam, etc.).
* Represent IFC property sets using API schemas or namespaced attributes.
* Encode decomposition and selected relationships using USD prim hierarchy + relationship attributes.
* Establish naming + namespace conventions (`ifc:` or schema-scoped attributes) and a validation stub (e.g., GlobalId uniqueness).
* Produce example `.usda` stages demonstrating the mapping.

## Non‑Goals (Early Phase)
* Full coverage of every IFC entity.
* Complete WHERE rule / constraint engine.
* Full geometric parametric reconstruction (sweeps, CSG, alignment models) — may be added later.

## Repository Contents
* `investigation.md` – Detailed investigation, key questions, architectural options, and recommended path.
* `USD IFC Conceptual Data Mapping.md` – Early conceptual notes.
* (Future) `schemas/` – Generated or authored USD schema definition files (`.usda`) and `plugInfo.json`.


## References
* IFC 4.3: https://ifc43-docs.standards.buildingsmart.org/
* OpenUSD: https://www.openusd.com/

---
This is an early-stage exploration; structure and naming may change rapidly.

