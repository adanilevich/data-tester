from typing import List, cast

from src.domain.testrun.testrun import TestRun, TestRunLoader
from src.domain_ports import (
    ExecuteTestRunCommand,
    ITestRun,
    ListTestRunsCommand,
    LoadTestCaseCommand,
    LoadTestRunCommand,
    SaveTestRunCommand,
)
from src.dtos import ObjectType, TestCaseDTO, TestRunDTO
from src.infrastructure_ports import IBackendFactory, IDtoStorage, INotifier


class TestRunAdapter(ITestRun):
    """Receives a command and executes testcases"""

    def __init__(
        self,
        backend_factory: IBackendFactory,
        notifiers: List[INotifier],
        dto_storage: IDtoStorage,
        max_testrun_threads: int = 4,
    ):
        self.backend_factory: IBackendFactory = backend_factory
        self.notifiers: List[INotifier] = notifiers
        self.dto_storage: IDtoStorage = dto_storage
        self.max_testrun_threads = max_testrun_threads
        self.loader = TestRunLoader(dto_storage)

    def execute_testrun(self, command: ExecuteTestRunCommand) -> TestRunDTO:
        testrun = TestRun(
            testrun_def=command.testrun_def,
            backend_factory=self.backend_factory,
            notifiers=self.notifiers,
            dto_storage=self.dto_storage,
            max_testrun_threads=self.max_testrun_threads,
            testrun_id=command.testrun_id,
        )

        return testrun.execute()

    def save_testrun(self, command: SaveTestRunCommand) -> None:
        """Saves a testrun, e.g. to disk"""
        self.dto_storage.write_dto(dto=command.testrun)

    def load_testrun(self, command: LoadTestRunCommand) -> TestRunDTO:
        """Loads a testrun, e.g. from disk"""
        return self.loader.load_testrun(command.testrun_id)

    def list_testruns(self, command: ListTestRunsCommand) -> List[TestRunDTO]:
        """Lists testruns by domain and optionally date."""
        return self.loader.list_testruns(domain=command.domain, date=command.date)

    def load_testcase(self, command: LoadTestCaseCommand) -> TestCaseDTO:
        """Loads a persisted testcase by ID."""

        dto = self.dto_storage.read_dto(
            object_type=ObjectType.TESTCASE, id=str(command.testcase_id)
        )
        return cast(TestCaseDTO, dto)
