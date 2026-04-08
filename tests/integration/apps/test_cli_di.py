"""
Integration tests for CLI Dependency Injection and driver functionality.

Tests that CliDependencyInjector correctly wires all dependencies and that
each driver produced by the DI container is functional.
"""

import io
from typing import List, cast

import polars as pl
import pytest
from src.apps.cli_di import CliDependencyInjector as CliDi
from src.config import Config
from src.domain_adapters import SpecAdapter
from src.domain_ports import (
    SaveDomainConfigCommand,
    SaveTestSetCommand,
)
from src.drivers import (
    DomainConfigDriver,
    ReportDriver,
    SpecDriver,
    TestRunDriver,
    TestSetDriver,
)
from src.drivers.testset_driver import TestSetNotFoundError
from src.dtos import (
    DomainConfigDTO,
    LocationDTO,
    ReportArtifact,
    ReportArtifactFormat,
    Result,
    SchemaSpecDTO,
    Status,
    TestCaseEntryDTO,
    TestObjectDTO,
    TestRunDTO,
    TestSetDTO,
    TestType,
)
from src.dtos.testrun_dtos import TestCaseDefDTO, TestRunDefDTO
from src.infrastructure.backend import DemoBackendFactory, DummyBackendFactory
from src.infrastructure.notifier import InMemoryNotifier, LogNotifier
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
    config = Config()
    config.DATATESTER_DATA_PLATFORM = "DUMMY"
    config.DATATESTER_USER_STORAGE_ENGINE = "MEMORY"
    config.DATATESTER_NOTIFIERS = ["IN_MEMORY", "LOG"]
    return CliDi(config)


# --- DI Wiring Tests ---


class TestCliDependencyInjection:
    def test_di_creates_drivers(self, di: CliDi):

        assert isinstance(di.dto_storage, MemoryDtoStorage)
        assert isinstance(di.user_storage, MemoryUserStorage)
        assert isinstance(di.backend_factory, DummyBackendFactory)
        assert len(di.notifiers) == 2
        assert any(isinstance(n, InMemoryNotifier) for n in di.notifiers)
        assert any(isinstance(n, LogNotifier) for n in di.notifiers)
        assert len(di.testcase_formatters) == 2
        assert len(di.testrun_formatters) == 1

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
                testcases={
                    "t1_SCHEMA": TestCaseEntryDTO(
                        testobject="t1",
                        testtype=TestType.SCHEMA,
                        domain="test_domain",
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
                "t1_SCHEMA": TestCaseEntryDTO(
                    testobject="t1",
                    testtype=TestType.SCHEMA,
                    domain="test_domain",
                )
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
                    testobject="nonexistent",
                    testtype=TestType.SCHEMA,
                    domain="test_domain",
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
                    testobject="customers",
                    testtype=TestType.SCHEMA,
                    domain="test_domain",
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
            spec_locations={},
            reports_location=LocationDTO("memory://my_location"),
            compare_datatypes=["int", "str"],
            sample_size_default=100,
            sample_size_per_object={},
        )

    def _make_testcase_def(
        self, testobject_name: str, testtype: TestType, dc: DomainConfigDTO
    ) -> TestCaseDefDTO:
        return TestCaseDefDTO(
            testobject=TestObjectDTO(
                domain="my_domain",
                stage="my_stage",
                instance="my_instance",
                name=testobject_name,
            ),
            testtype=testtype,
            specs=[
                SchemaSpecDTO(
                    location=LocationDTO(path="memory://my_location"),
                    testobject=testobject_name,
                ),
            ],
            domain_config=dc,
        )

    def _make_testrun_def(
        self, testcase_defs: List[TestCaseDefDTO], dc: DomainConfigDTO
    ) -> TestRunDefDTO:
        return TestRunDefDTO(
            testcase_defs=testcase_defs,
            domain="my_domain",
            stage="my_stage",
            instance="my_instance",
            domain_config=dc,
            testset_name="testset",
        )

    def test_execute_dummy_testcases(self):
        config = Config()
        config.DATATESTER_DATA_PLATFORM = "DUMMY"
        di = CliDi(config)
        driver = di.testrun_driver()

        dc = self._make_domain_config()
        names_and_types = [
            ("obj1", TestType.DUMMY_OK),
            ("obj2", TestType.DUMMY_NOK),
            ("obj3", TestType.DUMMY_EXCEPTION),
            ("obj4", TestType.UNKNOWN),
        ]
        testcase_defs = [self._make_testcase_def(n, t, dc) for n, t in names_and_types]
        testrun_def = self._make_testrun_def(testcase_defs, dc)

        result = driver.execute_testrun(testrun_def)

        assert len(result.results) == 4
        expected_map = {
            TestType.DUMMY_OK: (Result.OK, Status.FINISHED),
            TestType.DUMMY_NOK: (Result.NOK, Status.FINISHED),
            TestType.DUMMY_EXCEPTION: (Result.NA, Status.ERROR),
            TestType.UNKNOWN: (Result.NA, Status.ERROR),
        }
        for tc in result.results:
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
        testcase_def = self._make_testcase_def("obj_unknown", TestType.UNKNOWN, dc)
        testrun_def = self._make_testrun_def([testcase_def], dc)
        result = runner.execute_testrun(testrun_def)

        assert len(result.results) == 1
        tc = result.results[0]
        assert tc.result == Result.NA
        assert tc.status == Status.ERROR
        assert "unknown" in tc.summary.lower()


# --- ReportDriver ---


class TestReportDriverIntegration:
    def _make_domain_config(self) -> DomainConfigDTO:
        return DomainConfigDTO(
            domain="my_domain",
            instances={},
            spec_locations={},
            reports_location=LocationDTO("memory://my_location"),
            compare_datatypes=["int", "str"],
            sample_size_default=100,
            sample_size_per_object={},
        )

    def _make_testcase_def(
        self, testobject_name: str, testtype: TestType, dc: DomainConfigDTO
    ) -> TestCaseDefDTO:
        return TestCaseDefDTO(
            testobject=TestObjectDTO(
                domain="my_domain",
                stage="my_stage",
                instance="my_instance",
                name=testobject_name,
            ),
            testtype=testtype,
            specs=[
                SchemaSpecDTO(
                    location=LocationDTO(path="memory://my_location"),
                    testobject=testobject_name,
                ),
            ],
            domain_config=dc,
        )

    def test_create_artifacts_after_testrun(self):
        """Execute a testrun so testcases are persisted, then create artifacts."""
        config = Config()
        config.DATATESTER_DATA_PLATFORM = "DUMMY"
        di = CliDi(config)

        dc = self._make_domain_config()
        testcase_def = self._make_testcase_def("obj1", TestType.DUMMY_OK, dc)
        testrun_def = TestRunDefDTO(
            testcase_defs=[testcase_def],
            domain="my_domain",
            stage="my_stage",
            instance="my_instance",
            domain_config=dc,
            testset_name="testset",
        )
        testrun: TestRunDTO = di.testrun_driver().execute_testrun(testrun_def)
        assert len(testrun.results) == 1
        tc = testrun.results[0]

        report_driver = di.report_driver()

        # testcase REPORT/TXT artifact
        txt_artifact = report_driver.create_testcase_report_artifact(
            testcase_id=tc.id,
            artifact=ReportArtifact.REPORT,
            artifact_format=ReportArtifactFormat.TXT,
        )
        assert isinstance(txt_artifact, bytes)
        assert len(txt_artifact) > 0

        # testrun REPORT/XLSX artifact
        xlsx_artifact = report_driver.create_testrun_report_artifact(
            testrun_id=testrun.id,
            artifact_format=ReportArtifactFormat.XLSX,
        )
        assert isinstance(xlsx_artifact, bytes)
        assert xlsx_artifact.startswith(b"PK\x03\x04")
