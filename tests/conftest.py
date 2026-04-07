from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, NamedTuple
from uuid import uuid4
from datetime import datetime

import pytest
from fsspec.implementations.memory import MemoryFileSystem

from src.dtos.notification_dtos import Importance
from src.dtos.specification_dtos import SpecDTO, SpecType
from src.dtos.domain_config_dtos import (
    SchemaTestCaseConfigDTO,
    CompareTestCaseConfigDTO,
    DomainConfigDTO,
    TestCasesConfigDTO,
)
from src.dtos.testrun_dtos import (
    TestObjectDTO,
    TestCaseDTO,
    TestResult,
    TestStatus,
    TestType,
    TestDefinitionDTO,
)
from src.dtos.report_dtos import TestCaseReportDTO, TestRunReportDTO
from src.dtos.testrun_dtos import TestRunDTO
from src.dtos.storage_dtos import LocationDTO
from src.infrastructure_ports import IBackend
from src.infrastructure.notifier import InMemoryNotifier
from src.infrastructure.backend.dummy import DummyBackend
from src.domain.testrun.testcases import (
    AbstractTestCase,
    SchemaTestCase,
    RowCountTestCase,
    CompareTestCase,
    StageCountTestCase,
    DummyOkTestCase,
    DummyNokTestCase,
    DummyExceptionTestCase,
)
from src.domain.testrun.precondition_checks import Checkable
from tests.fixtures.demo.prepare_demo_artifacts import (
    prepare_demo_artifacts,
    clean_up_demo_artifacts,
)
from tests.fixtures.demo.prepare_demo_data import (
    prepare_demo_data,
    clean_up_demo_data,
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
def dummy_backend() -> IBackend:
    return DummyBackend()


@pytest.fixture
def in_memory_notifier() -> InMemoryNotifier:
    return InMemoryNotifier()


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
    testobject = TestObjectDTO(
        name="stage_customers",
        domain="payments",
        stage="test",
        instance="alpha",
    )
    return testobject


class DummyCheckable(Checkable):
    def __init__(self, testobject: TestObjectDTO, backend: IBackend):
        self.testobject = testobject
        self.backend = backend
        self.summary = ""
        self.details = []
        self.notifications: List[str] = []

    def update_summary(self, summary: str):
        self.summary += summary

    def add_detail(self, detail: Dict[str, str | int | float]):
        if self.details is None:
            self.details = []
        self.details.append(detail)

    def notify(self, message: str, importance: Importance = Importance.INFO):
        self.notifications.append(message)


class ICheckableCreator(ABC):
    @abstractmethod
    def create(self) -> Checkable:
        """Creates a checkable"""


@pytest.fixture
def checkable_creator(testobject, dummy_backend) -> ICheckableCreator:
    class CheckableCreator(ICheckableCreator):
        def create(self) -> Checkable:
            checkable = DummyCheckable(backend=dummy_backend, testobject=testobject)
            return checkable

    creator = CheckableCreator()

    return creator


class ITestCaseCreator(ABC):
    @abstractmethod
    def create(self, ttype: TestType) -> AbstractTestCase:
        """creates testcase of required type"""


@pytest.fixture
def testcase_creator(domain_config, testobject) -> ITestCaseCreator:
    class TestCaseCreator(ITestCaseCreator):
        def create(self, ttype: TestType) -> AbstractTestCase:
            testcase_class: type[AbstractTestCase]
            if ttype == TestType.SCHEMA:
                spec_type = SpecType.SCHEMA
                testcase_class = SchemaTestCase
            elif ttype == TestType.ROWCOUNT:
                spec_type = SpecType.ROWCOUNT
                testcase_class = RowCountTestCase
            elif ttype == TestType.COMPARE:
                spec_type = SpecType.COMPARE
                testcase_class = CompareTestCase
            elif ttype == TestType.STAGECOUNT:
                spec_type = SpecType.STAGECOUNT
                testcase_class = StageCountTestCase
            elif ttype == TestType.DUMMY_OK:
                testcase_class = DummyOkTestCase
                spec_type = SpecType.SCHEMA
            elif ttype == TestType.DUMMY_NOK:
                testcase_class = DummyNokTestCase
                spec_type = SpecType.SCHEMA
            elif ttype == TestType.DUMMY_EXCEPTION:
                testcase_class = DummyExceptionTestCase
                spec_type = SpecType.SCHEMA
            else:
                raise ValueError(f"Conftest: Invalid test type: {ttype}")

            definition = TestDefinitionDTO(
                testobject=testobject,
                testtype=ttype,
                specs=[
                    SpecDTO(
                        spec_type=spec_type,
                        location=LocationDTO("memory://my_location"),
                        testobject=testobject.name,
                    ),
                    SpecDTO(
                        spec_type=spec_type,
                        location=LocationDTO("memory://my_location"),
                        testobject=testobject.name,
                    ),
                ],
                domain_config=domain_config,
                testrun_id=uuid4(),
                labels=["my_label", "my_label2"],
            )

            testcase = testcase_class(
                definition=definition,
                backend=DummyBackend(),
                notifiers=[InMemoryNotifier()],
            )

            return testcase

    return TestCaseCreator()


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
