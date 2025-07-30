# Domain Layer

The domain layer contains the core business logic and entities of the Data Tester framework. This layer is independent of external frameworks and infrastructure concerns, focusing purely on business rules and domain concepts.

## Core Domain Modules

### `testcase/`
**Purpose**: Core testing execution engine and test run management

**Key Components**:
- `testrun.py`: Orchestrates test execution with precondition checks and result aggregation
- `handle_testruns.py`: Application service for managing test run lifecycle
- `testcases/`: Concrete test implementations (Schema, RowCount, Compare, Dummy tests)
- `precondition_checks/`: Validation checks executed before test runs

**Architecture Role**: Central domain entity that coordinates test execution workflows

### `specification/`
**Purpose**: Test specification discovery, parsing, and validation

**Key Components**:
- `specification.py`: Core specification entity and business rules
- `handle_specs.py`: Application service for specification management
- `plugins/`: Pluggable formatters for different specification formats (SQL, XLSX)

**Architecture Role**: Manages the "what to test" aspect of the domain

### `report/`
**Purpose**: Test result reporting and output formatting

**Key Components**:
- `report.py`: Core reporting entity and aggregation logic
- `handle_reports.py`: Application service for report generation
- `plugins/`: Multiple output formatters (TXT, XLSX, JSON)

**Architecture Role**: Handles the "how to present results" domain concern

### `domain_config/`
**Purpose**: Business domain configuration management

**Key Components**:
- `domain_config.py`: Configuration entity with business-specific settings
- `domain_config_handler.py`: Application service for configuration management

**Architecture Role**: Manages domain-specific configuration separate from technical config

### `testset/`
**Purpose**: Test organization test suites

**Key Components**:
- `testset.py`: Test suite entity for grouping related tests
- `handle_testsets.py`: Application service for test set management

**Architecture Role**: Provides higher-level test organization via test suites

## Domain Design Principles

- **Pure Business Logic**: No dependencies on infrastructure or frameworks
- **Rich Domain Models**: Entities contain business rules and validation logic
- **Application Services**: Coordinate domain entities to fulfill use cases
- **Plugin Architecture**: Extensible behavior through well-defined interfaces
- **Separation of Concerns**: Each module has a single, well-defined responsibility

## Usage Patterns

Domain modules are accessed through their application services (handle_* files) which coordinate between domain entities and external dependencies via ports/interfaces.