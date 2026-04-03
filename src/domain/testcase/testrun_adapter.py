from typing import List

from src.domain_ports import (
    ITestRun,
    ExecuteTestRunCommand,
    SaveTestRunCommand,
    LoadTestRunCommand,
    ListTestRunsCommand,
)
from src.infrastructure_ports import IBackendFactory, INotifier, IDtoStorage
from src.dtos import TestRunDTO
from .testrun import TestRun, TestRunLoader


class TestRunAdapter(ITestRun):
    """Receives a command and executes testcases"""

    def __init__(
        self,
        backend_factory: IBackendFactory,
        notifiers: List[INotifier],
        dto_storage: IDtoStorage,
    ):
        self.backend_factory: IBackendFactory = backend_factory
        self.notifiers: List[INotifier] = notifiers
        self.dto_storage: IDtoStorage = dto_storage
        self.loader = TestRunLoader(dto_storage)

    def execute_testrun(self, command: ExecuteTestRunCommand) -> TestRunDTO:
        testrun = TestRun(
            testrun=command.testrun,
            backend=self.backend_factory.create(
                domain_config=command.testrun.domain_config
            ),
            notifiers=self.notifiers,
            dto_storage=self.dto_storage,
        )

        result = testrun.execute()

        return result

    def save_testrun(self, command: SaveTestRunCommand) -> None:
        """Saves a testrun, e.g. to disk"""
        self.dto_storage.write_dto(dto=command.testrun)

    def load_testrun(self, command: LoadTestRunCommand) -> TestRunDTO:
        """Loads a testrun, e.g. from disk"""
        return self.loader.load_testrun(command.testrun_id)

    def list_testruns(self, command: ListTestRunsCommand) -> List[TestRunDTO]:
        """Lists testruns by domain and optionally date."""
        return self.loader.list_testruns(domain=command.domain, date=command.date)
