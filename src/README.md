# Source Code Structure

Data Tester follows hexagonal architecture principles with clear separation of concerns across multiple layers. The source code is organized into distinct modules that implement domain logic, infrastructure adapters, and application entry points.

## Architecture Overview

The codebase implements hexagonal architecture with the following layers:

- **Domain Layer** (`domain/`): Core business logic and entities
- **Domain Ports** (`domain_ports/`): Interfaces for domain services
- **Infrastructure Ports** (`infrastructure_ports/`): Interfaces for external dependencies
- **Infrastructure** (`infrastructure/`): Concrete implementations of infrastructure ports
- **DTOs** (`dtos/`): Data transfer objects for cross-layer communication
- **Configuration** (`config/`): Application-wide configuration management
- **Applications** (`apps/`): Dependency injection containers
- **Drivers** (`drivers/`): External entry points (CLI, HTTP)

## Core Modules

### Domain Modules
- **`testcase/`**: Test execution engine with support for SCHEMA, ROWCOUNT, and COMPARE tests
- **`specification/`**: Test specification discovery and parsing from multiple formats
- **`report/`**: Test result reporting and formatting with pluggable output formats
- **`domain_config/`**: Domain-specific configuration management via YAML
- **`testset/`**: Test organization and batch execution capabilities

### Infrastructure Modules
- **`backend/`**: Data platform adapters (DuckDB, demo platforms)
- **`storage/`**: File and blob storage abstractions with multiple backend support
- **`notifier/`**: Test execution notification systems

## Key Design Patterns

- **Dependency Injection**: Each domain module has DI containers in `apps/`
- **Plugin Architecture**: Extensible via interfaces for test cases, formatters, and backends
- **Port-Adapter Pattern**: Clean separation between domain logic and infrastructure concerns
- **Factory Pattern**: Dynamic creation of storage, backend, and formatter instances

## Extension Points

The architecture supports extension through well-defined interfaces:
- Add new test types via `AbstractTestCase`
- Add data platforms via `IBackend` interface
- Add storage backends via `IStorage` interface
- Add report formats via `IReportFormatter` interface
- Add specification formats via `ISpecFormatter` interface