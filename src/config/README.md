# Configuration Management

The configuration module provides centralized application configuration management using Pydantic Settings. It handles environment-specific settings, external service configuration, and runtime behavior control.

## Core Components

### `config.py`
**Purpose**: Application-wide configuration management

**Key Features**:
- `Config`: Main configuration class with environment variable integration
- Environment-prefixed settings (`DATATESTER_*`)
- Type-safe configuration with validation
- Default values for development and testing

## Configuration Categories

### Environment Configuration
- `DATATESTER_ENV`: Runtime environment (LOCAL, DEV, PROD)
- Environment-specific behavior and resource allocation

### Cloud Platform Configuration
- `DATATESTER_GCP_PROJECT`: Google Cloud Platform project settings
- `DATATESTER_USE_GCS_STORAGE`: Cloud storage enablement
- Integration with cloud-native services

### Data Platform Configuration
- `DATATESTER_DATA_PLATFORM`: Target data platform selection (DUMMY, DEMO, etc.)
- Platform-specific connection and capability settings

### Notification Configuration
- `DATATESTER_NOTIFIERS`: List of enabled notification channels
- Multi-channel notification routing

### Storage Configuration
- Storage backend selection and routing
- Location-specific storage configuration
- Serialization format preferences

## Design Principles

### Environment-Driven Configuration
- Twelve-factor app compliance
- Environment variable precedence
- Secure credential management

### Type Safety
- Pydantic-based validation ensures configuration integrity
- Runtime type checking prevents configuration errors
- Clear error messages for invalid settings

### Layered Configuration
- Application-level technical configuration (this module)
- Domain-level business configuration (`domain_config/`)
- Clear separation of technical vs. business concerns

## Usage Patterns

Configuration is typically:
1. Loaded once at application startup
2. Injected into dependency containers
3. Used by factories to select appropriate implementations
4. Accessed by infrastructure adapters for connection details

The configuration system supports both development flexibility and production reliability through environment-specific defaults and validation.