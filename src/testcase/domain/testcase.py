from __future__ import annotations
from abc import ABC, abstractmethod
from src.common_interfaces.testobject import TestObjectDTO
from src.common_interfaces.testcase import TestStatus, TestResult, TestCaseDTO
from src.common_interfaces.specification import SpecificationDTO
from typing import List


class IBackend(ABC):

    @abstractmethod
    def get_testobjects(self) -> List[TestObjectDTO]:
        pass


class INotifier(ABC):

    @abstractmethod
    def notify(self, message: str):
        pass


class TestCase:
    type: str = "ABSTRACT"
    preconditions: List[str] = []
    required_specs: List[str] = []
    __test__ = False  # prevents pytest collection

    @classmethod
    def create(cls, type: str, testobject: TestObjectDTO, specs: List[SpecificationDTO],
               backend: IBackend, notifiers: List[INotifier]) -> TestCase:
        """
        Creates a testcase object (subclass instance of TestCase) based on
        class attribute 'type'.
        """

        # check all defined subclasses
        known_testtypes = {}
        for cls_ in cls.__subclasses__():
            type_ = cls_.type
            # safeguard against defining same TestCase type twice
            if type_ in known_testtypes:
                raise ValueError(f"Testtype {type_} was defined twice!")
            else:
                known_testtypes[type_] = cls_

        if type not in known_testtypes:
            raise NotImplementedError(f"Testcase {type} is not implemented!")
        else:
            testcase = known_testtypes[type](
                testobject=testobject,
                specs=specs,
                backend=backend,
                notifiers=notifiers,
            )
            return testcase

    def __init__(self, testobject: TestObjectDTO, specs: List[SpecificationDTO],
                 backend: IBackend, notifiers: List[INotifier]) -> None:

        self.status: TestStatus = TestStatus.NOT_STARTED
        self.notifiers: List[INotifier] = notifiers
        self._notify(f"Initiating testcase {self.type} for {testobject.name}")

        self.testobject: TestObjectDTO = testobject
        self.specs: List[SpecificationDTO] = specs
        self.backend: IBackend = backend

        if self.type == "ABSTRACT":
            raise NotImplementedError("Can't instantiate ABSTRACT testcase")

        self.status = TestStatus.INITIATED
        self.result: TestResult = TestResult.NA

    def check_preconditions(self, checker: PreConditionChecker) -> bool:

        self.status = TestStatus.PRECONDITIONS

        self._notify("Checking specifications")
        for required_spec in self.required_specs:
            self._notify(f"Checking if {required_spec} is provided ...")
            if required_spec not in [spec.type for spec in self.specs]:
                self._notify(f"{required_spec} not provided. Stopping execution")
                self.status = TestStatus.ABORTED
                return False

        self._notify("Executing precondition checks")
        for check in self.preconditions:
            self._notify(f"Checking if {check}")
            check_result = checker.check(check=check, testcase=self)
            self._notify(f"Check {check} {str(check_result)}")
            if not check_result:
                self._notify("Stopping testcase executions due to failed preconditions.")
                self.result = TestResult.NA
                self.status = TestStatus.ABORTED
                return False

        self._notify("All precondition checks successful!")
        return True

    def _notify(self, message: str):
        for notifier in self.notifiers:
            notifier.notify(message)

    @abstractmethod
    def _execute(self) -> TestResult:
        pass

    def execute(self, checker: PreConditionChecker):
        self.status = TestStatus.EXECUTING
        self._notify("Starting execution of core testlogic")

        try:
            self._execute()
            self.status = TestStatus.FINISHED
            self._notify("Successfully finished test execution")
        except Exception as err:
            self.result = TestResult.NA
            self.status = TestStatus.ERROR
            self._notify(f"Technical error during test execution: {str(err)}")

        return TestCaseDTO(
            self.type, self.testobject, self.status, self.result, self.specs)


class PreConditionChecker:

    def check(self, check: str, testcase: TestCase) -> bool:
        return True
