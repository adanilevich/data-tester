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
from pathlib import Path
from typing import List

import polars as pl
from fsspec.implementations.local import LocalFileSystem

from src.dtos import (
    CompareTestCaseConfigDTO,
    DomainConfigDTO,
    LocationDTO,
    SchemaTestCaseConfigDTO,
    StagecountSpecDTO,
    TestCaseEntryDTO,
    TestCasesConfigDTO,
    TestSetDTO,
    TestType,
)

__all__ = ["prepare_demo_artifacts", "clean_up_demo_artifacts"]

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
    raw_file_encoding: str = "utf-8",
    skip_lines: int = 1,
) -> bytes:
    """Create a JSON-serialized StagecountSpecDTO."""
    spec = StagecountSpecDTO(
        location=LocationDTO(
            path=f"{specs_base}{domain}/{testobject}_STAGECOUNT.json",
        ),
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
    specs_base: str, reports_base: str,
) -> List[DomainConfigDTO]:
    return [
        DomainConfigDTO(
            domain="payments",
            instances={"test": ["alpha", "beta"], "uat": ["main"]},
            specifications_locations=[
                LocationDTO(f"{specs_base}payments/"),
            ],
            testreports_location=LocationDTO(reports_base),
            testcases=TestCasesConfigDTO(
                compare=CompareTestCaseConfigDTO(sample_size=100),
                schema=SchemaTestCaseConfigDTO(
                    compare_datatypes=["int", "string", "float", "date"],
                ),
            ),
        ),
        DomainConfigDTO(
            domain="sales",
            instances={"test": ["main"]},
            specifications_locations=[
                LocationDTO(f"{specs_base}sales/"),
            ],
            testreports_location=LocationDTO(reports_base),
            testcases=TestCasesConfigDTO(
                compare=CompareTestCaseConfigDTO(sample_size=50),
                schema=SchemaTestCaseConfigDTO(
                    compare_datatypes=["int", "string"],
                ),
            ),
        ),
    ]


def _testsets() -> List[TestSetDTO]:
    return [
        TestSetDTO(
            name="payments_full",
            description="Full regression for payments domain",
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
        TestSetDTO(
            name="sales_validation",
            description="Validation for sales domain",
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
                        "Compare: staging to core data accuracy "
                        "(NOK — africa filter)"
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
    ]


# ---------------------------------------------------------------------------
# Spec file content
# ---------------------------------------------------------------------------


def _payment_specs(specs_base: str) -> dict[str, bytes]:
    return {
        "stage_accounts_schema.xlsx": _create_schema_xlsx(
            columns=[
                "date", "id", "customer_id", "type", "name",
                "m__ts", "m__source_file", "m__source_file_path",
            ],
            types=[
                "STRING", "INTEGER", "INTEGER", "STRING", "STRING",
                "TIMESTAMP", "STRING", "STRING",
            ],
        ),
        "stage_transactions_schema.xlsx": _create_schema_xlsx(
            columns=[
                "date", "id", "customer_id", "account_id", "amount",
                "m__ts", "m__source_file", "m__source_file_path",
            ],
            types=[
                "STRING", "INTEGER", "INTEGER", "INTEGER", "FLOAT",
                "TIMESTAMP", "STRING", "STRING",
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
    }


def _sales_specs(specs_base: str) -> dict[str, bytes]:
    return {
        "stage_customers_schema.xlsx": _create_schema_xlsx(
            columns=[
                "date", "id", "region", "type", "name",
                "m__ts", "m__source_file", "m__source_file_path",
            ],
            types=[
                "STRING", "INTEGER", "STRING", "STRING", "STRING",
                "TIMESTAMP", "STRING", "STRING",
            ],
        ),
        "stage_transactions_schema.xlsx": _create_schema_xlsx(
            columns=[
                "date", "id", "customer_id", "account_id", "amount",
                "m__ts", "m__source_file", "m__source_file_path",
            ],
            types=[
                "STRING", "INTEGER", "INTEGER", "INTEGER", "FLOAT",
                "TIMESTAMP", "STRING", "STRING",
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
    }


# ---------------------------------------------------------------------------
# File writers
# ---------------------------------------------------------------------------


def _write_file(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _create_spec_files(location: Path, specs_base: str) -> None:
    specs_dir = location / "specs"
    for filename, content in _payment_specs(specs_base).items():
        _write_file(specs_dir / "payments" / filename, content)
    for filename, content in _sales_specs(specs_base).items():
        _write_file(specs_dir / "sales" / filename, content)


def _create_domain_configs(
    location: Path, specs_base: str, reports_base: str,
) -> None:
    configs_dir = location / "configs"
    configs_dir.mkdir(parents=True, exist_ok=True)
    for config in _domain_configs(specs_base, reports_base):
        path = configs_dir / f"domain_config_{config.domain}.json"
        path.write_text(config.to_json())


def _create_testsets(location: Path) -> None:
    for testset in _testsets():
        ts_dir = location / "testsets" / testset.domain
        ts_dir.mkdir(parents=True, exist_ok=True)
        path = ts_dir / f"testset_{testset.name}.json"
        path.write_text(testset.to_json())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def prepare_demo_artifacts(location: Path = Path(__file__).parent) -> None:
    """Generate and persist all demo artifacts at *location*.

    Creates specs/, configs/, and testsets/ subdirectories with all
    files needed for a demo deployment or e2e test.
    """
    specs_prefix = f"local://{location / 'specs'}/"
    reports_prefix = f"local://{location / 'testreports'}/"
    _create_spec_files(location, specs_base=specs_prefix)
    _create_domain_configs(
        location, specs_base=specs_prefix, reports_base=reports_prefix,
    )
    _create_testsets(location)


def clean_up_demo_artifacts(location: Path = Path(__file__).parent) -> None:
    """Delete the entire artifacts directory."""
    fs = LocalFileSystem()
    path = str(location)
    if fs.exists(path):
        fs.rm(path, recursive=True)
