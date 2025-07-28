from typing import List, cast

from src.domain.testcase.ports import (
    ITestRunCommandHandler,
    ExecuteTestRunCommand,
    SaveTestRunCommand,
    LoadTestRunCommand,
    SetReportIdsCommand,
)
from src.infrastructure.backend import IBackendFactory
from src.infrastructure.notifier import INotifier
from src.dtos import TestRunDTO, StorageObject
from src.domain.testcase.core import TestRun
from src.infrastructure.storage import IStorageFactory


class TestRunCommandHandler(ITestRunCommandHandler):
    """Receives a command and executes testcases"""

    def __init__(
        self,
        backend_factory: IBackendFactory,
        notifiers: List[INotifier],
        storage_factory: IStorageFactory,
    ):
        self.backend_factory: IBackendFactory = backend_factory
        self.notifiers: List[INotifier] = notifiers
        self.storage_factory: IStorageFactory = storage_factory

    def run(self, command: ExecuteTestRunCommand) -> TestRunDTO:
        testrun = TestRun(
            testrun=command.testrun,
            backend=self.backend_factory.create(
                domain_config=command.testrun.domain_config
            ),
            notifiers=self.notifiers,
            storage_factory=self.storage_factory,
            storage_location=command.storage_location,
        )

        result = testrun.execute()

        return result

    def save(self, command: SaveTestRunCommand) -> None:
        """Saves a testrun, e.g. to disk"""

        testrun = command.testrun
        storage = self.storage_factory.get_storage(command.storage_location)
        storage.write(
            dto=testrun,
            object_type=StorageObject.TESTRUN,
            location=command.storage_location,
        )

    def load(self, command: LoadTestRunCommand) -> TestRunDTO:
        """Loads a testrun, e.g. from disk"""

        storage = self.storage_factory.get_storage(command.storage_location)
        dto = storage.read(
            object_type=StorageObject.TESTRUN,
            object_id=command.testrun_id,
            location=command.storage_location,
        )
        return cast(TestRunDTO, dto)

    def set_report_ids(self, command: SetReportIdsCommand) -> None:
        """Sets report ids for testrun report and testcase reports and persists testrun"""

        testrun = command.testrun
        testrun.report_id = command.testrun_report.report_id

        storage = self.storage_factory.get_storage(command.storage_location)
        storage.write(
            dto=testrun,
            object_type=StorageObject.TESTRUN,
            location=command.storage_location,
        )
