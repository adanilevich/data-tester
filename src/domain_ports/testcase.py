from abc import ABC, abstractmethod

from src.dtos import (
    DTO,
    TestRunDTO,
    TestRunReportDTO,
)


class ExecuteTestRunCommand(DTO):
    testrun: TestRunDTO


class SaveTestRunCommand(DTO):
    testrun: TestRunDTO


class LoadTestRunCommand(DTO):
    testrun_id: str


class SetReportIdsCommand(DTO):
    testrun_report: TestRunReportDTO
    testrun: TestRunDTO

#TODO: implement a ListTestRunsCommand to list by domain and optionally date
#TODO implement list_test_runs method

class ITestRunCommandHandler(ABC):
    """Abstract interface to execute testcases"""

    @abstractmethod
    def execute_testrun(
        self, command: ExecuteTestRunCommand
    ) -> TestRunDTO:
        """Implement this method to execute testcases"""

    @abstractmethod
    def save_testrun(
        self, command: SaveTestRunCommand
    ) -> None:
        """Implement this method to save testrun results"""

    @abstractmethod
    def load_testrun(
        self, command: LoadTestRunCommand
    ) -> TestRunDTO:
        """Implement this method to load testrun results"""

    @abstractmethod
    def set_report_ids(
        self, command: SetReportIdsCommand
    ) -> None:
        """
        Set report ids from testrun report and testcase reports
        and persist testrun.
        """
