"""
End-to-end integration test for CliApp with DemoBackend.

Tests the full pipeline: domain config loading, testset loading, specification
finding, test execution, and report generation. Two domains are executed
concurrently on the same MemoryStorage to test for concurrency issues.

Test design leverages the deliberate data quality issue in prepare_data.py:
customers_2024-01-02.xlsx is truncated to 4/6 rows during staging load,
causing rowcount mismatches that produce NOK results. The sales domain has
no core layer, causing an ABORTED/NA result for core_customer_transactions.
"""

import concurrent.futures
import io
from typing import List, cast

import polars as pl

from src.apps.cli_app import CliApp
from src.apps.cli_di import CliDependencyInjector
from src.config import Config
from src.domain_ports import SaveTestSetCommand
from src.dtos import (
    CompareTestCaseConfigDTO,
    DomainConfigDTO,
    LocationDTO,
    SchemaTestCaseConfigDTO,
    TestCaseEntryDTO,
    TestCasesConfigDTO,
    TestResult,
    TestSetDTO,
    TestStatus,
    TestType,
)
from src.infrastructure.storage.user_storage import MemoryUserStorage


# --- Spec file helpers ---


def _put(storage: MemoryUserStorage, path: str, data: bytes) -> None:
    with storage.fs.open(path, mode="wb") as f:
        f.write(data)


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


# --- Domain configs ---

PAYMENTS_CONFIG = DomainConfigDTO(
    domain="payments",
    instances={"test": ["alpha", "beta"], "uat": ["main"]},
    specifications_locations=[LocationDTO("memory://specs/payments/")],
    testreports_location=LocationDTO("memory://testreports/"),
    testcases=TestCasesConfigDTO(
        compare=CompareTestCaseConfigDTO(sample_size=100),
        schema=SchemaTestCaseConfigDTO(
            compare_datatypes=["int", "string", "float", "date"]
        ),
    ),
)

SALES_CONFIG = DomainConfigDTO(
    domain="sales",
    instances={"test": ["main"]},
    specifications_locations=[LocationDTO("memory://specs/sales/")],
    testreports_location=LocationDTO("memory://testreports/"),
    testcases=TestCasesConfigDTO(
        compare=CompareTestCaseConfigDTO(sample_size=50),
        schema=SchemaTestCaseConfigDTO(compare_datatypes=["int", "string"]),
    ),
)


# --- Testsets ---

PAYMENTS_TESTSET = TestSetDTO(
    name="payments_full",
    description="Full regression for payments domain",
    labels=["regression", "payments"],
    domain="payments",
    default_stage="test",
    default_instance="alpha",
    testcases={
        "stage_customers_SCHEMA": TestCaseEntryDTO(
            testobject="stage_customers",
            testtype=TestType.SCHEMA,
            comment="Schema validation for stage_customers",
        ),
        "stage_transactions_SCHEMA": TestCaseEntryDTO(
            testobject="stage_transactions",
            testtype=TestType.SCHEMA,
            comment="Schema validation for stage_transactions",
        ),
        "core_customer_transactions_ROWCOUNT": TestCaseEntryDTO(
            testobject="core_customer_transactions",
            testtype=TestType.ROWCOUNT,
            comment="Rowcount: staging→core consistency",
        ),
        "core_customer_transactions_COMPARE": TestCaseEntryDTO(
            testobject="core_customer_transactions",
            testtype=TestType.COMPARE,
            comment="Compare: staging→core data accuracy",
        ),
        "stage_customers_ROWCOUNT": TestCaseEntryDTO(
            testobject="stage_customers",
            testtype=TestType.ROWCOUNT,
            comment="Rowcount: expects 10 but actual 8 due to truncated load → NOK",
        ),
    },
)

SALES_TESTSET = TestSetDTO(
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
            comment="Schema validation for stage_customers",
        ),
        "stage_customers_ROWCOUNT": TestCaseEntryDTO(
            testobject="stage_customers",
            testtype=TestType.ROWCOUNT,
            comment="Rowcount: expects 6 but actual 4 due to truncated load → NOK",
        ),
        "core_customer_transactions_SCHEMA": TestCaseEntryDTO(
            testobject="core_customer_transactions",
            testtype=TestType.SCHEMA,
            comment="Table does not exist in sales → precondition fails → NA",
        ),
    },
)


# --- Spec file setup ---


def _write_payments_specs(storage: MemoryUserStorage) -> None:
    base = "specs/payments/"

    # stage_customers schema (matches actual table in payments_test.alpha)
    _put(
        storage,
        base + "stage_customers_schema.xlsx",
        _create_schema_xlsx(
            columns=["date", "id", "region", "type", "name", "source_file"],
            types=["STRING", "INTEGER", "STRING", "STRING", "STRING", "STRING"],
        ),
    )

    # stage_transactions schema (matches actual table in payments_test.alpha)
    _put(
        storage,
        base + "stage_transactions_schema.xlsx",
        _create_schema_xlsx(
            columns=["date", "id", "customer_id", "amount", "source_file"],
            types=["STRING", "INTEGER", "INTEGER", "FLOAT", "STRING"],
        ),
    )

    # core_customer_transactions ROWCOUNT (proven correct: expected=actual=12) → OK
    # Note: __EXPECTED_ROWCOUNT__ marker required by RowcountSqlFormatter
    _put(
        storage,
        base + "core_customer_transactions_ROWCOUNT.sql",
        b"""-- __EXPECTED_ROWCOUNT__
        WITH __expected_count__ AS (
            SELECT COUNT(*)
            FROM payments_test.alpha.stage_transactions AS transactions
            LEFT JOIN payments_test.alpha.stage_customers AS customers
                ON transactions.customer_id = customers.id
                AND transactions.date = customers.date
            WHERE customers.region != 'africa'
        )
        , __actual_count__ AS (
            SELECT COUNT(*)
            FROM payments_test.alpha.core_customer_transactions
        )
        """,
    )

    # core_customer_transactions COMPARE SQL (proven correct) → OK
    # Note: __EXPECTED__ (uppercase) marker required by CompareSqlFormatter
    _put(
        storage,
        base + "core_customer_transactions_COMPARE.sql",
        b"""
        WITH __EXPECTED__ AS (
            SELECT
                customers.name AS customer_name,
                customers.id AS customer_id,
                transactions.id AS id,
                transactions.date AS transaction_date,
                transactions.amount AS amount
            FROM payments_test.alpha.stage_transactions AS transactions
            LEFT JOIN payments_test.alpha.stage_customers AS customers
                ON transactions.customer_id = customers.id
                AND transactions.date = customers.date
            WHERE customers.region != 'africa'
        )
        """,
    )

    # core_customer_transactions schema (required by COMPARE for primary key sampling)
    _put(
        storage,
        base + "core_customer_transactions_schema.xlsx",
        _create_schema_xlsx(
            columns=["customer_id", "transaction_date"],
            types=["INTEGER", "DATE"],
            pk_flags=["x", "x"],
        ),
    )

    # stage_customers ROWCOUNT: deliberately failing
    # Expects 10 (4 from file 1 + 6 from file 2) but actual is 8 (truncated) → NOK
    # Note: __EXPECTED_ROWCOUNT__ marker required by RowcountSqlFormatter
    _put(
        storage,
        base + "stage_customers_ROWCOUNT.sql",
        b"""-- __EXPECTED_ROWCOUNT__
        WITH __expected_count__ AS (
            SELECT 10 AS count
        )
        , __actual_count__ AS (
            SELECT COUNT(*) AS count FROM payments_test.alpha.stage_customers
        )
        """,
    )


def _write_sales_specs(storage: MemoryUserStorage) -> None:
    base = "specs/sales/"

    # stage_customers schema (same table structure as payments)
    _put(
        storage,
        base + "stage_customers_schema.xlsx",
        _create_schema_xlsx(
            columns=["date", "id", "region", "type", "name", "source_file"],
            types=["STRING", "INTEGER", "STRING", "STRING", "STRING", "STRING"],
        ),
    )

    # stage_customers ROWCOUNT: deliberately failing
    # Expects 6 (full customers_2 xlsx) but actual is 4 (truncated) → NOK
    # Note: __EXPECTED_ROWCOUNT__ marker required by RowcountSqlFormatter
    _put(
        storage,
        base + "stage_customers_ROWCOUNT.sql",
        b"""-- __EXPECTED_ROWCOUNT__
        WITH __expected_count__ AS (
            SELECT 6 AS count
        )
        , __actual_count__ AS (
            SELECT COUNT(*) AS count FROM sales_test.main.stage_customers
        )
        """,
    )

    # core_customer_transactions schema (spec provided but table doesn't exist → NA)
    _put(
        storage,
        base + "core_customer_transactions_schema.xlsx",
        _create_schema_xlsx(
            columns=["customer_id", "transaction_date"],
            types=["INTEGER", "DATE"],
        ),
    )


# --- E2E Test ---


class TestCliAppE2E:
    def test_concurrent_execution_of_two_domains(self, prepare_local_data):
        # --- Setup ---
        config = Config()
        config.DATATESTER_DATA_PLATFORM = "DEMO"
        di = CliDependencyInjector(config)

        # Save domain configs
        dc_driver = di.domain_config_driver()
        dc_driver.save_domain_config(config=PAYMENTS_CONFIG)
        dc_driver.save_domain_config(config=SALES_CONFIG)

        # Save testsets
        ts_driver = di.testset_driver()
        ts_driver.adapter.save_testset(SaveTestSetCommand(testset=PAYMENTS_TESTSET))
        ts_driver.adapter.save_testset(SaveTestSetCommand(testset=SALES_TESTSET))

        # Write spec files into MemoryUserStorage
        user_storage = cast(MemoryUserStorage, di.user_storage)
        _write_payments_specs(user_storage)
        _write_sales_specs(user_storage)

        # --- Concurrent execution ---
        app1 = CliApp(config)
        app2 = CliApp(config)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(app1.run_tests, "payments", "payments_full")
            future2 = executor.submit(app2.run_tests, "sales", "sales_validation")
            future1.result(timeout=120)
            future2.result(timeout=120)

        # --- Verify using fresh DI (reads from shared MemoryFileSystem) ---
        verify_di = CliDependencyInjector(config)

        # 1. Testruns persisted
        tr_driver = verify_di.testrun_driver()
        payments_testruns = tr_driver.list_testruns(domain="payments")
        sales_testruns = tr_driver.list_testruns(domain="sales")
        assert len(payments_testruns) == 1
        assert len(sales_testruns) == 1

        # 2. Payments testrun: 5 testcases, overall NOK
        payments_tr = payments_testruns[0]
        assert len(payments_tr.testcase_results) == 5
        assert payments_tr.result == TestResult.NOK
        assert payments_tr.status == TestStatus.FINISHED

        pr = {
            (tc.testobject.name, tc.testtype): tc
            for tc in payments_tr.testcase_results
        }
        cust_s, txn_s = TestType.SCHEMA, TestType.SCHEMA
        cust_rc, core_rc = TestType.ROWCOUNT, TestType.ROWCOUNT
        core_cmp = TestType.COMPARE
        assert pr[("stage_customers", cust_s)].result == TestResult.OK
        assert pr[("stage_transactions", txn_s)].result == TestResult.OK
        assert pr[("core_customer_transactions", core_rc)].result == TestResult.OK
        assert pr[("core_customer_transactions", core_cmp)].result == TestResult.OK
        assert pr[("stage_customers", cust_rc)].result == TestResult.NOK
        for tc in payments_tr.testcase_results:
            assert tc.status == TestStatus.FINISHED

        # 3. Sales testrun: 3 testcases, overall NOK
        sales_tr = sales_testruns[0]
        assert len(sales_tr.testcase_results) == 3
        assert sales_tr.result == TestResult.NOK
        assert sales_tr.status == TestStatus.FINISHED

        sr = {
            (tc.testobject.name, tc.testtype): tc
            for tc in sales_tr.testcase_results
        }
        assert sr[("stage_customers", TestType.SCHEMA)].result == TestResult.OK
        assert sr[("stage_customers", TestType.SCHEMA)].status == TestStatus.FINISHED
        assert sr[("stage_customers", TestType.ROWCOUNT)].result == TestResult.NOK
        assert sr[("stage_customers", TestType.ROWCOUNT)].status == TestStatus.FINISHED
        core_schema = sr[("core_customer_transactions", TestType.SCHEMA)]
        assert core_schema.result == TestResult.NA
        assert core_schema.status == TestStatus.ABORTED

        # 4. Reports persisted with correct results
        report_driver = verify_di.report_driver()

        payments_tr_reports = report_driver.list_testrun_reports(domain="payments")
        sales_tr_reports = report_driver.list_testrun_reports(domain="sales")
        assert len(payments_tr_reports) == 1
        assert len(sales_tr_reports) == 1

        payments_tc_reports = report_driver.list_testcase_reports(domain="payments")
        sales_tc_reports = report_driver.list_testcase_reports(domain="sales")
        assert len(payments_tc_reports) == 5
        assert len(sales_tc_reports) == 3

        # Verify report results match testrun results
        for report in payments_tc_reports:
            assert report.domain == "payments"
            assert report.result in (TestResult.OK.value, TestResult.NOK.value)

        for report in sales_tc_reports:
            assert report.domain == "sales"
            assert report.result in (
                TestResult.OK.value,
                TestResult.NOK.value,
                TestResult.NA.value,
            )

        # Verify NOK and NA reports exist
        nok = TestResult.NOK.value
        na = TestResult.NA.value
        payments_nok = [r for r in payments_tc_reports if r.result == nok]
        assert len(payments_nok) == 1
        sales_nok = [r for r in sales_tc_reports if r.result == nok]
        assert len(sales_nok) == 1
        sales_na = [r for r in sales_tc_reports if r.result == na]
        assert len(sales_na) == 1

        # 5. No cross-contamination
        for report in payments_tc_reports:
            assert report.domain == "payments"
        for report in sales_tc_reports:
            assert report.domain == "sales"
