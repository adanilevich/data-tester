from __future__ import annotations

import time
from abc import abstractmethod
from datetime import datetime
from functools import wraps
from typing import Any, ClassVar, Dict, List, Optional
from uuid import UUID, uuid4

from src.domain.testrun.precondition_checks import (
    Checkable,
    IPreconditionChecker,
    PreConditionChecker,
)
from src.dtos import (
    AnySpec,
    DomainConfigDTO,
    Importance,
    NotificationDTO,
    NotificationProcess,
    Result,
    Status,
    TestCaseDTO,
    TestObjectDTO,
    TestType,
)
from src.dtos.testrun_dtos import TestCaseDefDTO
from src.infrastructure_ports import IBackend, IDtoStorage, INotifier


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

    known_testcases: ClassVar[Dict[TestType, type[AbstractTestCase]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "ttype") and cls.ttype not in (
            TestType.ABSTRACT,
            TestType.UNKNOWN,
        ):
            AbstractTestCase.known_testcases[cls.ttype] = cls

    def __init__(
        self,
        definition: TestCaseDefDTO,
        testrun_id: UUID,
        backend: IBackend,
        notifiers: List[INotifier],
        dto_storage: IDtoStorage | None = None,
    ) -> None:
        # set infra
        self.notifiers: List[INotifier] = notifiers
        self.backend: IBackend = backend
        self.dto_storage: IDtoStorage | None = dto_storage
        # set testcase data (context fields first, before any notify call)
        self.id: UUID = uuid4()
        self.testrun_id: UUID = testrun_id
        self.testset_id: UUID | None = definition.testset_id
        self.testobject: TestObjectDTO = definition.testobject
        self.scenario: str | None = definition.scenario
        self.specs = definition.specs
        self.domain_config: DomainConfigDTO = definition.domain_config
        self.labels: List[str] = definition.labels
        self.start_ts: datetime = datetime.now()
        self.end_ts: datetime | None = None
        self.status: Status = Status.NOT_STARTED
        self.result: Result = Result.NA
        self.summary: str = "Testcase not started."
        # list of key facts about test execution
        self.facts: List[Dict[str, str | int]] = []
        self.details: List[Dict[str, str | int | float]] = []  # list of execution details
        self.diff: Dict[str, List | Dict] = dict()  # list of diffs
        self.status = Status.INITIATED
        self.notify(f"Initiating testcase {self.ttype} for {definition.testobject.name}")
        self.persist()

    def persist(self):
        if self.dto_storage is not None:
            self.dto_storage.write_dto(self.to_dto())

    def notify(self, message: str, importance: Importance = Importance.INFO):
        notification = NotificationDTO(
            domain=self.testobject.domain,
            process=NotificationProcess.TESTCASE,
            testrun_id=str(self.testrun_id),
            testcase_id=str(self.id),
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
        self.status = Status.PRECONDITIONS
        self.persist()

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
                self.result = Result.NA
                self.status = Status.ABORTED
                return False

        return True

    def to_dto(self) -> TestCaseDTO:
        dto = TestCaseDTO(
            id=self.id,
            testrun_id=self.testrun_id,
            testset_id=self.testset_id or uuid4(),
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
            self.persist()
            return self.to_dto()

        self.status = Status.EXECUTING
        self.notify("Starting execution of core testlogic ...")
        self.persist()

        try:
            self._execute()
            self.status = Status.FINISHED
            self.notify(f"Finished test execution with result: {self.result.name}")
        except Exception as err:
            self.result = Result.NA
            self.status = Status.ERROR
            msg = f"Technical error during test execution: {str(err)}"
            self.notify(msg, importance=Importance.ERROR)
            self.summary = msg

        self.end_ts = datetime.now()
        self.persist()
        result = self.to_dto()

        return result


class _UnknownTestCase(AbstractTestCase):
    """Handles execution of testcases with an unrecognised TestType."""

    ttype: TestType = TestType.UNKNOWN

    def _execute(self) -> None:
        raise TestCaseExecutionError(f"Test type {self.ttype.value} unknown!")


class TestCaseCreator:
    """Creates a testcase instance from a TestCaseDefDTO.

    Looks up the concrete class in known_testcases. If the testtype is not
    registered, falls back to _UnknownTestCase.
    """

    @staticmethod
    def create(
        definition: TestCaseDefDTO,
        testrun_id: UUID,
        backend: IBackend,
        notifiers: List[INotifier],
        dto_storage: IDtoStorage | None = None,
    ) -> AbstractTestCase:
        testcase_class = AbstractTestCase.known_testcases.get(definition.testtype)
        args = (definition, testrun_id, backend, notifiers, dto_storage)
        if testcase_class is None:
            return _UnknownTestCase(*args)
        return testcase_class(*args)


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
