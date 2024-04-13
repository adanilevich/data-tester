from __future__ import annotations
from abc import abstractmethod
from uuid import uuid4
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from src.dtos.testcase import (
    TestObjectDTO, TestStatus, TestResult, TestCaseResultDTO
)
from src.dtos.configs import DomainConfigDTO
from src.dtos.specifications import SpecificationDTO
from src.testcase.driven_ports.i_backend import IBackend
from src.testcase.driven_ports.i_notifier import INotifier
from src.testcase.precondition_checks import (
    ICheckable,
    IPreconditionChecker,
    PreConditionChecker,
)


def get_datetime() -> str:
    """Helper function to get datetime as formatted string"""
    return datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


class AbstractTestCase(ICheckable):

    ttype: str = "ABSTRACT"
    preconditions: List[str] = []
    required_specs: List[str] = []
    __test__ = False  # prevents pytest collection

    def __init__(self, testobject: TestObjectDTO, specs: List[SpecificationDTO],
                 domain_config: DomainConfigDTO, run_id: str,
                 backend: IBackend, notifiers: List[INotifier]) -> None:

        self.notifiers: List[INotifier] = notifiers
        self.notify(f"Initiating testcase {self.ttype} for {testobject.name}")
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
        self.facts: List[Dict[str, str]] = []  # list of key facts about test execution
        self.details: List[Dict[str, str]] = []  # list of in-depth details about execut.
        # diff is a list of lists or dicts:
        #  lists contain a record-oriented dict representation of a dataframe
        #
        self.diff: Dict[str, Union[List, Dict]] = dict()

        self.status = TestStatus.INITIATED

    def notify(self, message: str):
        for notifier in self.notifiers:
            notifier.notify(message)

    def add_fact(self, fact: Dict[str, Any]):
        self.facts.append(fact)

    def add_detail(self, detail: Dict[str, Any]):
        self.details.append(detail)

    def update_summary(self, summary: str):
        self.summary = summary

    def _check_preconditions(self, checker: IPreconditionChecker) -> bool:

        self.status = TestStatus.PRECONDITIONS

        for required_spec in self.required_specs:
            self.notify(f"Checking if {required_spec} is provided ...")
            if required_spec not in [spec.type for spec in self.specs]:
                self.notify(f"{required_spec} not provided. Stopping execution!")
                self.result = TestResult.NA
                self.status = TestStatus.ABORTED
                return False
            else:
                self.notify(f"{required_spec} found.")

        for check in self.preconditions:
            self.notify(f"Checking if {check} ...")
            check_result = checker.check(check=check, checkable=self)
            self.notify(f"Check result for {check}: {str(check_result)}")
            if not check_result:
                self.notify(f"Stopping execution due to failed precondition: {check}!")
                self.result = TestResult.NA
                self.status = TestStatus.ABORTED
                return False

        return True

    @abstractmethod
    def _execute(self):
        raise NotImplementedError(f"Implement _execute for {self.__class__}")

    def _as_dto(self) -> TestCaseResultDTO:
        dto = TestCaseResultDTO(
            id=self.id,
            run_id=self.run_id,
            testtype=self.ttype,
            testobject=self.testobject,
            status=self.status,
            summary=self.summary,
            details=self.details,
            result=self.result,
            diff=self.diff,  # must be set by specific implementation
            specifications=self.specs,
            start_ts=self.start_ts,
            end_ts=self.end_ts,
        )
        return dto

    def execute(self,
                checker: Optional[IPreconditionChecker] = None) -> TestCaseResultDTO:

        checker = checker or PreConditionChecker()
        if not self._check_preconditions(checker=checker):
            self.end_ts = get_datetime()
            return self._as_dto()

        self.status = TestStatus.EXECUTING
        self.notify("Starting execution of core testlogic ...")

        try:
            self._execute()
            self.status = TestStatus.FINISHED
            self.notify(f"Finished test execution with result: {self.result.name}")
        except Exception as err:
            self.result = TestResult.NA
            self.status = TestStatus.ERROR
            msg = f"Technical error during test execution: {str(err)}"
            self.notify(msg)
            self.summary = msg

        self.end_ts = get_datetime()
        return self._as_dto()
