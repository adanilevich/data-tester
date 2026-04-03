"""
Integration tests for CLI Dependency Injection and driver functionality.

Tests that CliDependencyInjector correctly wires all dependencies and that
each driver produced by the DI container is functional.
"""

import io
from typing import List, cast
from uuid import uuid4
from datetime import datetime

import pytest
import polars as pl

from src.apps.cli_di import CliDependencyInjector as CliDi
from src.config import Config
from src.domain_adapters import SpecAdapter
from src.drivers import (
    DomainConfigDriver,
    ReportDriver,
    SpecDriver,
    TestRunDriver,
    TestSetDriver,
)
from src.domain_ports import (
    LoadTestRunReportCommand,
    LoadTestCaseReportCommand,
    SaveDomainConfigCommand,
    SaveTestSetCommand,
)
from src.dtos import (
    CompareTestCaseConfigDTO,
    DomainConfigDTO,
    LocationDTO,
    SchemaTestCaseConfigDTO,
    SpecificationType,
    SpecificationDTO,
    TestCaseEntryDTO,
    TestCasesConfigDTO,
    TestDefinitionDTO,
    TestObjectDTO,
    TestResult,
    TestRunDTO,
    TestRunReportDTO,
    TestSetDTO,
    TestStatus,
    TestType,
)
from src.drivers.testset_driver import TestSetNotFoundError
from src.infrastructure.backend import DemoBackendFactory, DummyBackendFactory
from src.infrastructure.notifier import InMemoryNotifier, StdoutNotifier
from src.infrastructure.storage.dto_storage_file import MemoryDtoStorage
from src.infrastructure.storage.user_storage import MemoryUserStorage


# --- Helpers and Fixtures ---


def _put(storage: MemoryUserStorage, path: str, data: bytes) -> None:
    """Write test data into MemoryUserStorage."""
    with storage.fs.open(path, mode="wb") as f:
        f.write(data)


def _create_test_xlsx_schema(
    columns: List[str],
    types: List[str],
    pk_flags: List[str] | None = None,
    partition_flags: List[str] | None = None,
    cluster_flags: List[str] | None = None,
) -> bytes:
    """Create a test Excel file with schema data."""
    n = len(columns)
    data = {
        "column": columns,
        "type": types,
        "pk": pk_flags or [""] * n,
        "partition": partition_flags or [""] * n,
        "cluster": cluster_flags or [""] * n,
    }
    df = pl.DataFrame(data)
    buffer = io.BytesIO()
    df.write_excel(buffer, worksheet="schema")
    return buffer.getvalue()

@pytest.fixture
def di() -> CliDi:
    return CliDi(Config())


# --- DI Wiring Tests ---


class TestCliDependencyInjection:
    def test_di_creates_drivers(self, di: CliDi):

        assert isinstance(di.dto_storage, MemoryDtoStorage)
        assert isinstance(di.user_storage, MemoryUserStorage)
        assert isinstance(di.backend_factory, DummyBackendFactory)
        assert len(di.notifiers) == 2
        assert any(isinstance(n, InMemoryNotifier) for n in di.notifiers)
        assert any(isinstance(n, StdoutNotifier) for n in di.notifiers)
        assert len(di.testreport_formatters) == 3

        assert isinstance(di.domain_config_driver(), DomainConfigDriver)
        assert isinstance(di.testset_driver(), TestSetDriver)
        assert isinstance(di.specification_driver(), SpecDriver)
        assert isinstance(di.testrun_driver(), TestRunDriver)
        assert isinstance(di.report_driver(), ReportDriver)

    def test_di_demo_backend_factory(self):
        config = Config()
        config.DATATESTER_DATA_PLATFORM = "DEMO"
        di = CliDi(config)
        assert isinstance(di.backend_factory, DemoBackendFactory)


# --- DomainConfigDriver ---


class TestDomainConfigDriverIntegration:
    def test_save_and_load_roundtrip(self, di: CliDi, domain_config: DomainConfigDTO):
        driver = di.domain_config_driver()
        dc = domain_config.copy()
        dc.domain = "roundtrip_domain"
        driver.save_domain_config(config=dc)

        loaded = driver.load_domain_config(domain="roundtrip_domain")
        assert loaded.domain == "roundtrip_domain"
        assert loaded.instances == dc.instances
        assert loaded.testcases == dc.testcases

    def test_list_multiple_configs(self, di: CliDi, domain_config: DomainConfigDTO):
        driver = di.domain_config_driver()
        adapter = driver.adapter

        for name in ["domain_a", "domain_b", "domain_c"]:
            dc = domain_config.copy()
            dc.domain = name
            adapter.save_domain_config(SaveDomainConfigCommand(config=dc))

        found = driver.list_domain_configs()
        assert len(found) == 3
        assert set(found.keys()) == {"domain_a", "domain_b", "domain_c"}


# --- TestSetDriver ---


class TestTestSetDriverIntegration:
    def test_save_and_load_by_name(self, di: CliDi):
        driver = di.testset_driver()
        adapter = driver.adapter

        for name in ["SetA", "SetB"]:
            ts = TestSetDTO(
                name=name,
                domain="ts_domain",
                default_stage="dev",
                default_instance="inst1",
                testcases={"t1_SCHEMA": TestCaseEntryDTO(
                    testobject="t1", testtype=TestType.SCHEMA
                    )
                },
            )
            adapter.save_testset(SaveTestSetCommand(testset=ts))

        loaded_a = driver.load_domain_testset_by_name("ts_domain", "SetA")
        loaded_b = driver.load_domain_testset_by_name("ts_domain", "SetB")
        assert loaded_a.name == "SetA"
        assert loaded_b.name == "SetB"
        assert loaded_a.domain == "ts_domain"

    def test_load_by_name_not_found(self, di: CliDi):
        driver = di.testset_driver()
        adapter = driver.adapter

        ts = TestSetDTO(
            name="Existing",
            domain="nf_domain",
            default_stage="dev",
            default_instance="inst1",
            testcases={
                "t1_SCHEMA": TestCaseEntryDTO(testobject="t1", testtype=TestType.SCHEMA)
            },
        )
        adapter.save_testset(SaveTestSetCommand(testset=ts))

        with pytest.raises(TestSetNotFoundError):
            driver.load_domain_testset_by_name("nf_domain", "NonExistent")


# --- SpecDriver ---


class TestSpecDriverIntegration:
    def _get_storage(self, di: CliDi) -> MemoryUserStorage:
        driver = di.specification_driver()
        adapter = cast(SpecAdapter, driver.adapter)
        return cast(MemoryUserStorage, adapter.user_storage)

    def _setup_specs(self, di: CliDi) -> SpecDriver:
        storage = self._get_storage(di)
        _put(
            storage,
            "specs/customers_schema.xlsx",
            _create_test_xlsx_schema(
                columns=["id", "name", "email"],
                types=["INTEGER", "VARCHAR(255)", "VARCHAR(255)"],
            ),
        )
        _put(
            storage,
            "specs/products_schema.xlsx",
            _create_test_xlsx_schema(
                columns=["id", "name"],
                types=["INTEGER", "VARCHAR(100)"],
            ),
        )
        _put(
            storage,
            "specs/customers_ROWCOUNT.sql",
            b"SELECT COUNT(*) as __EXPECTED_ROWCOUNT__ FROM customers WHERE active = 1",
        )
        return di.specification_driver()

    def test_find_no_specs_returns_empty(self, di: CliDi):
        self._setup_specs(di)
        driver = di.specification_driver()

        testset = TestSetDTO(
            name="empty",
            domain="d",
            default_stage="s",
            default_instance="i",
            testcases={
                "nonexistent_SCHEMA": TestCaseEntryDTO(
                    testobject="nonexistent", testtype=TestType.SCHEMA
                )
            },
        )
        result = driver.find_specifications(testset, [LocationDTO("memory://specs/")])
        assert len(result) == 1
        assert len(result[0]) == 0

    def test_find_multiple_locations(self, di: CliDi):
        self._setup_specs(di)
        storage = self._get_storage(di)
        driver = di.specification_driver()

        _put(
            storage,
            "backup/customers_schema.xlsx",
            _create_test_xlsx_schema(
                columns=["id", "name"],
                types=["INTEGER", "VARCHAR(255)"],
            ),
        )

        testset = TestSetDTO(
            name="multi_loc",
            domain="d",
            default_stage="s",
            default_instance="i",
            testcases={
                "customers_SCHEMA": TestCaseEntryDTO(
                    testobject="customers", testtype=TestType.SCHEMA
                )
            },
        )
        result = driver.find_specifications(
            testset, [LocationDTO("memory://specs/"), LocationDTO("memory://backup/")]
        )
        assert len(result) == 1
        assert len(result[0]) == 2  # found in both locations


# --- TestRunDriver ---


class TestTestRunDriverIntegration:
    def _make_domain_config(self) -> DomainConfigDTO:
        return DomainConfigDTO(
            domain="my_domain",
            instances={},
            specifications_locations=[],
            testreports_location=LocationDTO("memory://my_location"),
            testcases=TestCasesConfigDTO(
                schema=SchemaTestCaseConfigDTO(compare_datatypes=["int", "str"]),
                compare=CompareTestCaseConfigDTO(sample_size=100),
            ),
        )

    def _make_definition(
        self, testobject_name: str, testtype: TestType, testrun_id, dc: DomainConfigDTO
    ) -> TestDefinitionDTO:
        return TestDefinitionDTO(
            testobject=TestObjectDTO(
                domain="my_domain",
                stage="my_stage",
                instance="my_instance",
                name=testobject_name,
            ),
            testtype=testtype,
            specs=[
                SpecificationDTO(
                    spec_type=SpecificationType.SCHEMA,
                    location=LocationDTO(path="memory://my_location"),
                    testobject=testobject_name,
                ),
            ],
            domain_config=dc,
            testrun_id=testrun_id,
        )

    def _make_testrun(
        self, definitions: List[TestDefinitionDTO], dc: DomainConfigDTO
    ) -> TestRunDTO:
        return TestRunDTO(
            testrun_id=uuid4(),
            testset_id=uuid4(),
            labels=[],
            testset_name="testset",
            stage="my_stage",
            instance="my_instance",
            domain="my_domain",
            domain_config=dc,
            start_ts=datetime.now(),
            end_ts=None,
            status=TestStatus.INITIATED,
            result=TestResult.NA,
            testdefinitions=definitions,
            testcase_results=[],
        )

    def test_execute_dummy_testcases(self):
        config = Config()
        config.DATATESTER_DATA_PLATFORM = "DUMMY"
        di = CliDi(config)
        driver = di.testrun_driver()

        dc = self._make_domain_config()
        testrun_id = uuid4()
        names_and_types = [
            ("obj1", TestType.DUMMY_OK),
            ("obj2", TestType.DUMMY_NOK),
            ("obj3", TestType.DUMMY_EXCEPTION),
            ("obj4", TestType.UNKNOWN),
        ]
        definitions = [
            self._make_definition(n, t, testrun_id, dc) for n, t in names_and_types
        ]
        testrun = self._make_testrun(definitions, dc)

        result = driver.execute_testrun(testrun)

        assert len(result.testcase_results) == 4
        expected_map = {
            TestType.DUMMY_OK: (TestResult.OK, TestStatus.FINISHED),
            TestType.DUMMY_NOK: (TestResult.NOK, TestStatus.FINISHED),
            TestType.DUMMY_EXCEPTION: (TestResult.NA, TestStatus.ERROR),
            TestType.UNKNOWN: (TestResult.NA, TestStatus.ERROR),
        }
        for tc in result.testcase_results:
            exp_result, exp_status = expected_map[tc.testtype]
            assert tc.result == exp_result
            assert tc.status == exp_status
            assert tc.start_ts is not None
            assert tc.end_ts is not None

    def test_execute_unknown_testtype(self):
        config = Config()
        config.DATATESTER_DATA_PLATFORM = "DUMMY"
        di = CliDi(config)
        runner = di.testrun_driver()

        dc = self._make_domain_config()
        testrun_id = uuid4()
        definition = self._make_definition(
            "obj_unknown", TestType.UNKNOWN, testrun_id, dc
        )
        testrun = self._make_testrun([definition], dc)
        result = runner.execute_testrun(testrun)

        assert len(result.testcase_results) == 1
        tc = result.testcase_results[0]
        assert tc.result == TestResult.NA
        assert tc.status == TestStatus.ERROR
        assert "unknown" in tc.summary.lower()


# --- ReportDriver ---


class TestReportDriverIntegration:
    def test_create_save_and_retrieve_reports(self, di: CliDi, testrun: TestRunDTO):
        driver = di.report_driver()
        adapter = driver.adapter

        testrun_report = driver.create_and_save_all_reports(testrun)

        assert isinstance(testrun_report, TestRunReportDTO)
        assert testrun.report_id == testrun_report.report_id

        for tc in testrun.testcase_results:
            assert tc.report_id is not None

        loaded_tr = adapter.load_testrun_report(
            LoadTestRunReportCommand(report_id=testrun_report.report_id)
        )
        assert str(loaded_tr.testrun_id) == str(testrun_report.testrun_id)
        assert len(loaded_tr.testcase_results) == len(testrun.testcase_results)

        for tc in testrun.testcase_results:
            assert tc.report_id is not None
            loaded_tc = adapter.load_testcase_report(
                LoadTestCaseReportCommand(report_id=tc.report_id)
            )
            assert str(loaded_tc.testcase_id) == str(tc.testcase_id)
            assert loaded_tc.testobject == tc.testobject.name
