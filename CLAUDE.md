# Project: Data Tester

## Overview
Data Tester is a flexible, extensible framework for automating business validation tests for ETL pipelines via testing the data objects (files, tables) created by ETL pipelines.

## Tech Stack
- Python
- pydantic for data validation
- fsspec for file system interaction

## Code Style and Quality Standards
Claude must follow these rules when implementing code changes
- All code must pass linter and formatter checks. Claude can automatically apply
formatting without asking for permission
- All code must pass typechecks. "... is defined" here messages from MyPy can be ignored
unless Claude is promted explicitely to address them
- Type hints are used in all signatures and function bodies

## Architecture
The project uses hexagonal architecture with clear separation between domain logic, application services and adapters
- `src/apps`: contains applications (cli client, http backend, etc.) which assemble drivers, ports, adapters and domain logic using dependency injection (`..._di.py` modules)
- `src/config`: contains the application configuration
- `src/domain`: contains the domain logic with the main domain objects being `domain_config`, `report`, `specification`, `testcase`, `testset`
- `src/domain_ports`: defines ports (interfaces) of the domain objects. These ports are used by drivers to execute business logic
- `src/drivers`: contains drivers for each app (cli, http) which define business use cases
- `src/dtos`: contains data objects which are used in whole codebase
- `src/infrastructure_ports`: contains driven (infrastructure) ports (interfaces) which are used as contracts by drivers and domain logic
- `src/infrastructure`: contains implementations of the infrastructure ports, the most important are `storage`, `notifiers`, `backend` (aka `data_platform`)

## Commands
- `uv sync`: install dependencies
- `uv sync --extra gcs`: install with optional GCS dependencies
- `uv run ruff check --fix`: Linting and formatting
- `uv run ty check`: Type checking
- `uv run pytest`: Run all tests
- `uv run pytest -m infrastructure`: Run infrastructure-dependent tests only
- `uv run pytest tests/unit/`: Run unit tests only
- `uv run pytest tests/integration/`: Run integration tests only
- `./run_checks.sh`: Run all checks: linting, formatting, typechecks, tests

## Important Notes
- always execute tests, formatter and linter checks and typechecks before finalizing code. Fix any occuring issues