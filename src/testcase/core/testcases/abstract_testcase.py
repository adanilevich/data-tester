from __future__ import annotations
from abc import abstractmethod
from functools import wraps
from uuid import uuid4, UUID
from datetime import datetime
from typing import Dict, List, Optional, Any
import time

from src.dtos import (
    TestObjectDTO, TestStatus, TestResult, TestCaseDTO, DomainConfigDTO,
    SpecificationDTO, TestType, TestDefinitionDTO
)

from src.testcase.ports import IDataPlatform, INotifier
from src.testcase.core.precondition_checks import (
    ICheckable,
    IPreconditionChecker,
    PreConditionChecker,
)


class AbstractTestCase(ICheckable):

    ttype: TestType = TestType.ABSTRACT
    preconditions: List[str] = []
    required_specs: List[str] = []
    __test__ = False  # prevents pytest collection

    def __init__(self, definition: TestDefinitionDTO,
                 backend: IDataPlatform, notifiers: List[INotifier]) -> None:

        self.notifiers: List[INotifier] = notifiers
        self.notify(f"Initiating testcase {self.ttype} for {definition.testobject.name}")
        self.testcase_id: UUID = uuid4()
        self.start_ts: datetime = datetime.now()
        self.end_ts: datetime | None = None
        self.status: TestStatus = TestStatus.NOT_STARTED
        self.testobject: TestObjectDTO = definition.testobject
        self.specs: List[SpecificationDTO] = definition.specs
        self.domain_config: DomainConfigDTO = definition.domain_config
        self.testrun_id: UUID = definition.testrun_id
        self.testset_id: UUID = definition.testset_id
        self.labels: List[str] = definition.labels
        self.backend: IDataPlatform = backend
        self.result: TestResult = TestResult.NA
        self.summary: str = "Testcase not started."
        # list of key facts about test execution
        self.facts: List[Dict[str, str | int]] = []
        self.details: List[Dict[str, str | int | float]] = []  # list of execution details
        self.diff: Dict[str, List | Dict] = dict()  # list of diffs
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

        for check in self.preconditions:
            check_name = check.replace("_", " ")
            self.notify(f"Checking that {check_name} ...")
            check_result = checker.check(check=check, checkable=self)
            self.notify(f"{check_name.title()}: {str(check_result)}")
            if not check_result:
                msg = f"Stopping execution due to failed precondition: {check_name}!"
                self.notify(msg)
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
            status=self.status,
            summary=self.summary,
            facts=self.facts,
            details=self.details,
            result=self.result,
            diff=self.diff,  # must be set by specific implementation
            specifications=self.specs,
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

    def execute(self,
                checker: Optional[IPreconditionChecker] = None) -> TestCaseDTO:

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
            self.notify(msg)
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
            duration = round_(end-start)
            detail = {f"Duration of {step_name} (s)": duration}
            msg = f"Duration of {step_name}: {duration} s"
            self.notify(msg)
            self.add_detail(detail)
            return result
        return wrapper
    return decorator
