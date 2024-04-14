from abc import ABC, abstractmethod
from typing import Dict

import pytest

from src.dtos.testcase import TestObjectDTO
from src.dtos.configs import (
    SchemaTestCaseConfigDTO,
    CompareSampleTestCaseConfigDTO,
    DomainConfigDTO
)
from src.dtos.specifications import SpecificationDTO
from src.testcase.ports import IBackend
from src.testcase.adapters.notifiers import InMemoryNotifier, StdoutNotifier
from src.testcase.adapters.backends import DummyBackend
from src.testcase.testcases import TestCaseFactory, AbstractTestCase
from src.testcase.precondition_checks import ICheckable
from tests.data.data.prepare_data import clean_up, prepare_data


@pytest.fixture
def dummy_backend() -> IBackend:
    return DummyBackend()


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
        compare_sample_testcase_config=CompareSampleTestCaseConfigDTO(sample_size=100),
        schema_testcase_config=SchemaTestCaseConfigDTO(
            compare_datatypes=["int", "string", "bool"])
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

    def __init__(self, testobject: TestObjectDTO, backend: IBackend):
        self.testobject = testobject
        self.backend = backend
        self.summary = ""
        self.details = []
        self.notifications = []

    def update_summary(self, summary: str):
        self.summary += summary

    def add_detail(self, detail: Dict[str, str]):
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
                    SpecificationDTO(type="spec", location="my_location"),
                    SpecificationDTO(type="sql", location="my_location"),
                ],
                domain_config=domain_config,
                run_id="my_run_id",
                backend=DummyBackend(),
                notifiers=[InMemoryNotifier(), StdoutNotifier()]
            )
            return testcase

    return TestCaseCreator()


@pytest.fixture(scope="session")
def prepare_local_data():
    prepare_data()
    yield
    clean_up()
