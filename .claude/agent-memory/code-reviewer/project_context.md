---
name: Project Context
description: Data Tester architecture, key patterns, and code review findings summary (latest: 2026-04-01 branch restructure-for-apps)
type: project
---

Data Tester is a hexagonal-architecture Python framework for ETL business validation. Key layers: domain (testcase, specification, report, testset, domain_config), domain_ports (command interfaces), infrastructure_ports (IBackend, IStorage, INotifier), infrastructure (DemoBackend/DummyBackend, FileStorage/DictStorage, formatters), apps/cli (DI wiring), drivers/cli (thin adapters).

## Code Review findings — 2026-04-01 (branch: restructure-for-apps)

### Still-open from prior review
- PreConditionChecker._checker_factory re-creates `self.known_checks` as an instance attribute on every call (should be module-level or class-level constant, or use `__init_subclass__` registry) — Medium
- `Literal[TestResult.OK]` / `Literal[TestResult.NOK]` used as inline type re-annotations on instance assignment in testrun.py line 102/104 — Low
- Silent broad `except Exception: pass` in report.retrieve_report (the cast never throws; the guard is dead code) — Low
- Silent broad `except Exception: continue` in specification.find_specs and testset.py — Medium

### New findings in this review pass
- DemoBackend.get_schema_from_query hardcodes `SELECT * FROM __expected__` appended to user query, which is incorrect SQL construction (line 237) — High
- DemoBackend._init_dbs attaches DuckDB files at construction time but never detaches them; if multiple DemoBackend instances are created (e.g. in tests), the ATTACH will silently succeed due to IF NOT EXISTS but state is shared via the module-level duckdb connection — Medium
- DummyBackend is missing the `supports_clustering`, `supports_partitions`, `supports_primary_keys` class attributes required by IBackend; SchemaTestCase will raise AttributeError when used with DummyBackend — High
- `AbstractCheck.__subclasses__()` only returns direct subclasses; deeply nested subclass hierarchies would be missed — Low
- `SpecFactory.create_from_dict` uses `SpecificationDTO.__subclasses__()` for the same reason — Low
- `DTO.object_id` raises NotImplementedError inside a property instead of using `@abstractmethod` — Low
- Config.model_post_init overwrites caller-set values silently when ENV==LOCAL — Medium
- `add_detail` in AbstractTestCase has a dead None-guard (details is always initialised as [] in __init__) — Low
- `CompareTestCase.sample_size` property also has a dead `if self.details is None` guard — Low

**Why:** Comprehensive review on branch restructure-for-apps.
**How to apply:** Use as baseline for future incremental reviews; don't re-flag already fixed issues.
