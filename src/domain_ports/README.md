# Domain Ports

**Purpose**: Domain-specific port interfaces that define contracts between domain application services and external concerns, following Command Query Responsibility Segregation (CQRS) patterns.

**Architecture Role**: Acts as the outbound ports in hexagonal architecture, allowing domain services to interact with external systems without coupling to specific implementations.

## Structure

### Command-Query Separation
This module follows CQRS principles by separating:
- **Commands**: Operations that modify state (Save, Create, Execute)
- **Queries**: Operations that retrieve data (Load, Fetch, List)

### Domain-Specific Handlers

#### `domain_config/`
**Purpose**: Domain configuration management contracts

**Key Interfaces**:
- `IDomainConfigHandler`: Configuration persistence and retrieval
- `FetchDomainConfigsCommand`: Query for loading domain configurations
- `SaveDomainConfigCommand`: Command for persisting configurations

#### `report/`
**Purpose**: Test reporting and artifact management contracts

**Key Interfaces**:
- `IReportCommandHandler`: Report creation and persistence
- `CreateReportCommand`: Command for generating reports
- `SaveReportCommand`: Command for persisting reports
- `LoadReportCommand`: Query for retrieving reports
- `GetReportArtifactCommand`: Query for report artifacts
- `SaveReportArtifactsForUsersCommand`: Command for user-specific artifacts

#### `specification/`
**Purpose**: Test specification handling contracts

**Key Interfaces**:
- `ISpecCommandHandler`: Specification parsing and management
- `FetchSpecsCommand`: Query for discovering specifications
- `ParseSpecCommand`: Command for processing specification files

#### `testcase/`
**Purpose**: Test execution and management contracts

**Key Interfaces**:
- `ITestRunCommandHandler`: Test execution coordination
- `ExecuteTestRunCommand`: Command for running tests
- `SaveTestRunCommand`: Command for persisting test results
- `LoadTestRunCommand`: Query for retrieving test results
- `SetReportIdsCommand`: Command for linking reports to tests

#### `testset/`
**Purpose**: Test suite organization contracts

**Key Interfaces**:
- `ITestSetCommandHandler`: Test set management
- `SaveTestSetCommand`: Command for persisting test sets
- `LoadTestSetCommand`: Query for retrieving test sets
- `ListTestSetsCommand`: Query for listing available test sets

## Design Principles

### Port-Adapter Pattern
- **Ports**: Define what the domain needs from external systems
- **Adapters**: Implement these ports using specific technologies
- **Inversion of Control**: Domain depends on abstractions, not implementations

### Command Objects
Each operation is encapsulated as a command object containing:
- Input parameters
- Validation rules
- Clear intent and semantics

### Technology Agnostic
Interfaces are defined without assumptions about:
- Storage technology (database, file system, cloud)
- Serialization format (JSON, XML, binary)
- Transport mechanism (HTTP, messaging, local calls)