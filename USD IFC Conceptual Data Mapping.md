# USD IFC Conceptual Data Mapping

2025-03-10

## Introduction

### Overview

### References

IFC 4.3: https://ifc43-docs.standards.buildingsmart.org/
IFC 2.3: https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/FINAL/HTML/
USD: https://www.openusd.com/

### General Assumptions and Constraints

### Definitions, Acronyms and Abbreviations

## Concepts


| IFC                          | OpeUSD               | Description                                                                                                                                                                                                           |
| ---------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Model                        | Stage                | A 3D model                                                                                                                                                                                                            |
| Object                       | Prim                 | The basic building block of a 3D model.                                                                                                                                                                               |
| Object typing                | references           | A mechanism to define an object by a reference object. in IFC, an object can be defined by a single _type_ object, while USD's _reference_ composition arc is more flexible and can express a super-set of behaviour. |
| Object Aggregation           | Model Hierarchy      | An aggregation indicates an internal unordered part composition relationship between the whole structure, referred to as the "composite", and the subordinate components, referred to as the "parts".                 |
| Object Nesting               | Model Hierarchy ???  | A nesting indicates an external ordered part composition relationship between the hosting structure, referred to as the "host", and the attached components, referred to as the "hosted elements".                    |
| Views                        | ??? Schemas          | Gradual levels of implementation, adding more advanced features.                                                                                                                                                      |
| Layers                       | USD Core Packages    |                                                                                                                                                                                                                       |
| Classifications              |                      |                                                                                                                                                                                                                       |
| Where Rules                  | Validation Framework |                                                                                                                                                                                                                       |
| Domain Specific Data Schemas | Schema Modules       |                                                                                                                                                                                                                       |
| PSets                        | API Schemas          |                                                                                                                                                                                                                       |


### Objects

Fundamental identifiable data sets 

### Object typing

### Object Properties

### Object Composition

### Object Definition

### Object Relationships

### Views

Reference View, Design Transfer View, Alignment-based View

### Layers

Domain, Interop, Core, Resource

### Class



### PSet

### Where Rules

### MVDs

### Properties

### 