---
name: Project Context
description: data-tester — ETL pipeline business validation framework using hexagonal architecture
type: project
---

data-tester is a Python framework for automating business validation tests for ETL pipelines. It follows hexagonal architecture.

Key layers:
- `src/dtos/` — Pydantic-based data transfer objects (no business logic)
- `src/domain/` — core business logic (testcase execution, specification parsing, reports)
- `src/domain_ports/` — abstract command handlers (application ports)
- `src/infrastructure_ports/` — abstract backend/storage/notifier interfaces (secondary ports)
- `src/infrastructure/` — concrete adapters (DuckDB backend, FileStorage, DictStorage)
- `src/apps/cli/` — dependency injection wiring per feature
- `src/drivers/cli/` — CLI entry points / managers
- `src/config/` — Pydantic-settings-based app config

Test types supported: SCHEMA, ROWCOUNT, COMPARE (plus DUMMY_OK/NOK/EXCEPTION for testing).

Storage: DictStorage (in-memory, default LOCAL), FileStorage (local/GCS/memory via fsspec), JSON serialization.

**Why:** First full code review performed 2026-03-31. No known ongoing bugs or incidents at time of review.
**How to apply:** When making suggestions, be aware of the architectural constraints: domain logic must not depend on infrastructure adapters directly — always via ports.
