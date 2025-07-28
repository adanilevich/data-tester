# Package specification

## Functional requirements

### Use Case 1: Finding Specifications
Requirement: Given a domain config and a testset, find and fetch specifications which correspond to the testcases in the testset

### Use Case 2: Parsing Specifications
Requirement: Given a specification file, parse it and return the contained specification(s)

### Cross cutting requirements
1. Specifications are searched in the locations as defined in the domain config
2. For each specification location from the domain config, the search is conducted with depth of one subfolder
4. Specification are found and matched to the testcases based on their file names
5. For name matching, plug-in naming conventions are used which define expected filename patterns based on testobject name, testtype, spec type and test scenario
6. Used naming conventions can differ based on the domain name
7. For each combination of <testobject>, <testtype>, <scenario> several specifications may be found
8. One specification file may be parsed to several specifications (e.g. xlsx files containing schema definition in one sheet and sql in an other)
9. Similarly to naming conventions, specifications can be stored in different file formats (e.g. xlsx spec for schema definition, .sql textfiles for rowcount sqls)
10. For this, plug-in formatters are provided which serialize and de-serialize from/to these formats
11. Different formats can be used by different domains

## Code Architecture

1. At the .core, the Specification class handles the core logic 
    - it is resonsible of searching for files, name matching and parsing
    - this is done via IStorage, INamingConventions and a list of IFormatters which it receives on __init__
2. External actors interact with the specification core logic via ports defined in .ports.drivers.i_handle_specs. This module defines 
    - the FetchSpecsCommand(DTO) to find specifications from a given location for a list of TestCaseEntryDTOs
    - the ParseSpecCommand(DTO) to parse specification(s) from a given file/byte object
    - the ISpecCommandHandler interface which defines the fetch_specs and parse_spec methods
3. For extensibility, interfaces INamingConventions, INamingConventionsFactory, ISpecFormatter, I SpecFormatterFactory are defined in .plugins
4. The .application.handle_specs.py contains the SpecCommandHandler class which implements the ISpecCommandHandler interface using Specification and the provided INamingConventionsFactory, IStorage and a IFormatterFactory
5. As plugins, in .plugins, a default tNamingConventions and Formatters are implemented
6. Also, in plugins, default Reqirements are implemented which specify what specs are required per testcase type (COMPARE, SCHEMA, ROWCOUNT)
