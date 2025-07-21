from abc import ABC, abstractmethod
from typing import Dict, List
import time
from uuid import uuid4
from datetime import datetime

import pytest
import polars as pl
from fsspec.implementations.local import LocalFileSystem  # type: ignore
from urllib import request

from src.dtos.specification import SpecificationDTO, SpecificationType
from src.dtos.domain_config import (
    SchemaTestCaseConfigDTO,
    CompareTestCaseConfigDTO,
    DomainConfigDTO,
    TestCasesConfigDTO,
)
from src.dtos.testcase import (
    TestObjectDTO,
    TestCaseDTO,
    TestResult,
    TestStatus,
    TestType,
    TestDefinitionDTO,
)
from src.dtos.report import TestCaseReportDTO, TestRunReportDTO
from src.dtos.testcase import TestRunDTO
from src.dtos.location import LocationDTO
from src.testcase.ports import IDataPlatform
from src.notifier import InMemoryNotifier, StdoutNotifier
from src.data_platform import DummyPlatform
from src.testcase.core.testcases import (
    AbstractTestCase,
    SchemaTestCase,
    RowCountTestCase,
    CompareTestCase,
    DummyOkTestCase,
    DummyNokTestCase,
    DummyExceptionTestCase,
)
from src.testcase.core.precondition_checks import ICheckable
from tests.fixtures.demo.prepare_data import clean_up, prepare_data


@pytest.fixture
def dummy_backend() -> IDataPlatform:
    return DummyPlatform()


@pytest.fixture
def in_memory_notifier() -> InMemoryNotifier:
    return InMemoryNotifier()


@pytest.fixture
def stdout_notifier() -> StdoutNotifier:
    return StdoutNotifier()


@pytest.fixture
def domain_config() -> DomainConfigDTO:
    domain_config = DomainConfigDTO(
        domain="payments",
        instances={"test": ["alpha", "beta"], "uat": ["main"]},
        specifications_locations=[
            LocationDTO("dict://sqls"),
            LocationDTO("dict://specs"),
        ],
        testreports_location=LocationDTO("dict://testreports"),
        testcases=TestCasesConfigDTO(
            compare=CompareTestCaseConfigDTO(
                sample_size=100, sample_size_per_object={}
            ),
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


class DummyCheckable(ICheckable):
    def __init__(self, testobject: TestObjectDTO, backend: IDataPlatform):
        self.testobject = testobject
        self.backend = backend
        self.summary = ""
        self.details = []
        self.notifications: List[str] = []

    def update_summary(self, summary: str):
        self.summary += summary

    def add_detail(self, detail: Dict[str, str | int | float]):
        self.details.append(detail)

    def notify(self, message: str):
        self.notifications.append(message)


class ICheckableCreator(ABC):
    @abstractmethod
    def create(self) -> ICheckable:
        """Creates a checkable"""


@pytest.fixture
def checkable_creator(testobject, dummy_backend) -> ICheckableCreator:
    class CheckableCreator(ICheckableCreator):
        def create(self) -> ICheckable:
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
                spec_type = SpecificationType.SCHEMA
                testcase_class = SchemaTestCase
            elif ttype == TestType.ROWCOUNT:
                spec_type = SpecificationType.ROWCOUNT_SQL
                testcase_class = RowCountTestCase
            elif ttype == TestType.COMPARE:
                spec_type = SpecificationType.COMPARE_SQL
                testcase_class = CompareTestCase
            elif ttype == TestType.DUMMY_OK:
                testcase_class = DummyOkTestCase
                spec_type = SpecificationType.SCHEMA
            elif ttype == TestType.DUMMY_NOK:
                testcase_class = DummyNokTestCase
                spec_type = SpecificationType.SCHEMA
            elif ttype == TestType.DUMMY_EXCEPTION:
                testcase_class = DummyExceptionTestCase
                spec_type = SpecificationType.SCHEMA
            else:
                raise ValueError(f"Conftest: Invalid test type: {ttype}")

            definition = TestDefinitionDTO(
                testobject=testobject,
                testtype=ttype,
                specs=[
                    SpecificationDTO(
                        spec_type=spec_type,
                        location=LocationDTO("dict://my_location"),
                        testobject=testobject.name,
                    ),
                    SpecificationDTO(
                        spec_type=spec_type,
                        location=LocationDTO("dict://my_location"),
                        testobject=testobject.name,
                    ),
                ],
                domain_config=domain_config,
                testrun_id=uuid4(),
                labels=["my_label", "my_label2"],
            )

            testcase = testcase_class(
                definition=definition,
                backend=DummyPlatform(),
                notifiers=[InMemoryNotifier(), StdoutNotifier()],
            )

            return testcase

    return TestCaseCreator()


@pytest.fixture(scope="session")
def prepare_local_data():
    prepare_data()
    yield
    clean_up()


@pytest.fixture
def performance_test_data() -> pl.DataFrame:  # type: ignore
    def download_performance_test_data(source_file: str, target_file: str):
        print("Starting download from", source_file)
        start = time.time()
        request.urlretrieve(source_file, target_file)
        end = time.time()
        print("Download Duration: ", (end - start), "s")

    def read_as_parquet(target_file: str) -> pl.DataFrame:
        start = time.time()
        df = pl.read_parquet(target_file)
        end = time.time()
        print("Reading parquet in a DataFrame: ", (end - start), "s")
        print("Dataset shape:", df.shape)
        return df

    def copy_data(df: pl.DataFrame) -> pl.DataFrame:
        start = time.time()
        df = df.hstack(df.cast(pl.String).rename(lambda x: x + "_str"))
        df = df.hstack(df.rename(lambda x: x + "_copy"))
        df = df.hstack(df.rename(lambda x: x + "_again"))
        end = time.time()
        print("Copying fixtures 8-fold: ", (end - start), "s")
        print("Dataset shape:", df.shape)

        return df

    def clean_up_performance_test_data(target_file: str):
        fs = LocalFileSystem()
        if fs.exists(path=target_file):
            print("Deleting target file", target_file)
            fs.rm_file(target_file)

    source_file_ = (
        "https://d37ci6vzurychx.cloudfront.net/trip-data/"
        "yellow_tripdata_2015-01.parquet"
    )
    target_file_ = "yellow_tripdata_2015-01.parquet"

    start_ = time.time()
    download_performance_test_data(source_file_, target_file_)
    df_ = read_as_parquet(target_file_)
    df_ = copy_data(df_)
    end_ = time.time()

    print("Overall time to set up fixture for performance test: ", (end_ - start_), "s")

    yield df_

    clean_up_performance_test_data(target_file_)


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
    return TestRunDTO.from_testcases(
        testcases=[testcase_result, testcase_result]
    )


@pytest.fixture
def testcase_report(testcase_result) -> TestCaseReportDTO:
    return TestCaseReportDTO.from_testcase_result(testcase_result)


@pytest.fixture
def testrun_report(testrun) -> TestRunReportDTO:
    return TestRunReportDTO.from_testrun(testrun)
