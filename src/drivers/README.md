# Drivers

**Purpose**: External entry points and adapters that drive the application by translating external requests into domain operations.

**Architecture Role**: Represents the "driving" side of hexagonal architecture - the left side adapters that receive external input and convert it into calls to application services.

## Structure

### `cli/`
**Purpose**: Command-line interface drivers for interactive and batch operations

**Key Components**:
- `CliDomainConfigManager`: CLI commands for domain configuration management
- `CliReportManager`: CLI commands for report generation and management  
- `CliSpecManager`: CLI commands for specification discovery and parsing
- `CliTestRunManager`: CLI commands for test execution and management
- `CliTestSetManager`: CLI commands for test suite organization

**Architecture Role**: Translates command-line arguments and options into domain commands

### `http/` (if applicable)
**Purpose**: HTTP/REST API drivers for web-based interactions

**Key Components**:
- HTTP endpoints and route handlers
- Request/response transformation
- API authentication and authorization

**Architecture Role**: Translates HTTP requests into domain operations

## Design Principles

### Adapter Pattern
- **Input Adaptation**: Convert external formats (CLI args, HTTP requests) to domain commands
- **Output Adaptation**: Transform domain results back to external formats
- **Protocol Independence**: Domain logic remains unaware of external protocols

### Separation of Concerns
- **Parsing**: Handle input validation and parsing
- **Routing**: Direct requests to appropriate application services
- **Formatting**: Convert domain responses to external formats
- **Error Handling**: Translate domain exceptions to appropriate external responses

### Technology Specific
Unlike ports (which are abstract), drivers contain:
- Framework-specific code (Click for CLI, FastAPI for HTTP)
- Protocol-specific handling (argument parsing, HTTP status codes)
- External library integrations

## Usage Patterns

### CLI Driver Flow
1. Parse command-line arguments
2. Validate input parameters  
3. Create appropriate command objects
4. Call domain application services
5. Format and display results

### Dependency Injection
Drivers typically:
- Receive application services via dependency injection
- Configure logging and error handling
- Manage application lifecycle (startup/shutdown)