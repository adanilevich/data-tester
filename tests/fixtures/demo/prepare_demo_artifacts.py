"""
Demo artifact generator for integration tests and demo deployments.

Creates and persists all non-DWH artifacts needed for a demo:
- Specification files (XLSX schemas, SQL rowcount/compare queries,
  JSON stagecount specs)
- Domain configuration JSONs
- Testset JSONs

These artifacts are written to disk so they can be read by the application
via LocalUserStorage (for specs) and loaded as DTOs (for configs/testsets).

Public API
----------
  prepare_demo_artifacts(location)  — create all artifacts at the given path
  clean_up_demo_artifacts(location) — delete everything created
"""

from __future__ import annotations

import io
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from uuid import uuid4

import polars as pl
from fsspec.implementations.local import LocalFileSystem

from src.dtos import (
    DomainConfigDTO,
    LocationDTO,
    Result,
    StagecountSpecDTO,
    Status,
    TestCaseDTO,
    TestCaseEntryDTO,
    TestObjectDTO,
    TestRunDTO,
    TestSetDTO,
    TestType,
)

__all__ = ["prepare_demo_artifacts", "clean_up_demo_artifacts"]

_TESTRUNS_PER_TESTSET = 10
_HISTORY_DAYS = 90  # approx 3 months

# (testobject, testtype) pairs that yield NOK, keyed by testset name
_TESTSET_NOK_KEYS: dict[str, set[tuple[str, TestType]]] = {
    "Payments Partial": {("stage_transactions", TestType.STAGECOUNT)},
    "Payments Full": {("stage_transactions", TestType.STAGECOUNT)},
    "Payments UAT": {("core_account_payments", TestType.SCHEMA)},
    "Sales Validation": {("core_customer_transactions", TestType.COMPARE)},
    "Sales Full": {("core_customer_transactions", TestType.COMPARE)},
}

# ---------------------------------------------------------------------------
# Schema XLSX helper
# ---------------------------------------------------------------------------


def _create_schema_xlsx(
    columns: List[str],
    types: List[str],
    pk_flags: List[str] | None = None,
) -> bytes:
    n = len(columns)
    data = {
        "column": columns,
        "type": types,
        "pk": pk_flags or [""] * n,
        "partition": [""] * n,
        "cluster": [""] * n,
    }
    df = pl.DataFrame(data)
    buffer = io.BytesIO()
    df.write_excel(buffer, worksheet="schema")
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Stagecount spec helper
# ---------------------------------------------------------------------------


def _create_stagecount_spec_json(
    testobject: str,
    specs_base: str,
    domain: str,
    stage_prefix: str = "",
    raw_file_encoding: str = "utf-8",
    skip_lines: int = 1,
) -> bytes:
    """Create a JSON-serialized StagecountSpecDTO.

    If *stage_prefix* is provided (e.g. ``"test"`` or ``"uat"``), the spec
    self-reference path will use ``{specs_base}{stage_prefix}/{domain}/``
    instead of the default ``{specs_base}{domain}/``.
    """
    if stage_prefix:
        path = f"{specs_base}{stage_prefix}/{domain}/{testobject}_STAGECOUNT.json"
    else:
        path = f"{specs_base}{domain}/{testobject}_STAGECOUNT.json"
    spec = StagecountSpecDTO(
        location=LocationDTO(path=path),
        testobject=testobject,
        raw_file_format="csv",
        raw_file_encoding=raw_file_encoding,
        skip_lines=skip_lines,
    )
    return spec.to_json().encode("utf-8")


# ---------------------------------------------------------------------------
# Domain configs
# ---------------------------------------------------------------------------


def _domain_configs(
    specs_base: str,
    reports_base: str,
) -> List[DomainConfigDTO]:
    return [
        DomainConfigDTO(
            domain="payments",
            instances={"test": ["alpha", "beta"], "uat": ["main"]},
            spec_locations={
                "test": [f"{specs_base}payments/"],
                "uat": [f"{specs_base}uat/payments/"],
            },
            reports_location=LocationDTO(reports_base),
            compare_datatypes=["int", "string", "float", "date"],
            sample_size_default=100,
            sample_size_per_object={},
        ),
        DomainConfigDTO(
            domain="sales",
            instances={"test": ["main"]},
            spec_locations={"test": [f"{specs_base}sales/"]},
            reports_location=LocationDTO(reports_base),
            compare_datatypes=["int", "string"],
            sample_size_default=50,
            sample_size_per_object={},
        ),
    ]


def _testsets() -> List[TestSetDTO]:
    return [
        # ------------------------------------------------------------------
        # Payments Partial — renamed from payments_full, test/alpha
        # ------------------------------------------------------------------
        TestSetDTO(
            name="Payments Partial",
            description=(
                "Partial regression for payments domain (schema + stagecount only)"
            ),
            comment=(
                "Expected failures:\n"
                "  - stage_transactions STAGECOUNT → NOK: "
                "transactions_2 is truncated to 500 rows during staging "
                "(1000 raw rows vs 500 staged rows)"
            ),
            labels=["regression", "payments"],
            domain="payments",
            default_stage="test",
            default_instance="alpha",
            testcases={
                "stage_accounts_SCHEMA": TestCaseEntryDTO(
                    testobject="stage_accounts",
                    testtype=TestType.SCHEMA,
                    domain="payments",
                    comment="Schema validation for stage_accounts",
                ),
                "stage_transactions_SCHEMA": TestCaseEntryDTO(
                    testobject="stage_transactions",
                    testtype=TestType.SCHEMA,
                    domain="payments",
                    comment="Schema validation for stage_transactions",
                ),
                "core_account_payments_ROWCOUNT": TestCaseEntryDTO(
                    testobject="core_account_payments",
                    testtype=TestType.ROWCOUNT,
                    domain="payments",
                    comment="Rowcount: staging to core consistency",
                ),
                "core_account_payments_COMPARE": TestCaseEntryDTO(
                    testobject="core_account_payments",
                    testtype=TestType.COMPARE,
                    domain="payments",
                    comment="Compare: staging to core data accuracy",
                ),
                "stage_accounts_STAGECOUNT": TestCaseEntryDTO(
                    testobject="stage_accounts",
                    testtype=TestType.STAGECOUNT,
                    domain="payments",
                    comment="Stagecount: raw vs stage for accounts",
                ),
                "stage_transactions_STAGECOUNT": TestCaseEntryDTO(
                    testobject="stage_transactions",
                    testtype=TestType.STAGECOUNT,
                    domain="payments",
                    comment=(
                        "Stagecount: raw vs stage for transactions "
                        "(NOK — transactions_2 truncated)"
                    ),
                ),
            },
        ),
        # ------------------------------------------------------------------
        # Payments Full — all testobjects, all applicable testcases, test/alpha
        # ------------------------------------------------------------------
        TestSetDTO(
            name="Payments Full",
            description="Full regression for payments domain covering all layers",
            comment=(
                "Expected failures:\n"
                "  - stage_transactions STAGECOUNT → NOK: "
                "transactions_2 is truncated to 500 rows during staging "
                "(1000 raw rows vs 500 staged rows)"
            ),
            labels=["regression", "payments", "full"],
            domain="payments",
            default_stage="test",
            default_instance="alpha",
            testcases={
                # stage layer
                "stage_accounts_SCHEMA": TestCaseEntryDTO(
                    testobject="stage_accounts",
                    testtype=TestType.SCHEMA,
                    domain="payments",
                    comment="Schema validation for stage_accounts",
                ),
                "stage_accounts_STAGECOUNT": TestCaseEntryDTO(
                    testobject="stage_accounts",
                    testtype=TestType.STAGECOUNT,
                    domain="payments",
                    comment="Stagecount: raw vs stage for accounts",
                ),
                "stage_transactions_SCHEMA": TestCaseEntryDTO(
                    testobject="stage_transactions",
                    testtype=TestType.SCHEMA,
                    domain="payments",
                    comment="Schema validation for stage_transactions",
                ),
                "stage_transactions_STAGECOUNT": TestCaseEntryDTO(
                    testobject="stage_transactions",
                    testtype=TestType.STAGECOUNT,
                    domain="payments",
                    comment=(
                        "Stagecount: raw vs stage for transactions "
                        "(NOK — transactions_2 truncated)"
                    ),
                ),
                # core layer
                "core_account_payments_SCHEMA": TestCaseEntryDTO(
                    testobject="core_account_payments",
                    testtype=TestType.SCHEMA,
                    domain="payments",
                    comment="Schema validation for core_account_payments",
                ),
                "core_account_payments_ROWCOUNT": TestCaseEntryDTO(
                    testobject="core_account_payments",
                    testtype=TestType.ROWCOUNT,
                    domain="payments",
                    comment="Rowcount: staging to core consistency",
                ),
                "core_account_payments_COMPARE": TestCaseEntryDTO(
                    testobject="core_account_payments",
                    testtype=TestType.COMPARE,
                    domain="payments",
                    comment="Compare: staging to core data accuracy",
                ),
                # mart layer
                "mart_account_payments_by_date_SCHEMA": TestCaseEntryDTO(
                    testobject="mart_account_payments_by_date",
                    testtype=TestType.SCHEMA,
                    domain="payments",
                    comment="Schema validation for mart_account_payments_by_date",
                ),
                "mart_account_payments_by_date_ROWCOUNT": TestCaseEntryDTO(
                    testobject="mart_account_payments_by_date",
                    testtype=TestType.ROWCOUNT,
                    domain="payments",
                    comment="Rowcount: core to mart consistency",
                ),
                "mart_account_payments_by_date_COMPARE": TestCaseEntryDTO(
                    testobject="mart_account_payments_by_date",
                    testtype=TestType.COMPARE,
                    domain="payments",
                    comment="Compare: core to mart aggregation accuracy",
                ),
            },
        ),
        # ------------------------------------------------------------------
        # Payments UAT — all testobjects in payments_uat, uat/main
        # ------------------------------------------------------------------
        TestSetDTO(
            name="Payments UAT",
            description="UAT acceptance tests for payments domain",
            comment=(
                "Expected failures:\n"
                "  - core_account_payments SCHEMA → NOK: "
                "UAT spec intentionally has wrong type for transaction_date "
                "(STRING instead of DATE) to demonstrate schema drift detection\n"
                "Expected N/A:\n"
                "  - stage_accounts SCHEMA → N/A: "
                "no schema spec provided for UAT stage_accounts"
            ),
            labels=["uat", "payments"],
            domain="payments",
            default_stage="uat",
            default_instance="main",
            testcases={
                # stage_accounts: STAGECOUNT only (no SCHEMA spec for UAT)
                "stage_accounts_STAGECOUNT": TestCaseEntryDTO(
                    testobject="stage_accounts",
                    testtype=TestType.STAGECOUNT,
                    domain="payments",
                    comment="Stagecount: raw vs stage for accounts (UAT)",
                ),
                # stage_transactions: SCHEMA + STAGECOUNT
                "stage_transactions_SCHEMA": TestCaseEntryDTO(
                    testobject="stage_transactions",
                    testtype=TestType.SCHEMA,
                    domain="payments",
                    comment="Schema validation for stage_transactions (UAT)",
                ),
                "stage_transactions_STAGECOUNT": TestCaseEntryDTO(
                    testobject="stage_transactions",
                    testtype=TestType.STAGECOUNT,
                    domain="payments",
                    comment="Stagecount: raw vs stage for transactions (UAT)",
                ),
                # core_account_payments: ROWCOUNT + SCHEMA (faulty → NOK) + COMPARE
                "core_account_payments_SCHEMA": TestCaseEntryDTO(
                    testobject="core_account_payments",
                    testtype=TestType.SCHEMA,
                    domain="payments",
                    comment=(
                        "Schema validation for core_account_payments (UAT) "
                        "— NOK: spec has transaction_date=STRING, actual is DATE"
                    ),
                ),
                "core_account_payments_ROWCOUNT": TestCaseEntryDTO(
                    testobject="core_account_payments",
                    testtype=TestType.ROWCOUNT,
                    domain="payments",
                    comment="Rowcount: staging to core consistency (UAT)",
                ),
                "core_account_payments_COMPARE": TestCaseEntryDTO(
                    testobject="core_account_payments",
                    testtype=TestType.COMPARE,
                    domain="payments",
                    comment="Compare: staging to core data accuracy (UAT)",
                ),
            },
        ),
        # ------------------------------------------------------------------
        # Sales Validation — renamed from sales_validation, test/main
        # ------------------------------------------------------------------
        TestSetDTO(
            name="Sales Validation",
            description="Validation for sales domain",
            comment=(
                "Expected failures:\n"
                "  - core_customer_transactions COMPARE → NOK: "
                "core load intentionally excludes rows where customer_region='africa', "
                "causing a mismatch between staging source and core target"
            ),
            labels=["validation", "sales"],
            domain="sales",
            default_stage="test",
            default_instance="main",
            testcases={
                "stage_customers_SCHEMA": TestCaseEntryDTO(
                    testobject="stage_customers",
                    testtype=TestType.SCHEMA,
                    domain="sales",
                    comment="Schema validation for stage_customers",
                ),
                "stage_transactions_SCHEMA": TestCaseEntryDTO(
                    testobject="stage_transactions",
                    testtype=TestType.SCHEMA,
                    domain="sales",
                    comment="Schema validation for stage_transactions",
                ),
                "core_customer_transactions_ROWCOUNT": TestCaseEntryDTO(
                    testobject="core_customer_transactions",
                    testtype=TestType.ROWCOUNT,
                    domain="sales",
                    comment="Rowcount: staging to core consistency",
                ),
                "core_customer_transactions_COMPARE": TestCaseEntryDTO(
                    testobject="core_customer_transactions",
                    testtype=TestType.COMPARE,
                    domain="sales",
                    comment=(
                        "Compare: staging to core data accuracy (NOK — africa filter)"
                    ),
                ),
                "stage_customers_STAGECOUNT": TestCaseEntryDTO(
                    testobject="stage_customers",
                    testtype=TestType.STAGECOUNT,
                    domain="sales",
                    comment="Stagecount: raw vs stage for customers",
                ),
                "stage_transactions_STAGECOUNT": TestCaseEntryDTO(
                    testobject="stage_transactions",
                    testtype=TestType.STAGECOUNT,
                    domain="sales",
                    comment="Stagecount: raw vs stage for transactions",
                ),
            },
        ),
        # ------------------------------------------------------------------
        # Sales Full — all testobjects, all applicable testcases, test/main
        # ------------------------------------------------------------------
        TestSetDTO(
            name="Sales Full",
            description="Full regression for sales domain covering all layers",
            comment=(
                "Expected failures:\n"
                "  - core_customer_transactions COMPARE → NOK: "
                "core load intentionally excludes rows where customer_region='africa', "
                "causing a mismatch between staging source and core target"
            ),
            labels=["regression", "sales", "full"],
            domain="sales",
            default_stage="test",
            default_instance="main",
            testcases={
                # stage layer
                "stage_customers_SCHEMA": TestCaseEntryDTO(
                    testobject="stage_customers",
                    testtype=TestType.SCHEMA,
                    domain="sales",
                    comment="Schema validation for stage_customers",
                ),
                "stage_customers_STAGECOUNT": TestCaseEntryDTO(
                    testobject="stage_customers",
                    testtype=TestType.STAGECOUNT,
                    domain="sales",
                    comment="Stagecount: raw vs stage for customers",
                ),
                "stage_transactions_SCHEMA": TestCaseEntryDTO(
                    testobject="stage_transactions",
                    testtype=TestType.SCHEMA,
                    domain="sales",
                    comment="Schema validation for stage_transactions",
                ),
                "stage_transactions_STAGECOUNT": TestCaseEntryDTO(
                    testobject="stage_transactions",
                    testtype=TestType.STAGECOUNT,
                    domain="sales",
                    comment="Stagecount: raw vs stage for transactions",
                ),
                # core layer
                "core_customer_transactions_SCHEMA": TestCaseEntryDTO(
                    testobject="core_customer_transactions",
                    testtype=TestType.SCHEMA,
                    domain="sales",
                    comment="Schema validation for core_customer_transactions",
                ),
                "core_customer_transactions_ROWCOUNT": TestCaseEntryDTO(
                    testobject="core_customer_transactions",
                    testtype=TestType.ROWCOUNT,
                    domain="sales",
                    comment="Rowcount: staging to core consistency",
                ),
                "core_customer_transactions_COMPARE": TestCaseEntryDTO(
                    testobject="core_customer_transactions",
                    testtype=TestType.COMPARE,
                    domain="sales",
                    comment=(
                        "Compare: staging to core data accuracy (NOK — africa filter)"
                    ),
                ),
                # mart layer
                "mart_customer_revenues_by_date_SCHEMA": TestCaseEntryDTO(
                    testobject="mart_customer_revenues_by_date",
                    testtype=TestType.SCHEMA,
                    domain="sales",
                    comment="Schema validation for mart_customer_revenues_by_date",
                ),
                "mart_customer_revenues_by_date_ROWCOUNT": TestCaseEntryDTO(
                    testobject="mart_customer_revenues_by_date",
                    testtype=TestType.ROWCOUNT,
                    domain="sales",
                    comment="Rowcount: core to mart consistency",
                ),
                "mart_customer_revenues_by_date_COMPARE": TestCaseEntryDTO(
                    testobject="mart_customer_revenues_by_date",
                    testtype=TestType.COMPARE,
                    domain="sales",
                    comment="Compare: core to mart aggregation accuracy",
                ),
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Spec file content
# ---------------------------------------------------------------------------


def _payment_specs(specs_base: str) -> dict[str, bytes]:
    """Test-stage payment specs — written to user/payments/."""
    return {
        "stage_accounts_schema.xlsx": _create_schema_xlsx(
            columns=[
                "date",
                "id",
                "customer_id",
                "type",
                "name",
                "m__ts",
                "m__source_file",
                "m__source_file_path",
            ],
            types=[
                "STRING",
                "INTEGER",
                "INTEGER",
                "STRING",
                "STRING",
                "TIMESTAMP",
                "STRING",
                "STRING",
            ],
        ),
        "stage_transactions_schema.xlsx": _create_schema_xlsx(
            columns=[
                "date",
                "id",
                "customer_id",
                "account_id",
                "amount",
                "m__ts",
                "m__source_file",
                "m__source_file_path",
            ],
            types=[
                "STRING",
                "INTEGER",
                "INTEGER",
                "INTEGER",
                "FLOAT",
                "TIMESTAMP",
                "STRING",
                "STRING",
            ],
        ),
        "core_account_payments_schema.xlsx": _create_schema_xlsx(
            columns=["account_id", "transaction_date"],
            types=["INTEGER", "DATE"],
            pk_flags=["x", "x"],
        ),
        "core_account_payments_ROWCOUNT.sql": b"""\
-- __EXPECTED_ROWCOUNT__
WITH __expected_count__ AS (
    SELECT COUNT(*)
    FROM stage_transactions AS transactions
    LEFT JOIN stage_accounts AS accounts
        ON transactions.account_id = accounts.id
        AND transactions.date = accounts.date
)
, __actual_count__ AS (
    SELECT COUNT(*)
    FROM core_account_payments
)
""",
        "core_account_payments_COMPARE.sql": b"""\
WITH __EXPECTED__ AS (
    SELECT
        accounts.name AS account_name,
        accounts.id AS account_id,
        transactions.id AS id,
        transactions.date AS transaction_date,
        transactions.amount AS amount
    FROM stage_transactions AS transactions
    LEFT JOIN stage_accounts AS accounts
        ON transactions.account_id = accounts.id
        AND transactions.date = accounts.date
)
""",
        "stage_accounts_STAGECOUNT.json": _create_stagecount_spec_json(
            testobject="stage_accounts",
            specs_base=specs_base,
            domain="payments",
        ),
        "stage_transactions_STAGECOUNT.json": _create_stagecount_spec_json(
            testobject="stage_transactions",
            specs_base=specs_base,
            domain="payments",
        ),
        # mart layer specs (used by Payments Full)
        "mart_account_payments_by_date_schema.xlsx": _create_schema_xlsx(
            columns=[
                "account_id",
                "transaction_date",
                "total_amount",
                "transaction_count",
            ],
            types=["INTEGER", "DATE", "FLOAT", "INTEGER"],
            pk_flags=["x", "x", "", ""],
        ),
        "mart_account_payments_by_date_ROWCOUNT.sql": b"""\
-- __EXPECTED_ROWCOUNT__
WITH __expected_count__ AS (
    SELECT COUNT(*)
    FROM (
        SELECT account_id, transaction_date
        FROM core_account_payments
        GROUP BY account_id, transaction_date
    )
)
, __actual_count__ AS (
    SELECT COUNT(*)
    FROM mart_account_payments_by_date
)
""",
        "mart_account_payments_by_date_COMPARE.sql": b"""\
WITH __EXPECTED__ AS (
    SELECT
        account_id,
        transaction_date,
        SUM(amount) AS total_amount,
        COUNT(*) AS transaction_count
    FROM core_account_payments
    GROUP BY account_id, transaction_date
)
""",
    }


def _payment_uat_specs(specs_base: str) -> dict[str, bytes]:
    """UAT-stage payment specs — written to user/uat/payments/.

    Deliberately omits stage_accounts_schema to produce N/A for that testcase.
    Uses a faulty schema for core_account_payments (transaction_date typed as
    STRING instead of DATE) to produce a NOK schema result for UAT only.
    """
    return {
        # stage_accounts: STAGECOUNT only — no schema spec (→ N/A)
        "stage_accounts_STAGECOUNT.json": _create_stagecount_spec_json(
            testobject="stage_accounts",
            specs_base=specs_base,
            domain="payments",
            stage_prefix="uat",
        ),
        # stage_transactions: SCHEMA + STAGECOUNT
        "stage_transactions_schema.xlsx": _create_schema_xlsx(
            columns=[
                "date",
                "id",
                "customer_id",
                "account_id",
                "amount",
                "m__ts",
                "m__source_file",
                "m__source_file_path",
            ],
            types=[
                "STRING",
                "INTEGER",
                "INTEGER",
                "INTEGER",
                "FLOAT",
                "TIMESTAMP",
                "STRING",
                "STRING",
            ],
        ),
        "stage_transactions_STAGECOUNT.json": _create_stagecount_spec_json(
            testobject="stage_transactions",
            specs_base=specs_base,
            domain="payments",
            stage_prefix="uat",
        ),
        # core_account_payments: faulty SCHEMA (transaction_date = STRING, not DATE → NOK)
        "core_account_payments_schema.xlsx": _create_schema_xlsx(
            columns=["account_id", "transaction_date"],
            types=["INTEGER", "STRING"],  # STRING instead of DATE — intentionally wrong
            pk_flags=["x", "x"],
        ),
        "core_account_payments_ROWCOUNT.sql": b"""\
-- __EXPECTED_ROWCOUNT__
WITH __expected_count__ AS (
    SELECT COUNT(*)
    FROM stage_transactions AS transactions
    LEFT JOIN stage_accounts AS accounts
        ON transactions.account_id = accounts.id
        AND transactions.date = accounts.date
)
, __actual_count__ AS (
    SELECT COUNT(*)
    FROM core_account_payments
)
""",
        "core_account_payments_COMPARE.sql": b"""\
WITH __EXPECTED__ AS (
    SELECT
        accounts.name AS account_name,
        accounts.id AS account_id,
        transactions.id AS id,
        transactions.date AS transaction_date,
        transactions.amount AS amount
    FROM stage_transactions AS transactions
    LEFT JOIN stage_accounts AS accounts
        ON transactions.account_id = accounts.id
        AND transactions.date = accounts.date
)
""",
    }


def _sales_specs(specs_base: str) -> dict[str, bytes]:
    return {
        "stage_customers_schema.xlsx": _create_schema_xlsx(
            columns=[
                "date",
                "id",
                "region",
                "type",
                "name",
                "m__ts",
                "m__source_file",
                "m__source_file_path",
            ],
            types=[
                "STRING",
                "INTEGER",
                "STRING",
                "STRING",
                "STRING",
                "TIMESTAMP",
                "STRING",
                "STRING",
            ],
        ),
        "stage_transactions_schema.xlsx": _create_schema_xlsx(
            columns=[
                "date",
                "id",
                "customer_id",
                "account_id",
                "amount",
                "m__ts",
                "m__source_file",
                "m__source_file_path",
            ],
            types=[
                "STRING",
                "INTEGER",
                "INTEGER",
                "INTEGER",
                "FLOAT",
                "TIMESTAMP",
                "STRING",
                "STRING",
            ],
        ),
        "core_customer_transactions_schema.xlsx": _create_schema_xlsx(
            columns=["customer_id", "transaction_date"],
            types=["INTEGER", "DATE"],
            pk_flags=["x", "x"],
        ),
        "core_customer_transactions_ROWCOUNT.sql": b"""\
-- __EXPECTED_ROWCOUNT__
WITH __expected_count__ AS (
    SELECT COUNT(*)
    FROM stage_transactions AS transactions
    LEFT JOIN stage_customers AS customers
        ON transactions.customer_id = customers.id
        AND transactions.date = customers.date
    WHERE customers.region != 'africa'
)
, __actual_count__ AS (
    SELECT COUNT(*)
    FROM core_customer_transactions
)
""",
        "core_customer_transactions_COMPARE.sql": b"""\
WITH __EXPECTED__ AS (
    SELECT
        customers.name AS customer_name,
        customers.id AS customer_id,
        transactions.id AS id,
        transactions.date AS transaction_date,
        transactions.amount AS amount
    FROM stage_transactions AS transactions
    LEFT JOIN stage_customers AS customers
        ON transactions.customer_id = customers.id
        AND transactions.date = customers.date
)
""",
        "stage_customers_STAGECOUNT.json": _create_stagecount_spec_json(
            testobject="stage_customers",
            specs_base=specs_base,
            domain="sales",
        ),
        "stage_transactions_STAGECOUNT.json": _create_stagecount_spec_json(
            testobject="stage_transactions",
            specs_base=specs_base,
            domain="sales",
        ),
        # mart layer specs (used by Sales Full)
        "mart_customer_revenues_by_date_schema.xlsx": _create_schema_xlsx(
            columns=[
                "customer_id",
                "transaction_date",
                "total_amount",
                "transaction_count",
            ],
            types=["INTEGER", "DATE", "FLOAT", "INTEGER"],
            pk_flags=["x", "x", "", ""],
        ),
        "mart_customer_revenues_by_date_ROWCOUNT.sql": b"""\
-- __EXPECTED_ROWCOUNT__
WITH __expected_count__ AS (
    SELECT COUNT(*)
    FROM (
        SELECT customer_id, transaction_date
        FROM core_customer_transactions
        GROUP BY customer_id, transaction_date
    )
)
, __actual_count__ AS (
    SELECT COUNT(*)
    FROM mart_customer_revenues_by_date
)
""",
        "mart_customer_revenues_by_date_COMPARE.sql": b"""\
WITH __EXPECTED__ AS (
    SELECT
        customer_id,
        transaction_date,
        SUM(amount) AS total_amount,
        COUNT(*) AS transaction_count
    FROM core_customer_transactions
    GROUP BY customer_id, transaction_date
)
""",
    }


# ---------------------------------------------------------------------------
# File writers
# ---------------------------------------------------------------------------


def _write_file(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _create_spec_files(specs_dir: Path, specs_base: str) -> None:
    for filename, content in _payment_specs(specs_base).items():
        _write_file(specs_dir / "payments" / filename, content)
    for filename, content in _payment_uat_specs(specs_base).items():
        _write_file(specs_dir / "uat" / "payments" / filename, content)
    for filename, content in _sales_specs(specs_base).items():
        _write_file(specs_dir / "sales" / filename, content)


def _create_domain_configs(
    configs_dir: Path,
    domain_configs: List[DomainConfigDTO],
) -> None:
    configs_dir.mkdir(parents=True, exist_ok=True)
    for config in domain_configs:
        (configs_dir / f"{config.id}.json").write_text(config.to_json())


def _create_testsets(testsets_dir: Path, testsets: List[TestSetDTO]) -> None:
    for testset in testsets:
        ts_dir = testsets_dir / testset.domain
        ts_dir.mkdir(parents=True, exist_ok=True)
        (ts_dir / f"{testset.id}.json").write_text(testset.to_json())


def _create_demo_testruns(
    testruns_dir: Path,
    testsets: List[TestSetDTO],
    domain_configs: List[DomainConfigDTO],
) -> None:
    dc_map = {dc.domain: dc for dc in domain_configs}
    rng = random.Random(42)
    now = datetime.now()

    for testset in testsets:
        dc = dc_map[testset.domain]
        nok_keys = _TESTSET_NOK_KEYS.get(testset.name, set())
        stage: str = testset.stage or testset.default_stage
        instance: str = testset.instance or testset.default_instance

        for _ in range(_TESTRUNS_PER_TESTSET):
            testrun_id = uuid4()
            start_ts = now - timedelta(seconds=rng.randint(0, _HISTORY_DAYS * 86400))
            end_ts = start_ts + timedelta(minutes=rng.randint(5, 30))

            tc_results = [
                TestCaseDTO(
                    testrun_id=testrun_id,
                    testset_id=testset.testset_id,
                    domain=testset.domain,
                    stage=stage,
                    instance=instance,
                    result=Result.NOK
                    if (entry.testobject, entry.testtype) in nok_keys
                    else Result.OK,
                    status=Status.FINISHED,
                    start_ts=start_ts,
                    end_ts=end_ts,
                    testset_name=testset.name,
                    labels=testset.labels,
                    domain_config=dc,
                    testobject=TestObjectDTO(
                        name=entry.testobject,
                        domain=testset.domain,
                        stage=stage,
                        instance=instance,
                    ),
                    testtype=entry.testtype,
                    diff={},
                    summary="",
                    facts=[],
                    details=[],
                    specs=[],
                )
                for entry in testset.testcases.values()
            ]

            testrun_dto = TestRunDTO(
                id=testrun_id,
                testset_id=testset.testset_id,
                domain=testset.domain,
                stage=stage,
                instance=instance,
                result=Result.NOK,
                status=Status.FINISHED,
                start_ts=start_ts,
                end_ts=end_ts,
                testset_name=testset.name,
                labels=testset.labels,
                domain_config=dc,
                results=tc_results,
            )

            date_str = start_ts.strftime("%Y-%m-%d")
            out_dir = testruns_dir / testset.domain / date_str
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / f"{testrun_id}.json").write_text(testrun_dto.to_json())


# ---------------------------------------------------------------------------
# Default location
# ---------------------------------------------------------------------------

_DEFAULT_LOCATION: Path = Path("tests/fixtures/demo/data")

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def prepare_demo_artifacts(location: Path = _DEFAULT_LOCATION) -> None:
    """Generate and persist all demo artifacts under *location*.

    Layout under *location*::

        internal/domain_configs/    — DomainConfigDTO JSONs (DtoStorageFile)
        internal/testsets/{domain}/ — TestSetDTO JSONs (DtoStorageFile)
        user/{domain}/              — spec files for test stage (xlsx/sql/json)
        user/uat/{domain}/          — spec files for uat stage (xlsx/sql/json)
    """
    user_dir = location / "user"
    internal_dir = location / "internal"
    specs_prefix = f"local://{user_dir}/"
    reports_prefix = f"local://{location / 'testreports'}/"

    domain_configs = _domain_configs(specs_prefix, reports_prefix)
    testsets = _testsets()

    _create_spec_files(user_dir, specs_base=specs_prefix)
    _create_domain_configs(internal_dir / "domain_configs", domain_configs)
    _create_testsets(internal_dir / "testsets", testsets)
    _create_demo_testruns(internal_dir / "testruns", testsets, domain_configs)


def clean_up_demo_artifacts(location: Path = _DEFAULT_LOCATION) -> None:
    """Delete the artifact subfolders (internal/ and user/) under *location*."""
    fs = LocalFileSystem()
    for sub in ("internal", "user"):
        path = str(location / sub)
        if fs.exists(path):
            fs.rm(path, recursive=True)
