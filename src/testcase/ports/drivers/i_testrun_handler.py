from abc import ABC, abstractmethod

from src.dtos import (
    DTO,
    LocationDTO,
    TestRunDTO,
    TestRunReportDTO,
)


class ExecuteTestRunCommand(DTO):
    testrun: TestRunDTO  # defition of testrun to be executed
    storage_location: LocationDTO  # location to store (intermediate) testrun results


class SaveTestRunCommand(DTO):
    testrun: TestRunDTO  # defition of testrun to be executed
    storage_location: LocationDTO  # location to store (intermediate) testrun results


class LoadTestRunCommand(DTO):
    testrun_id: str  # id of testrun to be loaded
    storage_location: LocationDTO  # location to load testrun results from


class SetReportIdsCommand(DTO):
    testrun_report: TestRunReportDTO  # testreport to extract ids from
    testrun: TestRunDTO  # testrun to be updated with report ids
    storage_location: LocationDTO  # location to store testrun results


class ITestRunCommandHandler(ABC):
    """Abstract interface to execute testcases"""

    @abstractmethod
    def run(self, command: ExecuteTestRunCommand) -> TestRunDTO:
        """Implement this method to execute testcases"""

    @abstractmethod
    def save(self, commands: SaveTestRunCommand) -> None:
        """Implement this method to save testrun results, e.g. to disk"""

    @abstractmethod
    def load(self, commands: LoadTestRunCommand) -> TestRunDTO:
        """Implement this method to load testrun results, e.g. from disk"""

    @abstractmethod
    def set_report_ids(self, command: SetReportIdsCommand) -> None:
        """
        Implement this method to set report ids from testrun report and testcase reports
        and persist testrun. This is done for cross-reference between testrun and reports.
        """
