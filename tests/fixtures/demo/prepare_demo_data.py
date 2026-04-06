"""
Mini data-warehouse fixture for integration tests.

Creates a DWH with raw (CSV files), staging (DuckDB tables), core
(DuckDB tables), and mart (DuckDB tables) layers. Data is generated
programmatically as CSV and loaded according to the plan below.

Domains / Stages / Instances
-----------------------------
Two business domains exist: **payments** and **sales**.
Each domain can have databases in stages **test** and **uat**.
Within each stage, named instances (alpha, beta, main) hold separate
copies of the data.

Source Data (generated as CSV)
------------------------------
  customers_2024-01-01.csv  (customers_1)    — ~100 customer rows
  customers_2024-01-02.csv  (customers_2)    — ~105 customer rows
  accounts_2024-01-01.csv   (accounts_1)     — ~200 account rows
  accounts_2024-01-02.csv   (accounts_2)     — ~210 account rows
  transactions_2024-01-01.csv (transactions_1) — ~1000 transaction rows
  transactions_2024-01-02.csv (transactions_2) — ~1000 transaction rows

Loading Plan
------------
  Domain    Stage  Instance  Files loaded                         Layers
  --------  -----  --------  -------------------------  -----------
  payments  uat    main      accounts_1, txn_1         raw+stg+core
  payments  test   alpha     accounts_1/2, txn_1/2     all layers
  payments  test   beta      accounts_1, txn_1         all layers
  sales     test   main      customers_1/2, txn_1/2    all layers

  Note: payments has accounts+transactions (no customers).
        sales has customers+transactions (no accounts).

Deliberate Data-Quality Issues (for testing)
--------------------------------------------
  1. transactions_2 is truncated by half during stage loading in ALL stages
     (payments domain) to simulate an incomplete load → triggers STAGECOUNT NOK.
  2. The sales core layer JOIN filters out rows where customer_region = 'africa'
     → triggers COMPARE NOK.

DWH Layout
----------
  CSV files ──► RAW layer (CSV)  ──► STAGE layer ──► CORE layer ──► MART layer
                <location>/raw/      <location>/dbs/  <location>/dbs/ <location>/dbs/

  payments_uat.db                     payments_test.db
  ┌───────────────────────┐           ┌──────────────────────────────────────────────┐
  │ schema: main          │           │ schema: alpha                                │
  │  ├─ stage_accounts    │           │  ├─ stage_accounts                           │
  │  ├─ stage_transactions│           │  ├─ stage_transactions  (txn_2 truncated)    │
  │  └─ core_account_payments         │  ├─ core_account_payments                    │
  └───────────────────────┘           │  └─ mart_account_payments_by_date            │
                                      ├──────────────────────────────────────────────┤
                                      │ schema: beta                                 │
                                      │  ├─ stage_accounts                           │
                                      │  ├─ stage_transactions                       │
                                      │  ├─ core_account_payments                    │
                                      │  └─ mart_account_payments_by_date            │
                                      └──────────────────────────────────────────────┘
  sales_test.db
  ┌─────────────────────────────────────────┐
  │ schema: main                            │
  │  ├─ stage_customers                     │
  │  ├─ stage_transactions                  │
  │  ├─ core_customer_transactions (no africa) │
  │  └─ mart_customer_revenues_by_date      │
  └─────────────────────────────────────────┘

Public API
----------
  prepare_demo_data(location)   — create the full DWH at the given path
  clean_up_demo_data()          — delete everything created by prepare_demo_data
"""

from __future__ import annotations

import random
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import duckdb
import polars as pl
from fsspec.implementations.local import LocalFileSystem

__all__ = ["prepare_demo_data", "clean_up_demo_data"]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SQL_DIR: Path = Path(__file__).parent

_REGIONS: list[str] = [
    "europe", "asia", "americas", "africa", "oceania",
]
_CUSTOMER_TYPES: list[str] = ["individual", "corporate", "government"]
_ACCOUNT_TYPES: list[str] = ["checking", "savings", "credit"]

# ---------------------------------------------------------------------------
# Data generation
# ---------------------------------------------------------------------------


def _generate_customers(n: int, date: str, seed: int) -> pl.DataFrame:
    """Generate n customer rows for a given date."""
    rng = random.Random(seed)
    return pl.DataFrame({
        "date": [date] * n,
        "id": list(range(1, n + 1)),
        "region": [rng.choice(_REGIONS) for _ in range(n)],
        "type": [rng.choice(_CUSTOMER_TYPES) for _ in range(n)],
        "name": [f"customer_{i}" for i in range(1, n + 1)],
    })


def _generate_accounts(
    n: int, date: str, max_customer_id: int, seed: int,
) -> pl.DataFrame:
    """Generate n account rows, each linked to a customer."""
    rng = random.Random(seed)
    return pl.DataFrame({
        "date": [date] * n,
        "id": list(range(1, n + 1)),
        "customer_id": [rng.randint(1, max_customer_id) for _ in range(n)],
        "type": [rng.choice(_ACCOUNT_TYPES) for _ in range(n)],
        "name": [f"account_{i}" for i in range(1, n + 1)],
    })


def _generate_transactions(
    n: int, date: str, max_customer_id: int, max_account_id: int, seed: int,
) -> pl.DataFrame:
    """Generate n transaction rows, each linked to a customer and account."""
    rng = random.Random(seed)
    return pl.DataFrame({
        "date": [date] * n,
        "id": list(range(1, n + 1)),
        "customer_id": [rng.randint(1, max_customer_id) for _ in range(n)],
        "account_id": [rng.randint(1, max_account_id) for _ in range(n)],
        "amount": [round(rng.uniform(1.0, 10000.0), 2) for _ in range(n)],
    })


# Source file definitions: key -> (generator_func, kwargs)
_SOURCE_FILES: dict[str, tuple] = {
    "customers_1": (
        _generate_customers, {"n": 100, "date": "2024-01-01", "seed": 42}
    ),
    "customers_2": (
        _generate_customers, {"n": 105, "date": "2024-01-02", "seed": 43}
    ),
    "accounts_1": (
        _generate_accounts,
        {"n": 200, "date": "2024-01-01", "max_customer_id": 100, "seed": 44},
    ),
    "accounts_2": (
        _generate_accounts,
        {"n": 210, "date": "2024-01-02", "max_customer_id": 105, "seed": 45},
    ),
    "transactions_1": (
        _generate_transactions,
        {
            "n": 1000, "date": "2024-01-01",
            "max_customer_id": 100, "max_account_id": 200, "seed": 46,
        },
    ),
    "transactions_2": (
        _generate_transactions,
        {
            "n": 1000, "date": "2024-01-02",
            "max_customer_id": 105, "max_account_id": 210, "seed": 47,
        },
    ),
}

# Mapping from file key to CSV filename
_CSV_FILENAMES: dict[str, str] = {
    "customers_1": "customers_2024-01-01.csv",
    "customers_2": "customers_2024-01-02.csv",
    "accounts_1": "accounts_2024-01-01.csv",
    "accounts_2": "accounts_2024-01-02.csv",
    "transactions_1": "transactions_2024-01-01.csv",
    "transactions_2": "transactions_2024-01-02.csv",
}


# ---------------------------------------------------------------------------
# Loading plan — one row per file-to-location mapping
# ---------------------------------------------------------------------------


class _LoadEntry(NamedTuple):
    """One row of the loading plan: a file loaded into a specific location."""

    file: str  # key into _SOURCE_FILES
    domain: str
    stage: str
    instance: str
    object_name: str  # 'customers', 'accounts', or 'transactions'


#   file               domain      stage   instance  object
#   ─────────────────  ──────────  ──────  ────────  ────────────
_LOADING_PLAN: list[_LoadEntry] = [
    # payments domain: accounts + transactions (no customers)
    _LoadEntry("accounts_1",     "payments", "uat",  "main",  "accounts"),
    _LoadEntry("accounts_1",     "payments", "test", "alpha", "accounts"),
    _LoadEntry("accounts_1",     "payments", "test", "beta",  "accounts"),
    _LoadEntry("accounts_2",     "payments", "test", "alpha", "accounts"),
    _LoadEntry("transactions_1", "payments", "uat",  "main",  "transactions"),
    _LoadEntry("transactions_1", "payments", "test", "alpha", "transactions"),
    _LoadEntry("transactions_1", "payments", "test", "beta",  "transactions"),
    _LoadEntry("transactions_2", "payments", "test", "alpha", "transactions"),
    # sales domain: customers + transactions (no accounts)
    _LoadEntry("customers_1",    "sales", "test", "main", "customers"),
    _LoadEntry("customers_2",    "sales", "test", "main", "customers"),
    _LoadEntry("transactions_1", "sales", "test", "main", "transactions"),
    _LoadEntry("transactions_2", "sales", "test", "main", "transactions"),
]  # fmt: skip

# Which (domain, stage, instance, core_table) combos get a core layer
_CORE_TARGETS: list[tuple[str, str, str, str]] = [
    ("payments", "test", "alpha", "core_account_payments"),
    ("payments", "test", "beta", "core_account_payments"),
    ("payments", "uat", "main", "core_account_payments"),
    ("sales", "test", "main", "core_customer_transactions"),
]

# Which (domain, stage, instance, mart_table) combos get a mart layer
_MART_TARGETS: list[tuple[str, str, str, str]] = [
    ("payments", "test", "alpha", "mart_account_payments_by_date"),
    ("payments", "test", "beta", "mart_account_payments_by_date"),
    ("sales", "test", "main", "mart_customer_revenues_by_date"),
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
    csv_name = _CSV_FILENAMES[entry.file]
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
    core_targets: list[tuple[str, str, str, str]],
    mart_targets: list[tuple[str, str, str, str]],
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
    for domain, stage, instance, table in core_targets:
        database = f"{domain}_{stage}"
        core_objects.add((database, instance, table))

    # Add mart layer entries
    mart_objects: set[tuple[str, str, str]] = set()
    for domain, stage, instance, table in mart_targets:
        database = f"{domain}_{stage}"
        mart_objects.add((database, instance, table))

    all_objects = sorted(stage_objects | core_objects | mart_objects)
    print("All database objects to be created: ", all_objects)

    # Clean and recreate database directory
    if fs.exists(str(db_path)):
        fs.rm(str(db_path), recursive=True)
    fs.mkdir(str(db_path), create_parents=False)

    attach_sql = _read_sql("ddl_attach_database.sql")
    ddl_templates: dict[str, str] = {
        "stage_customers": _read_sql("ddl_stage_customers.sql"),
        "stage_transactions": _read_sql("ddl_stage_transactions.sql"),
        "stage_accounts": _read_sql("ddl_stage_accounts.sql"),
        "core_customer_transactions": _read_sql(
            "ddl_core_customer_transactions.sql"
        ),
        "core_account_payments": _read_sql("ddl_core_account_payments.sql"),
        "mart_account_payments_by_date": _read_sql(
            "ddl_mart_account_payments_by_date.sql"
        ),
        "mart_customer_revenues_by_date": _read_sql(
            "ddl_mart_customer_revenues_by_date.sql"
        ),
    }

    for database, schema, table in all_objects:
        # Attach database file (creates .db on disk if not exists)
        db_filepath = str(db_path / database) + ".db"
        duckdb.execute(
            attach_sql.format(db_filepath=db_filepath, database=database)
        )

        # Create schema and table
        if table not in ddl_templates:
            raise ValueError(f"Unknown table name: {table}")
        duckdb.execute(
            ddl_templates[table].format(database=database, schema=schema)
        )

    created_tables = duckdb.sql(
        "SELECT * FROM INFORMATION_SCHEMA.TABLES "
        "ORDER BY table_catalog, table_schema, table_name"
    ).pl()
    print("Created tables: ", created_tables)


def _load_raw_layer(plan: list[_LoadEntry], raw_path: Path) -> None:
    """Generate CSV data and write into the raw layer."""
    print("\nLOADING RAW LAYER:")
    loaded: list[str] = []
    for entry in plan:
        gen_func, kwargs = _SOURCE_FILES[entry.file]
        df = gen_func(**kwargs)
        target = _csv_path(entry, raw_path)
        df.write_csv(str(target))
        loaded.append(str(target))
    print("Raw layer loaded files: ", loaded)


def _load_staging_layer(plan: list[_LoadEntry], raw_path: Path) -> None:
    """Load CSVs into DuckDB staging tables.

    Truncates transactions_2 to half its rows to simulate load errors
    in the payments domain.
    """
    print("\nLOADING STAGING LAYER:")
    insert_sql = _read_sql("dml_load_staging.sql")
    loaded_tables: list[str] = []

    # Use incrementing timestamps so each file load gets a distinct m__ts
    base_ts = datetime(2024, 1, 15, 10, 0, 0)
    ts_counter = 0

    for entry in plan:
        csv = _csv_path(entry, raw_path)
        database = f"{entry.domain}_{entry.stage}"
        table = f"stage_{entry.object_name}"
        filename = csv.name
        source_file_path = f"local://{csv}"

        # Truncate transactions_2 to half its rows in payments domain
        if entry.file == "transactions_2" and entry.domain == "payments":
            limit_clause = "LIMIT 500"
        else:
            limit_clause = ""

        # Each file load gets a unique timestamp
        load_ts = base_ts.replace(
            minute=ts_counter,
        ).strftime("%Y-%m-%d %H:%M:%S")
        ts_counter += 1

        duckdb.execute(
            insert_sql.format(
                database=database,
                schema=entry.instance,
                table=table,
                csv_filepath=str(csv),
                filename=filename,
                source_file_path=source_file_path,
                load_ts=load_ts,
                limit_clause=limit_clause,
            )
        )
        loaded_tables.append(f"{database}.{entry.instance}.{table}")

    loaded_tables = sorted(set(loaded_tables))
    print("Loaded staging tables: ", loaded_tables)

    # Sanity checks for payments_test.alpha
    accts = _count_rows("payments_test.alpha.stage_accounts")
    assert accts == 410, f"Expected 410 accounts, got {accts}"
    print(f"  payments_test.alpha.stage_accounts: {accts}")

    txns = _count_rows("payments_test.alpha.stage_transactions")
    assert txns == 1500, f"Expected 1500 transactions, got {txns}"
    print(f"  payments_test.alpha.stage_transactions: {txns}")

    # Sanity checks for sales_test.main
    custs = _count_rows("sales_test.main.stage_customers")
    assert custs == 205, f"Expected 205 customers, got {custs}"
    print(f"  sales_test.main.stage_customers: {custs}")

    sales_txns = _count_rows("sales_test.main.stage_transactions")
    assert sales_txns == 2000, f"Expected 2000 transactions, got {sales_txns}"
    print(f"  sales_test.main.stage_transactions: {sales_txns}")


def _load_core_layer(
    core_targets: list[tuple[str, str, str, str]],
) -> None:
    """Load core layer tables by joining staging tables."""
    print("\nLOADING CORE LAYER:")
    dml_templates: dict[str, str] = {
        "core_account_payments": _read_sql(
            "dml_load_core_account_payments.sql"
        ),
        "core_customer_transactions": _read_sql(
            "dml_load_core_customer_transactions.sql"
        ),
    }

    for domain, stage, instance, table in core_targets:
        database = f"{domain}_{stage}"
        dml = dml_templates[table]
        duckdb.execute(dml.format(database=database, schema=instance))
        count = _count_rows(f"{database}.{instance}.{table}")
        print(f"  {database}.{instance}.{table}: {count} rows")


def _load_mart_layer(
    mart_targets: list[tuple[str, str, str, str]],
) -> None:
    """Load mart layer tables by aggregating core tables."""
    print("\nLOADING MART LAYER:")
    dml_templates: dict[str, str] = {
        "mart_account_payments_by_date": _read_sql(
            "dml_load_mart_account_payments_by_date.sql"
        ),
        "mart_customer_revenues_by_date": _read_sql(
            "dml_load_mart_customer_revenues_by_date.sql"
        ),
    }

    for domain, stage, instance, table in mart_targets:
        database = f"{domain}_{stage}"
        dml = dml_templates[table]
        duckdb.execute(dml.format(database=database, schema=instance))
        count = _count_rows(f"{database}.{instance}.{table}")
        print(f"  {database}.{instance}.{table}: {count} rows")


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


def prepare_demo_data(location: Path = Path(__file__).parent) -> None:
    """Create the full mini-DWH (raw + staging + core + mart) at *location*."""
    global _active_location  # noqa: PLW0603
    _active_location = location

    raw_path = location / "raw"
    db_path = location / "dbs"

    _setup_raw_layer(_LOADING_PLAN, raw_path)
    _setup_databases(_LOADING_PLAN, _CORE_TARGETS, _MART_TARGETS, db_path)
    _load_raw_layer(_LOADING_PLAN, raw_path)
    _load_staging_layer(_LOADING_PLAN, raw_path)
    _load_core_layer(_CORE_TARGETS)
    _load_mart_layer(_MART_TARGETS)
    _detach_all_databases(db_path)


def clean_up_demo_data() -> None:
    """Delete all data created by the last prepare_demo_data() call."""
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
