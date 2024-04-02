import pytest

from src.testcase.dtos import TestObjectDTO, SpecificationDTO, DomainConfigDTO
from src.testcase.driven_ports.i_backend import IBackend
from src.testcase.driven_adapters.notifiers.in_memory_notifier import InMemoryNotifier
from src.testcase.driven_adapters.notifiers.stdout_notifier import StdoutNotifier
from src.testcase.testcases.testcase_factory import TestCaseFactory
from src.testcase.testcases.testcase import TestCase


class DummyBackend(IBackend):

    def get_testobjects(self, *args, **kwargs):
        return ["my_testobject", "your_testobject"]


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
def testcase_creator():
    def create_testcase(ttype: str) -> TestCase:
        testobject = TestObjectDTO(
            name="my_testobject",
            domain="my_domain",
            project="my_project",
            instance="my_instance",
        )

        domain_config = DomainConfigDTO(
            domain="my_domain",
            compare_sample_default_sample_size=1000,
            compare_sample_sample_size_per_object=dict(my_object=100, your_object=10)
        )

        testcase = TestCaseFactory.create(
            ttype=ttype,
            testobject=testobject,
            specs=[
                SpecificationDTO(type="spec", content="", valid=True, location="my_location"),
                SpecificationDTO(type="sql", content="", valid=True, location="my_location"),
            ],
            domain_config=domain_config,
            run_id="my_run_id",
            backend=DummyBackend(),
            notifiers=[InMemoryNotifier(), StdoutNotifier()]
        )

        return testcase

    return create_testcase
