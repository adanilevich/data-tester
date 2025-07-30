# Applications Layer

The applications layer contains dependency injection containers that wire together domain services, infrastructure implementations, and external dependencies. This layer serves as the composition root for the hexagonal architecture.

## Structure

### `cli/`
**Purpose**: Command-line interface dependency injection containers

**Key Components**:
- `domain_config_di.py`: Domain configuration service composition
- `report_di.py`: Report generation service composition  
- `specification_di.py`: Specification handling service composition
- `testcase_di.py`: Test execution service composition
- `testset_di.py`: Test set management service composition

## Dependency Injection Pattern

Each DI module follows a consistent pattern:

### Service Composition
- Instantiates infrastructure adapters based on configuration
- Wires domain services with their required dependencies
- Creates complete service graphs for specific use cases

### Configuration Integration
- Reads application configuration to select implementations
- Routes requests to appropriate infrastructure backends
- Manages environment-specific service composition

### Factory Coordination
- Coordinates multiple factory instances (storage, backend, notifier)
- Ensures consistent service initialization across the application
- Manages lifecycle of singleton and per-request services

## Architecture Role

The applications layer serves as the **composition root** in hexagonal architecture:

### Dependency Flow
- Outer layer that depends on all other layers
- No other layer depends on the applications layer
- Controls the flow of dependencies from infrastructure to domain

### Service Orchestration
- Assembles complete service graphs for specific use cases
- Coordinates between multiple domain services
- Manages cross-cutting concerns like configuration and logging

### Entry Point Integration
- Provides pre-configured services to entry points (CLI, HTTP)
- Abstracts complex dependency relationships from drivers
- Enables consistent service behavior across different interfaces

## Usage Patterns

Applications are typically used by:
1. **Drivers** (`drivers/`): Import DI modules to get configured services
2. **Test Infrastructure**: Use DI containers for integration testing
3. **Service Initialization**: Bootstrap application services at startup

This pattern enables:
- Clean separation between service composition and business logic
- Easy testing through dependency substitution
- Consistent service configuration across different entry points
- Runtime flexibility through configuration-driven composition