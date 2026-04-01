---
name: project_state
description: Snapshot of codebase state and key findings at time of full review
type: project
---

Full code review completed 2026-04-01 on branch `restructure-for-apps`.

**Why:** Regular quality gate review across all dimensions (architecture, correctness, security, performance, test coverage).

**Key structural facts (verified at time of review):**
- `StorageFactory` (`src/infrastructure/storage/storage_factory.py`) has a typo bug: MEMORY branch writes to `self.mem_storage` (no underscore) but reads from `self.mem_storage` — first access always creates new instance, caching is broken
- `DemoBackend._init_dbs` calls `duckdb.execute()` using f-string interpolation with `db_file` path from filesystem listing — not a user input vector but worth noting
- `DemoBackend.get_schema_from_query` uses `DROP TABLE IF EXISTS __query__` pattern in DuckDB which mutates shared module-level state — concurrent calls would collide
- `_get_testrun_id` in `TestRunDTO.from_testcases` checks `len(set(testrun_ids)) == 1` BEFORE checking `len(testrun_ids) == 0`, so an empty list raises the wrong error
- `RowCountTestCase._validate_counts` type-ignores on enum access `self.result.NA` — result field is typed as `TestResult` so `.NA` is valid but accessing via instance is an anti-pattern
- `CompareTestCase` passes `self.schema.primary_keys` directly with `# type: ignore` to backend methods that expect `List[str]` — primary_keys is `Optional[List[str]]`, the precondition check should have already guarded this but type safety is incomplete
- Silent `except Exception: continue` in `specification.py:170` swallows all parse errors without logging
- `Config.model_post_init` forces LOCAL-mode fields even when DATATESTER_ENV != LOCAL was set before (ENV var set in test changes global interpreter state)
- HTTP driver (`src/drivers/http/http.py`) is a stub ("To be implemented")
- `datetime.now()` (naive, system-local) used throughout — no timezone awareness
- `DTO.object_id` raises `NotImplementedError` at runtime; no abstract enforcement — several DTO subclasses (e.g. `SpecificationDTO`, `TestCaseDTO`, `TestDTO`) don't implement it

**How to apply:** Use these to quickly orient in future conversations rather than re-reading all files.
