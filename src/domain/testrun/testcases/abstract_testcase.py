from __future__ import annotations
from abc import abstractmethod
from functools import wraps
from uuid import uuid4, UUID
from datetime import datetime
from typing import Dict, List, Optional, Any
import time

from src.dtos import (
    AnySpec,
    TestObjectDTO,
    TestStatus,
    TestResult,
    TestCaseDTO,
    DomainConfigDTO,
    TestType,
    TestDefinitionDTO,
    Importance,
    NotificationDTO,
    NotificationProcess,
)

from src.infrastructure_ports import IBackend, INotifier
from src.domain.testrun.precondition_checks import (
    Checkable,
    IPreconditionChecker,
    PreConditionChecker,
)


class TestCaseError(Exception):
    """
    Exception raised when a testcase operation fails.
    """


class SpecNotFoundError(TestCaseError):
    """
    Exception raised when a specification is not found
    """


class TestCaseExecutionError(TestCaseError):
    """
    Exception raised when a testcase execution fails
    """


class BackendError(TestCaseError):
    """
    Exception raised when a backend operation fails
    """


class AbstractTestCase(Checkable):
    ttype: TestType = TestType.ABSTRACT
    preconditions: Optional[List[str]] = None
    required_specs: Optional[List[str]] = None
    specs: List[AnySpec]  # always set in __init__; narrows Optional from Checkable
    __test__ = False  # prevents pytest collection

    def __init__(
        self,
        definition: TestDefinitionDTO,
        backend: IBackend,
        notifiers: List[INotifier],
    ) -> None:
        # set infra
        self.notifiers: List[INotifier] = notifiers
        self.backend: IBackend = backend
        # set testcase data (context fields first, before any notify call)
        self.testcase_id: UUID = uuid4()
        self.testrun_id: UUID = definition.testrun_id
        self.testset_id: UUID = definition.testset_id
        self.testobject: TestObjectDTO = definition.testobject
        self.scenario: str | None = definition.scenario
        self.specs = definition.specs
        self.domain_config: DomainConfigDTO = definition.domain_config
        self.labels: List[str] = definition.labels
        self.start_ts: datetime = datetime.now()
        self.end_ts: datetime | None = None
        self.status: TestStatus = TestStatus.NOT_STARTED
        self.result: TestResult = TestResult.NA
        self.summary: str = "Testcase not started."
        # list of key facts about test execution
        self.facts: List[Dict[str, str | int]] = []
        self.details: List[Dict[str, str | int | float]] = []  # list of execution details
        self.diff: Dict[str, List | Dict] = dict()  # list of diffs
        self.status = TestStatus.INITIATED
        self.notify(f"Initiating testcase {self.ttype} for {definition.testobject.name}")

    def notify(self, message: str, importance: Importance = Importance.INFO):
        notification = NotificationDTO(
            domain=self.testobject.domain,
            process=NotificationProcess.TESTCASE,
            testrun_id=str(self.testrun_id),
            testcase_id=str(self.testcase_id),
            importance=importance,
            message=message,
        )
        for notifier in self.notifiers:
            notifier.notify(notification)

    def add_fact(self, fact: Dict[str, Any]):
        self.facts.append(fact)

    def add_detail(self, detail: Dict[str, Any]):
        if self.details is None:
            self.details = []
        if detail not in self.details:
            self.details.append(detail)

    def update_summary(self, summary: str):
        self.summary = summary

    def _check_preconditions(self, checker: IPreconditionChecker) -> bool:
        self.status = TestStatus.PRECONDITIONS

        if self.preconditions is None:
            return True

        for check in self.preconditions:
            check_name: str = check.replace("_", " ")
            self.notify(f"Checking that {check_name} ...")
            check_result: bool = checker.check(check=check, checkable=self)
            self.notify(f"{check_name.title()}: {str(check_result)}")
            if not check_result:
                msg = f"Stopping execution due to failed precondition: {check_name}!"
                self.notify(msg, importance=Importance.WARNING)
                self.result = TestResult.NA
                self.status = TestStatus.ABORTED
                return False

        return True

    def to_dto(self) -> TestCaseDTO:
        dto = TestCaseDTO(
            testcase_id=self.testcase_id,
            testrun_id=self.testrun_id,
            testset_id=self.testset_id,
            labels=self.labels,
            testtype=self.ttype,
            testobject=self.testobject,
            scenario=self.scenario,
            status=self.status,
            summary=self.summary,
            facts=self.facts,
            details=self.details or [],
            result=self.result,
            diff=self.diff,  # must be set by specific implementation
            specs=self.specs,
            start_ts=self.start_ts,
            end_ts=self.end_ts or datetime.now(),
            domain_config=self.domain_config,
            domain=self.testobject.domain,
            stage=self.testobject.stage,
            instance=self.testobject.instance,
        )
        return dto

    @abstractmethod
    def _execute(self):
        raise NotImplementedError(f"Implement _execute for {self.__class__}")

    def execute(self, checker: Optional[IPreconditionChecker] = None) -> TestCaseDTO:
        self.notify(f"Starting execution of {self.ttype} for {self.testobject}")
        checker = checker or PreConditionChecker()
        if not self._check_preconditions(checker=checker):
            self.end_ts = datetime.now()
            return self.to_dto()

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
            self.notify(msg, importance=Importance.ERROR)
            self.summary = msg

        self.end_ts = datetime.now()
        return self.to_dto()


def time_it(step_name: str):
    """Parametrized decorator (factory): Times function execution duration
    and broadcasts this info via the broadcast method of given function"""

    def round_(num):
        return float("%.2g" % num)

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            self = args[0]  # args[0] is 'self' of function
            start = time.time()
            result = function(*args, **kwargs)
            end = time.time()
            duration = round_(end - start)
            detail = {f"Duration of {step_name} (s)": duration}
            msg = f"Duration of {step_name}: {duration} s"
            self.notify(msg)
            self.add_detail(detail)
            return result

        return wrapper

    return decorator
