# Infrastructure Layer

The infrastructure layer provides concrete implementations of external dependencies and technical concerns. This layer implements the interfaces defined in `infrastructure_ports/` and handles all external system interactions.

## Infrastructure Modules

### `backend/`
**Purpose**: Data platform adapters and query execution

**Key Components**:
- `demo/`: Demo backend implementation with sample data and query handling
- `dummy/`: Dummy backend for testing and development
- `map.py`: Backend factory mapping for dynamic backend selection

**Interfaces Implemented**: `IBackend`, `IBackendFactory`

**Capabilities**:
- Query execution against different data platforms
- Schema introspection and validation
- Data comparison operations
- Support for clustering and partitioning (platform-dependent)

### `storage/`
**Purpose**: File and blob storage abstractions with multiple backend support

**Key Components**:
- `file_storage.py`: Local filesystem storage implementation
- `dict_storage.py`: In-memory storage for testing
- `storage_factory.py`: Dynamic storage backend selection
- `json_formatter.py`: JSON serialization for storage
- `formatter_factory.py`: Pluggable serialization formats

**Interfaces Implemented**: `IStorage`, `IStorageFactory`, `IFormatter`, `IFormatterFactory`

**Capabilities**:
- Local file system storage
- In-memory storage for testing
- Extensible serialization formats
- Location-based storage routing

### `notifier/`
**Purpose**: Test execution notification systems

**Key Components**:
- `stdout_notifier.py`: Console output notifications
- `in_memory_notifier.py`: In-memory notification storage for testing
- `map.py`: Notifier factory mapping

**Interfaces Implemented**: `INotifier`

**Capabilities**:
- Real-time test execution updates
- Multiple notification channels
- Pluggable notification backends

## Design Patterns

- **Adapter Pattern**: Each infrastructure module adapts external systems to domain interfaces
- **Factory Pattern**: Dynamic selection of implementations based on configuration
- **Strategy Pattern**: Pluggable algorithms for storage formatting and backend selection
- **Registry Pattern**: Maps for discovering and instantiating implementations

## Configuration Integration

Infrastructure implementations are selected and configured through the application's configuration system, allowing runtime switching between different backends, storage systems, and notification channels.

## Extension Points

New infrastructure implementations can be added by:
1. Implementing the corresponding interface from `infrastructure_ports/`
2. Adding factory registration in the appropriate `map.py` file
3. Updating configuration to support the new implementation