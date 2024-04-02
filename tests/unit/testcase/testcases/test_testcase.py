import pytest
from typing import List
from src.testcase.precondition_checkers.checker_interface import IPreconditionChecker
from src.testcase.precondition_checkers.checkable import AbstractCheckable
from src.testcase.testcases.testcase import TestCase
from src.testcase.dtos import (
    SpecificationDTO, TestObjectDTO, TestCaseResultDTO, TestResult, DomainConfigDTO
)
from src.testcase.driven_ports.notifier_interface import INotifier
from src.testcase.driven_ports.backend_interface import IBackend


class DummyTestCase(TestCase):
    type = "DUMMY"
    preconditions = []  # to be set by testcase
    required_specs = []  # to be set by testcase

    def _execute(self):
        self.result = TestResult.OK


class DummyChecker(IPreconditionChecker):
    def check(self, check: str, checkable: AbstractCheckable) -> bool:
        if check == "must_fail":
            return False
        else:
            return True


class TestExecutingTestcases:

    testobject = TestObjectDTO(name="to", domain="dom", project="proj", instance="inst")
    specifications = [
        SpecificationDTO(type="schema", content=None, location="loc", valid=True),
        SpecificationDTO(type="sql", content="sdfs", location="loc", valid=False),
    ]
    domain_config = DomainConfigDTO(
        domain="my_domain",
        compare_sample_default_sample_size=2,
        compare_sample_sample_size_per_object=dict()
    )
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
            domain_config=self.domain_config,
            run_id="my_id",
            backend=self.backend,
            notifiers=self.notifiers
        )
        return testcase

    def test_cant_create_unknown_testcase(self):

        with pytest.raises(NotImplementedError) as err:
            self.create_testcase(type="unknown")
            assert err.value == "Testcase bad is not implemented!"

    def test_creating_testcases(self):
        testcase = self.create_testcase(type="DUMMY")
        assert testcase.type == "DUMMY"
        assert testcase.status.value == "INITIATED"
        assert testcase.result.value == "N/A"
        assert "Initiating testcase" in self.notifications[0]

    def test_handling_fulfilled_preconditions(self):
        testcase = self.create_testcase(type="DUMMY")

        testcase.required_specs = []
        testcase.preconditions = ["ok", "any"]
        check_result = testcase._check_preconditions(checker=DummyChecker())

        assert check_result is True
        assert testcase.status.name == "PRECONDITIONS"
        for check in testcase.preconditions:
            assert f"Checking if {check} ..." in self.notifications

    def test_handling_nok_preconditions(self):
        testcase = self.create_testcase(type="DUMMY")

        testcase.required_specs = []
        testcase.preconditions = ["any", "must_fail"]
        check_result = testcase._check_preconditions(checker=DummyChecker())

        assert check_result is False
        assert testcase.status.name == "ABORTED"
        msgs = self.notifications
        assert "Check result for any: True" in msgs
        assert "Stopping execution due to failed precondition: must_fail!" in msgs

    def test_handling_when_specs_are_not_provided(self):
        testcase = self.create_testcase(type="DUMMY")

        testcase.required_specs = ["weird_input"]
        testcase.preconditions = []
        check_result = testcase._check_preconditions(checker=DummyChecker())

        assert check_result is False
        assert testcase.status.name == "ABORTED"
        assert "weird_input not provided. Stopping execution!" in self.notifications

    def test_handling_when_specs_are_provided(self):
        testcase = self.create_testcase(type="DUMMY")

        testcase.required_specs = ["sql", "schema"]
        testcase.preconditions = []
        check_result = testcase._check_preconditions(checker=DummyChecker())

        assert check_result is True
        assert testcase.status.name == "PRECONDITIONS"

    def test_execution_with_unfilfilled_preconditions(self):
        testcase = self.create_testcase(type="DUMMY")

        testcase.required_specs = []
        testcase.preconditions = ["must_fail"]
        result = testcase.execute(checker=DummyChecker())

        assert testcase.status.name == "ABORTED"
        assert testcase.result.name == "NA"
        assert isinstance(result, TestCaseResultDTO)

    def test_execution_with_exception(self):
        testcase = self.create_testcase(type="DUMMY")

        # substitute _execute method with an exception raiser
        def exc(*args, **kwarts):
            raise ValueError("Dummy Error!")

        testcase._execute = exc

        testcase.required_specs = []
        testcase.preconditions = []
        result = testcase.execute(checker=DummyChecker())

        assert testcase.status.name == "ERROR"
        assert testcase.result.name == "NA"
        assert isinstance(result, TestCaseResultDTO)

    def test_execution_when_everything_is_ok(self):
        testcase = self.create_testcase(type="DUMMY")

        testcase.required_specs = []
        testcase.preconditions = []
        result = testcase.execute(checker=DummyChecker())

        assert testcase.status.name == "FINISHED"
        assert testcase.result.name == "OK"
        assert isinstance(result, TestCaseResultDTO)

    def test_adding_details(self):
        testcase = self.create_testcase(type="DUMMY")
        detail_1 = {"detail1": "data_1"}
        detail_2 = {"detail2": "data_2"}
        testcase.add_detail(detail_1)
        testcase.add_detail(detail_2)

        assert detail_1 in testcase.details
        assert detail_2 in testcase.details
        assert len(testcase.details) == 2
