# flake8: noqa
from typing import List, Dict, cast
from datetime import datetime
from uuid import uuid4

from src.dtos import (
    TestRunDTO,
    TestDefinitionDTO,
    TestType,
    TestResult,
    TestCaseDTO,
    TestStatus,
    ObjectType,
    Importance,
    NotificationDTO,
    NotificationProcess,
)
from src.infrastructure_ports import IBackend, INotifier, IDtoStorage
from .testcases import (
    AbstractTestCase,
    SchemaTestCase,
    CompareTestCase,
    RowCountTestCase,
    DummyExceptionTestCase,
    DummyNokTestCase,
    DummyOkTestCase,
)


class TestCaseUnknownError(NotImplementedError):
    __test__ = False
    pass


class TestRunLoader:
    """Loads and lists TestRunDTO objects from storage."""

    def __init__(self, dto_storage: IDtoStorage):
        self.dto_storage = dto_storage

    def load_testrun(self, testrun_id: str) -> TestRunDTO:
        """Load a testrun by ID."""
        dto = self.dto_storage.read_dto(
            object_type=ObjectType.TESTRUN,
            id=testrun_id,
        )
        return cast(TestRunDTO, dto)

    def list_testruns(self, domain: str, date: str | None = None) -> List[TestRunDTO]:
        """List testruns by domain and optionally by date."""
        filters: Dict[str, str] = {"domain": domain}
        if date is not None:
            filters["date"] = date
        dtos = self.dto_storage.list_dtos(
            object_type=ObjectType.TESTRUN,
            filters=filters,
        )
        return [cast(TestRunDTO, dto) for dto in dtos]


class TestRun:

    def __init__(
        self,
        testrun: TestRunDTO,
        backend: IBackend,
        notifiers: List[INotifier],
        dto_storage: IDtoStorage,
    ):
        self.testrun = testrun
        self.backend = backend
        self.notifiers = notifiers
        self.dto_storage = dto_storage

        # set dynamic fields
        self.testrun.start_ts = datetime.now()
        self.testrun.end_ts = None
        self.testrun.result = TestResult.NA

        # set result fields
        self.testcase_results: List[TestCaseDTO] = []
        self.testrun.status = TestStatus.INITIATED

        # persist initial state
        self.persist()

    def notify(
        self, message: str, importance: Importance = Importance.INFO,
    ):
        notification = NotificationDTO(
            domain=self.testrun.domain,
            process=NotificationProcess.TESTRUN,
            testrun_id=str(self.testrun.testrun_id),
            importance=importance,
            message=message,
        )
        for notifier in self.notifiers:
            notifier.notify(notification)

    def execute(self) -> TestRunDTO:
        """
        Executes all testcases in the testrun.
        """

        self.testrun.status = TestStatus.EXECUTING
        self.persist()
        total = len(self.testrun.testdefinitions)
        self.notify(f"Starting testrun with {total} testcase(s)")

        for i, definition in enumerate(self.testrun.testdefinitions, 1):
            self.notify(
                f"Executing testcase {i}/{total}:"
                f" {definition.testtype.value} for"
                f" {definition.testobject.name}"
            )
            try:
                testcase = self._create_testcase(definition)
                result = testcase.execute()
            except TestCaseUnknownError:
                self.notify(
                    f"Unknown test type: {definition.testtype}",
                    importance=Importance.ERROR,
                )
                result = TestCaseDTO(
                    testcase_id=uuid4(),
                    result=TestResult.NA,
                    summary=f"Test type {definition.testtype} unknown!",
                    facts=[],
                    details=[],
                    status=TestStatus.ERROR,
                    start_ts=datetime.now(),
                    end_ts=datetime.now(),
                    testobject=definition.testobject,
                    testrun_id=self.testrun.testrun_id,
                    testset_id=self.testrun.testset_id,
                    labels=definition.labels,
                    diff=dict(),
                    testtype=definition.testtype,
                    specifications=definition.specs,
                    domain_config=definition.domain_config,
                    domain=definition.testobject.domain,
                    stage=definition.testobject.stage,
                    instance=definition.testobject.instance,
                )

            self.testcase_results.append(result)

        # testrun result is only OK if all testcases are OK
        if all(result.result == TestResult.OK for result in self.testcase_results):
            self.testrun.result = TestResult.OK
        elif any(result.result == TestResult.NOK for result in self.testcase_results):
            self.testrun.result = TestResult.NOK
        else:
            self.testrun.result = TestResult.NA

        self.testrun.status = TestStatus.FINISHED
        self.testrun.end_ts = datetime.now()
        self.notify(
            f"Testrun finished with result: {self.testrun.result.name}"
        )

        self.persist()

        return self.to_dto()

    def _create_testcase(self, definition: TestDefinitionDTO) -> AbstractTestCase:
        """
        Creates a testcase object (subclass instance of TestCase) based on class attribute
        'ttype' - the specified test type must be implemented as subclass of TestCase.
        """

        match definition.testtype:
            case TestType.SCHEMA:
                return SchemaTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers
                )
            case TestType.COMPARE:
                return CompareTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers,
                )
            case TestType.ROWCOUNT:
                return RowCountTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers,
                )
            case TestType.DUMMY_OK:
                return DummyOkTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers,
                )
            case TestType.DUMMY_NOK:
                return DummyNokTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers,
                )
            case TestType.DUMMY_EXCEPTION:
                return DummyExceptionTestCase(
                    definition=definition,
                    backend=self.backend,
                    notifiers=self.notifiers,
                )
            case _:
                raise TestCaseUnknownError(f"Test type {definition.testtype} unknown!")

    def to_dto(self) -> TestRunDTO:
        return TestRunDTO(
            testrun_id=self.testrun.testrun_id,
            testset_id=self.testrun.testset_id,
            labels=self.testrun.labels,
            start_ts=self.testrun.start_ts,
            end_ts=self.testrun.end_ts or datetime.now(),
            result=self.testrun.result,
            testcase_results=self.testcase_results,
            testdefinitions=self.testrun.testdefinitions,
            stage=self.testrun.stage,
            instance=self.testrun.instance,
            domain=self.testrun.domain,
            status=self.testrun.status,
            testset_name=self.testrun.testset_name,
            domain_config=self.testrun.domain_config,
        )

    def persist(self, dto: TestRunDTO | None = None) -> None:
        if dto is None:
            dto = self.to_dto()
        self.dto_storage.write_dto(dto)
