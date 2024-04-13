import pytest

from src.dtos.testcase import (
    TestObjectDTO
)
from src.dtos.configs import SchemaTestCaseConfigDTO, CompareSampleTestCaseConfigDTO, DomainConfigDTO
from src.dtos.specifications import SpecificationDTO
from src.testcase.driven_ports.i_backend import IBackend
from src.testcase.driven_adapters.notifiers.in_memory_notifier import InMemoryNotifier
from src.testcase.driven_adapters.notifiers.stdout_notifier import StdoutNotifier
from src.testcase.driven_adapters.backends.dummy.dummy_backend import DummyBackend
from src.testcase.testcases import TestCaseFactory, AbstractTestCase
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
        schema_testcase_config=SchemaTestCaseConfigDTO(compare_datatypes=["int", "str"])
    )
    return domain_config


@pytest.fixture
def testcase_creator(domain_config):
    def create_testcase(ttype: str) -> AbstractTestCase:
        testobject = TestObjectDTO(
            name="my_testobject",
            domain="my_domain",
            project="my_project",
            instance="my_instance",
        )

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

    return create_testcase


@pytest.fixture(scope="session")
def prepare_local_data():
    prepare_data()
    yield
    clean_up()
