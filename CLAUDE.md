# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Data Tester is a flexible framework for automating business validation tests for ETL pipelines. It uses hexagonal architecture with clear separation between domain logic, application services, and adapters.

## Development Commands

**Setup and Dependencies:**
```bash
# Install dependencies (uses uv package manager)
uv sync

# Install with optional GCS dependencies
uv sync --extra gcs
```

**Code Quality and Testing:**
```bash
# Run all checks interactively
./run_checks.sh

# Individual commands:
ruff check --fix      # Linting and formatting
mypy                  # Type checking
pytest                # Run all tests
coverage run          # Run tests with coverage (excludes infrastructure tests)
```

**Test Execution:**
```bash
# Run tests excluding infrastructure tests (default coverage config)
pytest -m 'not skip_test and not infrastructure'

# Run specific test categories
pytest -m infrastructure    # Infrastructure tests only
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
```

## Architecture

The codebase follows hexagonal architecture principles with these key patterns:

### Core Domain Structure
- **Core Logic**: Business rules and entities (e.g., `testrun.py`, `specification.py`)
- **Application Services**: Use cases that orchestrate domain logic (e.g., `handle_testruns.py`, `handle_specs.py`)
- **Ports**: Interfaces defining contracts between layers (in `ports/` directories)
- **Adapters**: Infrastructure implementations of ports (in `adapters/` directories)
- **Drivers**: External entry points like CLI commands (in `drivers/` directories)

### Main Domain Modules

1. **testcase/**: Core testing execution engine
   - Executes different test types (SCHEMA, ROWCOUNT, COMPARE)
   - Manages test runs and precondition checks
   - Plugin architecture for different test case implementations

2. **specification/**: Handles test specification discovery and parsing
   - Finds specification files based on naming conventions
   - Supports multiple formats (SQL, XLSX) via formatter plugins
   - Matches specifications to test cases

3. **report/**: Test result reporting and formatting
   - Generates reports in multiple formats (JSON, TXT, XLSX)
   - Plugin architecture for custom report formats

4. **domain_config/**: Domain-specific configuration management
   - YAML-based configuration for different business domains
   - Defines data platform connections, storage locations

5. **testset/**: Test organization and batch execution
   - Groups related tests for execution
   - Manages test scenarios and environments

### Dependency Injection Pattern
Each domain module has a `dependency_injection.py` file that wires together:
- Storage backends (file system, cloud storage)
- Data platform adapters (DuckDB, demo platforms)
- Notifiers for test execution updates
- Formatters and naming conventions

### Key Interfaces
- `IDataPlatform`: Abstraction for different data platforms
- `IStorage`: File/blob storage abstraction
- `INotifier`: Test execution notifications
- `ISpecFormatter`: Specification format parsers
- `INamingConventions`: File naming pattern matchers

## Configuration

Configuration is handled via `src/config/config.py` using Pydantic settings:
- Environment variables prefixed with `DATATESTER_`
- Support for local file storage and cloud storage (GCS via optional dependency)
- Configurable data platforms, notifiers, and storage engines

## Testing Strategy

- **Unit Tests**: Test individual components in isolation (`tests/unit/`)
- **Integration Tests**: Test component interactions (`tests/integration/`)
- **Infrastructure Marker**: Tests marked with `@pytest.mark.infrastructure` require external dependencies
- **Coverage**: Configured to exclude abstract methods and infrastructure tests from coverage reports

## Key DTOs
All data transfer objects are defined in `src/dtos/`:
- `TestRunDTO`: Complete test execution results
- `TestCaseDTO`: Individual test case results  
- `SpecificationDTO`: Test specifications
- `LocationDTO`: Storage location abstraction
- `DomainConfigDTO`: Domain configuration data

## Extension Points
- Add new test types by implementing `AbstractTestCase`
- Add new data platforms via `IDataPlatform` interface
- Add new specification formats via `ISpecFormatter`
- Add new report formats via `IReportFormatter`
- Add new storage backends via `IStorage`