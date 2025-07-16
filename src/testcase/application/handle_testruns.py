from typing import List

from src.testcase.ports import (
    ITestRunCommandHandler,
    ExecuteTestRunCommand,
    IDataPlatformFactory,
    INotifier,
    IStorage,
    SaveTestRunCommand,
    LoadTestRunCommand,
    SetReportIdsCommand,
    StorageTypeUnknownError,
)
from src.dtos import LocationDTO, TestRunDTO
from src.testcase.core import TestRun


class TestRunCommandHandler(ITestRunCommandHandler):
    """Receives a command and executes testcases"""

    def __init__(
        self,
        backend_factory: IDataPlatformFactory,
        notifiers: List[INotifier],
        storage: IStorage,
    ):
        self.backend_factory: IDataPlatformFactory = backend_factory
        self.notifiers: List[INotifier] = notifiers
        self.storage: IStorage = storage

    def run(self, command: ExecuteTestRunCommand) -> TestRunDTO:

        testrun = TestRun(
            testrun=command.testrun,
            backend=self.backend_factory.create(
                domain_config=command.testrun.domain_config
            ),
            notifiers=self.notifiers,
            storage=self.storage,
            storage_location=command.storage_location,
        )

        result = testrun.execute()

        return result

    def save(self, command: SaveTestRunCommand) -> None:
        """Saves a testrun, e.g. to disk"""

        testrun = command.testrun
        location = self._loc(command.storage_location, str(testrun.testrun_id))

        self.storage.write(testrun.to_json().encode(), location)

    def load(self, command: LoadTestRunCommand) -> TestRunDTO:
        """Loads a testrun, e.g. from disk"""

        location = self._loc(command.storage_location, command.testrun_id)

        json_bytes = self.storage.read(location)
        json_str = json_bytes.decode()
        dto = TestRunDTO.from_json(json_str)

        return dto

    def set_report_ids(self, command: SetReportIdsCommand) -> None:
        """Sets report ids for testrun report and testcase reports and persists testrun"""

        testrun = command.testrun
        testrun.report_id = command.testrun_report.report_id

        location = self._loc(command.storage_location, str(testrun.testrun_id))
        self.storage.write(testrun.to_json().encode(), location)

    def _loc(self, location: LocationDTO, testrun_id: str) -> LocationDTO:
        """Extends base location with filename, checks if storage type is supported"""

        location = location.append(str(testrun_id) + ".json")
        if location.store not in self.storage.supported_storage_types:
            raise StorageTypeUnknownError(f"Storage type {location.store} not supported!")

        return location
