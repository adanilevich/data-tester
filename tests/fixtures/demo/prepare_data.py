"""
Mini data-warehouse fixture for integration tests.

Creates a DWH with raw (CSV files), staging (DuckDB tables), and core
(DuckDB tables) layers. The data originates from four Excel files in
this directory and is loaded according to the plan below.

Domains / Stages / Instances
-----------------------------
Two business domains exist: **payments** and **sales**.
Each domain can have databases in stages **test** and **uat**.
Within each stage, named instances (alpha, beta, main) hold separate
copies of the data.

Source Files
------------
  customers_2024-01-01.xlsx  (customers_1)   — 4 customer rows
  customers_2024-01-02.xlsx  (customers_2)   — 6 customer rows
  transactions_2024-01-01.xlsx (transactions_1) — 9 transaction rows
  transactions_2024-01-02.xlsx (transactions_2) — 9 transaction rows

Loading Plan
------------
  Domain    Stage  Instance  Files loaded                         Layers
  --------  -----  --------  -----------------------------------  ----------------
  payments  uat    main      customers_1                          raw + stage
  payments  test   alpha     customers_1, customers_2,            raw + stage + core
                             transactions_1, transactions_2
  payments  test   beta      customers_1, transactions_1          raw + stage + core
  sales     test   main      customers_2                          raw + stage
  sales     uat    —         (nothing loaded)                     —

Deliberate Data-Quality Issues (for testing)
--------------------------------------------
  1. customers_2 is truncated to 4 of 6 rows during stage loading
     (LIMIT 4) to simulate an incomplete load.
  2. The core layer JOIN filters out rows where customer_region = 'africa'.
  3. The sales domain has no core layer at all → causes ABORTED/NA in tests.

DWH Layout
----------

  xlsx files ──► RAW layer (CSV)     ──► STAGE layer (DuckDB) ──► CORE layer (DuckDB)
                 <location>/raw/          <location>/dbs/           <location>/dbs/

  payments_uat.db                     payments_test.db
  ┌───────────────────────┐           ┌──────────────────────────────────────────────┐
  │ schema: main          │           │ schema: alpha                                │
  │  └─ stage_customers   │           │  ├─ stage_customers       (8 rows)           │
  └───────────────────────┘           │  ├─ stage_transactions    (18 rows)          │
                                      │  └─ core_customer_transactions (12 rows)     │
                                      ├──────────────────────────────────────────────┤
                                      │ schema: beta                                 │
                                      │  ├─ stage_customers                          │
                                      │  ├─ stage_transactions                       │
                                      │  └─ core_customer_transactions               │
                                      └──────────────────────────────────────────────┘
  sales_test.db
  ┌───────────────────────┐
  │ schema: main          │
  │  └─ stage_customers   │
  └───────────────────────┘

Assertions (sanity checks during loading)
-----------------------------------------
  payments_test.alpha.stage_customers:            8 rows
  payments_test.alpha.stage_transactions:        18 rows
  payments_test.alpha.core_customer_transactions: 12 rows

SQL / DDL
---------
All SQL statements live in .sql files next to this module.
See ddl_*.sql (table creation) and dml_*.sql (data loading).

Public API
----------
  prepare_data(location)  — create the full DWH at the given path
  clean_up()              — delete everything created by prepare_data
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import duckdb
import polars as pl
from fsspec.implementations.local import LocalFileSystem

__all__ = ["prepare_data", "clean_up"]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_XLSX_DIR: Path = Path(__file__).parent
_SQL_DIR: Path = Path(__file__).parent

_XLSX_FILES: dict[str, Path] = {
    "customers_1": _XLSX_DIR / "customers_2024-01-01.xlsx",
    "customers_2": _XLSX_DIR / "customers_2024-01-02.xlsx",
    "transactions_1": _XLSX_DIR / "transactions_2024-01-01.xlsx",
    "transactions_2": _XLSX_DIR / "transactions_2024-01-02.xlsx",
}

# ---------------------------------------------------------------------------
# Loading plan — one row per file-to-location mapping
# ---------------------------------------------------------------------------


class _LoadEntry(NamedTuple):
    """One row of the loading plan: a file loaded into a specific location."""

    file: str  # key into _XLSX_FILES
    domain: str
    stage: str
    instance: str
    object_name: str  # 'customers' or 'transactions'


#   file               domain      stage   instance  object
#   ─────────────────  ──────────  ──────  ────────  ────────────
_LOADING_PLAN: list[_LoadEntry] = [
    _LoadEntry("customers_1",    "payments", "uat",  "main",  "customers"),
    _LoadEntry("customers_1",    "payments", "test", "alpha", "customers"),
    _LoadEntry("customers_1",    "payments", "test", "beta",  "customers"),
    _LoadEntry("customers_2",    "payments", "test", "alpha", "customers"),
    _LoadEntry("customers_2",    "sales",    "test", "main",  "customers"),
    _LoadEntry("transactions_1", "payments", "test", "alpha", "transactions"),
    _LoadEntry("transactions_1", "payments", "test", "beta",  "transactions"),
    _LoadEntry("transactions_2", "payments", "test", "alpha", "transactions"),
]  # fmt: skip

# Which (domain, stage, instance) combos get a core layer
_CORE_TARGETS: list[tuple[str, str, str]] = [
    ("payments", "test", "alpha"),
    ("payments", "test", "beta"),
]

# ---------------------------------------------------------------------------
# SQL helpers
# ---------------------------------------------------------------------------


def _read_sql(filename: str) -> str:
    """Read a .sql template file from the SQL directory."""
    return (_SQL_DIR / filename).read_text()


# ---------------------------------------------------------------------------
# Module state for clean_up
# ---------------------------------------------------------------------------

_active_location: Path | None = None

# ---------------------------------------------------------------------------
# Private implementation
# ---------------------------------------------------------------------------


def _csv_path(entry: _LoadEntry, raw_path: Path) -> Path:
    """Derive the CSV filepath in the raw layer from a load entry."""
    xlsx_name = _XLSX_FILES[entry.file].name
    csv_name = xlsx_name.replace(".xlsx", ".csv")
    return (
        raw_path
        / entry.domain
        / entry.stage
        / entry.instance
        / entry.object_name
        / csv_name
    )


def _setup_raw_layer(plan: list[_LoadEntry], raw_path: Path) -> None:
    """Create folder structure for the raw CSV layer."""
    print("\nSETTING UP RAW LAYER:")
    fs = LocalFileSystem()

    # Collect unique folder paths
    folders: list[tuple[str, str, str, str]] = []
    for e in plan:
        key = (e.domain, e.stage, e.instance, e.object_name)
        if key not in folders:
            folders.append(key)
    print("All folder objects to be created: ", folders)

    # Clean and recreate
    if fs.exists(str(raw_path)):
        fs.rm(str(raw_path), recursive=True)

    created: list[str] = []
    for domain, stage, instance, obj in folders:
        target = str(raw_path / domain / stage / instance / obj)
        fs.mkdir(target, create_parents=True)
        created.append(target)
    print("Created folders: ", created)


def _setup_databases(
    plan: list[_LoadEntry],
    core_targets: list[tuple[str, str, str]],
    db_path: Path,
) -> None:
    """Create DuckDB databases, schemas, and empty tables."""
    print("\nSETTING UP DATABASES:")
    fs = LocalFileSystem()

    # Collect unique (database, schema, table) from staging entries
    stage_objects: set[tuple[str, str, str]] = set()
    for e in plan:
        database = f"{e.domain}_{e.stage}"
        stage_objects.add((database, e.instance, f"stage_{e.object_name}"))

    # Add core layer entries
    core_objects: set[tuple[str, str, str]] = set()
    for domain, stage, instance in core_targets:
        database = f"{domain}_{stage}"
        core_objects.add((database, instance, "core_customer_transactions"))

    all_objects = sorted(stage_objects | core_objects)
    print("All database objects to be created: ", all_objects)

    # Clean and recreate database directory
    if fs.exists(str(db_path)):
        fs.rm(str(db_path), recursive=True)
    fs.mkdir(str(db_path), create_parents=False)

    attach_sql = _read_sql("ddl_attach_database.sql")
    ddl_templates: dict[str, str] = {
        "stage_customers": _read_sql("ddl_stage_customers.sql"),
        "stage_transactions": _read_sql("ddl_stage_transactions.sql"),
        "core_customer_transactions": _read_sql("ddl_core_customer_transactions.sql"),
    }

    for database, schema, table in all_objects:
        # Attach database file (creates .db on disk if not exists)
        db_filepath = str(db_path / database) + ".db"
        duckdb.execute(attach_sql.format(db_filepath=db_filepath, database=database))

        # Create schema and table
        if table not in ddl_templates:
            raise ValueError(f"Unknown table name: {table}")
        duckdb.execute(ddl_templates[table].format(database=database, schema=schema))

    created_tables = duckdb.sql(
        "SELECT * FROM INFORMATION_SCHEMA.TABLES "
        "ORDER BY table_catalog, table_schema, table_name"
    ).pl()
    print("Created tables: ", created_tables)


def _load_raw_layer(plan: list[_LoadEntry], raw_path: Path) -> None:
    """Read xlsx files and write them as CSVs into the raw layer."""
    print("\nLOADING RAW LAYER:")
    loaded: list[str] = []
    for entry in plan:
        df = pl.read_excel(_XLSX_FILES[entry.file])
        target = _csv_path(entry, raw_path)
        df.write_csv(str(target))
        loaded.append(str(target))
    print("Raw layer loaded files: ", loaded)


def _load_staging_layer(plan: list[_LoadEntry], raw_path: Path) -> None:
    """Load CSVs into DuckDB staging tables. Truncates customers_2 to 4 rows."""
    print("\nLOADING STAGING LAYER:")
    insert_sql = _read_sql("dml_load_staging.sql")
    loaded_tables: list[str] = []

    for entry in plan:
        csv = _csv_path(entry, raw_path)
        database = f"{entry.domain}_{entry.stage}"
        table = f"stage_{entry.object_name}"
        filename = csv.name

        # Truncate customers_2 to 4/6 rows to simulate load errors
        limit_clause = "LIMIT 4" if entry.file == "customers_2" else ""

        duckdb.execute(
            insert_sql.format(
                database=database,
                schema=entry.instance,
                table=table,
                csv_filepath=str(csv),
                filename=filename,
                limit_clause=limit_clause,
            )
        )
        loaded_tables.append(f"{database}.{entry.instance}.{table}")

    loaded_tables = sorted(set(loaded_tables))
    print("Loaded staging tables: ", loaded_tables)

    # Sanity checks
    customers = _count_rows("payments_test.alpha.stage_customers")
    assert customers == 8, f"Expected 8 customers, got {customers}"
    print(f"Loaded {customers} customers into payments_test.alpha.stage_customers")

    transactions = _count_rows("payments_test.alpha.stage_transactions")
    assert transactions == 18, f"Expected 18 transactions, got {transactions}"
    print(
        f"Loaded {transactions} transactions into payments_test.alpha.stage_transactions"
    )


def _load_core_layer(core_targets: list[tuple[str, str, str]]) -> None:
    """Join staging tables into core_customer_transactions, filtering out africa."""
    print("\nLOADING CORE LAYER:")
    insert_sql = _read_sql("dml_load_core_customer_transactions.sql")

    for domain, stage, instance in core_targets:
        database = f"{domain}_{stage}"
        duckdb.execute(insert_sql.format(database=database, schema=instance))

    # Sanity check
    count = _count_rows("payments_test.alpha.core_customer_transactions")
    assert count == 12, f"Expected 12 core rows, got {count}"
    print(
        f"Loaded {count} transactions into payments_test.alpha.core_customer_transactions"
    )


def _detach_all_databases(db_path: Path) -> None:
    """Detach all databases from the default connection to release file handles."""
    fs = LocalFileSystem()
    if fs.exists(str(db_path)):
        for f in fs.ls(str(db_path)):
            if f.endswith(".db"):
                db_name = Path(f).stem
                duckdb.execute(f"DETACH DATABASE IF EXISTS {db_name};")


def _count_rows(table_fqn: str) -> int:
    """Count rows in a DuckDB table by fully-qualified name."""
    row = duckdb.sql(f"SELECT COUNT(*) AS n FROM {table_fqn}").fetchone()
    assert row is not None
    return row[0]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def prepare_data(location: Path = Path(__file__).parent) -> None:
    """Create the full mini-DWH (raw + staging + core layers) at *location*."""
    global _active_location  # noqa: PLW0603
    _active_location = location

    raw_path = location / "raw"
    db_path = location / "dbs"

    _setup_raw_layer(_LOADING_PLAN, raw_path)
    _setup_databases(_LOADING_PLAN, _CORE_TARGETS, db_path)
    _load_raw_layer(_LOADING_PLAN, raw_path)
    _load_staging_layer(_LOADING_PLAN, raw_path)
    _load_core_layer(_CORE_TARGETS)
    _detach_all_databases(db_path)


def clean_up() -> None:
    """Delete all data created by the last prepare_data() call."""
    global _active_location  # noqa: PLW0603
    if _active_location is None:
        return

    raw_path = _active_location / "raw"
    db_path = _active_location / "dbs"
    fs = LocalFileSystem()

    # Detach DuckDB databases before deleting files
    _detach_all_databases(db_path)

    for path in (raw_path, db_path):
        if fs.exists(str(path)):
            fs.rm(str(path), recursive=True)

    _active_location = None
