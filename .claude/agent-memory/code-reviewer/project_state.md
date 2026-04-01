---
name: project_state
description: Snapshot of codebase state and key findings at time of full review
type: project
---

Full code review completed 2026-04-01 on branch `restructure-for-apps`.

**Why:** Regular quality gate review across all dimensions (architecture, correctness, security, performance, test coverage).

**Key structural facts (verified at time of review):**
- `StorageFactory.get_storage()` creates a new `FileStorage` instance on every call (no caching for LOCAL/GCS/MEMORY) — potential concern for GCS auth overhead
- `GCSFileSystem` is constructed in `FileStorage.__init__` but `gcp_project` is never threaded from `Config` through `StorageFactory` — GCS path is broken for production
- `Report.retrieve_report()` has a dead `try/except Exception: pass` block around `cast()` calls — `cast()` never raises, so the `ReportNotRetrievableError` at line 129 is unreachable
- `TestRun.known_testtypes` class attribute (dict) is declared but never used; `testrun.py` uses a `match` statement instead
- `PreConditionChecker._checker_factory` rebuilds its `known_checks` dict on every call via `__subclasses__()` reflection
- Two `print()` calls in `specification.py` lines 140/145 — errors silently swallowed with only stdout output
- `datetime.now()` (naive, system-local) used throughout — no timezone awareness
- `Config.model_post_init` hard-codes LOCAL-mode overrides, making some field declarations on the model redundant and blocking non-LOCAL env without code changes
- HTTP driver (`src/drivers/http/http.py`) is a stub ("To be implemented")
- `tests/unit/infrastructure/storage/test_file_storage.py` exists and has tests (FileStorage with MEMORY backend)

**How to apply:** Use these to quickly orient in future conversations rather than re-reading all files.
