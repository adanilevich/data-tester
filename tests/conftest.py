from abc import ABC, abstractmethod
from typing import Dict, List
import time

import pytest
import polars as pl
from fsspec.implementations.local import LocalFileSystem  # type: ignore
from urllib import request

from src.report.testcase_report import TestCaseReport
from src.report.testrun_report import TestRunReport
from src.dtos import (
    SpecificationDTO, SchemaTestCaseConfigDTO, CompareSampleTestCaseConfigDTO,
    DomainConfigDTO, TestCasesConfigDTO, TestObjectDTO,
    TestCaseResultDTO, TestRunResultDTO, TestStatus, TestResult
)
from src.testcase.ports import IDataPlatform
from src.testcase.adapters.notifiers import InMemoryNotifier, StdoutNotifier
from src.testcase.adapters.data_platforms import DummyPlatform
from src.testcase.testcases import TestCaseFactory, AbstractTestCase
from src.testcase.precondition_checks import ICheckable
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
        instances={
            "test": ["alpha", "beta"],
            "uat": ["main"]
        },
        specifications_locations=["my_first_location", "my_second_location"],
        testmatrices_locations="my_location",
        testreports_locations=[],
        testcases=TestCasesConfigDTO(
            compare_sample=CompareSampleTestCaseConfigDTO(
                sample_size=100,
                sample_size_per_object={}
            ),
            schema=SchemaTestCaseConfigDTO(compare_datatypes=["int", "string", "bool"]),
        )
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
    def create(self, ttype: str) -> AbstractTestCase:
        """creates testcase of required type"""


@pytest.fixture
def testcase_creator(domain_config, testobject) -> ITestCaseCreator:

    class TestCaseCreator(ITestCaseCreator):

        def create(self, ttype: str) -> AbstractTestCase:

            testcase = TestCaseFactory.create(
                ttype=ttype,
                testobject=testobject,
                specs=[
                    SpecificationDTO(
                        type="spec",
                        location="my_location",
                        testobject=testobject.name,
                    ),
                    SpecificationDTO(
                        type="sql",
                        location="my_location",
                        testobject=testobject.name,
                    ),
                ],
                domain_config=domain_config,
                testrun_id="my_run_id",
                backend=DummyPlatform(),
                notifiers=[InMemoryNotifier(), StdoutNotifier()]
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

    source_file_ = "https://d37ci6vzurychx.cloudfront.net/trip-data/" \
        "yellow_tripdata_2015-01.parquet"
    target_file_ = "yellow_tripdata_2015-01.parquet"

    start_ = time.time()
    download_performance_test_data(source_file_, target_file_)
    df_ = read_as_parquet(target_file_)
    df_ = copy_data(df_)
    end_ = time.time()

    print("Overall time to set up fixture for performance test: ", (end_-start_), "s")

    yield df_

    clean_up_performance_test_data(target_file_)


# FIXTURES FOR DOMAIN CONFIG

@pytest.fixture
def testcase_result(testobject) -> TestCaseResultDTO:
    return TestCaseResultDTO(
        testcase_id="id",
        testrun_id="my_testrun_id",
        testobject=testobject,
        testtype="SCHEMA",
        status=TestStatus.FINISHED,
        result=TestResult.OK,
        diff={"a": [1, 2, 3], "b": {3: 5}},
        summary="My Summary",
        facts=[{"a": 5}, {"b": "2"}],
        details=[{"a": 5}, {"b": "2"}],
        specifications=[],
        start_ts="asdf",
        end_ts="gartw"
    )


@pytest.fixture
def formatter():

    class DummyFormatter:

        def __init__(self):

            self._format = None
            self._content = None
            self._content_type = None

        def format(self, report: TestCaseReport, format: str):

            self._format = format
            report.format = format

            self._content = format
            report.content = format

            self._content_type = format
            report.content_type = format

    return DummyFormatter()


@pytest.fixture
def storage():

    class DummyStorage:

        def __init__(self):
            self.written: List[str] = []

        def write(self, path: str, *args, **kwargs):
            self.written.append(path)

    return DummyStorage()


@pytest.fixture
def naming_conventions():

    class DummyNamingConventions:

        def report_name(self, *args, **kwargs) -> str:
            return "report"

    return DummyNamingConventions()


@pytest.fixture
def testcase_report(
    testcase_result, formatter, storage, naming_conventions) -> TestCaseReport:

    return TestCaseReport.from_testcase_result(
        testcase_result=testcase_result,
        formatter=formatter,
        naming_conventions=naming_conventions,
        storage=storage,
    )

@pytest.fixture
def testrun_report(
    testcase_result, formatter, storage, naming_conventions) -> TestRunReport:

    return TestRunReport.from_testrun_result(
        testrun_result=TestRunResultDTO.from_testcase_results(
            testcase_results=[testcase_result, testcase_result]),
        formatter=formatter,
        storage=storage,
        naming_conventions=naming_conventions,
    )

