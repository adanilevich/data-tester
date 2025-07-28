from src.dtos import LocationDTO, TestRunDTO, TestRunReportDTO
from src.domain.testcase import (
    ITestRunCommandHandler,
    ExecuteTestRunCommand,
    SetReportIdsCommand,
)


class CliTestRunManager:
    """Runs testcases in batch mode from CLI"""

    def __init__(self, handler: ITestRunCommandHandler, storage_location: LocationDTO):
        self.handler = handler
        self.storage_location = storage_location

    def execute_testrun(self, testrun: TestRunDTO) -> TestRunDTO:
        """Executes a testrun and returns the result as a DTO"""

        command = ExecuteTestRunCommand(
            testrun=testrun,
            storage_location=self.storage_location,
        )

        result = self.handler.run(command=command)

        return result

    def set_report_ids(self, testrun: TestRunDTO, report: TestRunReportDTO) -> None:
        """Sets report ids for testrun and testcase reports and persists testrun"""

        command = SetReportIdsCommand(
            testrun=testrun,
            testrun_report=report,
            storage_location=self.storage_location,
        )

        self.handler.set_report_ids(command=command)
