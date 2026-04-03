from src.dtos import TestRunDTO, TestRunReportDTO
from src.domain_ports import (
    ITestRunCommandHandler,
    ExecuteTestRunCommand,
    SetReportIdsCommand,
)


class TestRunDriver:
    # TODO: implement list_testruns method
    """Runs testcases in batch mode"""

    def __init__(
        self, handler: ITestRunCommandHandler
    ):
        self.handler = handler

    def execute_testrun(
        self, testrun: TestRunDTO
    ) -> TestRunDTO:
        """Executes a testrun and returns the result"""

        command = ExecuteTestRunCommand(testrun=testrun)
        result = self.handler.execute_testrun(command=command)

        return result

    def set_report_ids(
        self,
        testrun: TestRunDTO,
        report: TestRunReportDTO,
    ) -> None:
        """Sets report ids for testrun and testcase reports
        and persists testrun"""

        command = SetReportIdsCommand(
            testrun=testrun,
            testrun_report=report,
        )
        self.handler.set_report_ids(command=command)
