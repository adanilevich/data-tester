# Data Transfer Objects (DTOs)

DTOs provide immutable data structures for transferring information between layers of the application. Built on Pydantic models, they ensure type safety, validation, and consistent serialization across the system.

## Core DTOs

### `dto.py`
**Purpose**: Base DTO class with common functionality

**Key Features**:
- `DTO`: Base class for all data transfer objects
- Standardized serialization/deserialization (JSON, dict)
- Object identity management via `object_id` property
- Immutable data structures with copy semantics

### `testcase.py`
**Purpose**: Test execution data structures

**Key DTOs**:
- `TestRunDTO`: Complete test run results with execution metadata
- `TestCaseDTO`: Individual test case results and execution details
- `TestDefinitionDTO`: Test case configuration and parameters
- `TestType`, `TestResult`, `TestStatus`: Enumerations for test classification

### `specification.py`
**Purpose**: Test specification data structures

**Key DTOs**:
- `SpecificationDTO`: Test specification with validation rules
- `SchemaSpecificationDTO`: Database schema validation specifications
- `TestObjectDTO`: Target objects for testing (tables, views, etc.)

### `report.py`
**Purpose**: Reporting data structures

**Key DTOs**:
- `ReportDTO`: Test case and test run report data
- Report metadata and formatting information
- Aggregated results and summary statistics

### `location.py`
**Purpose**: Storage location abstraction

**Key DTOs**:
- `LocationDTO`: Abstract storage location representation
- `StorageObject`: Serializable object storage container
- Location routing and addressing information

### `domain_config.py`
**Purpose**: Domain configuration data structures

**Key DTOs**:
- `DomainConfigDTO`: Business domain configuration settings
- Environment-specific configuration parameters
- Storage paths and connection settings

### `testset.py`
**Purpose**: Test organization data structures

**Key DTOs**:
- `TestSetDTO`: Test suite definitions and grouping
- Batch execution configuration
- Test scenario management

## Design Principles

### Type Safety
Pydantic-based validation ensures:
- Runtime type checking
- Data validation on construction
- Clear error messages for invalid data

### Serialization
Consistent serialization support:
- JSON serialization for API responses
- Dictionary conversion for storage
- Copy operations for data transformation

## Usage Patterns

DTOs serve as the data contract between:
- Domain services and infrastructure adapters
- Application layers and external interfaces
- Storage systems and business logic
- API endpoints and internal processing

They provide a stable interface that isolates layers from internal implementation changes while ensuring data integrity and type safety throughout the application.