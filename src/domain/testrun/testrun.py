# flake8: noqa
import threading
from typing import List, Dict, cast
from datetime import datetime
from uuid import uuid4, UUID
from concurrent.futures import ThreadPoolExecutor, as_completed, Future

from src.dtos import (
    TestRunDTO,
    Result,
    TestCaseDTO,
    Status,
    ObjectType,
    Importance,
    NotificationDTO,
    NotificationProcess,
)
from src.dtos.testrun_dtos import TestCaseDefDTO, TestRunDefDTO
from src.infrastructure_ports import IBackendFactory, INotifier, IDtoStorage
from .testcases import (  # noqa: F401 — imported to trigger auto-registration in known_testcases
    AbstractTestCase,
    TestCaseCreator,
    SchemaTestCase,
    CompareTestCase,
    RowCountTestCase,
    StageCountTestCase,
    DummyExceptionTestCase,
    DummyNokTestCase,
    DummyOkTestCase,
)


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
        testrun_def: TestRunDefDTO,
        backend_factory: IBackendFactory,
        notifiers: List[INotifier],
        dto_storage: IDtoStorage,
        max_testrun_threads: int = 4,
        testrun_id: UUID | None = None,
    ):
        # flatten definition fields
        self.testcase_defs: List[TestCaseDefDTO] = testrun_def.testcase_defs
        self.domain: str = testrun_def.domain
        self.stage: str = testrun_def.stage
        self.instance: str = testrun_def.instance
        self.domain_config = testrun_def.domain_config
        self.testset_id: UUID = testrun_def.testset_id or uuid4()
        self.testset_name: str = testrun_def.testset_name or "Testset name not set"
        self.labels: List[str] = testrun_def.labels
        # infra
        self.backend_factory = backend_factory
        self.notifiers = notifiers
        self.dto_storage = dto_storage
        self.max_testrun_threads = max_testrun_threads
        self._lock = threading.Lock()
        # execution state
        self.id: UUID = testrun_id or uuid4()
        self.start_ts: datetime = datetime.now()
        self.end_ts: datetime | None = None
        self.result: Result = Result.NA
        self.status: Status = Status.INITIATED
        self.results: List[TestCaseDTO] = []

        # persist initial state
        self.persist()

    def notify(self, message: str, importance: Importance = Importance.INFO):
        notification = NotificationDTO(
            domain=self.domain,
            process=NotificationProcess.TESTRUN,
            testrun_id=str(self.id),
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

        self.status = Status.EXECUTING
        self.persist()
        total = len(self.testcase_defs)
        self.notify(f"Starting testrun with {total} testcase(s)")

        with ThreadPoolExecutor(max_workers=self.max_testrun_threads) as executor:
            futures: Dict[Future[TestCaseDTO], TestCaseDefDTO] = {}
            for definition in self.testcase_defs:
                future = executor.submit(self._execute_single_testcase, definition)
                futures[future] = definition

            for future in as_completed(futures):
                result = future.result()
                with self._lock:
                    self.results.append(result)
                    self.persist()

        # testrun result is only OK if all testcases are OK
        if all(result.result == Result.OK for result in self.results):
            self.result = Result.OK
        elif any(result.result == Result.NOK for result in self.results):
            self.result = Result.NOK
        else:
            self.result = Result.NA

        self.status = Status.FINISHED
        self.end_ts = datetime.now()
        self.notify(f"Testrun finished with result: {self.result.name}")

        self.persist()

        return self.to_dto()

    def _execute_single_testcase(self, definition: TestCaseDefDTO) -> TestCaseDTO:
        """Execute a single testcase in its own thread with its own backend.

        The backend is closed after the testcase finishes so that any resources
        it holds are released promptly instead of waiting for garbage collection.
        """
        backend = self.backend_factory.create(domain_config=self.domain_config)
        with backend:
            testcase = TestCaseCreator.create(definition, self.id, backend, self.notifiers)
            return testcase.execute()

    def to_dto(self) -> TestRunDTO:
        return TestRunDTO(
            id=self.id,
            testset_id=self.testset_id,
            labels=self.labels,
            start_ts=self.start_ts,
            end_ts=self.end_ts or datetime.now(),
            result=self.result,
            results=self.results,
            testdefinitions=self.testcase_defs,
            stage=self.stage,
            instance=self.instance,
            domain=self.domain,
            status=self.status,
            testset_name=self.testset_name,
            domain_config=self.domain_config,
        )

    def persist(self) -> None:
        self.dto_storage.write_dto(self.to_dto())
