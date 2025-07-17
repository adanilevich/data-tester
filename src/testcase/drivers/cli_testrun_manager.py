from src.config import Config
from src.dtos import LocationDTO, TestRunDTO, TestRunReportDTO
from src.testcase.ports import (
    ITestRunCommandHandler,
    ExecuteTestRunCommand,
    SetReportIdsCommand,
)


# TODO remove configuration handling from here and put to dependency injection
class CliTestRunManager:
    """Runs testcases in batch mode from CLI"""

    def __init__(self, handler: ITestRunCommandHandler, config: Config):
        self.handler = handler
        self.config = config

        # set storage location
        storage_location_str = self.config.INTERNAL_TESTRUN_LOCATION
        if storage_location_str is None:
            raise ValueError("INTERNAL_TESTRUN_LOCATION is not set")
        self.storage_location = LocationDTO(storage_location_str)

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
