import pytest
from typing import List
from src.testcase.domain.testcase import IBackend, INotifier, TestCase
from src.common_interfaces.testobject import TestObjectDTO
from src.common_interfaces.specification import SpecificationDTO


class DummyTestCase(TestCase):
    type = "DUMMY"
    preconditions = ["dummy_check_fulfilled"]


class TestExecutingTestcases:

    testobject = TestObjectDTO(name="to", domain="dom", project="proj", instance="inst")
    specifications = [
        SpecificationDTO(type="schema", content=None, location="loc", valid=True),
        SpecificationDTO(type="sql", content="sdfs", location="loc", valid=False),
    ]
    notifications: List[str] = []

    @pytest.fixture(autouse=True)
    def setup_backend(self):
        class DummyBackend(IBackend):
            def get_testobjects():
                return [self.testobject, self.testobject]

        self.backend = DummyBackend()

    @pytest.fixture(autouse=True)
    def setup_notifiers(self):

        # empty notification queue
        self.notifications = []

        class PrintNotifier(INotifier):
            def notify(self, message: str):
                print(message)

        notifications = self.notifications

        class DummyNotifier(INotifier):

            def notify(self, message: str):
                notifications.append(message)

        self.notifiers = [PrintNotifier(), DummyNotifier()]

    def create_testcase(self, type: str) -> TestCase:
        """Helper closure function to create testcases"""
        testcase = TestCase.create(
            type=type,
            testobject=self.testobject,
            specs=self.specifications,
            backend=self.backend,
            notifiers=self.notifiers
        )
        return testcase

    def test_that_unknown_testcase_cant_be_created(self):

        with pytest.raises(NotImplementedError) as err:
            self.create_testcase(type="unknown")
            assert err.value == "Testcase bad is not implemented!"

    def test_testcase_is_created(self):
        testcase = self.create_testcase(type="DUMMY")
        assert testcase.type == "DUMMY"
        assert testcase.status.value == "INITIATED"
        assert testcase.result.value == "N/A"
        assert "Initiating testcase" in self.notifications[0]

    def test_redundant_testtype_definition(self):

        class RedundantTestcase(TestCase):
            type = "DUMMY"  # create should throw an error since this type already exists

        with pytest.raises(ValueError) as err:
            self.create_testcase(type="DUMMY")
            assert "Testtype DUMMY was defined twice" in err
