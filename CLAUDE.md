# Project: Data Tester

## Overview
Data Tester is a flexible, extensible framework for automating business validation tests for ETL pipelines via testing the data objects (files, tables) created by ETL pipelines.

## Tech Stack
- Python
- pydantic for data validation
- FastAPI for backend
- NiceGUI for frontend
- fsspec for file system interaction

## Code Style and Quality Standards
Claude must follow these rules when implementing code changes
- All code must pass linter, formatter checks. Apply formatting without asking permission
- All code must pass typechecks.
- Type hints are used in all signatures
- Always format code with ruff
- Imports are ALWAYS at the top of the module: Standard python library, then 3rd party, then own modules

## Architecture
The project uses hexagonal architecture with clear separation between domain logic, application services and adapters
- `src/config`: contains the application configuration
- `src/domain`: contains the domain logic with the main domain objects
- `src/domain_ports`: defines ports (interfaces) of the domain objects
- `src/domain_adapters`: containes implementations of domain_ports
- `src/drivers`: contains drivers which execute domain logic via domain ports
- `src/dtos`: contains data objects which are used in whole codebase
- `src/infrastructure_ports`: contains driven (infrastructure) ports (interfaces) which are used as contracts by drivers and domain logic
- `src/infrastructure`: contains implementations of the infrastructure ports, the most important are `storage`, `notifiers`, `backend` (aka `data_platform`)
- `src/apps`: contains applications (`..._app.py` modules, e.g. cli client, http client) and dependency injection which assemble all objects (`..._di.py` modules)
- `src/ui`: contains ui code

## Commands
- `uv sync`: install dependencies
- `uv sync --extra gcs`: install with optional GCS dependencies
- `uv run ruff check --fix`: Linting and formatting
- `uv run ty check`: Type checking
- `uv run pytest`: Run all tests
- `uv run pytest -m infrastructure`: Run infrastructure-dependent tests only
- `uv run pytest tests/unit/`: Run unit tests only
- `uv run pytest tests/integration/`: Run integration tests only

**MANDATORY**: DO NOT ask for permissions if they are already provided in `local.settings.json`.

## MANDATORY: Planning and Summary Workflow
1. Write your final plan in HUMAN-READABLE format to `project-root/agent-artifacts/{task-title}-plan.md`. **DO NOT prompt for permission to create folders**
2. DO NOT prompt for implementation until step 1 is complete
3. After implementation write a summary to `agent-artifacts/{task-title}-summary.md`

- [ ] Before prompting for implementation final plan persisted to `agent-artifacts/plans/plan-{task-title}.md`
- [ ] Summary persisted to `agent-artifacts/summaries/summary-{task-title}.md`