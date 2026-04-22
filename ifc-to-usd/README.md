# IFC to USD Converter

This is a demonstration script that takes a set of IFC files and converts them into a set of IFC files. The converted files have the following structure:

- stick-set.usda
  - discipline-A.usda
  - discipline-B.usda
  - etc...

`stick-set.usda` includes the main data layout, a bare scenegraph as follows:

- IfcProject
  - IfcSite
    - IfcBuilding
      - IfcStorey
        - IfcSpace
        - ...
      - ...
      - IfcRoof

We expect these elements to be duplicated in each of the inputs files. Each input file will result in a usd file that has `over` definitions