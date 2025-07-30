# Infrastructure Ports

Infrastructure ports define the contracts between the domain layer and external systems. These interfaces abstract away infrastructure concerns and enable dependency inversion, allowing the domain to remain independent of specific technologies.

## Port Categories

### `backend/`
**Purpose**: Data platform abstraction interfaces

**Key Interfaces**:
- `IBackend`: Core interface for data platform operations
  - Query execution and result retrieval
  - Schema introspection and validation
  - Data comparison capabilities
  - Platform-specific feature flags (clustering, partitioning)
- `IBackendFactory`: Factory interface for creating backend instances

**Domain Usage**: Enables testcases to execute queries and validate data across different platforms

### `storage/`
**Purpose**: Storage system abstraction interfaces

**Key Interfaces**:
- `IStorage`: Core storage operations interface
  - Object persistence and retrieval
  - Location-based storage routing
  - Serialization format abstraction
- `IStorageFactory`: Factory interface for creating storage instances based on location

**Domain Usage**: Enables domain entities to persist and retrieve data without coupling to specific storage technologies

### `notifier/`
**Purpose**: Notification system abstraction

**Key Interfaces**:
- `INotifier`: Event notification interface
  - Test execution progress updates
  - Result publication
  - Error and status notifications

**Domain Usage**: Allows domain services to communicate test progress and results to external systems

## Design Principles

### Dependency Inversion
Infrastructure ports ensure that:
- Domain layer depends on abstractions, not concrete implementations
- Infrastructure implementations depend on domain-defined interfaces
- Dependencies flow inward toward the domain core

### Interface Segregation
Each port interface is focused and cohesive:
- Single responsibility per interface
- Minimal method surface area
- Clear behavioral contracts

### Abstraction Level
Ports are designed at the right level of abstraction:
- Hide infrastructure complexity from domain
- Expose necessary capabilities for business logic
- Maintain technology independence

## Usage Patterns

Infrastructure ports are typically:
1. Defined in this module as abstract interfaces
2. Implemented in the `infrastructure/` module
3. Injected into domain services through dependency injection
4. Used by domain entities and application services to fulfill business requirements

This pattern enables clean architecture, testability, and technology independence throughout the application.