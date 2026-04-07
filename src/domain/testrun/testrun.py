# flake8: noqa
import threading
from typing import List, Dict, cast
from datetime import datetime
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor, as_completed, Future

from src.dtos import (
    TestRunDTO,
    TestRunSummaryDTO,
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
from src.infrastructure_ports import IBackendFactory, INotifier, IDtoStorage
from .testcases import (
    AbstractTestCase,
    SchemaTestCase,
    CompareTestCase,
    RowCountTestCase,
    StageCountTestCase,
    DummyExceptionTestCase,
    DummyNokTestCase,
    DummyOkTestCase,
)


# Maps each TestType to its concrete TestCase class.
_TESTCASE_CLASSES: Dict[TestType, type[AbstractTestCase]] = {
    TestType.SCHEMA: SchemaTestCase,
    TestType.COMPARE: CompareTestCase,
    TestType.ROWCOUNT: RowCountTestCase,
    TestType.STAGECOUNT: StageCountTestCase,
    TestType.DUMMY_OK: DummyOkTestCase,
    TestType.DUMMY_NOK: DummyNokTestCase,
    TestType.DUMMY_EXCEPTION: DummyExceptionTestCase,
}


class TestRunLoader:
    """Loads and lists TestRunDTO objects from storage."""

    def __init__(self, dto_storage: IDtoStorage):
        self.dto_storage = dto_storage

    def load_testrun(self, testrun_id: str) -> TestRunDTO:
        """Load a testrun by ID."""
        dto = self.dto_storage.read_dto(object_type=ObjectType.TESTRUN, id=testrun_id)
        return cast(TestRunDTO, dto)

    def list_testruns(self, domain: str, date: str | None = None) -> List[TestRunDTO]:
        """List testruns by domain and optionally by date."""
        filters: Dict[str, str] = {"domain": domain}
        if date is not None:
            filters["date"] = date
        dtos = self.dto_storage.list_dtos(object_type=ObjectType.TESTRUN, filters=filters)
        return [cast(TestRunDTO, dto) for dto in dtos]


class TestRun:
    def __init__(
        self,
        testrun: TestRunDTO,
        backend_factory: IBackendFactory,
        notifiers: List[INotifier],
        dto_storage: IDtoStorage,
        max_testrun_threads: int = 4,
    ):
        self.testrun = testrun
        self.backend_factory = backend_factory
        self.notifiers = notifiers
        self.dto_storage = dto_storage
        self.max_testrun_threads = max_testrun_threads
        self._lock = threading.Lock()

        # set dynamic fields
        self.testrun.start_ts = datetime.now()
        self.testrun.end_ts = None
        self.testrun.result = TestResult.NA

        # set result fields
        self.testcase_results: List[TestCaseDTO] = []
        self.testrun.status = TestStatus.INITIATED
        total_testcases = len(self.testrun.testdefinitions)
        self.testrun.summary = TestRunSummaryDTO(total_testcases=total_testcases)

        # persist initial state
        self.persist()

    def notify(self, message: str, importance: Importance = Importance.INFO):
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
        Executes all testcases in the testrun in parallel using a thread pool.
        Each testcase gets its own backend instance for thread safety.
        Results are persisted after each testcase completes.
        """

        self.testrun.status = TestStatus.EXECUTING
        self.persist()
        total = len(self.testrun.testdefinitions)
        self.notify(f"Starting testrun with {total} testcase(s)")

        with ThreadPoolExecutor(max_workers=self.max_testrun_threads) as executor:
            futures: Dict[Future[TestCaseDTO], TestDefinitionDTO] = {}
            for definition in self.testrun.testdefinitions:
                future = executor.submit(self._execute_single_testcase, definition)
                futures[future] = definition

            for i, future in enumerate(as_completed(futures), 1):
                definition = futures[future]
                result = future.result()
                with self._lock:
                    self.testcase_results.append(result)
                    self._update_summary(result)
                    self.notify(
                        f"Completed testcase {i}/{total}:"
                        f" {definition.testtype.value} for"
                        f" {definition.testobject.name}"
                        f" — {result.result.name}"
                    )
                    self.persist()

        # testrun result is only OK if all testcases are OK
        if all(result.result == TestResult.OK for result in self.testcase_results):
            self.testrun.result = TestResult.OK
        elif any(result.result == TestResult.NOK for result in self.testcase_results):
            self.testrun.result = TestResult.NOK
        else:
            self.testrun.result = TestResult.NA

        self.testrun.status = TestStatus.FINISHED
        self.testrun.end_ts = datetime.now()
        self.notify(f"Testrun finished with result: {self.testrun.result.name}")

        self.persist()

        return self.to_dto()

    def _execute_single_testcase(self, definition: TestDefinitionDTO) -> TestCaseDTO:
        """Execute a single testcase in its own thread with its own backend.

        The backend is closed after the testcase finishes so that any resources
        it holds (e.g. a DemoBackend's DuckDB connection and file handles) are
        released promptly instead of waiting for garbage collection.
        """
        backend = self.backend_factory.create(domain_config=self.testrun.domain_config)
        testcase_class = _TESTCASE_CLASSES.get(definition.testtype)
        ttype = definition.testtype
        if testcase_class is None:
            self.notify(f"Unknown test type: {ttype}", importance=Importance.ERROR)
            return TestCaseDTO(
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
                specs=definition.specs,
                domain_config=definition.domain_config,
                domain=definition.testobject.domain,
                stage=definition.testobject.stage,
                instance=definition.testobject.instance,
            )
        with backend:
            testcase = testcase_class(definition, backend, self.notifiers)
            return testcase.execute()

    def _update_summary(self, result: TestCaseDTO) -> None:
        """Update the testrun summary counters after a testcase completes."""
        self.testrun.summary.completed_testcases += 1
        match result.result:
            case TestResult.OK:
                self.testrun.summary.ok_testcases += 1
            case TestResult.NOK:
                self.testrun.summary.nok_testcases += 1
            case TestResult.NA:
                self.testrun.summary.na_testcases += 1

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

    def persist(self) -> None:
        self.dto_storage.write_dto(self.to_dto())
