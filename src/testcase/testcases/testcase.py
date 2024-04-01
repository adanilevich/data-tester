from __future__ import annotations
from dataclasses import dataclass
from abc import abstractmethod
from enum import Enum
from uuid import uuid4
from datetime import datetime
from src.testcase.driven_ports.backend_interface import IBackend
from src.testcase.driven_ports.notifier_interface import INotifier
from src.testcase.precondition_checkers.checker import (
    AbstractChecker, PreConditionChecker
)
from src.testcase.precondition_checkers.checkable import AbstractCheckable
from typing import Dict, List, Optional, Union, Any


@dataclass
class TestObjectDTO:
    __test__ = False  # prevents pytest collection
    name: str
    domain: str
    project: str
    instance: str


@dataclass
class SpecificationDTO:
    type: str
    content: Any
    location: str
    valid: Union[bool, None] = None


class TestStatus(Enum):
    __test__ = False  # prevents pytest collection
    NOT_STARTED = "NOT STARTED"
    INITIATED = "INITIATED"
    ABORTED = "ABORTED"
    PRECONDITIONS = "CHECKING PRECONDITIONS"
    EXECUTING = "EXECUTING"
    ERROR = "ERROR"
    FINISHED = "FINISHED"


class TestResult(Enum):
    __test__ = False  # prevents pytest collection
    NA = "N/A"
    OK = "OK"
    NOK = "NOK"


@dataclass
class TestCaseResultDTO:
    __test__ = False  # prevents pytest collection
    id: str
    run_id: str
    type: str
    testobject: TestObjectDTO
    status: TestStatus
    result: TestResult
    specifications: List[SpecificationDTO]
    start_ts: str
    end_ts: Union[str, None]


@dataclass
class DomainConfigDTO:
    """
    This serves as a generic data container for business-related configurations.
    The required attributes are defined by configuration needs of implemented Testcases,
    e.g., the testcase compare_sample requires a sample size definition.
    """
    domain: str
    compare_sample_default_sample_size: int
    compare_sample_sample_size_per_object: Dict[str, int]


def get_datetime() -> str:
    """Helper function to get datetime as formatted string"""
    return datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


class TestCase(AbstractCheckable):
    type: str = "ABSTRACT"
    preconditions: List[str] = []
    required_specs: List[str] = []
    __test__ = False  # prevents pytest collection

    @classmethod
    def create(cls, type: str, testobject: TestObjectDTO, specs: List[SpecificationDTO],
               domain_config: DomainConfigDTO, run_id: str,
               backend: IBackend, notifiers: List[INotifier]) -> TestCase:
        """
        Creates a testcase object (subclass instance of TestCase) based on class attribute
        'type' - the specified test type must be implemented as subclass of TestCase.
        """

        # check all defined subclasses
        known_testtypes: Dict[str, cls.__class__] = dict()
        for cls_ in cls.__subclasses__():
            type_ = cls_.type
            known_testtypes[type_] = cls_

        if type not in known_testtypes:
            raise NotImplementedError(f"Testcase {type} is not implemented!")
        else:
            testcase = known_testtypes[type](
                testobject=testobject,
                specs=specs,
                domain_config=domain_config,
                run_id=run_id,
                backend=backend,
                notifiers=notifiers,
            )
            return testcase

    def __init__(self, testobject: TestObjectDTO, specs: List[SpecificationDTO],
                 domain_config: DomainConfigDTO, run_id: str,
                 backend: IBackend, notifiers: List[INotifier]) -> None:

        if self.type == "ABSTRACT":
            raise NotImplementedError("Can't instantiate ABSTRACT testcase")

        self.notifiers: List[INotifier] = notifiers
        self.notify(f"Initiating testcase {self.type} for {testobject.name}")

        self.id: str = str(uuid4())
        self.start_ts: str = get_datetime()
        self.end_ts: Union[str, None] = None
        self.status: TestStatus = TestStatus.NOT_STARTED
        self.testobject: TestObjectDTO = testobject
        self.specs: List[SpecificationDTO] = specs
        self.domain_config: DomainConfigDTO = domain_config
        self.run_id: str = run_id
        self.backend: IBackend = backend
        self.result: TestResult = TestResult.NA
        self.summary: str = "Testcase not started."
        self.details: List[Dict[str, str]] = []

        self.status = TestStatus.INITIATED

    def notify(self, message: str):
        for notifier in self.notifiers:
            notifier.notify(message)

    def add_detail(self, detail: Dict[str, str]):
        self.details.append(detail)

    def update_summary(self, summary: str):
        self.summary = summary

    def _check_preconditions(self, checker: AbstractChecker) -> bool:

        self.status = TestStatus.PRECONDITIONS

        self.notify("Checking specifications ...")
        for required_spec in self.required_specs:
            self.notify(f"Checking if {required_spec} is provided ...")
            if required_spec not in [spec.type for spec in self.specs]:
                self.notify(f"{required_spec} not provided. Stopping execution!")
                self.status = TestStatus.ABORTED
                return False

        self.notify("Executing precondition checks ...")
        for check in self.preconditions:
            self.notify(f"Checking if {check} ...")
            check_result = checker.check(check=check, checkable=self)
            self.notify(f"Check result for {check}: {str(check_result)}")
            if not check_result:
                self.notify(f"Stopping execution due to failed precondition: {check}!")
                self.result = TestResult.NA
                self.status = TestStatus.ABORTED
                return False

        self.notify("All precondition checks successful!")
        return True

    @abstractmethod
    def _execute(self):
        raise NotImplementedError(f"Implement _execute for {self.__class__}")

    def _as_dto(self) -> TestCaseResultDTO:
        dto = TestCaseResultDTO(
            id=self.id,
            run_id=self.run_id,
            type=self.type,
            testobject=self.testobject,
            status=self.status,
            result=self.result,
            specifications=self.specs,
            start_ts=self.start_ts,
            end_ts=self.end_ts,
        )
        return dto

    def execute(self, checker: Optional[AbstractChecker] = None) -> TestCaseResultDTO:

        checker = checker or PreConditionChecker()
        if not self._check_preconditions(checker=checker):
            self.end_ts = get_datetime()
            return self._as_dto()

        self.status = TestStatus.EXECUTING
        self.notify("Starting execution of core testlogic ...")

        try:
            self._execute()
            self.status = TestStatus.FINISHED
            self.notify("Successfully finished test execution")
        except Exception as err:
            self.result = TestResult.NA
            self.status = TestStatus.ERROR
            self.notify(f"Technical error during test execution: {str(err)}")

        self.end_ts = get_datetime()
        return self._as_dto()
