from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import NamedTuple
from uuid import uuid4

import pytest
from fsspec.implementations.memory import MemoryFileSystem

from src.dtos import (
    CompareTestCaseConfigDTO,
    DomainConfigDTO,
    SchemaTestCaseConfigDTO,
    TestCasesConfigDTO,
    TestCaseReportDTO,
    TestRunReportDTO,
    LocationDTO,
    TestCaseDTO,
    TestObjectDTO,
    TestResult,
    TestRunDTO,
    TestStatus,
    TestType,
)
from tests.fixtures.demo.prepare_demo_artifacts import (
    clean_up_demo_artifacts,
    prepare_demo_artifacts,
)
from tests.fixtures.demo.prepare_demo_data import (
    clean_up_demo_data,
    prepare_demo_data,
)


@pytest.fixture(autouse=True)
def _clear_memory_filesystem():
    """Clear MemoryFileSystem shared state before and after each test."""
    MemoryFileSystem.store.clear()
    yield
    MemoryFileSystem.store.clear()


class DemoData(NamedTuple):
    """Session-scoped demo DWH + artifacts paths."""

    location: Path
    raw_path: str
    db_path: str
    internal_location: str


_DEMO_DIR = Path(__file__).parent / "fixtures" / "demo" / "data"


@pytest.fixture(scope="session")
def demo_data():  # noqa: ANN201
    """Create demo DWH and artifacts once for the entire test session.

    Layout under ``tests/fixtures/demo/data/``::

        raw/        — raw CSV files
        dbs/        — DuckDB .db files (staging/core/mart)
        internal/   — domain_configs/ + testsets/ (DtoStorageFile-compatible)
        user/       — spec files (LocalUserStorage-compatible)

    No shared DuckDB connection is created — each ``DemoBackend`` instance
    opens its own connection on the .db files.
    """

    # Clean up any stale state from a previous interrupted run, then build.
    clean_up_demo_artifacts(_DEMO_DIR)
    clean_up_demo_data(_DEMO_DIR)

    prepare_demo_data(_DEMO_DIR)
    prepare_demo_artifacts(_DEMO_DIR)

    yield DemoData(
        location=_DEMO_DIR,
        raw_path=str(_DEMO_DIR / "raw"),
        db_path=str(_DEMO_DIR / "dbs"),
        internal_location=f"local://{_DEMO_DIR / 'internal'}/",
    )

    clean_up_demo_artifacts(_DEMO_DIR)
    clean_up_demo_data(_DEMO_DIR)


@pytest.fixture
def domain_config() -> DomainConfigDTO:
    domain_config = DomainConfigDTO(
        domain="payments",
        instances={"test": ["alpha", "beta"], "uat": ["main"]},
        specifications_locations=[
            LocationDTO("memory://sqls"),
            LocationDTO("memory://specs"),
        ],
        testreports_location=LocationDTO("memory://testreports"),
        testcases=TestCasesConfigDTO(
            compare=CompareTestCaseConfigDTO(sample_size=100, sample_size_per_object={}),
            schema=SchemaTestCaseConfigDTO(compare_datatypes=["int", "string", "bool"]),
        ),
    )
    return domain_config


@pytest.fixture
def testobject() -> TestObjectDTO:
    return TestObjectDTO(
        name="stage_customers",
        domain="payments",
        stage="test",
        instance="alpha",
    )


@pytest.fixture
def testcase_result(testobject, domain_config) -> TestCaseDTO:
    return TestCaseDTO(
        testcase_id=uuid4(),
        testrun_id=uuid4(),
        testobject=testobject,
        testtype=TestType.SCHEMA,
        status=TestStatus.FINISHED,
        result=TestResult.OK,
        diff={"my_diff": {"a": [1, 2, 3], "b": ["c", "d", "e"]}},
        summary="My Summary",
        facts=[{"a": 5}, {"b": "2"}],
        details=[{"a": 5}, {"b": "2"}],
        specifications=[],
        domain_config=domain_config,
        start_ts=datetime.now(),
        end_ts=datetime.now(),
        labels=["my_label", "my_label2"],
        domain=testobject.domain,
        stage=testobject.stage,
        instance=testobject.instance,
    )


@pytest.fixture
def testrun(testcase_result) -> TestRunDTO:
    return TestRunDTO.from_testcases(testcases=[testcase_result, testcase_result])


@pytest.fixture
def testcase_report(testcase_result) -> TestCaseReportDTO:
    return TestCaseReportDTO.from_testcase_result(testcase_result)


@pytest.fixture
def testrun_report(testrun) -> TestRunReportDTO:
    return TestRunReportDTO.from_testrun_result(testrun)
